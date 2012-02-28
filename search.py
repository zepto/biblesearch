#!/usr/bin/env python
# vim: sw=4:ts=4:sts=4:fdm=indent:fdl=0:
# -*- coding: UTF8 -*-
#
# A sword KJV indexed search module.
# Copyright (C) 2011 Josiah Gordon <josiahg@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


""" KJV indexer and search modules.

BibleSearch:  Can index and search the 'KJV' sword module using different types of searches, including the following:
    Strongs number search       -   Searches for all verses containing either
                                    the phrase strongs phrase, any strongs
                                    number or a superset of the strongs
                                    numbers.
    Morphological tags search   -   Same as the strongs...
    Word or phrase search       -   Same as the strongs...
    Regular expression search   -   Searches the whole Bible using the provided
                                    regular expression.

"""

from sys import argv, exit, stderr
from optparse import OptionParser
from time import strftime, mktime, localtime
from textwrap import wrap, fill, TextWrapper
from struct import unpack
from termios import TIOCGWINSZ
from fcntl import ioctl
from collections import defaultdict
from tarfile import TarFile, TarInfo
from io import BytesIO
import dbm
import os
import json
import gzip
import re
import locale

import Sword

# Key function used to sort a list of verse references.
sort_key = lambda r: Sword.VerseKey(r).Index()

def get_encoding():
    """ Figure out the encoding to use for strings.

    """

    # Hopefully get the correct encoding to use.
    lang, enc = locale.getlocale()
    if not lang or lang == 'C':
        encoding = 'ascii'
    else:
        encoding = enc

    return encoding

def parse_range(ref_str):
    """ Returns a set of verse references in the ranges provided.

    """

    # First split the string at all the spaces.
    ref_list = ref_str.split()
    # Then join it with commas to make sure it is formated the way we
    # want, then split it again at the commas to retrieve the seperate
    # ranges or verses.
    ref_list = ','.join(ref_list).split(',')
    verse_set = set()
    for ref_range in ref_list:
        # Make sure the list is sorted in ascending order, so the range
        # isn't broken.
        range_list = sorted(ref_range.split('-'), key=sort_key)
        if len(range_list) == 2:
            # Valid ranges are only between two verses.
            verse_set.update(VerseIter(*range_list))
        else:
            # All others are added as seperate verses.
            verse_set.update(parse_verse_list(range_list))

    return verse_set

def set_from_ref(book, verse_g):
    """ Build a set from the book and a group of verse/chap:verses

    """

    ref_set = set()

    if verse_g.isdigit():
        ref_set.update(ChapterIter(book, verse_g))
        return ref_set

    chap_range_regx = re.compile(r'([\d]?[\s]*\D+)[\s]*([\d,-:]+)$')

    verse_l = verse_g.split(',')
    chap = ''
    start = end = ''

    for i in verse_l:
        if '-' in i:
            t, i = i.split('-')
            if ':' in t:
                chap, t = t.split(':')
            if not chap:
                start = '%s%s:%s' % (book, t, 1)
            else:
                start = '%s%s:%s' % (book, chap, t)
            chap_range_match = chap_range_regx.match(i)
            if chap_range_match:
                book, verse_g = chap_range_match.groups()
                end = set_from_ref(book, verse_g).pop()
        if ':' in i:
            chap, v = i.split(':')
        else:
            if not chap:
                chap, v = i, 1
            else:
                v = i
        if start:
            if not end:
                end = '%s%s:%s' % (book, chap, v)
            ref_set.update(VerseIter(start, end))
            start = end = ''
        else:
            ref_set.add('%s%s:%s' % (book, chap, v))
    return ref_set

def parse_verse_range(verse_ref_list):
    """ Uses VerseKey ParseVerseList to parse the reference list.  Then it
    parses the range text output and returns a set of verse references in
    that range.

    """

    # Make the argument a parseable string.
    if isinstance(verse_ref_list, str):
        verse_ref_str = verse_ref_list
    else:
        verse_ref_str = ' '.join(verse_ref_list)
    verse_key = Sword.VerseKey()

    # Parse the list. 
    # args: verse_list, default_key, expand_range, chapter_as_verse?
    verse_list = verse_key.ParseVerseList(verse_ref_str, 'Genesis 1:1', True,
                                          False)

    # Get the nice range text.
    range_text = verse_list.getRangeText().strip()
    if not any(range_text):
        return set()
    # Split it into ranges and single verses.
    range_list = range_text.split(';')
    verse_set = set()
    for verse_range in range_list:
        # Split the ranges.
        split_range = verse_range.split('-')
        # Check if it was a single verse or a range.
        if len(split_range) == 2:
            # Add the range.
            verse_set.update(VerseIter(*split_range))
        else:
            # Add the single verse.
            #verse = split_range[0]
            #if verse
            verse_set.add(split_range[0])
    # Return range set.
    return verse_set

def parse_verse_list(verse_ref_list):
    """ Returns a valid list of verse references from the supplied list.
    If just a book name is in the list that entire book is added.

    """

    # Match a book chapter:verse reference.
    chap_verse_regx = re.compile(r'([\d]?[\s]*\D+)[\s]*(\d+):(\d+[,\-:\d+]*)')
    # Match a book chapter reference.
    chap_regx = re.compile(r'([\d]?[\s]*\D+)[\s]*(\d+)')
    verse_set = set()
    for ref in verse_ref_list:
        ref = ''.join(ref)
        chap_verse_m = chap_verse_regx.match(ref)
        if chap_verse_m:
            #verse_set.add(Sword.VerseKey(ref).getText())
            book, chap, verses = chap_verse_m.groups()
            print(chap_verse_m.groups(), ref)
            if ',' in verses:
                for verse in verses.split(','):
                    new_ref = '%s%s:%s' % (book, chap, verse)
                    verse_set.add(Sword.VerseKey(new_ref).getText())
            else:
                first, last = verses.split('-')
                print(first, last)
                exit()
                start = '%s%s:%s' % (book, chap, first)
                if ':' in last:
                    end = '%s%s' % (book, last)
                else:
                    end = '%s%s:%s' % (book, chap, last)
                verse_set.update(VerseIter(start, end))
            continue
        book_chap = chap_regx.match(ref)
        if book_chap:
            # Only a book and chapter were given so we get that entire
            # chapter.
            book, chap = book_chap.groups()
            verse_set.update(ChapterIter(book, chap))
        else:
            # No verse or chapter were given so we will get the entire
            # book.
            verse_set.update(BookIter(ref))

    return verse_set

