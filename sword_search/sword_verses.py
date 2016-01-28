#!/usr/bin/env python
# vim: sw=4:ts=4:sts=4:fdm=indent:fdl=0:
# -*- coding: UTF8 -*-
#
# A sword KJV indexed search module.
# Copyright (C) 2012-2013 Josiah Gordon <josiahg@gmail.com>
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
# along with this program.  If not, see <http:#www.gnu.org/licenses/>.

from collections import defaultdict
from xml.dom.minidom import parseString
from textwrap import fill
from os.path import dirname as os_dirname
from os.path import join as os_join
import dbm
import sys
import re

import Sword

from .utils import *

data_path = os_join(os_dirname(__file__), 'data')


def book_gen():
    """ A Generator function that yields book names in order.

    """

    # Yield a list of all the book names in the bible.
    verse_key = Sword.VerseKey('Genesis 1:1')
    for testament in [1, 2]:
        for book in range(1, verse_key.bookCount(testament) + 1):
            yield(verse_key.bookName(testament, book))
# book_list = list(book_gen())
try:
    book_list = []
    for book in book_gen():
        book_list.append(book)
except:
    pass


# Key function used to sort a list of verse references.
def sort_key(ref):
    """ Sort verses by book.

    """

    try:
        book, chap_verse = ref.rsplit(' ', 1)
        chap, verse = chap_verse.split(':')
        val = '%02d%03d%03d' % (int(book_list.index(book)), int(chap),
                                int(verse))
        return val
    except Exception as err:
        print('Error sorting "%s": %s' % (ref, err), file=sys.stderr)
        sys.exit()


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
    verse_list = verse_key.parseVerseList(verse_ref_str, 'Genesis 1:1', True,
                                          False)

    verse_set = set()
    for i in range(verse_list.getCount()):
        key = Sword.VerseKey(verse_list.getElement(i))
        if key:
            upper = key.getUpperBound().getText()
            lower = key.getLowerBound().getText()
            if upper != lower:
                verse_set.update(VerseIter(lower, upper))
            else:
                verse_set.add(key.getText())

    return verse_set


def add_context(ref_set, count=0):
    """ Add count number of verses before and after each reference.

    """

    if count == 0:
        return ref_set

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


def mod_to_dbm(module: str, key_iter: iter, path: str) -> str:
    """ Reads all the elements of key_iter from the module and saves them to a
    dbm file.

    """

    lookup = Lookup(module_name=module)
    dbm_name = '%s/%s.dbm' % (path, module)

    with IndexDbm(dbm_name, 'nf') as dbm_file:
        for key in key_iter:
            dbm_file[key] = lookup.get_raw_text(key)

    return dbm_name


def make_daily_dbm(path: str=INDEX_PATH) -> str:
    """ Saves the daily devotional to a dbm file.

    """

    from datetime import date, timedelta

    # Use a leap year to get all the days in February.
    start = date(2012, 1, 1)

    date_iter = ((start + timedelta(i)).strftime('%m.%d') for i in range(365))
    return mod_to_dbm('Daily', date_iter, path)


def make_strongs_dbm(path: str=INDEX_PATH) -> str:
    """ Saves the StrongsReal modules as dbms.

    """

    keys = IndexDict('KJV')['_strongs_']
    greek_keys = (i[1:] for i in keys if i.startswith('G'))
    hebrew_keys = (i[1:] for i in keys if i.startswith('H'))

    greek_file = mod_to_dbm('StrongsRealGreek', greek_keys, path)
    hebrew_file = mod_to_dbm('StrongsRealHebrew', hebrew_keys, path)

    return '\n'.join((greek_file, hebrew_file))


def make_robinson_dbm(path: str=INDEX_PATH) -> str:
    """ Save robinson morph definitions in a dbm.

    """

    keys = IndexDict('KJV')['_morph_']
    robinson_keys = (i for i in keys if not i.startswith('TH'))

    return mod_to_dbm('Robinson', robinson_keys, path)


