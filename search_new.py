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
from functools import wraps
from optparse import OptionParser
from time import strftime, mktime, localtime
from textwrap import wrap, fill, TextWrapper, dedent
from struct import unpack
from termios import TIOCGWINSZ
from fcntl import ioctl
from collections import defaultdict
from tarfile import TarFile, TarInfo
from io import BytesIO
from contextlib import closing
from itertools import product
import dbm
#import shelve
import os
import json
import gzip
import re
import locale

import Sword

def book_gen():
    """ A Generator function that yields book names in order.

    """

    # Yield a list of all the book names in the bible.
    verse_key = Sword.VerseKey('Genesis 1:1')
    for testament in [1, 2]:
        for book in range(1, verse_key.bookCount(testament) + 1):
            yield(verse_key.bookName(testament, book))

book_list = list(book_gen())

# Key function used to sort a list of verse references.
def sort_key(ref):
    """ Sort verses by book.

    """

    try:
        book, chap_verse = ref.rsplit(' ', 1)
        chap, verse = chap_verse.split(':')
        val = '%02d%03d%03d' % (int(book_list.index(book)), int(chap), int(verse))
        return val
    except:
        print(ref)
        exit()

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

def parse_verse_range(verse_ref_list):
    """ Uses VerseKey ParseVerseList to parse the reference list.

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

    verse_set = set()
    for i in range(verse_list.Count()):
        key = Sword.VerseKey(verse_list.GetElement(i))
        if key:
            upper = key.UpperBound().getText()
            lower = key.LowerBound().getText()
            if upper != lower:
                verse_set.update(VerseIter(lower, upper))
            else:
                verse_set.add(key.getText())

    return verse_set

def add_context(ref_set, count=0):
    """ Add count number of verses before and after each reference.

    """

    if count == 0: return ref_set

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
        clone_set.update(VerseIter(start.getText(), end.getText()))

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

def render_verses(ref_list, wrap=True, strongs=False, morph=False,
                  highlight_func=None, *args):
    """ Renders a the verse text at verse_ref.  
    Returns a strong "verse_ref: verse_text"
        wrap            -   Whether to wrap the text.
        strongs         -   Include Strong's Numbers in the output.
        morph           -   Include Morphological Tags in the output.
        highlight_func  -   A function to highlight anything else 
                            (i.e. search terms.)
        *args           -   Any additional arguments to pass to hightlight_func

        highlight_func should take at least three arguments, strongs, morph,
        and the verse_text.

    """

    # The Strong's and Morphology matching regular expressions.
    strongs_regx = re.compile(r'<([GH]\d*)>')
    morph_regx = re.compile(r'\(([A-Z\d-]*)\)')

    # Set the colors of different items.
    strongs_color = '\033[36m'
    morph_color = '\033[35m'
    ref_color = '\033[32m'
    end_color = '\033[m'

    # Build replacement strings that highlight Strong's Numbers and 
    # Morphological Tags.
    strongs_highlight = '<%s\\1%s>' % (strongs_color, end_color)
    morph_highlight = '(%s\\1%s)' % (morph_color, end_color)

    # Get the local text encoding.
    encoding = get_encoding()

    # Get an iterator over all the requested verses.
    verse_iter = IndexedVerseTextIter(iter(ref_list), strongs, morph)
    for verse_ref, verse_text in verse_iter:
        # Encode than decode the verse text to make it compatable with
        # the locale.
        verse_text = verse_text.strip().encode(encoding, 'replace')
        verse_text = verse_text.decode(encoding, 'replace')
        verse_text = '%s: %s' % (verse_ref, verse_text)
        # The text has to be word wrapped before adding any color, or else the
        # color will add to the line length and the line will wrap too soon.
        if wrap:
            verse_text = fill(verse_text, screen_size()[1], 
                              break_on_hyphens=False)
        # Color the verse reference.
        verse_text = re.sub(verse_ref, '%s%s%s' % (ref_color, verse_ref,
                                                   end_color), verse_text)

        # Highlight the different elements.
        if highlight_func:
            # First highlight with highlight_func so we don't mess up the
            # verse text for it.
            verse_text = highlight_func(verse_text, strongs, morph, *args)
        # Highlight Strong's and Morphology if they are visible.
        if strongs:
            verse_text = strongs_regx.sub(strongs_highlight, verse_text)
        if morph:
            verse_text = morph_regx.sub(morph_highlight, verse_text)

        # Finally produce the formated text.
        yield verse_text

def highlight_search_terms(verse_text, strongs, morph, search_str, flags):
    """ Highlight search terms in the verse text.

    """

    if strongs or morph:
        # Use an or'ed list of search terms so at least the
        # indevidual items will be highlighted.  This catches more
        # than the phrase so it doesn't look right.
        search_str = search_str.replace(' ', '|')
    # Catch each strongs/morph/word in the verse...Seems to work.
    reg_str = r'(\(|<|\b)(%s)(\b|>|\))' % search_str
    highlight_regex = re.compile(reg_str, flags)

    highlight_color = '\033[1m'
    word_highlight = '\\1%s\\2\033[m\\3' % highlight_color

    # Return the highlighted text.
    return highlight_regex.sub(word_highlight, verse_text)

def mod_lookup(mod, items):
    """ Looks up items in a module and returns the formated text.

    """

    item_lookup = Lookup(mod)

    # Seperate all elements by a comma.
    item_list = ','.join(items.split()).split(',')
    text_list = []
    for item in item_list:
        item_text = item_lookup.get_formatted_text(item)
        text_list.append('\033[1m%s\033[m:\n%s' % (item, item_text))
    return '\n\n'.join(text_list)


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

        self._bold_regx = re.compile(r'<b>(\w+)</b>')
        self._italic_regx = re.compile(r'<i>(\w+)</i>')
        self._br_regx = re.compile(r'<br[\s]*/>[\s]?')
        self._cleanup_regx = re.compile(r'<[^>]*>')
        self._brace_regx = re.compile(r'\{([\W]*)([\w]*)([\W]*)\}')
        self._parenthesis_regx = re.compile(r'\(([\W]*)([\w]*)([\W]*)\)')
        self._bracket_regx = re.compile(r'\[([\W]*)([\w ]*)([\W]*)\]')
        self._verse_ref_regx = re.compile(r'<scripRef[^>]*>([^<]*)</scripRef>')

    def get_text(self, key):
        """ Get the text at the given key in the module.
        i.e. get_text('3778') returns the greek strongs.

        """

        encoding = get_encoding()
        self._module.setKey(Sword.SWKey(key))
        item_text = self._module.RenderText()
        print(self._module.getRawEntry())
        # Make the text printable.
        item_text = item_text.encode(encoding, 'replace')
        item_text = item_text.decode(encoding, 'replace')
        return fill(item_text, screen_size()[1])

    def get_raw_text(self, key):
        """ Get the text at the given key in the module.
        i.e. get_text('3778') returns the greek strongs.

        """

        encoding = get_encoding()
        self._module.setKey(Sword.SWKey(key))
        item_text = self._module.getRawEntry()

        # Make the text printable.
        item_text = item_text.encode(encoding, 'replace')
        item_text = item_text.decode(encoding, 'replace')
        return item_text

    def get_formatted_text(self, key):
        """ Returns the formated raw text of the specified key.

        """

        text = self.get_raw_text(key)

        # Format and highlight the text.
        text = self._bold_regx.sub('\033[1m\\1\033[m', text)
        text = self._italic_regx.sub('\033[36m\\1\033[m', text)
        text = self._br_regx.sub('\n', text)
        text = self._bracket_regx.sub('[\\1\033[33m\\2\033[m\\3]', text)
        text = self._brace_regx.sub('{\\1\033[35m\\2\033[m\\3}', text)
        text = self._parenthesis_regx.sub('(\\1\033[34m\\2\033[m\\3)', text)
        text = self._verse_ref_regx.sub('\033[32m\\1\033[m', text)
        text = self._cleanup_regx.sub('', text)

        return text


class VerseTextIter(object):
    """ An iterable object for accessing verses in the Bible.  Maybe it will
    be easier maybe not.

    """

    def __init__(self, reference_iter, strongs=False, morph=False,
                 module='KJV', markup=Sword.FMT_PLAIN):
        """ Initialize.

        """

        markup = Sword.MarkupFilterMgr(markup)
        
        # We don't own this or it will segfault.
        markup.thisown = False
        self._library = Sword.SWMgr(markup)
        self._library.setGlobalOption("Headings", "On")
        self._library.setGlobalOption("Cross-references", "Off")

        if strongs:
            self._library.setGlobalOption("Strong's Numbers", "On")
        else:
            self._library.setGlobalOption("Strong's Numbers", "Off")
        if morph:
            self._library.setGlobalOption("Morphological Tags", "On")
        else:
            self._library.setGlobalOption("Morphological Tags", "Off")
        
        # Strings for finding the heading.
        self._head_str = Sword.SWBuf('Heading')
        self._preverse_str = Sword.SWBuf('Preverse')
        self._canon_str = Sword.SWBuf('canonical')

        self._module = self._library.getModule(module)
        self._key = self._module.getKey()

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
        self._key.setText(verse_ref)

        # Set the verse and render the text.
        verse_text = self._get_text(verse_ref)

        return (verse_ref, verse_text)

    def __iter__(self):
        """ Returns an iterator of self.

        """

        return self

    def _get_text(self, verse_ref):
        """ Returns the verse text.  Override this to produce formatted verse
        text.

        """

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
                for k, val in preverse_attrs.items():
                    if canon_str in heading_attrs[k]:
                        if heading_attrs[k][canon_str].c_str() == 'true':
                            heading_list.append(val.c_str())

        if heading_list:
            return self._module.RenderText(''.join(heading_list))
        else:
            return ''


class IndexedVerseTextIter(object):
    """ An iterable object for accessing verses in the Bible.  Maybe it will
    be easier maybe not.

    """

    def __init__(self, reference_iter, strongs=False, morph=False, 
                 module='KJV'):
        """ Initialize.

        """

        self._clean_morph_regex = re.compile(r' \(([A-Z\d-]*)\)')
        self._clean_strongs_regex = re.compile(r' <([GH]\d*)>')

        self._index_dict = IndexDict('%s' % module)

        self._ref_iter = reference_iter
        self._strongs = strongs
        self._morph = morph

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

        return (verse_ref, verse_text)

    def __iter__(self):
        """ Returns an iterator of self.

        """

        return self

    def _get_text(self, verse_ref):
        """ Returns the verse text.  Override this to produce formatted verse
        text.

        """

        verse_text = self._index_dict[verse_ref]
        if not self._strongs:
            verse_text = self._clean_strongs_regex.sub('', verse_text)
        if not self._morph:
            verse_text = self._clean_morph_regex.sub('', verse_text)

        return verse_text


class VerseIter(object):
    """ Iterator of verse references.

    """

    def __init__(self, start, end='Revelation of John 22:21'):
        """ Setup the start and end references of the range.

        """

        # Make sure the range is in order.
        start, end = sorted([start, end], key=sort_key)
        self._verse = Sword.VerseKey(start, end)
        self._end_ref = self._verse.UpperBound().getText()

        self._verse_ref = ''

    def __next__(self):
        """ Returns the next verse reference.

        """

        # End the iteration when we reach the end of the range.
        if self._verse_ref == self._end_ref:
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


class ChapterIter(VerseIter):
    """ Iterates over just one chapter.

    """

    def __init__(self, book='Genesis', chapter=1):
        """ Setup iterator.

        """

        start = Sword.VerseKey('%s %s:1' % (book, chapter))
        end = Sword.VerseKey(start.clone())
        end.setVerse(end.getVerseMax())

        super(ChapterIter, self).__init__(start.getText(), end.getText())


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

        super(BookIter, self).__init__(start.getText(), end.getText())


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

    def set(self, key, value):
        """ Write the list database under the given name.

        """

        # Encode the buffer into bytes. 
        byte_buffer = json.dumps(value).encode(self._encoding(), 'replace')

        # Write buffer to tar file.
        self._dbm[key] = byte_buffer

        return len(byte_buffer)

    def get(self, key, default=[]):
        """ Read the named list out of the database.

        """

        try:
            str_buffer = self._dbm[key].decode(self._encoding(), 'replace')
            return json.loads(str_buffer)
        except Exception as err:
            #print("Error reading %s: %s" % (key, err), file=stderr)
            return default

    def update(self, dic):
        """ Write a dictionary to the database.
        
        """

        for k, v in dic.items():
            self.set(k, v)

        return len(dic)

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

        self._module_dict = defaultdict(list)
        # lower_case is used to store lower_case words case sensitive
        # counterpart.
        self._module_dict.update({ 'lower_case': defaultdict(list) })

        self._index_dict = {
                '%s_index' % self._module_name: self._module_dict
                }

        self._index_built = False

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
            self._module_dict[strongs_num].append(verse_ref)

    def _index_morph(self, verse_ref, verse_text):
        """ Update the modules mophological dictionary from the verse text.

        """

        morph_list = set(self._morph_regx.findall(verse_text))
        for morph_num in morph_list:
            self._module_dict[morph_num].append(verse_ref)

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

        # Include the capitalized words for case sensitive search.
        word_set = set(verse_text.split())
        word_set.update(set(clean_text.split()))

        for word in word_set:
            if word:
                self._module_dict[word].append(verse_ref)
                l_word = word.lower()
                if l_word != word:
                    # Map the lowercase word to the regular word for case
                    # insensitive searches.
                    if word not in self._module_dict['lower_case'][l_word]:
                        self._module_dict['lower_case'][l_word].append(word)

    def _index_book(self, book_name="Genesis"):
        """ Creates indexes for strongs, morphology and words.

        """

        book_iter = BookIter(book_name)
        verse_iter = VerseTextIter(book_iter, True, True, self._module_name)

        for verse_ref, verse_text in verse_iter:
            print('\033[%dD\033[KIndexing...%s' % \
                    (len(verse_ref) + 20, verse_ref), file=stderr, end='')
            stderr.flush()

            self._index_strongs(verse_ref, verse_text)
            self._index_morph(verse_ref, verse_text)
            self._index_words(verse_ref, verse_text)
            # Put the entire Bible in the index, so we can pull it out
            # faster.
            self._module_dict[verse_ref] = verse_text

    def build_index(self):
        """ Create index files of the bible for strongs numbers, 
        morphological tags, and case (in)sensitive words.

        """

        print("Indexing %s could take a while..." % self._module_name, 
              file=stderr)
        for book in self._book_gen():
            self._index_book(book)

        print('\nDone.', file=stderr)

        self._index_built = True

    def write_index(self):
        """ Write all the index dictionaries to their respective files.  If
        Any of the dictionaries is empty, then build the index.

        The indexes are just json-ed dictionaries.  The keys are the indexed
        items and the values are the verse references that contain the key.

        """

        if not self._index_built:
            self.build_index()
        # Build the index if it's not already built.
        for name, dic in self._index_dict.items():
            print("Writing %s.dbm..." % name, file=stderr)
            # Save as just a plain text file.  Has to be loaded all at once, 
            # so it is really slow.
            #with open(name, 'w') as index_file:
                #json.dump(dic, index_file, indent=4)
        #return
            # Save a dbm database that we can access without loading it all
            # into memeory so it is fast.
            with IndexDbm('%s.dbm' % name, 'nf') as index_file:
                #with open(name, 'r') as i_file:
                    #dic =json.load(i_file)
                index_file.update(dic)


class IndexDict(dict):
    """ A Bible index container, that provides on-demand loading of indexed
    items.

    """

    def __init__(self, name=None):
        """ Initialize the index.

        """

        super(IndexDict, self).__init__()

        self._name = name
        self._lower_case = self.get('lower_case', {})

    # In case we need to access the name externally we don't want it changed.
    name = property(lambda self: self._name)

    def __getitem__(self, key):
        """ If a filename was given then use it to retrieve keys when
        they are needed.

        """

        if self._name and (key not in self):
            # Load the value from the database if we don't have it.
            with IndexDbm('%s_index.dbm' % self._name, 'r') as dbm_dict:
                self[key] = dbm_dict.get(key)

        return super(IndexDict, self).__getitem__(key)

    def get(self, key, default=[]):
        """ Returns the value associated with key, or default.

        """

        value = self[key]
        return value if value else default

    def value_intersect(self, key_list, case_sensitive=False):
        """ Returns a set with only the verses that contain all the items in
        search_list.

        """


        # There may be a better way to do this.  Start with a set of the
        # verses containing the least common item, then update it with the
        # intersections it has with the sets of the remaining words.
        # Effectively removing any verse from the original set that does not
        # contain all the other search items.
        result_set = set()
        for word in key_list:
            temp_set = set(self[word])
            # When its not a case sensitive search, combine all the references
            # that contain word in any form.
            if not case_sensitive:
                # If word is 'the', u_word could be in ['The', 'THE'], so
                # get the list of references that contain those words and
                # combine them with the set of references for word.
                temp_set.update(self[word.lower()])
                for u_word in self._lower_case.get(word.lower(), []):
                    temp_set.update(self[u_word])

            if result_set:
                result_set.intersection_update(temp_set)
            else:
                result_set.update(temp_set)
        return result_set

    def value_sym_diff(self, key_list, case_sensitive=False):
        """ Finds the symmetric difference of all the references that contain
        the keys in key_list.  (only a set with either or not both keys)

        """

        # Create an either or set.
        verse_set = set()
        for item in key_list:
            if not case_sensitive:
                verse_set.symmetric_difference_update(self[item.lower()])
                for word in self._lower_case.get(item.lower(), []):
                    verse_set.symmetric_difference_update(self[word])
            verse_set.symmetric_difference_update(self[item])
        return verse_set

    def value_union(self, key_list, case_sensitive=False):
        """ Returns a set with all the verses that contain each item in
        search_list.

        """

        # Create one big set of all the verses that contain any one or more of
        # the search items.
        verse_set = set()
        for item in key_list:
            if not case_sensitive:
                verse_set.update(self[item.lower()])
                for word in self._lower_case.get(item.lower(), []):
                    verse_set.update(self[word])
            verse_set.update(self[item])
        return verse_set


class CombinedParse(object):
    """ A parser for simple combined search parsing.
        ((in OR tree) AND the) AND (house OR bush) =>
        ['in the house', 'in the bush', 'tree the house', 'tree the bush']
        Also it has a NOT word list.
        created NOT (and OR but) => ['created'] ['and', 'but']

    """

    def __init__(self, arg_str):
        """ Initialize the parser and parse the arg string.

        """

        self._arg_str = arg_str
        self._arg_list = arg_str.split()
        parsed_list = self.parse_string(list(arg_str))
        self._word_list, self._not_list = self.parse_list(parsed_list)

    # Make the results accesable via read-only properties.
    word_list = property(lambda self: self._word_list)
    not_list = property(lambda self: self._not_list)

    def parse_list(self, arg_list):
        """ Parse a list such as ['created', 'NOT', ['and', 'OR', 'but']] into
        search_args = ['created'] not_list = ['and', 'but']

        """

        # The list we're working on building.
        working_list = []
        # The list of words not to include.
        not_list = []
        for i in arg_list:
            # Skip 'OR's
            if i == 'OR':
                continue
            if isinstance(i, list):
                # A list was found so parse it and get the results.
                temp_list, temp_not_list = self.parse_list(i)
                # Add the returned not list to the current not list.
                not_list.extend(temp_not_list)
                if working_list:
                    if working_list[-1] == 'AND':
                        # Pop the 'AND' off the end of the list.
                        working_list.pop()
                        # Combine each element of the working listh with each
                        # element of the returned list replace the working
                        # list with those combinations. 
                        # (i.e. working_list = ['this', 'that'] 
                        #       temp_list = ['tree', 'house']
                        #       result = ['this tree', 'this house',
                        #                 'that tree', 'that house']
                        working_list = ['%s %s' % j for j in product(working_list, temp_list)]
                    elif working_list[-1] == 'NOT':
                        # Take the 'NOT' off to show we've processed it.
                        working_list.pop()
                        # Add the returned list to the NOT list.
                        not_list.extend(temp_list)
                    else:
                        # Just extend the working list with the retuned list.
                        working_list.extend(temp_list)
                else:
                    # Just extend the working list with the retuned list.
                    working_list.extend(temp_list)
            else:
                if i == 'AND':
                    # Put the 'AND' on the list for later processing.
                    working_list.append(i)
                elif working_list:
                    if working_list[-1] == 'AND':
                        # Take the 'AND' off the list.
                        working_list.pop()
                        # Combine all the elements of working_list with i, and
                        # replace working list with the resulting list.
                        # (i.e. working_list = ['he', 'it'] i = 'said'
                        #       result = ['he said', 'it said']
                        working_list = ['%s %s' % (j, i) for j in working_list]
                    elif working_list[-1] == 'NOT':
                        # Remove the 'NOT'.
                        working_list.pop()
                        # Add the word to the not list.
                        not_list.append(i)
                    else:
                        # Add the word to the working list.
                        working_list.append(i)
                else:
                    # Add the word to the working list.
                    working_list.append(i)

        # Split and then combine all the strings in working_list.
        # Basically removes runs of whitespace.
        working_list = [' '.join(i.split()) for i in working_list]

        # Return the final list and not list.
        return working_list, not_list

    def parse_parenthesis(self, arg_list):
        """ Recursively processes strings in parenthesis converting them
        to nested lists of strings.

        """

        # The return list.
        return_list = []
        # Temorary string.
        temp_str = ''
        while arg_list:
            # Get the next character.
            c = arg_list.pop(0)
            if c == '(':
                # An opening parenthesis was found so split the current string
                # at the spaces putting them in the return list, and clean
                # the string.
                if temp_str:
                    return_list.extend(temp_str.split())
                    temp_str = ''
                # Process from here to the closing perenthesis.
                return_list.append(self.parse_parenthesis(arg_list))
            elif c == ')':
                # The parenthesis is closed so return back to the calling
                # function.
                break
            else:
                # Append the current not parenthesis character to the string.
                temp_str += c
        if temp_str:
            # Split and add the string to the return list.
            return_list.extend(temp_str.split())
        # Return what we found.
        return return_list

    def parse_string(self, arg_list):
        """ Parse a combined search arg string.  Convert a string such as:
        'created NOT (and OR but)' => ['created', 'NOT', ['and', 'OR', 'but']]

        """


        # This does the same thing only using json.
        #
        # Regular expression to group all words.
        #word_regx = re.compile(r'\b(\w*)\b')
        # Put quotes around all words and opening replace paranthesis with
        # brackets, put all of that in brackets.
        #temp_str = '[%s]' % word_regx.sub('"\\1"', arg_str).replace('(', '[')
        # Replace closing parenthesis with brackets and replace a '" ' with
        # '", '. 
        #temp_str = temp_str.replace(')', ']').replace('" ', '",')
        # finally replace '] ' with '], '.  The end result should be a valid
        # json string that can be converted to a list.
        #temp_str = temp_str.replace('] ', '],')
        # Convert the string to a list.
        #return_list = json.loads(temp_str)
        #return return_list

        # The return list.
        return_list = []
        # Temporary string.
        temp_str = ''
        while arg_list:
            # Pop the next character.
            c = arg_list.pop(0)
            if c == '(':
                # A parenthesis was found store and reset the string.
                # And parse the what is in the parenthesis.
                if temp_str:
                    return_list.extend(temp_str.split())
                    temp_str = ''
                return_list.append(self.parse_parenthesis(arg_list))
            else:
                # Append the non parenthesis character to the string.
                temp_str += c

        if temp_str:
            # Store the final string in the list.
            return_list.extend(temp_str.split())

        #print(return_list)
        # Return the list.
        return return_list


class Search(object):
    """ Provides a simple way of searching an IndexDict for verses.

    """

    def __init__(self, module='KJV'):
        """ Initialize the search.

        """

        # The index dictionary.
        self._index_dict = IndexDict(module)

        self._module_name = module

        # Cleanup regular expressions.
        self._non_alnum_regx = re.compile(r'\W')
        self._fix_regx = re.compile(r'\s+')

        # Searching regular expressions.
        self._strongs_regx = re.compile(r'<([GH]\d*)>')
        self._morph_regx = re.compile(r'\(([A-Z\d-]*)\)')

    def _sorted_iter(self, verse_ref_set):
        """ Returns an iterator over a sorted version of verse_ref_set.

        """

        # Speed up the iteration by first sorting the range.
        return iter(sorted(verse_ref_set, key=sort_key))

    def _clean_text(self, text):
        """ Return a clean (only alphanumeric) text of the provided string.

        """

        # Do we have to use two regular expressions to do this.
        # Replace all non-alphanumeric characters with a space.
        temp_text = self._non_alnum_regx.sub(' ', text) 
        # Replace one or more spaces with one space.
        clean_text = self._fix_regx.sub(' ', temp_text)

        return clean_text.strip()

    def _process_search(func):
        """ Returns a wrapper function that processes the search terms, calls
        the wrapped function, and, if applicable, confines the resulting verse
        set to a range.

        """

        @wraps(func)
        def wrapper(self, search_terms, strongs=False, morph=False,
                    case_sensitive=False, range_str=''):
            """ Process the search terms according to the wrapped functions
            requirements, then apply the range, if given, to the returned set
            of verses.

            """

            if not isinstance(search_terms, str):
                # Combine the terms for use by the different methods.
                search_terms = ' '.join(search_terms)

            # Get a valid set of verse references that conform to the passed
            # range.
            range_set = parse_verse_range(range_str)

            # Regular expression and combined searches get the search terms as
            # they were passed.
            if func.__name__ in ['multiword_search', 'anyword_search', 
                                 'phrase_search']:
                if not strongs and not morph:
                    # Get rid of any non-alphanumeric characters from the
                    # search string.
                    search_str = self._clean_text(search_terms).strip()
                    if not case_sensitive:
                        search_str = search_str.lower()
                else:
                    # Strong's numbers and Morphological tags are all
                    # uppercase.
                    search_str = search_terms.upper().strip()
            else:
                search_str = search_terms

            # Get the set of found verses.
            found_set = func(self, search_str, strongs, morph, case_sensitive,
                             range_set)

            # The phrase, regular expression, and combined searches apply the
            # range before searching, so only multi-word and any-word searches
            # have it applied here.
            print("Confining to range '%s'..." % range_str)
            if func.__name__ in ['multiword_search', 'anyword_search']:
                if range_set:
                    found_set.intersection_update(range_set)
            return found_set

        # Return wrapper function.
        return wrapper

    @_process_search
    def combined_search(self, search_terms, strongs=False, morph=False,
                        case_sensitive=False, range_str=''):
        """ combined_search(self, search_terms, strongs=False, morph=False,
                        case_sensitive=False, range_str=''): ->
        Perform a combined search.  Search terms could be
        'created NOT (and OR but)' and it would find all verses with the word
        'created' in them and remove any verse that had either 'and' or 'but.'

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        print("Searching for '%s'..." % search_terms)

        # Process the search_terms.
        arg_parser = CombinedParse(search_terms)
        # Get the list of words and/or phrases to include.
        word_list = arg_parser.word_list
        # Get the list of words and/or phrases to NOT include.
        not_list = arg_parser.not_list

        phrase_search = self.phrase_search
        multiword_search = self.multiword_search

        def combine_proc(str_list):
            """ Performs combined search on the strings in str_list, and
            returns a set of references that match.

            """

            and_it = False
            temp_set = set()
            for word in str_list:
                # A '+' before or after a word means it should have a phrase
                # search done on it and the words with it.
                if '+' in word:
                    # Do a phrase search on the word string.
                    result_set = phrase_search(word.replace('+', ' '), strongs,
                                               morph, case_sensitive,
                                               range_str)
                elif word == '&':
                    # Combine the next search results with this one.
                    and_it = True
                    continue
                else:
                    # Do a multi-word search on the word string.
                    result_set = multiword_search(word, strongs, morph,
                                                  case_sensitive, range_str)
                if and_it:
                    # The previous word said to find verses that match both.
                    temp_set.intersection_update(result_set)
                    and_it = False
                else:
                    # Only keep the verses that have either one group or the
                    # other but not both.
                    temp_set.symmetric_difference_update(result_set)

            return temp_set

        # Remove any verses that have the NOT words in them.
        found_set = combine_proc(word_list).difference(combine_proc(not_list))

        return found_set

    @_process_search
    def combined_phrase_search(self, search_terms, strongs=False, morph=False,
                               case_sensitive=False, range_str=''):
        """ combined_phrase_search(self, search_terms, strongs=False,
                morph=False, case_sensitive=False, range_str=''): ->
        Perform a combined phrase search.  Search terms could be
        'created NOT (and AND but)' and it would find all verses with the word
        'created' in them and remove any verse that had the phrase 'and but.'

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        print("Searching for '%s'..." % search_terms)

        # Process the search_terms.
        arg_parser = CombinedParse(search_terms)
        # Get the list of words and/or phrases to include.
        word_list = arg_parser.word_list
        # Get the list of words and/or phrases to NOT include.
        not_list = arg_parser.not_list

        phrase_search = self.phrase_search

        def combine_proc(str_list):
            """ Performs combined phrase search on the strings in str_list, and
            returns a set of references that match.

            """

            temp_set = set()
            for word in str_list:
                # Do a phrase search on the word string.
                result_set = phrase_search(word.replace('+', ' '), strongs,
                                           morph, case_sensitive,
                                           range_str)
                # Include all the verses that have any of the word groups.
                temp_set.update(result_set)

            return temp_set

        # Remove any verses that have the NOT words in them.
        found_set = combine_proc(word_list).difference(combine_proc(not_list))

        return found_set

    @_process_search
    def regex_search(self, search_terms, strongs=False, morph=False,
                     case_sensitive=False, range_str=''):
        """ regex_search(self, search_terms, strongs=False, morph=False,
              case_sensitive=False, range_str='') -> 
        Perform a regular expression search.

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        print("Searching for regular expression '%s'..." % search_terms)

        # re.I is case insensitive.
        flags = re.I if not case_sensitive else 0
        # Make a regular expression from the search_terms.
        search_regx = re.compile(r'%s' % search_terms, flags)

        if range_str:
            # Only search through the supplied range.
            v_iter = self._sorted_iter(range_str)
        else:
            # Search the entire Bible.
            v_iter = VerseIter('Genesis 1:1')

        # The iter returns a tuple (verse_ref, verse_text).
        verse_iter = IndexedVerseTextIter(v_iter, strongs=strongs, morph=morph,
                                          module=self._module_name)

        # The set that will be returned with all the references whose text
        # matches the regular expression.
        found_verses = set()
        for verse_ref, verse_text in verse_iter:
            # Take this out to gain a little speed.
            print('\033[%dD\033[KSearching...%s' % \
                    (len(verse_ref) + 20, verse_ref), file=stderr, end='')
            stderr.flush()

            if search_regx.search(verse_text):
                found_verses.add(verse_ref)
            elif not strongs and not morph:
                # Should we do this or should we trust the user knows what
                # puctuation are in the verses?
                clean_verse_text = self._clean_text(verse_text)
                if search_regx.search(clean_verse_text):
                    found_verses.add(verse_ref)

        print("...Done.", file=stderr)

        return found_verses

    @_process_search
    def multiword_search(self, search_terms, strongs=False, morph=False,
                         case_sensitive=False, range_str=''):
        """ multiword_search(self, search_terms, strongs=False, morph=False,
                  case_sensitive=False, range_str='') -> 
        Perform a multiword search using the search_terms.

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        print("Searching for verses with all these words '%s'..." % ', '.join(search_terms.split()))

        # All that needs to be done is find all references with all the
        # searched words in them.
        found_set = self._index_dict.value_intersect(search_terms.split(), 
                                                     case_sensitive)

        return found_set

    @_process_search
    def eitheror_search(self, search_terms, strongs=False, morph=False,
                        case_sensitive=False, range_str=''):
        """ eitheror_search(self, search_terms, strongs=False, morph=False,
                case_sensitive=False, range_str='') -> 
        Perform a search returning any verse with one and only one of the terms
        searched for.

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        print("Searching for verses with one and not all of these words '%s'..." % ', '.join(search_terms.split()))

        # Any verse with one and only one of the searched words.
        found_set = self._index_dict.value_sym_diff(search_terms.split(), 
                                                    case_sensitive)

        return found_set

    @_process_search
    def anyword_search(self, search_terms, strongs=False, morph=False,
                       case_sensitive=False, range_str=''):
        """ anyword_search(self, search_terms, strongs=False, morph=False,
                case_sensitive=False, range_str='') -> 
        Perform a search returning any verse with one or more of the search
        terms.

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        print("Searching for verses with any of these words '%s'..." % ', '.join(search_terms.split()))
        # Any verse with one or more of the searched words.
        found_set = self._index_dict.value_union(search_terms.split(), 
                                                 case_sensitive)

        return found_set

    @_process_search
    def phrase_search(self, search_terms, strongs=False, morph=False, 
                      case_sensitive=False, range_str=''):
        """ phrase_search(self, search_terms, strongs=False, morph=False,
               case_sensitive=False, range_str='') -> 
        Perform a phrase search.
                
            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        print("Searching for verses with this phrase '%s'..." % search_terms)

        # First make sure we are only searching verses that have all the
        # search terms in them.
        ref_set = self._index_dict.value_intersect(search_terms.split(), 
                                                   case_sensitive)
        if range_str:
            # Only search through the supplied range.
            ref_set.intersection_update(range_str)

        # No need to search for a single word phrase.
        if len(search_terms.split()) == 1:
            return ref_set

        # Sort the list so it may be a little faster.  Only needed if we're
        # using the sword module to look them up.
        ref_iter = self._sorted_iter(ref_set)
        #verse_iter = IndexedVerseTextIter(ref_iter, strongs=strongs, 
                                          #morph=morph, 
                                          #module=self._module_name)
        verse_iter = IndexedVerseTextIter(ref_iter, strongs=True, 
                                          morph=True, 
                                          module=self._module_name)

        # Put a space at the beginning and end so 'the' doesn't match 'their.'
        #search_str = ' %s ' % search_terms
        # Make all the terms the same case if case doesn't matter.
        if not case_sensitive:
            #search_str = search_str.lower()
            flags = re.I
        else:
            flags = 0

        # Mabye gain a little speed making lambda functions to process the
        # verse text.
        #if strongs: 
            # Returns a list of strongs numbers as they were found in the
            # text.
            #clean_up = lambda t: self._strongs_regx.findall(t)
        #elif morph: 
            # Returns a list of morphological tags in the order they were in
            # the text.
            #clean_up = lambda t: self._morph_regx.findall(t)
        #else: 
            # Clean out all the puctuation and return a list of words.
            #clean_up = lambda t: self._non_alnum_regx.sub(' ', t).split()
        if strongs:
            search_reg_str = search_terms.replace(' ', r'>[^<]*<')
        elif morph:
            search_reg_str = search_terms.replace(' ', r'\)[^\(]*\(')
        else:
            search_reg_str = '\\b%s\\b' % search_terms.replace(' ', 
                    r'\b(<[^>]*>|\([^\)]*\)|\W)*\b')
        search_regx = re.compile(search_reg_str, flags)

        found_set = set()
        for verse_ref, verse_text in verse_iter:
            if search_regx.search(verse_text):
                found_set.add(verse_ref)
            continue
            #print(search_regx.search(verse_text), search_reg_str)
            
            #print(verse_text)
            #exit()
            # Put a space at the start and end of the cleaned verse text, so
            # it will match the space at the start and end of search_str.
            verse_text = ' %s ' % ' '.join(clean_up(verse_text))
            if not case_sensitive:
                verse_text = verse_text.lower()
            # Let python handle the search.
            if search_str in verse_text:
                found_set.add(verse_ref)

        return found_set

    def mixed_search(self, search_terms, strongs=False, morph=False, 
                      case_sensitive=False, range_str=''):
        """ mixed_search(self, search_terms, strongs=False, morph=False,
               case_sensitive=False, range_str='') -> 
        Perform a mixed search.
                
            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        found_set = set()
        not_set = set()
        and_set = set()
        or_set = set()
        xor_set = set()

        combine_dict = {
                '!' : not_set.difference_update,
                '+' : and_set.intersection_update,
                '|' : or_set.update,
                '^' : xor_set.symmetric_difference_update,
                }

        # Match strongs numbers.
        strongs_regx = re.compile(r'[GH]\d+')
        # It needs to match with parenthesis or it will catch all capitalized
        # word and words with '-'s in them.
        morph_regx = re.compile(r'\([A-Z\d-]+\)')
        for term in search_terms:
            if term[0] in '!+^|':
                # Set the correct combining function, and cleanup the item.
                if term[0] == '+' and not and_set:
                    combine_func = and_set.update
                elif term[0] == '!' and not not_set:
                    combine_func = not_set.update
                else:
                    combine_func = combine_dict[term[0]]
                term = term[1:]
            else:
                combine_func = found_set.update

            if ' ' in term:
                # Search term is a quoted string, so treat it like a phrase.
                search_func = self.phrase_search
            else:
                # A single word should be multi-word.
                search_func = self.multiword_search

            # Perform a strongs search.
            strongs = bool(strongs_regx.match(term.upper()))
            # Perform a morpholagical search.
            morph = bool(morph_regx.match(term.upper()))

            # Search for words or phrases.
            temp_set = search_func(term, strongs, morph, case_sensitive,
                                   range_str)

            # Add the results to the correct set.
            combine_func(temp_set)
            #print(term, len(found_set), len(not_set), len(or_set), len(and_set))

        # Update the result set.
        found_set.update(or_set)
        found_set.symmetric_difference_update(xor_set)

        # If add_set is empty don't empty found_set too.
        if and_set:
            found_set = and_set.union(found_set.intersection(and_set))

        # Finally remove all the verses that are in the not_set.
        found_set.difference_update(not_set)

        return found_set

    def sword_search(self, search_terms, strongs=False, morph=False,
                     case_sensitive=False, range_str='', search_type='lucene'):
        """ sword_search(self, search_terms, strongs=False, morph=False,
                case_sensitive=False, range_str='', search_type=-4) -> 
        Use the sword module to search for the terms.

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.
            search_type     -   What search type to use.

        """

        search_terms = ' '.join(search_terms)

        print("Searching using the Sword library for '%s'..." % search_terms)
        
        found_set = set()

        search_type_dict = {
                'regex'         :  0,
                'phrase'        : -1,
                'multiword'     : -2,
                'entryattrib'   : -3,   # (e.g. Word//Lemma//G1234)
                'lucene'        : -4
                }

        try:
            # Render the text as plain.
            markup = Sword.MarkupFilterMgr(Sword.FMT_PLAIN)
            # Don't own this or it will crash.
            markup.thisown = False
            mgr = Sword.SWMgr(markup)
            # Load the module.
            module = mgr.getModule(self._module_name)

            # Make sure we can search like this.
            if not module.isSearchSupported(search_terms, -4):
                print("Search not supported")
                return found_set()

            # Get the range key.
            if not range_str:
                range_str = 'Genesis-Revelation'
            range_k = Sword.VerseKey().ParseVerseList(range_str, 'Genesis 1:1',
                                                      True)

            flags = re.I if not case_sensitive else 0

            # Set the search type based on the search_type argument.
            search_type = search_type_dict.get(search_type.lower(), -4)

            if strongs:
                # Search for strongs numbers.
                # I don't know how to search for morphological tags using
                # Swords search function.
                prefix = 'lemma:'
                for term in ','.join(search_terms.split()).split(','):
                    if not term.startswith('lemma:'):
                        # Make the term start with lemma: so sword will find
                        # it.
                        term = '%s%s' % (prefix, term)
                    # Perform the search.
                    resource = module.doSearch(term, search_type, flags,
                                               range_k)
                    # Get the list of references from the range text.
                    found_set.update(resource.getRangeText().split('; '))
            else:
                # Perform the search.
                resource = module.doSearch(search_terms, search_type, flags,
                                           range_k)
                # Get the list of references from the range text.
                found_set.update(resource.getRangeText().strip().split('; '))
        except Exception as err:
            print("There was a problem while searching: %s" % err)

        found_set.discard('')

        return found_set

def main(arg_list, **kwargs):
    """ Takes a string of arguments, and a bunch of keyword arguments.

    """

    print("\nProcessing arguments...\n")
    s = Search()
    print(len(s.phrase_search(' '.join(arg_list))))
    exit()

    # Build the index.
    if kwargs['build_index']:
        indexer = IndexBible()
        indexer.write_index()
        exit()

    # Make an argument string.
    arg_str = ' '.join(arg_list)

    # Get the search related arguments.
    search_type = kwargs['search_type']
    strongs_search = kwargs['search_strongs']
    morph_search = kwargs['search_morphology']
    case_sensitive = kwargs['case_sensitive']
    search_range = kwargs['search_range']

    # Get the lookup related arguments
    lookup = kwargs['verse_reference']
    define_strongs = kwargs['numbers']
    define_morph = kwargs['tags']
    define_word = kwargs['words']
    define_kjv_word = kwargs['kjv_words']
    daily = kwargs['day']

    # Set the highlight string to the arg_str by default.
    highlight_str = arg_str

    if lookup:
        # Lookup verses in the argument string.
        results = parse_verse_range(arg_str)
    elif define_strongs:
        # Lookup all the Strong's Numbers in the argument list.
        # Make all the numbers seperated by a comma.
        strongs_list = ','.join(define_strongs.upper().split()).split(',')
        #TODO: Find what Strong's Modules are available and use the best,
        #      or let the user decide.
        greek_strongs_lookup = Lookup('StrongsRealGreek')
        hebrew_strongs_lookup = Lookup('StrongsRealHebrew')
        for strongs_num in strongs_list:
            # Greek Strong's Numbers start with a 'G' and Hebrew ones start
            # with an 'H.'
            if strongs_num.upper().startswith('G'):
                mod_name = 'StrongsRealGreek'
            else:
                mod_name = 'StrongsRealHebrew'
            print('%s\n' % mod_lookup(mod_name, strongs_num[1:]))
        exit()
    elif define_morph:
        # Lookup all the Morphological Tags in the argument list.
        # I don't know how to lookup Hebrew morphological tags, so I
        # only lookup Greek ones in 'Packard.'
        print('%s\n' % mod_lookup('Packard', define_morph.upper()))
        exit()
    elif define_word:
        # Lookup words in the dictionary.
        print('%s\n' % mod_lookup('WebstersDict', define_word))
        exit()
    elif define_kjv_word:
        # Lookup words in the KJV dictionary.
        print('%s\n' % mod_lookup('KJVD', define_kjv_word))
        exit()
    elif daily:
        # Lookup the specified daily devotional.
        if daily.lower() == 'today':
            # Today is an alias for today's date.
            daily = strftime('%m.%d')
        daily_lookup = Lookup('Daily')
        # Try to make the output nicer.
        print(daily_lookup.get_formatted_text(daily))
        exit()
    else:
        # Perform the specified search.
        search = Search()

        extras = ()

        if search_type in ['combined', 'combined_phrase']:
            # Combined searches are complicated.
            # Parse the search argument and build a highlight string from the
            # result.
            arg_parser = CombinedParse(arg_str)
            parsed_args = arg_parser.word_list
            not_l = arg_parser.not_list
            if search_type == 'combined_phrase':
                # A phrase search needs to highlight phrases.
                highlight_str = '|'.join(parsed_args)
            else:
                highlight_str = '|'.join(['|'.join(p.split()) for p in parsed_args])
            # Remove any stray '+'s.
            highlight_str = highlight_str.replace('|+', ' ')
        elif search_type.startswith('sword_'):
            extras = (search_type[6:],)
            search_type = search_type[:5]
        else:
            # Build the highligh string for the other searches.
            # Don't modify regular expression searches.
            if search_type not in ['phrase', 'regex', 'mixed']:
                # Multiword and anyword searches should have an or'ed 
                # highlight string.
                highlight_str = '|'.join(arg_str.split())
            elif search_type == 'phrase':
                # Phrase searches should not be split at whitespace.
                highlight_str = ' '.join(arg_list)
                #highlight_str = '\\b%s\\b' % arg_str.replace(' ', 
                        #r'\b(<[^>]*>|\([^\)]*\)|\W)*\b')
            elif search_type == 'mixed':
                # Just join the search list so it should highlight correctly.
                highlight_str = '|'.join(arg_list)

        # Remove anything that will break a regular expression.
        print(highlight_str)
        fix_highlight_regx = re.compile(r'(^\||[^\w\| ])')
        fix_space_regx = re.compile(r'[[:space:]]+')
        fix_pipe_regx = re.compile(r'\|+')
        word_bound_regx = re.compile(r'\b')
        highlight_str = fix_highlight_regx.sub('', highlight_str)
        highlight_str = fix_space_regx.sub(' ', highlight_str)
        highlight_str = fix_pipe_regx.sub('|', highlight_str)
        highlight_str = word_bound_regx.sub(r'\\b', highlight_str)
        print(highlight_str)

        try:
            # Get the search function asked for.
            search_func = getattr(search, '%s_search' % search_type)
        except AttributeError as err:
            # An invalid search type was specified.
            print("Invalid search type: %s" % search_type, file=stderr)
            exit()

        # Search.
        results = search_func(arg_list, strongs_search, morph_search,
                              case_sensitive, search_range, *extras)

        
    count = len(results)
    print("\nFound %s verse%s.\n" % (count, 's' if count != 1 else ''), 
          file=stderr)

    if kwargs['quiet']:
        # Only the verse count was given.
        exit()
    elif kwargs['list_only']:
        # Print a sorted list of references.
        print('\n'.join(sorted(results, key=sort_key)))
        exit()
    else:
        # Get the output arguments.
        show_strongs = kwargs['show_numbers'] or strongs_search
        show_morph = kwargs['show_tags'] or morph_search
        # Flags for the highlight string.
        flags = re.I if not case_sensitive else 0
        # Add the specified number of verses before and after to provide
        # context.
        context_results = sorted(add_context(results, kwargs['context']), 
                                 key=sort_key)
        # Get a formated verse string generator.
        verse_gen = render_verses(context_results, not kwargs['one_line'],
                                  show_strongs, show_morph, 
                                  highlight_search_terms, highlight_str, flags)
        if kwargs['one_line']:
            # Print it all on one line.
            print('  '.join(verse_gen))
        else:
            # Print the verses on seperate lines.
            print('\n'.join(verse_gen))


if __name__ == '__main__':
    parser = OptionParser(description="Bible search.")
    parser.add_option('-i', '--index', action='store_true', default=False,
                        help='(Re-)build the search index.',
                        dest='build_index')
    parser.add_option('-s', '--search-type', action='store', default='phrase',
            help='Valid search types are: phrase, multiword, anyword, eitheror, mixed, regex, combined, combined_phrase, sword, sword_phrase, sword_multiword, sword_entryattrib, and sword_lucene. (default: phrase)',
            dest='search_type')
    parser.add_option('-S', '--strongs', action='store_true', default=False,
                        help='Search for strongs numbers. (Ignored in mixed search)', dest='search_strongs')
    parser.add_option('-M', '--morph', action='store_true', default=False,
                        help='Search for morphological tags. (Ignored in mixed search)', dest='search_morphology')
    parser.add_option('-C', '--case', action='store_true', default=False,
                        help='Case sensitive. (Ignored in regex search)',
                        dest='case_sensitive')
    parser.add_option('-R', '--range', action='store', default='',
                        help='Range to search in...', dest='search_range')
    parser.add_option('-l', '--lookup', action='store_true', default=False,
                        help='Lookup verses by reference.',
                        dest='verse_reference')
    parser.add_option('-d', '--daily', action='store',
                      default='', help='Lookup the devotional in \
                            Bagsters Daily light.', dest='day')
    parser.add_option('', '--lookup-strongs', action='store', default='',
                        help="A comma seperated list of Strong's Numbers to lookup.", dest='numbers')
    parser.add_option('', '--lookup-morphology', action='store', default='',
                        help='A comma seperated list of Morphological Tags to lookup.', dest='tags')
    parser.add_option('', '--lookup-webster', action='store', default='',
                        help='A comma seperated list of words to lookup in websters dictionary.', dest='words')
    parser.add_option('', '--lookup-kjvd', action='store', default='',
                        help='A comma seperated list of words to lookup in kjv dictionary.', dest='kjv_words')
    parser.add_option('', '--one-line', action='store_true', default=False,
                        help='Print all the verses on one line.', 
                        dest='one_line')
    parser.add_option('', '--context', action='store', default=0, type="int",
                        help='The number of verses before and after the match\
                              to include in the output.',
                        dest='context')
    parser.add_option('-n', '--numbers', action='store_true', default=False,
                        help="Include the Strong's numbers in the verse \
                              output.", dest='show_numbers')
    parser.add_option('-t', '--tags', action='store_true', default=False,
                        help="Include the Morphological tags in the verse \
                              output.", dest='show_tags')
    parser.add_option('-r', '--verse_ref', action='store_true', default=False,
                        help='Show only a sorted list of references', 
                        dest='list_only')
    parser.add_option('-q', '--quiet', action='store_true', default=False,
                        help='Only print the number of verses found.', 
                        dest='quiet')

    options, args = parser.parse_args()
    main(args, **options.__dict__)