def lookup_verses(verse_ref_list, range_str=''):
    """ Return a list of valid verse refrences.

    """

    if range_str:
        # Parse the range string.
        range_set = parse_verse_range(range_str)
    else:
        range_set = set()

    verse_set = parse_verse_range(verse_ref_list)

    # Combine and return a set of verses.
    return VerseList(verse_set.union(range_set))

def add_context(ref_set, count=1):
    """ Add count number of verses before and after each reference.

    """

    # Make a copy to work on.
    clone_set = set(ref_set)
    for ref in ref_set:
        start = Sword.VerseKey(ref)
        end = Sword.VerseKey(ref)
        # Pass the beginning of the book.
        start.decrement()
        start.decrement(count - 1)
        # Pass the end of the book.
        end.increment()
        end.increment(count - 1)
        clone_set.update(VerseIter(start, end))

    return clone_set

def screen_size():
    """ Returns a tuple containing the hight and width of the screen in
    characters (i.e. (25, 80)).

    """

    get_size = lambda fd: unpack("hh", ioctl(fd, TIOCGWINSZ, '0000'))
    try:
        for i in [0, 1, 2]:
            return get_size(i)
    except Exception as err:
        try:
            with os.open(os.ctermid(), os.O_RDONLY) as term_fd:
                return get_size(term_fd)
        except:
            return (25, 80)


class Lookup(object):
    """ A generic object to lookup refrences in differend sword modules.

    """

    def __init__(self, module_name='KJV', markup=Sword.FMT_PLAIN):
        """ Setup the module to look up information in.

        """

        markup = Sword.MarkupFilterMgr(markup)
        
        # We don't own this or it will segfault.
        markup.thisown = False
        self._library = Sword.SWMgr(markup)
        self._module = self._library.getModule(module_name)

    def get_text(self, key):
        """ Get the text at the given key in the module.
        i.e. get_text('3778') returns the greek strongs.

        """

        self._module.setKey(Sword.SWKey(key))
        return fill(self._module.RenderText(), screen_size()[1])


class SortedVerseTuple(tuple):
    """ An immutable set of sorted verse references.

    """

    def __init__(self, reference_set=set()):
        """ Initialize the set.

        """

        self._sorted_list = sorted(reference_set, key=sort_key)
        super(VerseTuple, self).__init__(self._sorted_list)


class VerseList(object):
    """ A container for holding and rendering sets of verses.

    """

    def __init__(self, reference_set=set(), module_name='KJV'):
        """ Holds verse references in a sorted list. 

        """

        self._orig_set = reference_set
        self._set = self._orig_set.copy()

        self._module_name = module_name
        self._provide_context = 0

        self._end = '\n'

        self._strongs = self._morphology = False

        self._strongs_regx = re.compile(r'<([GH]\d*)>')
        self._morph_regx = re.compile(r'\(([A-Z\d-]*)\)')
        strongs_color = '\033[36m'
        morph_color = '\033[35m'
        self._ref_color = '\033[32m'
        self._end_color = '\033[m'

        self._strongs_highlight = '<%s\\1%s>' % (strongs_color, 
                                                 self._end_color)
        self._morph_highlight = '(%s\\1%s)' % (morph_color,
                                               self._end_color)

    def __iter__(self):
        """ Returns an iter over the internal set.

        """

        return iter(sorted(self._set, key=sort_key))

    def __repr__(self):
        """ A representation of this list.

        """

        return sorted(self._set, key=sort_key)

    def __str__(self):
        """ Returns a string of verse reference and text.

        """

        verse_text = self._end.join(self._create_list())
        if '\n' not in self._end:
            verse_text = fill(verse_text, screen_size()[1])
        return verse_text

    def __len__(self):
        """ Return the length of the list.

        """

        return len(self._set)

    @property
    def end(self):
        """ The character(s) to put at the end of each verse.

        """

        return self._end

    @end.setter
    def end(self, value):
        """ Render on only one line.

        """

        self._end = value

    @property
    def strongs(self):
        """ Show Strong's Numbers in formated output.

        """

        return self._strongs

    @strongs.setter
    def strongs(self, value):
        """ Show Strong's Numbers in formated output.

        """

        self._strongs = value

    @property
    def morphology(self):
        """ Show Morphological Tags in formated output.

        """

        return self._morphology

    @morphology.setter
    def morphology(self, value):
        """ Show Morphological Tags in formated output.

        """

        self._morphology = value

    @property
    def context(self):
        """ The number of verses before and after to include in the output.

        """

        return self._provide_context

    @context.setter
    def context(self, value):
        """ The number of verses before and after to include in the output.

        """

        self._set = self._orig_set.copy()
        if value > 0:
            self._set = add_context(self._set, value)

        self._provide_context = value

    def _create_list(self):
        """ Return a list of formated and (if specified) highlighted
        verses.

        """

        if not self:
            return []

        verse_iter = VerseTextIter(iter(self), module=self._module_name)
        verse_iter.morph = self._morphology
        verse_iter.strongs = self._strongs

        verse_list = []
        wrapper = TextWrapper(width=screen_size()[1])

        encoding = get_encoding()

        for verse_ref, verse_text in verse_iter:
            verse_text = verse_text.strip()
            verse_text = self._highlight_text(verse_text)
            # Convoluted way to do it, but first encode the string, then
            # decode it again to put it in the string.  Do this or it will
            # either have an error in non-utf8 environments or it will show
            # ugly characters.  Hasn't been tested thoroughly.
            verse_text = verse_text.encode(encoding, 'ignore')
            verse_text = "%s%s%s: %s" % (self._ref_color, verse_ref.strip(), 
                                           self._end_color,
                                           verse_text.decode(encoding, 
                                                             'ignore'))
            # Make a list of all the 'reference: text' strings.
            if '\n' in self._end:
                verse_text = wrapper.fill(verse_text)
            verse_list.append(verse_text)

        return verse_list

    def _highlight_text(self, verse_text):
        """ Returns a highlighted version of verse_text.  All Strong's
        numbers, and morphological tags are hightlighted.

        """

        verse_text = self._strongs_regx.sub(self._strongs_highlight,
                                            verse_text)
        verse_text = self._morph_regx.sub(self._morph_highlight, verse_text)

        return verse_text