def make_raw_kjv_dbm(path: str=INDEX_PATH) -> str:
    """ Saves the KJV modules raw text as a dbm.

    """

    verse_iter = VerseIter('Genesis 1:1')
    return mod_to_dbm('KJV', verse_iter, path)


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

        self._bold_regx = re.compile(r'<b>(\w+)</b>', re.I)
        self._italic_regx = re.compile(r'''
                            (?:<i>|<hi\s*type="italic">)
                            ([\w\s]+)(?:</i>|</hi>)
                            ''', re.I | re.X)
        self._br_regx = re.compile(r'(<br[\s]*/>|<lb/>)[\s]?', re.I)
        self._cleanup_regx = re.compile(r'<[^>]*>')
        self._brace_regx = re.compile(r'\{([\W]*)([\w]*)([\W]*)\}')
        self._parenthesis_regx = re.compile(r'\(([\W]*)([\w]*)([\W]*)\)')
        self._bracket_regx = re.compile(r'\[([\W]*)([\w ]*)([\W]*)\]')
        self._verse_ref_regx = re.compile(r'''
                            <scripRef[^>]*>
                            ([^<]*)
                            </scripRef>
                            ''', re.I)

    def get_text(self, key):
        """ Get the text at the given key in the module.
        i.e. get_text('3778') returns the greek strongs.

        """

        encoding = get_encoding()
        self._module.setKey(Sword.SWKey(key))
        item_text = self._module.renderText()
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
                 module='KJV', markup=Sword.FMT_PLAIN, render=''):
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

        if render.lower() == 'raw':
            self._render_func = self._module.getRawEntry
        elif render.lower() == 'render_raw':
            self._fix_space_regx = re.compile(r'([^\.:\?!])\s+')
            self._fix_end_regx = re.compile(r'\s+([\.:\?!,;])')
            self._fix_start_tag_regx = re.compile(r'(<[npi]>)\s*')
            self._fix_end_tag_regx = re.compile(r'\s*(</[npi]>)')
            self._upper_divname_regx = re.compile(r'(\w+)([\'s]*)')
            self._render_func = \
                    lambda: self._parse_raw(self._module.getRawEntry(),
                                            strongs, morph)
        else:
            self._render_func = self._module.renderText

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

        verse_text = self._render_func()
        if self._render_func == self._module.renderText:
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
            return self._module.renderText(''.join(heading_list))
        else:
            return ''

    def _parse_xml(self, xml_dom, strongs=False, morph=False):
        """ Recursively parse all the childNodes in a xml minidom, and build
        the verse text.

        """

        # The string that will hold the verse.
        verse_text = ''
        # The name of the current tag.
        name = xml_dom.localName if xml_dom.localName else ''
        strongs_str = morph_str = ''
        if xml_dom.attributes:
            attr_dict = dict(xml_dom.attributes.items())
            info_print(attr_dict, tag=4)
            # Get any paragraph marker.
            if 'marker' in attr_dict:
                verse_text = '<p>%s</p> ' % attr_dict['marker']
            else:
                verse_text = ''
            italic_str = '%s'
            note_str = '%s'
            for key, value in attr_dict.items():
                # Italicize any added text.
                if 'added' in value.lower():
                    italic_str = '<i>%s</i> '
                # Label study notes.
                elif 'study' in value.lower() or 'note' in name.lower():
                    note_str = '<n>%s</n>'
                # Check for strongs.
                elif 'lemma' in key.lower() and strongs:
                    for num in value.split():
                        strongs_str += ' <%s>' % num.split(':')[1]
                # Check for morphology.
                elif 'morph' in key.lower() and morph:
                    for tag in value.split():
                        morph_str += ' {%s}' % tag.split(':')[1]
        # Recursively build the text from all the child nodes.
        for node in xml_dom.childNodes:
            child_s = self._parse_xml(node, strongs, morph)
            if 'divine' in name.lower():
                verse_text += \
                        ' %s' % self._upper_divname_regx.sub(
                                lambda m: m.group(1).upper() + m.group(2),
                                child_s)
            else:
                verse_text += '%s' % child_s

        if xml_dom.attributes:
            return italic_str % note_str % '%s%s%s' % (verse_text, strongs_str,
                                                       morph_str)
        if hasattr(xml_dom, 'data'):
            info_print(xml_dom.data, tag=4)
            return xml_dom.data
        return verse_text.strip()

    def _parse_raw(self, raw_text, strongs=False, morph=False):
        """ Parse raw verse text and return a formated version.

        """

        # A hack to make the raw text parse as xml.
        xml_text = '''<?xml version="1.0"?>
        <root xmlns="%s">
        %s
        </root>'''

        # It works now we can parse the xml dom.
        try:
            parsed_xml = parseString(xml_text % ('verse', raw_text))
            parsed_str = self._parse_xml(parsed_xml, strongs, morph)
        except Exception as err:
            print('Error %s while processing %s.\n' % (err, raw_text),
                  file=sys.stderr)
            parsed_str = raw_text
        # Make all the spacing correct.
        fixed_str = self._fix_end_regx.sub('\\1', parsed_str)
        fixed_str = self._fix_space_regx.sub('\\1 ', fixed_str)
        fixed_str = self._fix_start_tag_regx.sub('\\1', fixed_str)
        fixed_str = self._fix_end_tag_regx.sub('\\1', fixed_str)
        return fixed_str.replace('\n', '')


