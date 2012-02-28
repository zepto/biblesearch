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

import Sword

class BibleSearch(object):
    """ Search the bible for a phrase or any of the following:
        
        Strongs numbers
        Morphological tags
        Words

        Also it has an indexing function to index the bible.

    """

    def __init__(self, module='KJV'):
        """ Initialize the module and library information.

        """

        self._module_name = module
        self._common_words = ['am', 'is', 'are', 'was', 'were', 'be', 'being', 
                              'been', 'have', 'has', 'had', 'do', 'does',
                              'did', 'shall', 'will', 'should', 'would', 'may',
                              'might', 'must', 'can', 'could', 'the', 'and',
                              'but', 'so', 'about', 'above', 'across', 'after',
                              'against', 'amid', 'among', 'around', 'at',
                              'atop', 'before', 'behind', 'below', 'beneeth',
                              'beside', 'between', 'behond', 'by', 'because',
                              'concerning', 'down', 'in', 'with', 'within',
                              'without', 'my', 'they', 'ye', 'them', 'he',
                              'she', 'him', 'her', 'to', 'that', 'which', 'if',
                              'we', 'from']

        self._non_alnum_regx = re.compile(r'\W')
        self._fix_regx = re.compile(r'[ ]+')
        self._strongs_regx = re.compile(r'<([GH]\d*)>')
        self._morph_regx = re.compile(r'\((\d*)\)')
        self._word_regx = re.compile(r'\b(\w*)\b')

        markup = Sword.MarkupFilterMgr(Sword.FMT_PLAIN)
        markup.thisown = False
        self._library = Sword.SWMgr(markup)
        self._library.setGlobalOption("Cross-references", "Off")
        self._library.setGlobalOption("Strong's Numbers", "Off")
        self._library.setGlobalOption("Morphological Tags", "Off")

        self._module = self._library.getModule(module)
        self._show_strongs = self._library.getGlobalOption("Strong's Numbers")
        self._show_morph = self._library.getGlobalOption("Morphological Tags")

    def build_index(self):
        """ Create index files of the bible for strongs numbers, 
        morphological tags, and words.

        """

        key = Sword.SWKey('Genesis 1:1')
        self._module.setKey(key)
        key_text = Sword.SWKey().getText()

        strongs_dict = {}
        morph_dict = {}
        word_dict = {}
        word_count_dict = {}

        print("Indexing %s could take a while..." % self._module_name, end='')
        perc_str = '|/-\\'
        count = 0
        verse_count = 0
        while self._module.getKeyText() != key_text:
            print('\033[1D\033[K%s' % perc_str[count], end='')
            stdout.flush()
            count = (count + 1) % len(perc_str)

            self._library.setGlobalOption("Strong's Numbers", "On")
            self._library.setGlobalOption("Morphological Tags", "On")

            verse_ref = self._module.getKeyText()
            verse_text = self._module.RenderText()

            strongs_list = set(self._strongs_regx.findall(verse_text))
            for strongs_num in strongs_list:
                temp_list = strongs_dict.get(strongs_num, [])
                temp_list.append(verse_ref)
                strongs_dict[strongs_num] = temp_list

            morph_list = set(self._morph_regx.findall(verse_text))
            for morph_num in morph_list:
                temp_list = morph_dict.get(morph_num, [])
                temp_list.append(verse_ref)
                morph_dict[morph_num] = temp_list

            verse_text = self._strongs_regx.sub('', verse_text)
            verse_text = self._morph_regx.sub('', verse_text)
            verse_text = self._non_alnum_regx.sub(' ', verse_text)
            verse_text = self._fix_regx.sub(' ', verse_text)
            verse_set = set(verse_text.lower().split())

            self._library.setGlobalOption("Strong's Numbers", "Off")
            self._library.setGlobalOption("Morphological Tags", "Off")
            verse_ref = self._module.getKeyText()
            verse_text = self._module.RenderText()

            verse_text = self._non_alnum_regx.sub(' ', verse_text)
            verse_text = self._fix_regx.sub(' ', verse_text)
            verse_set = verse_set.union(set(verse_text.lower().split()))
            
            #word_list = self._word_regx.findall(verse_text.lower())
            for word in verse_set: #set(verse_text.lower().split()):
                if word:
                    temp_list = word_dict.get(word, [])
                    temp_list.append(verse_ref)
                    word_dict[word] = temp_list
                    word_count_dict[word] = word_count_dict.get(word, 0) + 1
            verse_count += 1
            key_text = self._module.getKeyText()
            self._module.increment()

        word_count_dict['verse_count'] = verse_count
        print('\033[1D\033[KDone.')

        print("Writing strongs.dump...")
        with open('strongs.dump', 'w') as strongs_file:
            strongs_file.write(json.dumps(strongs_dict))

        print("Writing morph.dump...")
        with open('morph.dump', 'w') as morph_file:
            morph_file.write(json.dumps(morph_dict))

        print("Writing word.dump...")
        with open('word.dump', 'w') as word_file:
            word_file.write(json.dumps(word_dict))

        print("Writing word_count.dump...")
        with open('word_count.dump', 'w') as word_count_file:
            word_count_file.write(json.dumps(word_count_dict))

        self._library.setGlobalOption("Strong's Numbers", 'Off')
        self._library.setGlobalOption("Morphological Tags", 'Off')

    @property
    def show_strongs(self):
        """ Show whether strongs are shown.

        """

        return True if self._show_strongs == 'On' else False

    @show_strongs.setter
    def show_strongs(self, value):
        """ Set whether strongs should be shown.

        """

        self._show_strongs = 'On' if value else 'Off'

    @property
    def show_morphological(self):
        """ Show whether morphological tags are shown.

        """

        return True if self._show_morph == 'On' else False

    @show_strongs.setter
    def show_morphological(self, value):
        """ Set whether morphological tags should be shown.

        """

        self._show_morph = 'On' if value else 'Off'

    def _sort_by_book(self, verse_ref): 
        """ Sort function for sorting books of the bible.

        """

        name_list = [
                "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
                "Joshua", "Judges", "Ruth", "I Samuel", "II Samuel", "I Kings",
                "II Kings", "I Chronicles", "II Chronicles", "Ezra",
                "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
                "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah",
                "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
                "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah",
                "Haggai", "Zechariah", "Malachi", "Matthew", "Mark", "Luke",
                "John", "Acts", "Romans", "I Corinthians", "II Corinthians",
                "Galatians", "Ephesians", "Philippians", "Colossians", 
                "I Thessalonians", "II Thessalonians", "I Timothy", 
                "II Timothy", "Titus", "Philemon", "Hebrews", "James", 
                "I Peter", "II Peter", "I John", "II John", "III John", "Jude",
                "Revelation of John"
                ]

        name, chap_verse = verse_ref.rsplit(" ", 1)
        try:
            index =  name_list.index(name)
        except:
            print(name)
        chap, verse = chap_verse.split(':')
        num = "%03d%03d%03d" % (index, int(chap), int(verse))
        return num

    def lookup(self, verse_ref_list):
        """ Return a list of valid verse refrences.

        """

        ref_list = []

        for ref in verse_ref_list:
            self._module.setKey(Sword.SWKey(ref))
            ref_list.append(self._module.getKeyText())

        return list(set(ref_list))

    def verse_text(self, verse_ref):
        """ Return the verse text of the provided reference.

        """

        self._module.setKey(Sword.SWKey(verse_ref))
        verse_text = self._module.RenderText()

        return verse_text

    def clean_text(self, text):
        """ Return a clean (only alphanumeric) text of the provided string.

        """

        temp_text = self._non_alnum_regx.sub(' ', text) 
        clean_text = self._fix_regx.sub(' ', temp_text)

        return clean_text

    def print_verse_list(self, verse_ref_list, highlight=False):
        """ Print each verse in the list.

        """

        self._library.setGlobalOption("Strong's Numbers", self._show_strongs)
        self._library.setGlobalOption("Morphological Tags", self._show_morph)

        verse_ref_list.sort(key=self._sort_by_book)

        if highlight:
            highlight_regx = re.compile(r'(\(|<|\b)(%s)(\b|>|\))' % self._search_string, re.I)
        for verse_ref in verse_ref_list:
            verse_text = self.verse_text(verse_ref).strip()
            if highlight:
                verse_text = highlight_regx.sub('\\1\033[1;32m\\2\033[m\\3',
                                                verse_text.encode().decode('ascii', 'ignore'))
            print("%s: %s\n" % (verse_ref, verse_text))

        self._library.setGlobalOption("Strong's Numbers", 'Off')
        self._library.setGlobalOption("Morphological Tags", 'Off')

    def Search(self, search_list, strongs=False, morph=False, phrase=False,
               search_any=False, regex=False, build_index=False):
        """ Search(search_list, strongs=False, morph=False, phrase=False, 
        search_any=False, regex=False, build_index=False) -> Search for the
        items in the provided search_list. 
                
                strongs     -   Use the search list as strongs numbers
                morph       -   Use the search list as morphological tags
                regex       -   Use the search list as a regular expression
                search_any  -   Find all verses that have any of the search
                                items or common words.
                build_index -   Re-build the search index before searching.

        """

        if build_index:
            self.build_index()

        self._search_string = '|'.join(search_list)
        search_list = ' '.join(search_list).split()

        if strongs:
            return self._strongs_morph_search(search_list, phrase, search_any)
        elif morph:
            return self._strongs_morph_search(search_list, phrase, search_any,
                                              strongs=False)
        elif regex:
            return self._regex_search(' '.join(search_list), strongs, morph)
        else:
            return self._word_search(search_list, phrase, search_any)

    def _phrase_search(self, verse_ref, search_regx, strongs=False, morph=False):
        """ Searches for the phrase search phrase in the verse.

        """

        verse_text = self.verse_text(verse_ref)

        if strongs:
            strongs_list = self._strongs_regx.findall(verse_text)
            verse_text = ' '.join(strongs_list)
        elif morph:
            morph_list = self._morph_regx.findall(verse_text)
            verse_text = ' '.join(morph_list)

        clean_verse_text = self.clean_text(verse_text)

        if search_regx.search(clean_verse_text):
            return True
        else:
            return False

    def _all_search(self, verse_ref, search_str, strongs=False, morph=False):
        """ Returns True if search_set is a sub-set of verse.

        """

        search_set = set(search_str.split())

        verse_text = self.verse_text(verse_ref)

        if not strongs and not morph:
            search_set = set(search_str.lower().split())
            verse_set = set(verse_text.lower().split())
        elif strongs:
            strongs_list = self._strongs_regx.findall(verse_text)
            verse_set = set(strongs_list)
        elif morph:
            morph_list = self._morph_regx.findall(verse_text)
            verse_set = set(morph_list)

        if search_set.issubset(verse_set):
            return True
        else:
            clean_verse_text = self.clean_text(verse_text.lower())
            verse_set = set(clean_verse_text.split())
            return search_set.issubset(verse_set)

    def _set_intersect(self, search_list, verse_dict):
        """ Returns a set with only the verses that contain all the items in
        search_list.

        """

        least_common_set = set(verse_dict.get(search_list.pop(0), []))

        if least_common_set:
            for item in search_list:
                temp_set = set(verse_dict.get(item, []))
                least_common_set.intersection_update(temp_set)

        return tuple(least_common_set)

    def _set_union(self, search_list, verse_dict):
        """ Returns a set with all the verses that contain each item in
        search_list.

        """

        verse_set = set()
        for item in search_list:
            temp_set = set(verse_dict.get(item, []))
            verse_set.update(temp_set)
        return verse_set

    def _regex_search(self, search_str, strongs=False, morph=False):
        """ Uses the search_str as a regular expression to search the bible and
        returns a list of matching verses.

        """

        if strongs:
            self._library.setGlobalOption("Strong's Numbers", "On")
        if morph:
            self._library.setGlobalOption("Morphological Tags", "On")

        key = Sword.SWKey('Genesis 1:1')
        self._module.setKey(key)
        key_text = Sword.SWKey().getText()

        found_verses = []

        search_regx = re.compile(search_str)

        print("Searching using the regular expression '%s'" % search_str)
        perc_str = '|/-\\'
        count = 0
        while self._module.getKeyText() != key_text:
            print('\033[1D\033[K%s' % perc_str[count], end='')
            stdout.flush()
            count = (count + 1) % len(perc_str)
            verse_ref = self._module.getKeyText()
            verse_text = self._module.RenderText()

            if search_regx.search(verse_text) or \
                    search_regx.search(verse_text.lower()):
                found_verses.append(verse_ref)
            elif not strongs and not morph:
                clean_verse_text = self.clean_text(verse_text)
                if search_regx.search(clean_verse_text) or \
                        search_regx.search(clean_verse_text.lower()):
                    found_verses.append(verse_ref)

            key_text = self._module.getKeyText()
            self._module.increment()

        self._library.setGlobalOption("Strong's Numbers", "Off")
        self._library.setGlobalOption("Morphological Tags", "Off")

        found_verses = list(set(found_verses))
        return found_verses

    def _generic_search(self, search_str, index_dict, phrase, search_any, 
                        strongs=False, morph=False):
        """ A generic search function used for words, phrases, strongs, and
        morphology.

        """

        sorted_search_list = sorted(set(search_str.split()), 
                key=lambda i: len(index_dict[i]))
        common_num = len(index_dict.keys()) // 2

        if not phrase:
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

            print("Done.\nFound %s verses." % len(found_verses))

            return list(found_verses)
        else:
            search_regx = re.compile(r'\b%s\b' % search_str, re.I)
            found_verses = set()
            stdout.flush()
            #verse_set = self._set_intersect(sorted_search_list, index_dict)
            least_common_index = sorted_search_list[0]
            print('Searching for "%s"...' % search_str, end='')
            stdout.flush()
            for verse_ref in index_dict.get(least_common_index, []):
            #for verse_ref in verse_set:
                if self._phrase_search(verse_ref, search_regx, strongs=strongs, 
                                       morph=morph):
                    found_verses.add(verse_ref)

            print("Done.\nFound %s verses." % len(found_verses))

            return list(found_verses)

    def _word_search(self, search_list, phrase=False, search_any=False):
        """ _word_search(search_list, phrase=False, search_any=False) -> For the
        list of search terms.
                phrase       -   Find only the phrase phrase.
                search_any  -   Find any verse with the common words in the
                                search list

        """

        temp_str = self._non_alnum_regx.sub(' ', ' '.join(search_list))
        search_str = self._fix_regx.sub(' ', temp_str)

        print("Loading word dictionary...")
        with open('word.dump', 'r') as word_file:
            word_dict = json.loads(word_file.read())

        #print("Loading word count dictionary...")
        #with open('word_count.dump', 'r') as word_count_file:
            #word_count_dict = json.loads(word_count_file.read())

        return self._generic_search(search_str.lower(), word_dict, phrase,
                                    search_any)

        common_num = word_count_dict['verse_count'] / 2

        sorted_word_list = sorted(set(search_str.lower().split()), 
                                  key=word_count_dict.get)

        search_regx = re.compile(r'\b%s\b' % search_str, re.I)

        if not phrase:
            if not search_any:
                print('Searching for "%s"...' % \
                        ' AND '.join(search_str.split()), end='')
                found_verses = self._set_intersect(sorted_word_list, word_dict)
            else:
                print('Searching for "%s"...' % \
                        ' OR '.join(search_str.split()), end='')
                found_verses = self._set_union(sorted_word_list, word_dict)

            print("Done.\nFound %s verses." % len(found_verses))

            return list(found_verses)
        else:
            found_verses = set()
            stdout.flush()
            #verse_set = self._set_intersect(sorted_word_list, word_dict)
            least_common_word = sorted_word_list[0]
            print('Searching for "%s"...' % search_str, end='')
            stdout.flush()
            for verse_ref in word_dict.get(least_common_word, []):
            #for verse_ref in verse_set:
                if self._phrase_search(verse_ref, search_regx):
                    found_verses.add(verse_ref)

            print("Done.\nFound %s verses." % len(found_verses))

            return list(found_verses)

    def _strongs_morph_search(self, search_list, phrase=False, search_any=False,
                              strongs=True, morph=False):
        """ _strongs_morph_search(search_list, phrase=False, search_any=False,
        strongs=True) -> For the list of
        search terms.
                phrase       -   Find only the phrase phrase.
                search_any  -   Find any verse with the common words in the
                                search list
                strongs     -   If True it will search for strongs numbers
                                otherwise it will search for morphological tags.

        """

        search_str = ' '.join(search_list).upper()
        search_regx = re.compile(r'\b%s\b' % search_str, re.I)

        if strongs:
            self._library.setGlobalOption("Strong's Numbers", "On")
        else:
            self._library.setGlobalOption("Morphological Tags", "On")

        filename = 'strongs.dump'
        if not strongs:
            filename = 'morph.dump'

        print("Loading %s" % filename)
        with open(filename, 'r') as index_file:
            index_dict = json.loads(index_file.read())

        return self._generic_search(search_str.upper(), index_dict, phrase,
                                    search_any, strongs, morph)

        sorted_search_list = sorted(set(search_str.upper().split()), 
                key=lambda i: len(index_dict[i]))

        if not phrase:
            if not search_any:
                print('Searching for "%s"...' % \
                        ' AND '.join(search_list), end='')
                found_verses = self._set_intersect(sorted_search_list, 
                                                   index_dict)
            else:
                print('Searching for "%s"...' % \
                        ' OR '.join(search_list), end='')
                found_verses = self._set_union(sorted_search_list, index_dict)

            print("Done.\nFound %s verses." % len(found_verses))

            return list(found_verses)
        else:
            found_verses = set()
            stdout.flush()
            #verse_set = self._set_intersect(sorted_search_list, index_dict)
            least_common_index = sorted_search_list[0]
            print('Searching for "%s"...' % search_str, end='')
            stdout.flush()
            for verse_ref in index_dict.get(least_common_index, []):
            #for verse_ref in verse_set:
                if self._phrase_search(verse_ref, search_regx, strongs=strongs, 
                                       morph=not strongs):
                    found_verses.add(verse_ref)

            print("Done.\nFound %s verses." % len(found_verses))

            return list(found_verses)


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
                        help='Search phrase phrase.', dest='phrase')
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

    options, args = parser.parse_args()
    if args or options.build_index:
        search = BibleSearch()
        if options.build_index and not args:
            search.build_index()
            exit(0)
        options_dict = options.__dict__
        if options_dict.pop('show_numbers'):
            search.show_strongs = True
        if options_dict.pop('show_tags'):
            search.show_morphological = True
        list_only = options_dict.pop('list_only')
        lookup = options_dict.pop('lookup')
        if not lookup:
            verse_list = search.Search(args, **options_dict)
        else:
            verse_list = search.lookup(args)
        if options.strongs:
            search.show_strongs = True
        elif options.morph:
            search.show_morphological = True

        if list_only:
            for i in sorted(verse_list, key=search._sort_by_book):
                print(i)
        else:
            search.print_verse_list(verse_list, highlight=not lookup)
        print("Found %d verses." % len(verse_list))
    else:
        parser.print_help()