class SearchedList(VerseList):
    """ A VerseList with searched string highlighting.

    """

    def __init__(self, reference_set=set(), highlight_string='', phrase=False,
                 case_sensitive=False, module_name='KJV'):
        """ Setup the verse list. 
            highlight_list  -   A list of words to highlight.
            phrase          -   Highlight phrases.
            case_sensitive  -   Case sensitive highlighting.

        """

        super(SearchedList, self).__init__(reference_set, module_name)


        self._highlight_string = highlight_string
        self._phrase = phrase

        # Everything is ascii.
        self._flags = re.A
        if not case_sensitive:
            # Case insensitive.
            self._flags |= re.I

        highlight_color = '\033[1m'
        self._word_highlight = '\\1%s\\2%s\\3' % (highlight_color, 
                                                  self._end_color)

        self._highlight_regex = None

    def _setup_highlight(self):
        """ Build the regular expression for highlighting.

        """

        if self._strongs or self._morphology:
            # Use an ored list of search terms so at least the
            # indevidual items will be highlighted.  This catches more
            # than the phrase so it doesn't look right.
            self._highlight_string = '|'.join(self._highlight_string.split())
        # Catch each strongs/morph/word in the verse...Seems to work.
        reg_str = r'(\(|<|\b)(%s)(\b|>|\))' % self._highlight_string
        self._highlight_regex = re.compile(reg_str, self._flags)

    def _create_list(self):
        """ Return a list of formated and (if specified) highlighted
        verses.

        """

        if self._highlight_string:
            self._setup_highlight()

        return super(SearchedList, self)._create_list()

    def _highlight_text(self, verse_text):
        """ Returns a highlighted version of verse_text.  All Strong's
        numbers, morphological tags, and the search_text is hightlighted.

        """

        # Highlight the search terms.  Why is this here?
        if self._highlight_regex:
            verse_text = self._highlight_regex.sub(self._word_highlight, 
                                                   verse_text)

        return super(SearchedList, self)._highlight_text(verse_text)


class VerseTextIter(object):
    """ An iterable object for accessing verses in the Bible.  Maybe it will
    be easier maybe not.

    """

    def __init__(self, reference_iter, module='KJV', markup=Sword.FMT_PLAIN):
        """ Initialize.

        """

        markup = Sword.MarkupFilterMgr(markup)
        
        # We don't own this or it will segfault.
        markup.thisown = False
        self._library = Sword.SWMgr(markup)
        self._library.setGlobalOption("Headings", "On")
        self._library.setGlobalOption("Cross-references", "Off")
        self._library.setGlobalOption("Strong's Numbers", "Off")
        self._library.setGlobalOption("Morphological Tags", "Off")
        
        # Strings for finding the heading.
        self._head_str = Sword.SWBuf('Heading')
        self._preverse_str = Sword.SWBuf('Preverse')
        self._canon_str = Sword.SWBuf('canonical')

        self._module = self._library.getModule(module)

        self._ref_iter = reference_iter

    def next(self):
        """ Returns the next verse reference and text.

        """

        return self.__next__()

    def __next__(self):
        """ Returns a tuple of the next verse reference and text.

        """

        # Retrieve the next reference.
        verse_ref = next(self._ref_iter)

        # Set the verse and render the text.
        verse_text = self._get_text(verse_ref)
        self._verse_ref = self._module.getKeyText()

        return (self._verse_ref, verse_text)

    def __iter__(self):
        """ Returns an iterator of self.

        """

        return self

    def _get_text(self, verse_ref):
        """ Returns the verse text.  Override this to produce formatted verse
        text.

        """

        self._module.setKey(Sword.VerseKey(verse_ref))
        verse_text = self._module.RenderText()
        verse_text = '%s %s' % (self._get_heading(), verse_text)
        return verse_text

    def _get_heading(self):
        """ Returns the verse heading if there is one.

        """

        attr_map = self._module.getEntryAttributesMap()
        heading_list = []
        head_str = self._head_str
        preverse_str = self._preverse_str
        canon_str = self._canon_str
        if head_str in attr_map:
            heading_attrs = attr_map[head_str]
            if self._preverse_str in heading_attrs:
                preverse_attrs = heading_attrs[preverse_str]
                for k, attrs in heading_attrs.items():
                    if canon_str in attrs:
                        canonical = (attrs[canon_str].c_str() == 'true')
                    if k in preverse_attrs and canonical:
                        heading_list.append(preverse_attrs[k].c_str())

        if heading_list:
            return self._module.RenderText(''.join(heading_list))
        else:
            return ''

    def _get_options(func):
        """ Wraps the strongs and morph getter properties.

        """

        def wrap_func(self, *args):
            if func.__name__ == 'strongs':
                value = self._library.getGlobalOption("Strong's Numbers")
            else:
                value = self._library.getGlobalOption("Morphological Tags")
            return True if value == 'On' else False

        return wrap_func

    def _set_options(func):
        """ Wraps the strongs and morph setter properties.

        """

        def wrap_func(self, value):
            value = 'On' if value else 'Off'
            if func.__name__ == 'strongs':
                return self._library.setGlobalOption("Strong's Numbers", value)
            else:
                return self._library.setGlobalOption("Morphological Tags",
                                                     value)
        return wrap_func

    @property
    @_get_options
    def strongs(self): pass

    @strongs.setter
    @_set_options
    def strongs(self, value): pass

    @property
    @_get_options
    def morph(self): pass

    @morph.setter
    @_set_options
    def morph(self, value): pass


