#!/usr/bin/env python
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


""" KJV indexer and search module.

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

from sys import argv, exit, stdout
from optparse import OptionParser
import json
import re
import locale

import Sword

class BibleBase(object):
    """ Base class for the bible searcher and the indexer.

    """

    def __init__(self, one_line=False, module='KJV'):
        """ Initializes the bible and other common things.

        """

        self._one_line = '\n' if not one_line else ' '
        self._module_name = module

        self._non_alnum_regx = re.compile(r'\W')
        self._fix_regx = re.compile(r'[ ]+')
        self._strongs_regx = re.compile(r'<([GH]\d*)>')
        self._morph_regx = re.compile(r'\(([A-Z\d-]*)\)')
        self._word_regx = re.compile(r'\b(\w*)\b')
        self._highlight_regx = None

        self._highlight_color = '\033[1m'
        self._strongs_color = '\033[36m'
        self._morph_color = '\033[35m'
        self._ref_color = '\033[32m'
        self._end_color = '\033[m'

        self._strongs_highlight = '<%s\\1%s>' % (self._strongs_color, 
                                                 self._end_color)
        self._morph_highlight = '(%s\\1%s)' % (self._morph_color,
                                               self._end_color)
        self._word_highlight = '\\1%s\\2%s\\3' % (self._highlight_color, 
                                                  self._end_color)

        markup = Sword.MarkupFilterMgr(Sword.FMT_PLAIN)

        # We don't own this or it will segfault.
        markup.thisown = False
        self._library = Sword.SWMgr(markup)
        self._library.setGlobalOption("Cross-references", "Off")
        self._library.setGlobalOption("Strong's Numbers", "Off")
        self._library.setGlobalOption("Morphological Tags", "Off")

        self._module = self._library.getModule(module)

        self._show_strongs = self._library.getGlobalOption("Strong's Numbers")
        self._show_morph = self._library.getGlobalOption("Morphological Tags")

        lang, enc = locale.getlocale()
        if not lang or lang == 'C':
            self._enc = 'ascii'
        else:
            self._enc = enc

        self._search_list = []
        self.case_sensitive = False
        self._split_highlight = False

    def verses(self, start, end='Revelation of John 22:21', strongs=False,
               morph=False):
        """ Generator that yields all the verses between start and end.

        """

        self._toggle_strongs('On' if strongs else 'Off')
        self._toggle_morph('On' if morph else 'Off')

        start = verse_ref = Sword.VerseKey(start).getText()
        end = Sword.VerseKey(end).getText()
        self._module.setKey(Sword.SWKey(start))
        while verse_ref != end:
            verse_ref = self._module.getKeyText()
            verse_text = self._module.RenderText()
            yield (verse_ref, verse_text)
            self._module.increment()

        self._toggle_strongs('Off')
        self._toggle_morph('Off')

    def in_range(self, verse_ref, range_list):
        """ Checks to see if verse_ref is in the provided range.
        If an empy range is provided than the return value is True.

        """

        if not range_list:
            return True

        verse_key1 = Sword.VerseKey(range_list[0])
        verse_key2 = Sword.VerseKey(range_list[1])

        verse_key = Sword.VerseKey(verse_ref)

        if verse_key >= verse_key1 and verse_key <= verse_key2:
            return True
        
        return False

    def _make_in_range(self, verse_set, range_list):
        """ Return a set of verses from verse_set that are in the range
        range_list.

        """

        range_set = set(VerseRefIter(*range_list))
        return range_set.intersection(verse_set)

    def _show_strongs_morph(func):
        """ Temporary toggle the rendering of Morphological tags, and
        Strong's numbers while running func.

        """

        def wrapper(self, *args, **kwargs):
            self._toggle_strongs('On' if self.strongs else 'Off')
            self._toggle_morph('On' if self.morph else 'Off')

            ret_val = func(self, *args, **kwargs)

            self._toggle_strongs('Off')
            self._toggle_morph('Off')

            return ret_val
        return wrapper

    def _toggle_strongs(self, toggle):
        """ Enable/disable Strong's Number rendering.

        """

        self._library.setGlobalOption("Strong's Numbers", toggle)

    def _toggle_morph(self, toggle):
        """ Enable/disable Morphological tag rendering.

        """

        self._library.setGlobalOption("Morphological Tags", toggle)

    def _get_options(func):
        """ Wraps the strongs and morph getter properties.

        """

        def wrap_func(self, *args):
            if func.__name__ == 'strongs':
                return True if self._show_strongs == 'On' else False
            else:
                return True if self._show_morph == 'On' else False

        return wrap_func

    def _set_options(func):
        """ Wraps the strongs and morph setter properties.

        """

        def wrap_func(self, value):
            value = 'On' if value else 'Off'
            if func.__name__ == 'strongs':
                self._show_strongs = value
            else:
                self._show_morph = value

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

    def index(self, verse_ref): 
        """ Returns the index of the verse in the bible.

        """

        return Sword.VerseKey(verse_ref).Index()

    def _verse_range(self, ref_str):
        """ Returns a set of verse references in the ranges provided.

        """

        ref_list = ref_str.split()
        verse_set = set()
        ref_list = ','.join(ref_list).split(',')
        for i in range(0, len(ref_list), 2):
            range_list = sorted(ref_list[i:i + 2], key=self.index)
            if len(range_list) != 1:
                verse_set.update(VerseRefIter(*range_list))
            elif range_list[0]:
                verse_set.add(range_list[0])

        return verse_set

    def lookup(self, verse_ref_list, range_str=''):
        """ Return a list of valid verse refrences.

        """

        if range_str:
            return self._verse_range(range_str)

        verse_list = Sword.VerseKey().ParseVerseList(' '.join(verse_ref_list))
        return set(verse_list.getRangeText().split(';'))

    def verse_text(self, verse_ref):
        """ Return the verse text of the provided reference.

        """

        self._module.setKey(Sword.SWKey(verse_ref))
        verse_text = self._module.RenderText().strip()

        return verse_text

    def clean_text(self, text):
        """ Return a clean (only alphanumeric) text of the provided string.

        """

        temp_text = self._non_alnum_regx.sub(' ', text) 
        clean_text = self._fix_regx.sub(' ', temp_text)

        return clean_text.strip()

    def verse_list(self, verse_ref_set, highlight=False):
        """ Return a list of formated and (if specified) highlighted
        verses.

        """

        if highlight and self._search_list:
            if self.strongs or self.morph or self._split_highlight:
                search_string = '|'.join(self._search_list)
            else:
                search_string = ' '.join(self._search_list)
            reg_str = r'(\(|<|\b)(%s)(\b|>|\))' % search_string
            flags = re.A
            if not self.case_sensitive:
                flags |= re.I
            self._highlight_regx = re.compile(reg_str, flags)

        verse_list = []

        if not verse_ref_set:
            return []

        verse_iter = VerseIter(verse_list_iter(verse_ref_set))
        verse_iter.morph = self.morph
        verse_iter.strongs = self.strongs

        for verse_ref, verse_text in verse_iter:
            if highlight:
                verse_text = self._highlight(verse_text.strip())
            verse_text = verse_text.encode(self._enc, 'ignore')
            verse_text = "%s%s%s: %s%s" % (self._ref_color, verse_ref.strip(), 
                                           self._end_color,
                                           verse_text.decode(self._enc, 'ignore'),
                                           self._one_line)
            verse_list.append(verse_text)
        return verse_list

    @_show_strongs_morph
    def print_verse_list(self, verse_ref_list, highlight=False):
        """ Print each verse in the list.

        """

        verse_text = self._one_line.join(self.verse_list(verse_ref_list, 
                                                         highlight))
        print(verse_text)

    def _highlight(self, verse_text):
        """ Returns a highlighted version of verse_text.  All Strong's
        numbers, morphological tags, and the search_text is hightlighted.

        """

        if self._highlight_regx:
            verse_text = self._highlight_regx.sub(self._word_highlight, 
                                                  verse_text)

        verse_text = self._strongs_regx.sub(self._strongs_highlight, verse_text)
        verse_text = self._morph_regx.sub(self._morph_highlight, verse_text)

        return verse_text

def verse_list_iter(verse_ref_set):
    """ Returns an iterator over a sorted version of verse_ref_set.

    """

    # Speed up the iteration by first sorting the range.
    sort_key = lambda r: Sword.VerseKey(r).Index()
    return iter(sorted(verse_ref_set, key=sort_key))

class VerseRefIter(object):
    """ Iterator of verse references.

    """

    def __init__(self, start, end='Revelation of John 22:21'):
        """ Initialize.

        """

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

class VerseIter(object):
    """ An iterable object for accessing verses in the Bible.  Maybe it will
    be easier maybe not.

    """

    def __init__(self, reference_iter, module='KJV'):
        """ Initialize.

        """

        markup = Sword.MarkupFilterMgr(Sword.FMT_PLAIN)
        
        # We don't own this or it will segfault.
        markup.thisown = False
        self._library = Sword.SWMgr(markup)
        self._library.setGlobalOption("Cross-references", "Off")
        self._library.setGlobalOption("Strong's Numbers", "Off")
        self._library.setGlobalOption("Morphological Tags", "Off")

        self._module = self._library.getModule(module)

        self._ref_iter = reference_iter

    def next(self):
        """ Returns the next verse reference and text.

        """

        return self.__next__()

    def __next__(self):
        """ Returns the next verse reference and text.

        """

        self._verse_ref = next(self._ref_iter)
        self._module.setKey(Sword.VerseKey(self._verse_ref))
        verse_text = self._module.RenderText()

        return (self._verse_ref, verse_text)

    def __iter__(self):
        """ Returns an iterator of self.

        """

        return self

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

class BookIter(VerseRefIter):
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
        self._fix_regx = re.compile(r'[ ]+')
        self._strongs_regx = re.compile(r'<([GH]\d*)>')
        self._morph_regx = re.compile(r'\(([A-Z\d-]*)\)')

        self._strongs_dict = {}
        self._morph_dict = {}
        self._word_dict = {}
        self._case_word_dict = {}

    def _book_gen(self):
        """ A Generator function that yields book names in order.

        """

        verse_key = Sword.VerseKey('Genesis 1:1')
        for testament in range(1, 3):
            for book in range(1, verse_key.bookCount(testament) + 1):
                yield(verse_key.bookName(testament, book))
                
    def _index_strongs(self, verse_ref, verse_text):
        """ Update the modules strongs dictionary from the verse text.

        """

        strongs_list = set(self._strongs_regx.findall(verse_text))
        for strongs_num in strongs_list:
            temp_list = self._strongs_dict.get(strongs_num, [])
            temp_list.append(verse_ref)
            self._strongs_dict[strongs_num] = temp_list

    def _index_morph(self, verse_ref, verse_text):
        """ Update the modules mophological dictionary from the verse text.

        """

        morph_list = set(self._morph_regx.findall(verse_text))
        for morph_num in morph_list:
            temp_list = self._morph_dict.get(morph_num, [])
            temp_list.append(verse_ref)
            self._morph_dict[morph_num] = temp_list

    def _index_words(self, verse_ref, verse_text):
        """ Update the modules word dictionary from the verse text.

        """

        clean_text = self._cleanup_regx.sub('', verse_text)
        clean_text = self._non_alnum_regx.sub(' ', clean_text) 
        clean_text = self._fix_regx.sub(' ', clean_text).strip()

        verse_text = self._strongs_regx.sub('', verse_text)
        verse_text = self._morph_regx.sub('', verse_text)

        # Strip out all unicode so we can search correctly.
        verse_text = verse_text.encode('ascii', 'ignore')
        verse_text = verse_text.decode('ascii', 'ignore')
        verse_text = self._non_alnum_regx.sub(' ', verse_text) 
        verse_text = self._fix_regx.sub(' ', verse_text).strip()
        verse_set = set(verse_text.lower().split())
        verse_set.update(set(clean_text.lower().split()))
        
        for word in verse_set:
            if word:
                temp_list = self._word_dict.get(word, [])
                temp_list.append(verse_ref)
                self._word_dict[word] = temp_list

        # Include the capitalized words for case sensitive search.
        case_verse_set = set(verse_text.split())
        case_verse_set.update(set(clean_text.split()))

        for word in case_verse_set:
            if word:
                temp_list = self._case_word_dict.get(word, [])
                temp_list.append(verse_ref)
                self._case_word_dict[word] = temp_list

    def _index_book(self, book_name="Genesis"):
        """ Creates an indexes for strongs, morphology and words.

        """

        book_iter = BookIter(book_name)
        verse_iter = VerseIter(book_iter, self._module_name)
        verse_iter.strongs = verse_iter.morph = True

        for verse_ref, verse_text in verse_iter:
            print('\033[%dD\033[KIndexing...%s' % \
                    (len(verse_ref) + 20, verse_ref), end='')
            stdout.flush()

            self._index_strongs(verse_ref, verse_text)
            self._index_morph(verse_ref, verse_text)
            self._index_words(verse_ref, verse_text)

    def build_index(self):
        """ Create index files of the bible for strongs numbers, 
        morphological tags, and words.

        """

        print("Indexing %s could take a while..." % self._module_name)
        for book in self._book_gen():
            self._index_book(book)

        print('\nDone.')

    def write_indexes(self):
        """ Write all the index dictionaries to their respective files.  If
        Any of the dictionaries is empty, then build the index.

        """

        if not self._word_dict or not self._strongs_dict or not \
                self._morph_dict:
            self.build_index()

        print("Writing strongs.dump...")
        with open('strongs.dump', 'w') as strongs_file:
            strongs_file.write(json.dumps(self._strongs_dict, indent=4))

        print("Writing morph.dump...")
        with open('morph.dump', 'w') as morph_file:
            morph_file.write(json.dumps(self._morph_dict, indent=4))

        print("Writing word.dump...")
        with open('word.dump', 'w') as word_file:
            word_file.write(json.dumps(self._word_dict, indent=4))

        print("Writing case_word.dump...")
        with open('case_word.dump', 'w') as word_file:
            word_file.write(json.dumps(self._case_word_dict, indent=4))

class BibleSearch(BibleBase):
    """ Search the bible for a phrase or any of the following:
        
        Strongs numbers
        Morphological tags
        Words

        Also it has an indexing function to index the bible.

    """

    def __init__(self, one_line=False, module='KJV'):
        """ Initialize the module and library information.

        """

        super(BibleSearch, self).__init__(one_line, module)

        self._range_set = set()

    def Search(self, search_list, strongs=False, morph=False, phrase=False,
               search_any=False, regex=False, case=False, search_range=''):
        """ Search(search_list, strongs=False, morph=False, phrase=False, 
        search_any=False, regex=False, case=False, search_range=None) -> Search
        for the items in the provided search_list. 
                
                strongs     -   Use the search list as strongs numbers
                morph       -   Use the search list as morphological tags
                regex       -   Use the search list as a regular expression
                phrase      -   Search for the search list as a phrase
                search_any  -   Find all verses that have any of the search
                                items or common words.
                build_index -   Re-build the search index before searching.
                default     -   Find all verses that have all the search
                                terms.

        """

        if case:
            self.case_sensitive = True

        if search_range:
            self._range_set = self._verse_range(search_range)

        self._search_list = ' '.join(search_list).split()
        if not phrase:
            self._split_highlight = True

        if regex:
            return self._regex_search(' '.join(self._search_list), strongs, 
                                      morph)
        else:
            return self._search(self._search_list, phrase, search_any, strongs,
                                morph)

    def _phrase_search(self, verse_ref, search_str, strongs=False,
                       morph=False):
        """ Searches for the phrase search phrase in the verse.

        """

        if self._range_set and verse_ref not in self._range_set:
            return False

        verse_text = self.verse_text(verse_ref)

        if strongs:
            verse_list = self._strongs_regx.findall(verse_text)
        elif morph:
            verse_list = self._morph_regx.findall(verse_text)
        else:
            if not self.case_sensitive:
                verse_text = verse_text.lower()
            verse_list = self.clean_text(verse_text).split()

        search_list = search_str.split()

        if search_list[0] not in verse_list:
            return False

        if ' %s ' % search_str in ' %s ' % ' '.join(verse_list):
            return True

        search_len = len(search_list)
        cur_index = -1
        while search_list[0] in verse_list[cur_index + 1:]:
            cur_index = verse_list.index(search_list[0], cur_index + 1)
            if search_list == verse_list[cur_index: cur_index + search_len]:
                return True
        return False

    def _phrase_search2(self, search_str, ref_list, strongs=False, morph=False):
        """ Searches for the phrase search phrase in the verse.

        """

        if self._range_set:
            ref_list = self._range_set.intersection(ref_list)

        found_set = set()
        verse_iter = VerseIter(verse_list_iter(set(ref_list)))
        verse_iter.strongs = strongs
        verse_iter.morph = morph
        search_list = search_str.split()
        search_len = len(search_list)
        for verse_ref, verse_text in verse_iter:
            if strongs:
                verse_list = self._strongs_regx.findall(verse_text)
            elif morph:
                verse_list = self._morph_regx.findall(verse_text)
            else:
                if not self.case_sensitive:
                    verse_text = verse_text.lower()
                verse_list = self.clean_text(verse_text).split()

            if search_list[0] not in verse_list:
                continue

            if ' %s ' % search_str in ' %s ' % ' '.join(verse_list):
                found_set.add(verse_ref)
            #cur_index = -1
            #while search_list[0] in verse_list[cur_index + 1:]:
                #cur_index = verse_list.index(search_list[0], cur_index + 1)
                #if search_list == verse_list[cur_index: cur_index + search_len]:
                    #found_set.add(verse_ref)
        return found_set

    def _phrase_search3(self, search_str, ref_list, strongs=False, morph=False):
        """ Searches for the phrase search phrase in the verse.

        """

        if self._range_set:
            ref_list = self._range_set.intersection(ref_list)

        found_set = set()
        search_list = search_str.split()
        search_len = len(search_list)
        for verse_ref in sorted(ref_list, key=self.index):
            verse_text = self.verse_text(verse_ref)
            if strongs:
                verse_list = self._strongs_regx.findall(verse_text)
            elif morph:
                verse_list = self._morph_regx.findall(verse_text)
            else:
                if not self.case_sensitive:
                    verse_text = verse_text.lower()
                verse_list = self.clean_text(verse_text).split()

            if search_list[0] not in verse_list:
                continue

            if ' %s ' % search_str in ' %s ' % ' '.join(verse_list):
                found_set.add(verse_ref)
            #cur_index = -1
            #while search_list[0] in verse_list[cur_index + 1:]:
                #cur_index = verse_list.index(search_list[0], cur_index + 1)
                #if search_list == verse_list[cur_index: cur_index + search_len]:
                    #found_set.add(verse_ref)
        return found_set

    def _set_intersect(self, search_list, verse_dict):
        """ Returns a set with only the verses that contain all the items in
        search_list.

        """


        least_common_set = set(verse_dict.get(search_list.pop(0), []))
        if least_common_set:
            for item in search_list:
                least_common_set.intersection_update(verse_dict.get(item, []))

        return least_common_set

    def _set_union(self, search_list, verse_dict):
        """ Returns a set with all the verses that contain each item in
        search_list.

        """

        verse_set = set(verse_dict.get(search_list.pop(0), []))
        for item in search_list:
            verse_set.update(verse_dict.get(item, []))
        return verse_set

    def _search(self, search_list, phrase=False, search_any=False,
                strongs=True, morph=False):
        """ _search(search_list, phrase=False, search_any=False, strongs=True)
        -> For the list of search terms.
                phrase      -   Find only the phrase phrase.
                search_any  -   Find any verse with the common words in the
                                search list
                strongs     -   If True it will search for strongs numbers.
                morph       -   If True it will search for morphological tags.

        """

        if not strongs and not morph:
            search_str = self.clean_text(' '.join(search_list)).strip()
            if not self.case_sensitive:
                search_str = search_str.lower()
                filename = 'word.dump'
            else:
                filename = 'case_word.dump'
        else:
            search_str = ' '.join(search_list).upper().strip()
            if strongs:
                self._library.setGlobalOption("Strong's Numbers", "On")
                filename = 'strongs.dump'
            else:
                self._library.setGlobalOption("Morphological Tags", "On")
                filename = 'morph.dump'

        if not search_str:
            return []

        print("Loading %s" % filename)
        try:
            with open(filename, 'r') as index_file:
                index_dict = json.loads(index_file.read())
        except IOError as err:
            print("Error loading file %s: %s" % (filename, err))

        return self._generic_search(search_str, index_dict, phrase,
                                    search_any, strongs, morph)

    def _generic_search(self, search_str, index_dict, phrase, search_any, 
                        strongs=False, morph=False):
        """ A generic search function used for words, phrases, strongs, and
        morphology.

        """

        sorted_search_list = sorted(set(search_str.split()), 
                key=lambda i: len(index_dict.get(i, [])))

        if not phrase or len(sorted_search_list) <= 1:
            if not search_any:
                search_list = sorted_search_list
                print('Searching for "%s"...' % \
                        ' AND '.join(search_str.split()), end='')
                found_verses = self._set_intersect(sorted_search_list, 
                                                   index_dict)
            else:
                print('Searching for "%s"...' % \
                        ' OR '.join(search_str.split()), end='')
                found_verses = self._set_union(sorted_search_list, index_dict)

            if self._range_set:
                found_verses = found_verses.intersection(self._range_set)
        else:
            found_verses = set()
            least_common_index = sorted_search_list[0]
            print('Searching for phrase "%s"...' % search_str, end='')
            stdout.flush()
            verse_list = self._set_intersect(sorted_search_list, index_dict)
            #verse_list = index_dict.get(least_common_index, [])
            found_verses = self._phrase_search2(search_str, verse_list,
                                                strongs=strongs, morph=morph)
            #found_verses = self._phrase_search3(search_str, verse_list,
                                                #strongs=strongs, morph=morph)
            #for verse_ref in sorted(verse_list, key=self.index):
            #for verse_ref in index_dict.get(least_common_index, []):
                #if self._phrase_search(verse_ref, search_str, strongs=strongs, 
                                       #morph=morph):
                    #found_verses.add(verse_ref)

        count = len(found_verses)
        print("Done.\nFound %s verse%s." % (count, 's' if count != 1 else ''))

        return found_verses

    def _regex_search(self, search_str, strongs=False, morph=False):
        """ Uses the search_str as a regular expression to search the bible and
        returns a list of matching verses.

        """

        print("Searching using the regular expression '%s'" % search_str)

        found_verses = set()
        search_regx = re.compile(search_str)

        if self._range_set:
            verse_iter = VerseIter(verse_list_iter(self._range_set))
        else:
            verse_iter = VerseIter('Genesis 1:1')
        verse_iter.strongs = strongs
        verse_iter.morph = morph

        for verse_ref, verse_text in verse_iter:
            print('\033[%dD\033[KSearching...%s' % \
                    (len(verse_ref) + 20, verse_ref), end='')
            stdout.flush()

            if search_regx.search(verse_text):
                found_verses.add(verse_ref)
            elif not strongs and not morph:
                clean_verse_text = self.clean_text(verse_text)
                if search_regx.search(clean_verse_text):
                    found_verses.add(verse_ref)

        return found_verses

if __name__ == '__main__':
    parser = OptionParser(description="Bible search.")
    parser.add_option('-i', '--index', action='store_true', default=False,
                        help='(Re-)build the search index.', dest='build_index')
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
    parser.add_option('', '--one-line', action='store_true', default=False,
                        help='Print all the verses on one line.', 
                        dest='one_line')
    parser.add_option('-q', '--quiet', action='store_true', default=False,
                        help='Only print the number of verses found.', 
                        dest='quiet')

    options, args = parser.parse_args()
    if args or options.build_index or options.search_range:
        options_dict = options.__dict__
        if options_dict.pop('build_index'):
            indexer = IndexBible()
            indexer.write_indexes()
            exit(0)
        one_line = options_dict.pop('one_line')
        search = BibleSearch(one_line=one_line)
        if options_dict.pop('show_numbers') or options.strongs:
            search.strongs = True
        if options_dict.pop('show_tags') or options.morph:
            search.morph = True
        quiet = options_dict.pop('quiet')
        list_only = options_dict.pop('list_only')
        lookup = options_dict.pop('lookup')
        if not args:
            verse_list = search.lookup('', options.search_range)
        elif not lookup:
            verse_list = search.Search(args, **options_dict)
        else:
            verse_list = search.lookup(args, options.search_range)

        if not quiet:
            print()
            if list_only:
                for i in sorted(verse_list, key=search.index):
                    print(i)
                print()
            else:
                search.print_verse_list(verse_list, highlight=True)
        count = len(verse_list)
        print("Done.\nFound %s verse%s." % (count, 's' if count != 1 else ''))
    else:
        parser.print_help()