class RawDict(object):
    """ Parse raw verse text into a dictionary so it can easly be found out how
    words are translated and how Strong's numbers are used.

    """

    def __init__(self, reference_iter,  module='KJV'):
        """ Initialize the sword module.

        """

        # This doesn't matter.
        markup = Sword.MarkupFilterMgr(Sword.FMT_PLAIN)

        # We don't own this or it will segfault.
        markup.thisown = False
        self._library = Sword.SWMgr(markup)

        self._module = self._library.getModule(module)
        self._key = self._module.getKey()

        self._ref_iter = reference_iter

        self._fix_space_regx = re.compile(r'([^\.:\?!])\s+')
        self._fix_end_regx = re.compile(r'\s+([\.:\?!,;])')
        self._remove_tag_regx = re.compile(r'(<i>\s?|\s?</i>)')
        self._fix_start_tag_regx = re.compile(r'(<i>)\s*')
        self._fix_end_tag_regx = re.compile(r'\s*(</i>)')

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
        verse_dict = self.get_dict(verse_ref)

        return (verse_ref, verse_dict)

    def __iter__(self):
        """ Returns an iterator of self.

        """

        return self

    def get_dict(self, verse_reference):
        """ Lookup the verse reference in the sword module specified and
        return a dictionary from it.

        """

        self._key.setText(verse_reference)
        raw_text = self._module.getRawEntry()
        return self._get_parsed_dict(raw_text, True, True)

    def _raw_to_dict(self, xml_dom, strongs=False, morph=False):
        """ Recursively parse all the childNodes in a xml minidom, and build
        a dictionary to use for telling what strongs numbers go to what words
        and vise versa.

        """

        # The dictionary that will hold the verse.
        verse_dict = defaultdict(list)
        verse_dict['_words'].append(defaultdict(list))
        # Recursively build the text from all the child nodes.
        child_s = ''
        # The string that will hold the verse.
        verse_text = ''
        # The name of the current tag.
        name = xml_dom.localName if xml_dom.localName else ''
        # Build up the dictionary and verse text from the child nodes.
        for node in xml_dom.childNodes:
            child_s, child_d = self._raw_to_dict(node, strongs, morph)
            if 'divine' in name.lower():
                # Uppercase 'LORD's in the text.
                verse_text += ' %s' % child_s.upper()
            else:
                verse_text += ' %s' % child_s
            for key, value in child_d.items():
                # Cleanup the items in the dictionary.
                if value and not isinstance(value[0], dict):
                    new_list = set(value).union(verse_dict[key])
                else:
                    new_list = value
                if key == '_words':
                    # Update the words dictionary.
                    for words, lst in value[0].items():
                        new_list = filter(any, lst)
                        verse_dict['_words'][0][words].extend(new_list)
                else:
                    # Make sure all items in the list are not None.
                    verse_dict[key].extend(filter(any, new_list))

        if xml_dom.attributes:
            attr_dict = dict(xml_dom.attributes.items())
            # Cleanup and format the verse text.
            verse_text = self._fix_end_regx.sub('\\1', verse_text)
            verse_text = self._fix_space_regx.sub('\\1 ', verse_text)
            verse_text = self._fix_start_tag_regx.sub('\\1', verse_text)
            verse_text = self._fix_end_tag_regx.sub('\\1', verse_text)
            verse_text = verse_text.replace('\n', '')
            # Text clean of all italic tags.
            clean_text = self._remove_tag_regx.sub('', verse_text)
            italic_str = '%s'
            # Dictionary to hold Strong's and Morphological attributes.
            attrib_dict = defaultdict(list)
            strongs_str = morph_str = ''
            for key, value in attr_dict.items():
                # Check for strongs.
                if 'lemma' in key.lower():
                    for num in value.split():
                        # Get the number.
                        num = num.split(':')[1]
                        attrib_dict['strongs'].append(num)
                        # Associate the text with the number.
                        verse_dict[num].append(clean_text.strip())
                        if strongs:
                            strongs_str += ' <%s> ' % num
                    # Cleanup the attribute dictionary.
                    attrib_dict['strongs'] = list(set(attrib_dict['strongs']))
                # Check for morphology.
                elif 'morph' in key.lower():
                    for tag in value.split():
                        # Get the tag.
                        tag = tag.split(':')[1]
                        attrib_dict['morph'].append(tag)
                        # Associate the text with the tag.
                        verse_dict[tag].append(clean_text.strip())
                        if morph:
                            morph_str += ' {%s} ' % tag
                    # Cleanup the attribute dictionary.
                    attrib_dict['morph'] = list(set(attrib_dict['morph']))
            if attrib_dict:
                # Associate the numbers and tags with the text.
                verse_dict['_words'][0][clean_text.strip()].append(attrib_dict)
            elif 'type' in attr_dict or 'subType' in attr_dict:
                _sub_type = attr_dict.get('subType', '')
                _type = attr_dict.get('type', _sub_type)
                if _type.lower() == 'x-p' or 'marker' in attr_dict:
                    # Get any paragraph marker.
                    verse_dict['_x-p'].append(attr_dict['marker'].strip())
                elif 'study' in _type.lower() or 'note' in name.lower():
                    verse_dict['_notes'].append(verse_text.strip())
                if 'added' in _type.lower() or 'added' in _sub_type.lower():
                    if 'marker' not in attr_dict:
                        # Italicize any added text.
                        italic_str = '<i>%s</i>'
                        verse_dict['_added'].append(verse_text.strip())
                elif 'section' in _type.lower() or \
                     'preverse' in _sub_type.lower():
                    # Add the preverse heading.
                    verse_dict['_preverse'].append(verse_text.strip())
                else:
                    # Don't include unwanted tags (e.g. strongs markup and
                    # notes) in the text.
                    verse_text = ''
            elif 'xmlns' in attr_dict:
                verse_text = verse_text.strip()
                # Include the entire verse text in the dictionary.
                verse_dict['_%s' % attr_dict['xmlns']].append(verse_text)

            # Build up the verse string.
            temp_str = '%s%s%s' % (verse_text, strongs_str, morph_str)
            verse_text = italic_str % temp_str
        if hasattr(xml_dom, 'data'):
            return xml_dom.data, verse_dict

        return verse_text, verse_dict

    def _get_parsed_dict(self, raw_text, strongs=False, morph=False):
        """ Parse raw verse text and return a formated version.

        """

        info_print(raw_text, tag=31)

        # A hack to make the raw text parse as xml.
        xml_text = '''<?xml version="1.0"?>
        <root xmlns="%s">
        %s
        </root>''' % ('verse_text', raw_text)

        # It works now we can parse the xml dom.
        try:
            parsed_xml = parseString(xml_text)
            return self._raw_to_dict(parsed_xml, strongs, morph)
        except Exception as err:
            info_print('Error %s while processing %s.\n' % (err, raw_text),
                       tag=31)
            return raw_text, {'_verse_text': [raw_text],
                              '_words': [defaultdict(list)]}