class FormatVerseTextIter(VerseTextIter):
    """ A Formated verse iter.

    """

    def __init__(self, reference_iter, module='KJV', markup=Sword.FMT_PLAIN):
        """ Initialize.

        """

        super(FormatVerseTextIter, self).__init__(reference_iter, module, markup)

        self._strongs_regx = re.compile(r'<([GH]\d*)>')
        self._morph_regx = re.compile(r'\(([A-Z\d-]*)\)')
        self._ref_color = '\033[32m'
        self._end_color = '\033[m'

        strongs_color = '\033[36m'
        morph_color = '\033[35m'
        self._strongs_highlight = '<%s\\1%s>' % (strongs_color, 
                                                 self._end_color)
        self._morph_highlight = '(%s\\1%s)' % (morph_color,
                                               self._end_color)

        self._enc = get_encoding()

    def _get_text(self, verse_ref):
        """ Returns a formated version of the verse text.

        """

        # First get the original text.
        verse_text = super(FormatVerseTextIter, self)._get_text(verse_ref)

        verse_text = verse_text.strip()
        verse_text = self._highlight_text(verse_text)
        # Convoluted way to do it, but first encode the string, then
        # decode it again to put it in the string.  Do this or it will
        # either have an error in non-utf8 environments or it will show
        # ugly characters.  Hasn't been tested thoroughly.
        verse_text = verse_text.encode(self._enc, 'ignore')
        verse_text = "%s%s%s: %s" % (self._ref_color, verse_ref.strip(), 
                                       self._end_color,
                                       verse_text.decode(self._enc, 
                                                         'ignore'))
        # Make a list of all the 'reference: text' strings.
        if '\n' in self._end:
            verse_text = fill(verse_text, width=screen_size()[1])

        # Return a formated version
        return verse_text

    def _highlight_text(self, verse_text):
        """ Returns a highlighted version of verse_text.  All Strong's
        numbers, and morphological tags are hightlighted.

        """

        verse_text = self._strongs_regx.sub(self._strongs_highlight,
                                            verse_text)
        verse_text = self._morph_regx.sub(self._morph_highlight, verse_text)

        return verse_text


class VerseIter(object):
    """ Iterator of verse references.

    """

    def __init__(self, start, end='Revelation of John 22:21'):
        """ Setup the start and end references of the range.

        """

        start, end = sorted([start, end], key=sort_key)
        self._start = Sword.VerseKey(start)
        self._end = Sword.VerseKey(end)

        self._verse = Sword.VerseKey(start)
        self._verse_ref = ''

    def __next__(self):
        """ Returns the next verse reference.

        """

        # End the iteration when we reach the end of the range.
        if self._verse_ref == self._end.getText():
            raise StopIteration()

        # Get the current verse reference.
        self._verse_ref = self._verse.getText()

        # Load the next verse in the range.
        self._verse.increment()

        # Return only the reference.
        return self._verse_ref

    def __iter__(self):
        """ Returns an iterator of self.

        """

        return self

    def next(self):
        """ Returns the next verse reference.

        """

        return self.__next__()


class BookIter(VerseIter):
    """ Iterates over just one book.

    """

    def __init__(self, book='Genesis'):
        """ Setup iterator.

        """

        start = Sword.VerseKey('%s 1:1' % book)
        end = Sword.VerseKey(start.clone())
        end.setChapter(end.getChapterMax())
        end.setVerse(end.getVerseMax())

        super(BookIter, self).__init__(start, end)


class ChapterIter(VerseIter):
    """ Iterates over just one chapter.

    """

    def __init__(self, book='Genesis', chapter=1):
        """ Setup iterator.

        """

        start = Sword.VerseKey('%s %s:1' % (book, chapter))
        end = Sword.VerseKey(start.clone())
        end.setVerse(end.getVerseMax())

        super(ChapterIter, self).__init__(start, end)


class IndexTar(TarFile):
    """ A tarfile object to write directly to a tar file bypassing the 
    filesystem.  It uses a BytesIO stream as the file object when writing
    and the standard tarfile.ExFileObject for reading.  It as to encode any
    strings to bytes before writing, and decode them after reading.

    """

    def __init__(self, name=None, mode='r', compressionlevel=9):
        """ Create a gzip file to use as the fileobj to TarFile.

        """

        if ':' in mode:
            mode = mode[0]
            fileobj = open(name, mode + b)
            gzfile = gzip.GzipFile(name, mode, compresionlevel, fileobj)
        else:
            gzfile = None
        super(IndexTar, self).__init__(name, mode, gzfile) 

    def _encoding(self):
        """ Figure out the encoding to use for strings.

        """

        # Hopefully get the correct encoding to use.
        lang, enc = locale.getlocale()
        if not lang or lang == 'C':
            encoding = 'ascii'
        else:
            encoding = enc

        return encoding

    def write_string(self, name, str_buffer):
        """ Write the buffer string to the tar file under the given name.

        """

        # Encode the buffer into bytes. 
        byte_buffer = str_buffer.encode(self._encoding(), 'replace')

        # Create a tarinfo for a file.
        tarinfo = TarInfo(name)
        tarinfo.size = len(byte_buffer)
        tarinfo.mtime = int(mktime(localtime()))

        # Fill the byte io object.
        byte_io = BytesIO()
        byte_io.write(byte_buffer)
        byte_io.seek(0)

        # Write buffer to tar file.
        self.addfile(tarinfo=tarinfo, fileobj=byte_io)
        byte_io.close()

        return len(str_buffer)

    def read_string(self, name):
        """ Read the named buffer out of the tarfile.

        """

        try:
            # Get a file object to read the data from.
            ex_file = self.extractfile(name)
            # Read bytes from the tar.
            byte_buffer = ex_file.read()
        except Exception as err:
            print("Error reading %s: %s" % (name, err), file=stderr)
            return None

        # Decode the buffer back into a string, and return it.
        return byte_buffer.decode(self._encoding(), 'replace')

    def __enter__(self):
        """ Add the functionality to use pythons with statement.

        """

        try:
            return self
        except Exception as err:
            print("Error in __enter__: %s" % err, file=stderr)
            return None

    def __exit__(self, exc_type, exc_value, traceback):
        """ Close the file and exit.

        """

        try:
            self.close()
            if exc_type:
                return False
            return True
        except Exception as err:
            print("Error in __exit__: %s" % err, file=stderr)
            return False


class IndexDbm(object):
    """ A dbm database writer.

    """


    def __init__(self, name=None, mode='r'):
        """ Create a databse.

        """

        self._dbm = dbm.open(name, mode)

    def _encoding(self):
        """ Figure out the encoding to use for strings.

        """

        # Hopefully get the correct encoding to use.
        lang, enc = locale.getlocale()
        if not lang or lang == 'C':
            encoding = 'ascii'
        else:
            encoding = enc

        return encoding

    def write_list(self, name, lst):
        """ Write the list database under the given name.

        """

        # Encode the buffer into bytes. 
        byte_buffer = json.dumps(lst).encode(self._encoding(), 'replace')

        # Write buffer to tar file.
        self._dbm[name] = byte_buffer

        return len(byte_buffer)

    def write_dict(self, dic):
        """ Write a dictionary to the database.
        
        """

        for k, v in dic.items():
            self.write_list(k, v)

        return len(dic)

    def read_list(self, name):
        """ Read the named list out of the database.

        """

        try:
            str_buffer = self._dbm[name].decode(self._encoding(), 'replace')
            lst = json.loads(str_buffer)
        except Exception as err:
            print("Error reading %s: %s" % (name, err), file=stderr)
            return None

        return lst


    def read_dict(self):
        """ Read out the entire dictionary.

        """

        temp_dict = {}
        key = self._dbm.firstkey()
        while key:
            temp_dict[key] = self._dbm[key]
            key = self._dbm.nextkey(key)

        return temp_dict

    def __enter__(self):
        """ Add the functionality to use pythons with statement.

        """

        try:
            return self
        except Exception as err:
            print("Error in __enter__: %s" % err, file=stderr)
            return None

    def __exit__(self, exc_type, exc_value, traceback):
        """ Close the file and exit.

        """

        try:
            self._dbm.close()
            if exc_type:
                return False
            return True
        except Exception as err:
            print("Error in __exit__: %s" % err, file=stderr)
            return False