class VerseIter(object):
    """ Iterator of verse references.

    """

    def __init__(self, start, end='Revelation of John 22:21'):
        """ Setup the start and end references of the range.

        """

        # Make sure the range is in order.
        start, end = sorted([start, end], key=sort_key)
        self._verse = Sword.VerseKey(start, end)
        self._end_ref = self._verse.getUpperBound().getText()

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


class IndexBible(object):
    """ Index the bible by Strong's Numbers, Morphological Tags, and words.

    """

    def __init__(self, module='KJV', path=''):
        """ Initialize the index dicts.

        """

        self._module_name = module
        self._path = path if path else INDEX_PATH

        # Remove morphological and strongs information.
        self._cleanup_regx = re.compile(r'\s*(<([GH]\d*)>|\{([A-Z\d-]*)\})')
        # Note removal regular expression.
        self._remove_notes_regex = re.compile(r'\s?<n>\s?(.*?)\s?</n>', re.S)
        self._remove_tags_regex = re.compile(r'<[/]?[pin]>')

        self._non_alnum_regx = re.compile(r'\W')
        self._fix_regx = re.compile(r'\s+')
        self._strongs_regx = re.compile(r'\s<([GH]\d+)>', re.I)
        self._morph_regx = re.compile(r'\s\{([\w-]+)\}', re.I)

        self._module_dict = defaultdict(list)
        # lower_case is used to store lower_case words case sensitive
        # counterpart.  _Words_ is for easy key lookup for partial words.
        self._words_set = set()
        self._strongs_set = set()
        self._morph_set = set()
        self._module_dict.update({'lower_case': defaultdict(list)})

        self._index_dict = {
                '%s_index_i' % self._module_name: self._module_dict
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
            self._strongs_set.add(strongs_num)
            self._module_dict[strongs_num].append(verse_ref)

    def _index_morph(self, verse_ref, verse_text):
        """ Update the modules mophological dictionary from the verse text.

        """

        morph_list = set(self._morph_regx.findall(verse_text))
        for morph_num in morph_list:
            self._morph_set.add(morph_num)
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
                self._words_set.add(word)
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
        verse_iter = VerseTextIter(book_iter, True, True, self._module_name,
                                   render='render_raw')

        for verse_ref, verse_text in verse_iter:
            info_print('\033[%dD\033[KIndexing...%s' % \
                       (len(verse_ref) + 20, verse_ref), end='')

            # Put the entire Bible in the index, so we can pull it out
            # faster.
            self._module_dict[verse_ref] = verse_text
            # Remove the notes so we don't search them.
            verse_text = self._remove_notes_regex.sub('', verse_text)
            # Remove tags so they don't mess anything up.
            verse_text = self._remove_tags_regex.sub('', verse_text)

            # Index everything else.
            self._index_strongs(verse_ref, verse_text)
            self._index_morph(verse_ref, verse_text)
            self._index_words(verse_ref, verse_text)

    def build_index(self):
        """ Create index files of the bible for strongs numbers,
        morphological tags, and case (in)sensitive words.

        """

        info_print("Indexing %s could take a while..." % self._module_name)
        try:
            for book in self._book_gen():
                self._index_book(book)
        except:
            pass
        self._module_dict['_words_'].extend(self._words_set)
        self._module_dict['_strongs_'].extend(self._strongs_set)
        self._module_dict['_morph_'].extend(self._morph_set)

        info_print('\nDone.')

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
            info_print("Writing %s.dbm..." % name)
            # Save as just a plain text file.  Has to be loaded all at once,
            # so it is really slow.
            #with open(name, 'w') as index_file:
                #json.dump(dic, index_file, indent=4)
        #return
            # Save a dbm database that we can access without loading it all
            # into memeory so it is fast.
            dbm_name = '%s/%s.dbm' % (self._path, name)
            with IndexDbm(dbm_name, 'nf') as index_file:
                #with open(name, 'r') as i_file:
                    #dic =json.load(i_file)
                index_file.update(dic)