class IndexBible(object):
    """ Index the bible by Strong's Numbers, Morphological Tags, and words.

    """

    def __init__(self, module='KJV'):
        """ Initialize the index dicts.

        """
        
        self._module_name = module

        # Remove morphological and strongs information.
        self._cleanup_regx = re.compile(r' (<([GH]\d*)>|\(([A-Z\d-]*)\))')

        self._non_alnum_regx = re.compile(r'\W')
        self._fix_regx = re.compile(r'\s+')
        self._strongs_regx = re.compile(r'<([GH]\d*)>')
        self._morph_regx = re.compile(r'\(([A-Z\d-]*)\)')

        self._strongs_dict = defaultdict(list)
        self._morph_dict = defaultdict(list)
        self._word_dict = defaultdict(list)
        self._case_word_dict = defaultdict(list)

        self._index_dict = {
                'strongs.dump': self._strongs_dict,
                'morph.dump': self._morph_dict,
                'word.dump': self._word_dict,
                'case_word.dump': self._case_word_dict
                }

    def _book_gen(self):
        """ A Generator function that yields book names in order.

        """

        # Yield a list of all the book names in the bible.
        verse_key = Sword.VerseKey('Genesis 1:1')
        for testament in [1, 2]:
            for book in range(1, verse_key.bookCount(testament) + 1):
                yield(verse_key.bookName(testament, book))
                
    def _index_strongs(self, verse_ref, verse_text):
        """ Update the modules strongs dictionary from the verse text.

        """

        strongs_list = set(self._strongs_regx.findall(verse_text))
        for strongs_num in strongs_list:
            self._strongs_dict[strongs_num].append(verse_ref)

    def _index_morph(self, verse_ref, verse_text):
        """ Update the modules mophological dictionary from the verse text.

        """

        morph_list = set(self._morph_regx.findall(verse_text))
        for morph_num in morph_list:
            self._morph_dict[morph_num].append(verse_ref)

    def _index_words(self, verse_ref, verse_text):
        """ Update the modules word dictionary from the verse text.

        """

        # Remove all the morphological and strongs stuff.
        clean_text = self._cleanup_regx.sub('', verse_text)
        # Remove any non-alpha-numeric stuff.
        clean_text = self._non_alnum_regx.sub(' ', clean_text) 
        # Replace runs of one or more spaces with just a single space.
        clean_text = self._fix_regx.sub(' ', clean_text).strip()

        # Remove the strongs and morphological stuff in such a way that
        # split words are still split (i.e. where in, instead of wherein).
        # So there are split versions and non-split versions just to be sure
        # that the correct one is in there.
        verse_text = self._strongs_regx.sub('', verse_text)
        verse_text = self._morph_regx.sub('', verse_text)

        # Strip out all unicode so we can search correctly.
        verse_text = verse_text.encode('ascii', 'ignore')
        verse_text = verse_text.decode('ascii', 'ignore')
        verse_text = self._non_alnum_regx.sub(' ', verse_text) 
        verse_text = self._fix_regx.sub(' ', verse_text).strip()

        # Save the case insesitive index.
        verse_set = set(verse_text.lower().split())
        verse_set.update(set(clean_text.lower().split()))
        
        for word in verse_set:
            if word:
                self._word_dict[word].append(verse_ref)

        # Include the capitalized words for case sensitive search.
        case_verse_set = set(verse_text.split())
        case_verse_set.update(set(clean_text.split()))

        for word in case_verse_set:
            if word:
                self._case_word_dict[word].append(verse_ref)

    def _index_book(self, book_name="Genesis"):
        """ Creates indexes for strongs, morphology and words.

        """

        book_iter = BookIter(book_name)
        verse_iter = VerseTextIter(book_iter, self._module_name)
        verse_iter.strongs = verse_iter.morph = True

        for verse_ref, verse_text in verse_iter:
            print('\033[%dD\033[KIndexing...%s' % \
                    (len(verse_ref) + 20, verse_ref), file=stderr, end='')
            stderr.flush()

            self._index_strongs(verse_ref, verse_text)
            self._index_morph(verse_ref, verse_text)
            self._index_words(verse_ref, verse_text)

    def build_index(self):
        """ Create index files of the bible for strongs numbers, 
        morphological tags, and case (in)sensitive words.

        """

        print("Indexing %s could take a while..." % self._module_name, 
              file=stderr)
        for book in self._book_gen():
            self._index_book(book)

        print('\nDone.', file=stderr)

    def write_indexes(self):
        """ Write all the index dictionaries to their respective files.  If
        Any of the dictionaries is empty, then build the index.

        The indexes are just json-ed dictionaries.  The keys are the indexed
        items and the values are the verse references that contain the key.

        """

        # Build the index if it's not already built.
        if not self._word_dict or not self._strongs_dict or not \
                self._morph_dict:
            self.build_index()
            #self._word_dict['hello'] = ['this', 'is', 'a', 'test']
        #with IndexTar('%s.tar' % self._module_name, 'w') as index_file:
            #for name, dic in self._index_dict.items():
                #print("Writing %s..." % name, file=stderr)
                #index_file.write_string(name, json.dumps(dic, indent=4))
        #for name, dic in self._index_dict.items():
            #print("Writing %s..." % name, file=stderr)
            #with open(name, 'w') as index_file:
                #json.dump(index_file, dic, indent=4)

        for name, dic in self._index_dict.items():
            with IndexDbm('%s.dbm' % name, 'nf') as index_file:
                print("Writing %s..." % name, file=stderr)
                index_file.write_dict(dic)


class BibleSearch(object):
    """ Search the bible for a phrase or any of the following:
        
        Strongs numbers
        Morphological tags
        Words

    """

    def __init__(self, case_sensitive=False, strongs=False, morph=False, 
                 no_punctuation=False, module='KJV'):
        """ Initialize the module and library information.

        """

        self._case_sensitive = case_sensitive
        self._strongs = strongs
        self._morph = morph
        self._no_punct = no_punctuation
        self._module_name = module

        # Cleanup regular expressions.
        self._non_alnum_regx = re.compile(r'\W')
        self._fix_regx = re.compile(r'\s+')

        # Searching regular expressions.
        self._strongs_regx = re.compile(r'<([GH]\d*)>')
        self._morph_regx = re.compile(r'\(([A-Z\d-]*)\)')

        # The range to search in.
        self._range_set = set()

        if not strongs and not morph:
            filename = 'word.dump' if not case_sensitive else 'case_word.dump'
        else:
            filename = 'strongs.dump' if strongs else 'morph.dump'
        self._filename = filename

        self._indexed_dict = {}

    def _clean_text(self, text):
        """ Return a clean (only alphanumeric) text of the provided string.

        """

        # Do we have to use two regular expressions to do this.
        # Replace all non-alphanumeric characters with a space.
        temp_text = self._non_alnum_regx.sub(' ', text) 
        # Replace one or more spaces with one space.
        clean_text = self._fix_regx.sub(' ', temp_text)

        return clean_text.strip()

    def _verse_list_iter(self, verse_ref_set):
        """ Returns an iterator over a sorted version of verse_ref_set.

        """

        # Speed up the iteration by first sorting the range.
        return iter(sorted(verse_ref_set, key=sort_key))

    def find(self, search_list, phrase=False, search_any=False, regex=False,
             search_range=''):
        """ find(search_list, phrase=False, search_any=False, regex=False,
        search_range=None) -> Search for the items in the provided 
        search_list. 
                
                default     -   Find verses that have all the search
                                terms.
                phrase      -   Search for the search list as a phrase
                search_any  -   Find all verses that have any of the search
                                items or common words.
                regex       -   Use the search list as a regular expression
                search_range-   Search only in the specified range.

        """

        if search_range:
            self._range_set = parse_verse_range(search_range)

        if regex:
            result_set = self._regex_search(' '.join(search_list))
        else:
            # Get rid of any non-alphanumeric characters from the search
            # string.
            if not self._strongs and not self._morph:
                search_str = self._clean_text(' '.join(search_list)).strip()
                if not self._case_sensitive:
                    search_str = search_str.lower()
            else:
                search_str = ' '.join(search_list).upper().strip()
            # Load the index.
            self._indexed_dict = self._load_index(set(search_str.split())) 
            result_set = self._search(search_str, phrase, search_any)

        count = len(result_set)
        print("Found %s verse%s." % (count, 's' if count != 1 else ''), 
              file=stderr)

        if phrase or regex:
            # Highlight the phrase.  Doesn't work if there were strange
            # characters in the destination verse.
            highlight_string = ' '.join(' '.join(search_list).split())
        else:
            highlight_string = '|'.join(' '.join(search_list).split())

        return SearchedList(result_set, highlight_string, phrase,
                         self._case_sensitive)

    def _load_index(self, search_set):
        """ _load_index(search_set) -> Load and return a dictionary from one of
        the index files.

        """

        filename = self._filename
        print("Loading %s" % filename, file=stderr)
        index_dict = {}
        with IndexDbm('%s.dbm' % filename, 'r') as dbm_dict:
            for i in search_set:
                index_dict[i] = dbm_dict.read_list(i)
        return index_dict
        try:
            with IndexTar('%s.tar' % self._module_name, 'r') as index_file:
                index_dict = json.loads(index_file.read_string(filename))
            #with open(filename, 'r') as index_file:
                #index_dict =json.load(index_file)
        except IOError as err:
            print("Error loading file %s: %s" % (filename, err), file=stderr)

        return index_dict

    def _search(self, search_str, phrase, search_any):
        """ A generic search function used for words, phrases, strongs, and
        morphology.

        """

        search_list = sorted(set(search_str.split()), 
                             key=lambda i: len(self._indexed_dict.get(i, [])))

        if not phrase or len(search_list) == 1:
            if not search_any:
                print('Searching for "%s"...' % \
                        ' AND '.join(search_list), end='', file=stderr)
                found_verses = self._set_intersect(search_list) 
            else:
                print('Searching for "%s"...' % \
                        ' OR '.join(search_list), end='', file=stderr)
                found_verses = self._set_union(search_list)
            if self._range_set:
                found_verses = found_verses.intersection(self._range_set)
        else:
            print('Searching for phrase "%s"...' % search_str, end='', 
                  file=stderr)
            stderr.flush()
            verse_list = self._set_intersect(search_list)
            found_verses = self._phrase_search(search_str, verse_list)

        print("Done.", file=stderr)

        return found_verses

    def _phrase_search(self, search_str, ref_list):
        """ Searches for the search phrase in the verses.

        """

        if self._range_set:
            # Make sure not to waste time searching through out of range
            # verses.  This gets only the items in both sets.
            ref_list = self._range_set.intersection(ref_list)

        print("Creating verse iter...", end='', file=stderr)
        stderr.flush()
        verse_iter = VerseTextIter(self._verse_list_iter(set(ref_list)))
        verse_iter.strongs = self._strongs
        verse_iter.morph = self._morph
        print("Done...", end='', file=stderr)
        stderr.flush()

        search_list = search_str.split()
        # Get this out here so we can maybe save a little time later.
        search_len = len(search_list)
        found_set = set()
        for verse_ref, verse_text in verse_iter:
            # This slows it down.
            #print('\033[%dD\033[KSearching...%s' % \
                    #(len(verse_ref) + 20, verse_ref), end='', file=stderr)
            #stderr.flush()
            if self._strongs:
                verse_list = self._strongs_regx.findall(verse_text)
            elif self._morph:
                verse_list = self._morph_regx.findall(verse_text)
            else:
                if not self._case_sensitive:
                    verse_text = verse_text.lower()
                verse_list = self._non_alnum_regx.sub(' ', verse_text).split()

            if search_list[0] not in verse_list:
                continue

            # This one seems faster sometimes.
            if ' %s ' % search_str in ' %s ' % ' '.join(verse_list):
                found_set.add(verse_ref)
            continue

            # Jump from slice to slice.  Only looking at slices that are the
            # size of the search string, and that begin with the first item in
            # the search string.
            cur_index = -1
            # No point looking any further since the first item in the in the
            # search list is not in the remaining slice.
            while search_list[0] in verse_list[cur_index + 1:]:
                # The index of the start of the next slice is the next index
                # that of the first search term.
                cur_index = verse_list.index(search_list[0], cur_index + 1)
                # Check the next slice.
                if search_list == verse_list[cur_index: cur_index + search_len]:
                    found_set.add(verse_ref)
        return found_set

    def _set_intersect(self, search_list):
        """ Returns a set with only the verses that contain all the items in
        search_list.

        """


        # There may be a better way to do this.  Start with a set of the
        # verses containing the least common item, then update it with the
        # intersections it has with the sets of the remaining words.
        # Effectively removing any verse from the original set that does not
        # contain all the other search items.
        least_common_set = set(self._indexed_dict.get(search_list.pop(0), []))
        if least_common_set:
            for item in search_list:
                verse_list = self._indexed_dict.get(item, [])
                least_common_set.intersection_update(verse_list)

        return least_common_set

    def _set_union(self, search_list):
        """ Returns a set with all the verses that contain each item in
        search_list.

        """

        # Create one big set of all the verses that contain any one or more of
        # the search items.
        verse_set = set(self._indexed_dict.get(search_list.pop(0), []))
        for item in search_list:
            verse_set.update(self._indexed_dict.get(item, []))
        return verse_set

    def _regex_search(self, search_str):
        """ Uses the search_str as a regular expression to search the bible and
        returns a list of matching verses.

        """

        print("Searching using the regular expression '%s'" % search_str,
              file=stderr)

        found_verses = set()
        flags = re.I if not self._case_sensitive else 0
        search_regx = re.compile(r'%s' % search_str, flags)

        if self._range_set:
            verse_iter = VerseTextIter(self._verse_list_iter(self._range_set))
        else:
            verse_iter = VerseTextIter(VerseIter('Genesis 1:1'))
        strongs = verse_iter.strongs = self._strongs
        morph = verse_iter.morph = self._morph

        for verse_ref, verse_text in verse_iter:
            print('\033[%dD\033[KSearching...%s' % \
                    (len(verse_ref) + 20, verse_ref), file=stderr, end='')
            stderr.flush()

            if search_regx.search(verse_text):
                found_verses.add(verse_ref)
            elif not strongs and not morph and self._no_punct:
                clean_verse_text = self._clean_text(verse_text)
                if search_regx.search(clean_verse_text):
                    found_verses.add(verse_ref)

        print("...Done.", file=stderr)

        return found_verses


if __name__ == '__main__':
    parser = OptionParser(description="Bible search.")
    parser.add_option('-i', '--index', action='store_true', default=False,
                        help='(Re-)build the search index.',
                        dest='build_index')
    parser.add_option('-d', '--daily', action='store',
                      default='', help='Lookup the devotional in \
                            Bagsters Daily light.', dest='daily')
    parser.add_option('-l', '--lookup', action='store_true', default=False,
                        help='Lookup verses by reference.', dest='lookup')
    parser.add_option('-o', '--verse_ref', action='store_true', default=False,
                        help='Show only a sorted list of references', 
                        dest='list_only')
    parser.add_option('-p', '--phrase', action='store_true', default=False,
                        help='Search for phrase.', dest='phrase')
    parser.add_option('-s', '--strongs', action='store_true', default=False,
                        help='Search for strongs numbers.', dest='strongs')
    parser.add_option('-m', '--morph', action='store_true', default=False,
                        help='Search for morphological tags.', dest='morph')
    parser.add_option('-n', '--numbers', action='store_true', default=False,
                        help="Include the Strong's numbers in the verse \
                              output.", dest='show_numbers')
    parser.add_option('-t', '--tags', action='store_true', default=False,
                        help="Include the Morphological tags in the verse \
                              output.", dest='show_tags')
    parser.add_option('-a', '--any', action='store_true', default=False,
                        help='Search any word in the search string',
                        dest='search_any')
    parser.add_option('-r', '--regex', action='store_true', default=False,
                        help='Use the search string as a regular expression.',
                        dest='regex')
    parser.add_option('-c', '--case', action='store_true', default=False,
                        help='Case sensitive, only for multi-word phrase.',
                        dest='case')
    parser.add_option('', '--range', action='store', default='',
                        help='Range to search in..', dest='search_range')
    parser.add_option('', '--lookup-strongs', action='store', default='',
                        help='Lookup a strongs number.', dest='strongs_lookup')
    parser.add_option('', '--lookup-morphology', action='store', default='',
                        help='Lookup a morphology tag.', dest='morph_lookup')
    parser.add_option('', '--one-line', action='store_true', default=False,
                        help='Print all the verses on one line.', 
                        dest='one_line')
    parser.add_option('', '--context', action='store', default=0, type="int",
                        help='The number of verses before and after the match\
                              to include in the output.',
                        dest='context')
    parser.add_option('-q', '--quiet', action='store_true', default=False,
                        help='Only print the number of verses found.', 
                        dest='quiet')

    options, args = parser.parse_args()
    if args or options.build_index or options.search_range or \
            options.daily or options.strongs_lookup or options.morph_lookup:
        options_dict = options.__dict__.copy()
        daily = options_dict.pop('daily')
        if daily:
            if daily == 'today':
                daily = strftime('%m.%d')
            test = Lookup('Daily')
            print('\n'.join(test.get_text(daily).replace('Morning:',
                  'Morning:\n').partition('Evening:')))
            exit(0)
        strongs_lookup = options_dict.pop('strongs_lookup')
        morph_lookup = options_dict.pop('morph_lookup')
        if strongs_lookup:
            if strongs_lookup.upper().startswith('G'):
                mod = 'StrongsRealGreek'
            else:
                mod = 'StrongsRealHebrew'
            strongs_l = Lookup(mod)
            print(strongs_l.get_text(strongs_lookup[1:]))
            exit(0)
        if morph_lookup:
            morph_l = Lookup("Packard")
            print(morph_l.get_text(morph_lookup))
            exit(0)
        if options_dict.pop('build_index'):
            indexer = IndexBible()
            indexer.write_indexes()
            exit(0)
        one_line = options_dict.pop('one_line')
        quiet = options_dict.pop('quiet')
        list_only = options_dict.pop('list_only')
        lookup = options_dict.pop('lookup')
        context = options_dict.pop('context')
        show_strongs = options_dict.pop('show_numbers')
        show_morph = options_dict.pop('show_tags')
        if not args:
            verse_list = lookup_verses('', options.search_range)
        elif not lookup:
            search = BibleSearch(options_dict.pop('case'),
                                 options_dict.pop('strongs'),
                                 options_dict.pop('morph'))
            verse_list = search.find(args, **options_dict)
        else:
            verse_list = lookup_verses(args, options.search_range)
        if not quiet:
            verse_list.context = context
            verse_list.end = ' ' if one_line else '\n'
            verse_list.strongs = show_strongs or options.strongs
            verse_list.morphology = show_morph or options.morph

            print()
            if list_only:
                for i in verse_list:
                    print(i)
                print()
            else:
                print(verse_list)
    else:
        parser.print_help()
