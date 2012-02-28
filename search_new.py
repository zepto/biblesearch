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

from sys import argv, exit
import sys
from os import getcwd, getenv
from functools import wraps, partial
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
from xml.dom.minidom import parseString
import dbm
import os
import json
import re
import locale

import Sword

VERBOSE_LEVEL = 1
COLOR_LEVEL = 3
INDEX_PATH = getcwd()

# Highlight colors.
highlight_color = '\033[7m'
highlight_text = '%s\\1\033[m' % highlight_color
word_regx = re.compile(r'\b([\w-]+)\b')
# Strip previous color.
strip_color_regx = re.compile('\033\[[\d;]*m')

def info_print(data, end='\n', tag=0):
    """ Print the data to stderr as info.

    """

    if tag <= VERBOSE_LEVEL:
        print(data, end=end, file=sys.stderr)
        sys.stderr.flush()

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
    except Exception as err:
        print('Error sorting "%s": %s' % (ref, err), file=sys.stderr)
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

def render_raw2(verse_text, strongs=False, morph=False):
    """ Render raw verse text.

    """

    strong_regx = re.compile(r'strong:([GH]\d+)', re.I)
    morph_regx = re.compile(r'(?:Morph|robinson):([\w-]*)', re.I)
    test_regx = re.compile(r'([^<]*)<(?P<tag>seg|q|w|transChange|note)([^>]*)>([\w\W]*?)</(?P=tag)>([^<]*)', re.I)
    divname_regx = re.compile(r'<(?:divineName)>([^<]*?)([\'s]*)</(?:divineName)>', re.I)
    div_upper = lambda m: m.group(1).upper() + m.group(2)
    marker_regx = re.compile(r'.*marker="(.)".*', re.I)
    info_print(verse_text, tag=4)

    def recurse_tag(text):
        """ Recursively parse raw verse text using regular expressions, and
        returns the correctly formatted text.

        """

        v_text = ''
        for match in test_regx.finditer(text):
            opt, tag_name, tag_attr, tag_text, punct = match.groups()
            strongs_str = ''
            morph_str = ''
            italic_str = '<i>%s</i>' if 'added' in tag_attr.lower() else '%s'
            if 'note' in tag_name.lower() or 'study' in tag_attr.lower():
                note_str = ' <n>%s</n>' 
            else:
                note_str = '%s'
            if strongs and strong_regx.search(tag_attr):
                strongs_list = strong_regx.findall(tag_attr)
                strongs_str = ' <%s>' % '> <'.join(strongs_list)
            if  morph and morph_regx.search(tag_attr):
                morph_list = morph_regx.findall(tag_attr)
                morph_str = ' {%s}' % '} {'.join(morph_list)

            if match.re.search(tag_text):
                temp_text = recurse_tag(tag_text) + strongs_str + morph_str
                v_text += note_str % italic_str % (temp_text)
            else:
                info_print((opt, tag_name, tag_attr, tag_text, punct), tag=4)
                opt = marker_regx.sub('<p>\\1</p> ', opt)
                tag_text = divname_regx.sub(div_upper, tag_text)
                tag_text = note_str % italic_str % tag_text
                v_text += opt + tag_text + strongs_str + morph_str
            v_text += punct

        return v_text

    return recurse_tag(verse_text)

def render_raw(verse_text, strongs=False, morph=False):
    """ Render raw verse text.

    """

    strong_regx = re.compile(r'strong:([GH]\d+)', re.I)
    morph_regx = re.compile(r'(?:Morph|robinson):([\w-]*)', re.I)
    test_regx = re.compile(r'([^<]*)<(?P<tag>q|w|transChange|note)([^>]*)>([\w\W]*?)</(?P=tag)>([^<]*)', re.I)
    divname_regx = re.compile(r'(?:<seg>)?<(?:divineName)>+([^<]*?)([\'s]*)</(?:divineName)>(?:</seg>)?', re.I)
    xadded_regx = re.compile(r'<seg subType="x-added"[^>]*>([^<]*)</seg>', re.I)
    div_upper = lambda m: m.group(1).upper() + m.group(2)
    marker_regx = re.compile(r'.*marker="(.)".*', re.I)
    v_text = ''
    info_print(verse_text, tag=4)

    for match in test_regx.finditer(verse_text):
        opt, tag_name, tag_attr, tag_text, punct = match.groups()
        italic_str = '%s'
        if match.re.search(tag_text):
            if 'added' in tag_attr.lower():
                italic_str = '<i>%s</i>' + punct
                punct = ''
            match_list = match.re.findall(tag_text + punct)
        else:
            match_list = [match.groups()]
        temp_text = ''
        for opt, tag_name, tag_attr, tag_text, punct in match_list:
            info_print((opt, tag_name, tag_attr, tag_text, punct), tag=4)
            tag_text = divname_regx.sub(div_upper, tag_text)
            tag_text = xadded_regx.sub('<i>\\1</i>', tag_text)
            if 'marker' in opt.lower():
                temp_text += '<p>%s</p> ' % marker_regx.sub('\\1', opt)
                opt = ''
            if 'note' in tag_name.lower() or 'study' in tag_attr.lower():
                temp_text += ' <n>%s</n>' % tag_text
                tag_text = ''
            temp_italic = '<i>%s</i>' if 'added' in tag_attr.lower() else '%s'
            temp_text += temp_italic % (opt + tag_text)
            if tag_name.strip().lower() in ['transchange', 'w', 'seg']:
                if strong_regx.search(tag_attr) and strongs:
                    temp_text += ' <%s>' % '> <'.join(strong_regx.findall(tag_attr))
                if morph_regx.search(tag_attr) and morph:
                    temp_text += ' {%s}' % '} {'.join(morph_regx.findall(tag_attr))
            temp_text += punct

        v_text += italic_str % temp_text

        continue
        opt, tag_name, tag_attr, tag_text, punct = match.groups()
        tag_text = divname_regx.sub(lambda m: m.group(1).upper() + m.group(2), tag_text)
        if 'marker' in opt.lower():
            v_text += '<p>%s</p> ' % marker_regx.sub('\\1', opt)
        if 'added' in tag_attr.lower():
            v_text += '<i>'
        elif 'note' in tag_name.lower() or 'study' in tag_attr.lower():
            v_text += ' <n>%s</n>' % tag_text
        if match.re.search(tag_text):
            for i in match.re.finditer(tag_text):
                info_print(i.groups(), tag=4)
                o, t_n, t_a, t_t, p = i.groups()
                if t_n.strip().lower() in ['transchange', 'w']:
                    v_text += o + t_t
                    if strong_regx.search(t_a) and strongs:
                        v_text += ' <%s>' % '> <'.join(strong_regx.findall(t_a))
                    if morph_regx.search(t_a) and morph:
                        v_text += ' {%s}' % '} {'.join(morph_regx.findall(t_a))
                v_text += p
        else:
            if tag_name.strip().lower() in ['transchange', 'w']:
                v_text += tag_text
                if strong_regx.search(tag_attr) and strongs:
                    v_text += ' <%s>' % '> <'.join(strong_regx.findall(tag_attr))
                if morph_regx.search(tag_attr) and morph:
                    v_text += ' {%s}' % '} {'.join(morph_regx.findall(tag_attr))
        if 'added' in tag_attr.lower():
            v_text += '</i>'
        v_text += punct
        info_print('%s: %s: %s: %s: %s' % (opt, tag_name, tag_attr, tag_text, punct), tag=4)
    return v_text

def render_verses_with_italics(ref_list, wrap=True, strongs=False, 
                               morph=False, added=True, notes=False,
                               highlight_func=None, *args):
    """ Renders a the verse text at verse_ref with italics highlighted.  
    Returns a strong "verse_ref: verse_text"
        wrap            -   Whether to wrap the text.
        strongs         -   Include Strong's Numbers in the output.
        morph           -   Include Morphological Tags in the output.
        added           -   Include added text (i.e. italics) in the output.
        notes           -   Include study notes at the end of the text.
        highlight_func  -   A function to highlight anything else 
                            (i.e. search terms.)
        *args           -   Any additional arguments to pass to 
                            hightlight_func

        highlight_func should take at least three arguments, strongs, morph,
        and the verse_text.

    """

    # Set the colors of different items.
    end_color = '\033[m'

    # Build replacement strings that highlight Strong's Numbers and 
    # Morphological Tags.
    if COLOR_LEVEL >= 2:
        # The Strong's and Morphology matching regular expressions.
        # Match strongs numbers.
        strongs_regx = re.compile(r'<((?:\033\[[\d;]*m)*?[GH]?\d+?(?:\033\[[\d;]*m)*?)>', re.I)
        # It needs to match with braces or it will catch all capitalized
        # word and words with '-'s in them.
        morph_regx = re.compile(r'\{((?:\033\[[\d+;]*m)*?[\w-]*?(?:\033\[[\d+;]*m)*?)\}')
        strongs_color = '\033[36m'
        morph_color = '\033[35m'
        strongs_highlight = '<%s\\1%s>' % (strongs_color, end_color)
        morph_highlight = '{%s\\1%s}' % (morph_color, end_color)

    if COLOR_LEVEL >= 0:
        ref_color = '\033[32m'
        ref_highlight = '%s\\1%s' % (ref_color, end_color)

    if COLOR_LEVEL >= 1 and added:
        italic_color = '\033[4m'
        italic_regx = re.compile(r'<i>\s?(.*?)\s?</i>', re.S)
        italic_highlight = '%s\\1%s' % (italic_color, end_color)

    # Get the local text encoding.
    encoding = get_encoding()

    # A substitution replacement function for highlighting italics.
    def italic_color(match):
        """ Color italic text, but first remove any previous color.

        """
        
        # Strip any previous colors.
        match_text = strip_color_regx.sub('', match.groups()[0])
        # Color the italics.
        return word_regx.sub(italic_highlight, match_text)

    # Get an iterator over all the requested verses.
    verse_iter = IndexedVerseTextIter(iter(ref_list), strongs, morph,
                                      italic_markers=(COLOR_LEVEL >= 1),
                                      added=added, paragraph=added,
                                      notes=notes)
    if VERBOSE_LEVEL == 20:
        verse_iter = VerseTextIter(iter(ref_list), strongs, morph,
                                   markup=Sword.FMT_PLAIN, render='render_raw')
    if VERBOSE_LEVEL >= 30:
        verse_iter = RawDict(iter(ref_list))
    for verse_ref, verse_text in verse_iter:
        if VERBOSE_LEVEL >= 30:
            len_longest_key = len(max(verse_text[1].keys(), key=len))
            for key, value in verse_text[1].items():
                print('\033[33m{0:{1}}\033[m: {2}'.format(key, len_longest_key, value))
            verse_text = verse_text[1]['_verse_text'][0]
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

        if COLOR_LEVEL >= 0:
            # Color the verse reference.
            colored_ref = word_regx.sub(ref_highlight, verse_ref)
            verse_text = re.sub(verse_ref, colored_ref, verse_text)

        if COLOR_LEVEL >= 1 and added:
            # Highlight the italic text we previously pulled out.
            verse_text = italic_regx.sub(italic_color, verse_text)

        if COLOR_LEVEL >= 2:
            # Highlight Strong's and Morphology if they are visible.
            if strongs:
                verse_text = strongs_regx.sub(strongs_highlight, verse_text)
            if morph:
                verse_text = morph_regx.sub(morph_highlight, verse_text)

        if COLOR_LEVEL >= 3:
            # Highlight the different elements.
            if highlight_func:
                verse_text = highlight_func(verse_text, strongs, morph, *args)

        # Finally produce the formated text.
        yield verse_text

def highlight_search_terms(verse_text, strongs, morph, regx_list, flags):
    """ Highlight search terms in the verse text.

    """

    def highlight_group(match):
        """ Highlight each word/Strong's Number/Morphological Tag in the
        match.

        """

        match_text = match.group()
        for word in match.groups():
            if word:
                info_print(word, tag=20)
                match_text = re.sub('((?:\033\[[\d+;]*m|\\b)+%s(?:\033\[[\d+;]*m|\\b)+)' % re.escape(word), highlight_text, match_text)
            #match_text = match_text.replace(word, '\033[7m%s\033[m' % word) 
        #print(match_text)
        return match_text

        # Strip any previous colors.
        match_text = strip_color_regx.sub('', match.group())
        return word_regx.sub(highlight_text, match_text)

    verse_text = verse_text.strip()
    # Apply each highlighting regular expression to the text.
    for regx in regx_list:
        verse_text = regx.sub(highlight_group, verse_text)

    return verse_text

def build_highlight_regx(search_list, case_sensitive, sloppy=False):
    """ Build a regular expression and highlight string to colorize the
    items in search_list as they appear in a verse.

    """

    if not search_list:
        return []

    regx_list = []
    # Extra word boundry to catch ansi color escape sequences.
    word_bound='(?:\033\[[\d;]*m|\\\\b)+'
    # Extra space filler to pass over ansi color escape sequences.
    extra_space='|\033\[[\d;]*m|\033'
    for item in search_list:
        item = item.strip()
        is_regex=(('*' in item and ' ' not in item) or item.startswith('&'))
        if ('*' in item and ' ' not in item) and  not item.startswith('&'):
            # Build a little regular expression to highlight partial words.
            item = item[1:] if item[0] in '!^+|' else item
            item = item.replace('*', '\w*')
            item = r'{0}({1}){0}'.format('(?:\033\[[\d;]*m|\\b)+', item)
        if item.startswith('&'):
            # Just use a regular expression. ('&' marks the term as a regular
            # expression.)
            item = item[1:]

        regx_list.append(Search.search_terms_to_regex(item, case_sensitive,
                word_bound=word_bound, extra_space=extra_space,
                sloppy=(sloppy or '~' in item), is_regex=is_regex))

    return regx_list

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


class StdoutRedirect(object):
    """ Redirect stdout to a specified output function.

    """

    def __init__(self, output_func, *args):
        """ Set the output function and get the extra arguments to pass to it.

        """

        self._output_func = output_func
        self._args = args
        self._old_stdout = sys.stdout

    def write(self, data):
        """ Write data to the output function.

        """

        if data.strip():
            self._output_func(data, *self._args)

    def __enter__(self):
        """ Change sys.stdout to this class.

        """

        try:
            sys.stdout = self
            return self
        except Exception as err:
            print("Error in __enter__: %s" % err, file=sys.stderr)
            return None

    def __exit__(self, exc_type, exc_value, traceback):
        """ Change sys.stdout back to its old value.

        """

        try:
            sys.stdout = self._old_stdout
            if exc_type:
                return False
            return True
        except Exception as err:
            print("Error in __exit__: %s" % err, file=sys.stderr)
            return False


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
        self._italic_regx = re.compile(r'(?:<i>|<hi\s*type="italic">)([\w\s]+)(?:</i>|</hi>)', re.I)
        self._br_regx = re.compile(r'(<br[\s]*/>|<lb/>)[\s]?', re.I)
        self._cleanup_regx = re.compile(r'<[^>]*>')
        self._brace_regx = re.compile(r'\{([\W]*)([\w]*)([\W]*)\}')
        self._parenthesis_regx = re.compile(r'\(([\W]*)([\w]*)([\W]*)\)')
        self._bracket_regx = re.compile(r'\[([\W]*)([\w ]*)([\W]*)\]')
        self._verse_ref_regx = re.compile(r'<scripRef[^>]*>([^<]*)</scripRef>', re.I)

    def get_text(self, key):
        """ Get the text at the given key in the module.
        i.e. get_text('3778') returns the greek strongs.

        """

        encoding = get_encoding()
        self._module.setKey(Sword.SWKey(key))
        item_text = self._module.RenderText()
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
            self._render_func = lambda: self._parse_raw(self._module.getRawEntry(), strongs, morph)
        else:
            self._render_func = self._module.RenderText

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
        if self._render_func == self._module.RenderText:
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
                verse_text = '<p>%s</p>' % attr_dict['marker']
            else:
                verse_text = ''
            italic_str = '%s'
            note_str = '%s'
            for key, value in attr_dict.items():
                # Italicize any added text.
                if 'added' in value.lower():
                    italic_str = '<i>%s</i>'
                # Label study notes.
                elif 'study' in value.lower() or 'note' in name.lower():
                    note_str = '<n>%s</n>'
                # Check for strongs.
                elif 'lemma' in key.lower() and strongs:
                    for num in value.split():
                        strongs_str += ' <%s> ' % num.split(':')[1]
                # Check for morphology.
                elif 'morph' in key.lower() and morph:
                    for tag in value.split():
                        morph_str += ' {%s} ' % tag.split(':')[1]
        # Recursively build the text from all the child nodes.
        for node in xml_dom.childNodes:
            child_s = self._parse_xml(node, strongs, morph)
            if 'divine' in name.lower():
                verse_text += ' %s' % self._upper_divname_regx.sub(lambda m: m.group(1).upper() + m.group(2), child_s)
            else:
                verse_text += ' %s' % child_s

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
        </root>''' % ('verse', raw_text)

        # It works now we can parse the xml dom.
        parsed_xml = parseString(xml_text)
        parsed_str = self._parse_xml(parsed_xml, strongs, morph)
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
                if _type.lower() == 'x-p' or 'marker' in attr_dict :
                    # Get any paragraph marker.
                    verse_dict['_x-p'].append(attr_dict['marker'].strip())
                elif 'study' in _type.lower() or 'note' in name.lower():
                    verse_dict['_notes'].append(verse_text.strip())
                if 'added' in _type.lower() or 'added' in _sub_type.lower():
                    if 'marker' not in attr_dict:
                        # Italicize any added text.
                        italic_str = '<i>%s</i>'
                        verse_dict['_added'].append(verse_text.strip())
                elif 'section' in _type.lower() or 'preverse' in _sub_type.lower():
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
        parsed_xml = parseString(xml_text)
        return self._raw_to_dict(parsed_xml, strongs, morph)


class IndexedVerseTextIter(object):
    """ An iterable object for accessing verses in the Bible.  Maybe it will
    be easier maybe not.

    """

    def __init__(self, reference_iter, strongs=False, morph=False, 
                 module='KJV', italic_markers=False, added=True, 
                 paragraph=True, notes=False, path=''):
        """ Initialize.

        """

        reg_list = []
        if not strongs:
            reg_list.append(r'\s*<([GH]\d+)>')
        if not morph:
            reg_list.append(r'\s*\{([\w-]+)\}')
        if not added:
            reg_list.append(r'\s?<i>\s?(.*?)\s?</i>')
        if not italic_markers:
            reg_list.append(r'(<i>\s?|\s?</i>)')
        if not paragraph:
            reg_list.append(r'\s?<p>\s?(.*?)\s?</p>')
        else:
            reg_list.append(r'(<p>\s?|\s?</p>)')
        reg_str = r'(?:%s)' % r'|'.join(reg_list)
        self._clean_regex = re.compile(reg_str, re.S)

        self._notes_regex = re.compile(r'\s?<n>\s?(.*?)\s?</n>', re.S)
        self._notes_str = ' (Notes: \\1)' if notes else ''

        self._index_dict = IndexDict('%s' % module, path)

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

        return (verse_ref, verse_text.strip())

    def __iter__(self):
        """ Returns an iterator of self.

        """

        return self

    def _get_text(self, verse_ref):
        """ Returns the verse text.  Override this to produce formatted verse
        text.

        """

        verse_text = self._index_dict[verse_ref]
        verse_text = self._clean_regex.sub('', verse_text)
        verse_text = self._notes_regex.sub(self._notes_str, verse_text)

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

    def firstkey(self):
        """ Return the first key.

        """

        key = self._dbm.firstkey()
        if key:
            key = key.decode(self._encoding(), 'replace')
        return key

    def nextkey(self, key):
        """ Returns the next key from key.

        """

        key = key.encode(self._encoding(), 'replace')
        return_key = self._dbm.nextkey(key)
        if return_key:
            return_key = return_key.decode(self._encoding(), 'replace')
        return return_key

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
            #print("Error reading %s: %s" % (key, err), file=sys.stderr)
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
            print("Error in __enter__: %s" % err, file=sys.stderr)
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
            print("Error in __exit__: %s" % err, file=sys.stderr)
            return False


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
        self._strongs_regx = re.compile(r'<([GH]\d+)>', re.I)
        self._morph_regx = re.compile(r'\{([\w-]+)\}', re.I)

        self._module_dict = defaultdict(list)
        # lower_case is used to store lower_case words case sensitive
        # counterpart.  _Words_ is for easy key lookup for partial words.
        self._words_set = set()
        self._module_dict.update({ 'lower_case': defaultdict(list) })

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
        for book in self._book_gen():
            self._index_book(book)
        self._module_dict['_words_'].extend(self._words_set)

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
            with IndexDbm('%s/%s.dbm' % (self._path, name), 'nf') as index_file:
                #with open(name, 'r') as i_file:
                    #dic =json.load(i_file)
                index_file.update(dic)


class IndexDict(dict):
    """ A Bible index container, that provides on-demand loading of indexed
    items.

    """

    def __init__(self, name='', path=''):
        """ Initialize the index.

        """

        self._non_key_text_regx = re.compile(r'[<>\{\}]')

        self._name = name
        self._path = path if path else INDEX_PATH
        self._lower_case = self.get('lower_case', {})

        super(IndexDict, self).__init__()

    # In case we need to access the name externally we don't want it changed.
    name = property(lambda self: self._name)

    def __getitem__(self, key):
        """ If a filename was given then use it to retrieve keys when
        they are needed.

        """

        # Cleanup Strong's and Morphology
        key = self._non_key_text_regx.sub('', key).strip()
        if self._name and (key not in self):
            # Load the value from the database if we don't have it.
            with IndexDbm('%s/%s_index_i.dbm' % (self._path, self._name), 'r') as dbm_dict:
                self[key] = dbm_dict.get(key)

        return super(IndexDict, self).__getitem__(key)

    def get(self, key, default=[]):
        """ Returns the value associated with key, or default.

        """

        value = self[key]
        return value if value else default

    def keys(self):
        """ Yields each key.

        """

        with IndexDbm('%s/%s_index_i.dbm' % (self._path, self._name), 'r') as dbm_dict:
            key = dbm_dict.firstkey()
            while key:
                yield key
                key = dbm_dict.nextkey(key)

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

    def from_partial(self, partial_list, case_sensitive=False, 
                     common_limit=31103):
        """ Returns a set of verses that have any the partial words in the
        list.

        """

        flags = re.I if not case_sensitive else 0
        verse_set = set()

        # Search through each word key in the index for any word that contains
        # the partial word.
        for word in self['_words_']:
            for partial_word in partial_list:
                # A Regular expression that matches any number of word
                # characters for every '*' in the term.
                reg_str = '\\b%s\\b' % partial_word.replace('*', '\w*')
                word_regx = re.compile(reg_str, flags)
                if word_regx.match(word):
                    temp_list = self[word]
                    if len(temp_list) < common_limit:
                        verse_set.update(temp_list)

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
                # Process from here to the closing parenthesis.
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

        #info_print(return_list)
        # Return the list.
        return return_list


class Search(object):
    """ Provides a simple way of searching an IndexDict for verses.

    """

    # To check for spaces.
    _whitespace_regx = re.compile(r'\s')

    # Cleanup regular expressions.
    _non_alnum_regx = re.compile(r'[^\w\*<>\{\}\(\)-]')
    _fix_regx = re.compile(r'\s+')

    # Match strongs numbers.
    _strongs_regx = re.compile(r'[<]?(\b[GH]\d+\b)[>]?', re.I)
    # It needs to match with braces or it will catch all capitalized
    # word and words with '-'s in them.
    _morph_regx = re.compile(r'[\(\{](\b[\w-]+\b)[\}\)]', re.I)
    _word_regx = re.compile(r'\b([\w\\-]+)\b')
    _space_regx = re.compile(r'\s+')
    _non_word_regx = re.compile(r'[<>\(\)]')

    _fix_strongs = classmethod(lambda c, m: '<%s>' % m.groups()[0].upper())
    _fix_morph = classmethod(lambda c, m: '{%s}' % m.groups()[0].upper())

    # Escape the morphological tags.
    _escape_morph = classmethod(lambda c, m: '\{%s\}' % re.escape(m.groups()[0]).upper())

    def __init__(self, module='KJV', path='', multiword=False):
        """ Initialize the search.

        """

        # The index dictionary.
        self._index_dict = IndexDict(module, path)

        self._module_name = module
        self._multi = multiword

    @classmethod
    def search_terms_to_regex(cls, search_terms, case_sensitive, 
                              word_bound='\\\\b', extra_space='', 
                              sloppy=False, is_regex=False):
        """ Build a regular expression from the search_terms to match a verse
        in the Bible.

        """

        # Set the flags for the regular expression.
        flags = re.I if not case_sensitive else 0

        if is_regex:
            reg_str = search_terms
            info_print('\nUsing regular expression: %s\n' % reg_str, tag=2)

            return re.compile(reg_str, flags)

        # This will skip words.
        not_words_str = r'\b\w+\b'
        # This will skip Strong's Numbers.
        not_strongs_str = r'<[^>]*>'
        # This wil skip Morphological Tags.
        not_morph_str = r'\{[^\}]*\}'
        # This will skip all punctuation.  Skipping ()'s is a problem for
        # searching Morphological Tags, but it is necessary for the
        # parenthesized words.  May break highlighting.
        not_punct_str = r'[\s,\?\!\.;:\\/_\(\)\[\]"\'-]'
        # This will skip ansi color.
        not_color_str = r'\033\[[\d;]*m'
        # Match all *'s
        star_regx = re.compile(r'\*')

        # Hold the string that fills space between search terms.
        space_str = ''

        # Get stars past so we can replace them with '\w*' later.
        temp_str, word_count = star_regx.subn(r'_star_', search_terms)

        # Hack to get rid of unwanted characters.
        temp_str = cls._non_alnum_regx.sub(' ', temp_str).split()
        temp_str = ' '.join(temp_str)
        # Phrases will have spaces in them
        phrase = bool(cls._whitespace_regx.search(temp_str))
        # Escape the morphological tags, and also find how many there are.
        temp_str, morph_count = cls._morph_regx.subn(cls._escape_morph, 
                                                         temp_str)
        # Make all Strong's Numbers uppercase, also find how many there are.
        temp_str, strongs_count = cls._strongs_regx.subn(cls._fix_strongs, 
                                                         temp_str)
        # Select all words.
        #repl = '(\\\\b\\1\\\\b)'
        # This works = temp_str, word_count = cls._word_regx.subn('{0}(\\1){0}'.format(word_bound), temp_str)
        repl = '({0}(\\1){0})'.format(word_bound)
        temp_str, word_count = cls._word_regx.subn(repl, temp_str)
        # Replace what used to be *'s with '\w*'.
        temp_str = temp_str.replace('_star_', '\w*')

        # All the Strong's and Morphology were changed in the previous
        # substitution, so if that number is greater than the number of
        # Strong's plus Morphology then there were words in the search terms.
        # I do this because I don't know how to only find words.
        words_found = (strongs_count + morph_count) < word_count
        if phrase:
            # Build the string that is inserted between the items in the 
            # search string.
            space_str = r'(?:%s%s' % (not_punct_str, extra_space)
            if not bool(strongs_count) or sloppy:
                # Skip over all Strong's Numbers.
                space_str = r'%s|%s' % (space_str, not_strongs_str)
            if not bool(morph_count) or sloppy:
                # Skip all Morphological Tags.
                space_str = r'%s|%s' % (space_str, not_morph_str)
            if not words_found or bool(morph_count) or bool(strongs_count) or \
                    sloppy:
                # Skip words.  If word attributes are in the search we can
                # skip over words and still keep it a phrase.
                space_str = r'%s|%s' % (space_str, not_words_str)
            # Finally make it not greedy.
            space_str = r'%s)*?' % space_str
        else:
            space_str = ''
        # Re-combine the search terms with the regular expression string
        # between each element.
        reg_str = space_str.join(temp_str.split())
        info_print('\nUsing regular expression: %s\n' % reg_str, tag=2)

        return re.compile(reg_str, flags)

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

    def _fix_strongs_morph(self, search_terms):
        """ Make any Strong's or Morphology uppercase, put parenthesis around
        the Morphological Tags, and put <>'s around the Strong's Numbers.

        """

        # Capitalize all strongs numbers and remove the <> from them.
        temp_str = self._strongs_regx.sub(self._fix_strongs, search_terms)
        # Capitalize all morphological tags and make sure they are in
        # parenthesis.
        temp_str = self._morph_regx.sub(self._fix_morph, temp_str)

        return temp_str

    def _process_search(func):
        """ Returns a wrapper function that processes the search terms, calls
        the wrapped function, and, if applicable, confines the resulting verse
        set to a range.

        """

        @wraps(func)
        def wrapper(self, search_terms, strongs=False, morph=False,
                    added=True, case_sensitive=False, range_str=''):
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

            if func.__name__ not in ['regex_search', 'partial_word_search']:
                # Try to catch and fix any Strong's Numbers or Morphological
                # Tags.
                search_terms = self._fix_strongs_morph(search_terms)

            # Regular expression and combined searches get the search terms as
            # they were passed.
            if func.__name__ in ['multiword_search', 'anyword_search',
                                 'phrase_search', 'mixed_phrase_search']: 
                # Get rid of any non-alphanumeric or '-' characters from
                # the search string.
                search_str = self._clean_text(search_terms).strip()
                if strongs or morph:
                    # Strong's numbers and Morphological tags are all
                    # uppercase.  This is only required if the Morphological
                    # Tags were not surrounded by parenthesis.
                    search_str = search_str.upper().strip()
            else:
                search_str = search_terms

            # Get the set of found verses.
            found_set = func(self, search_str, strongs, morph, added,
                             case_sensitive, range_set)

            # The phrase, regular expression, and combined searches apply the
            # range before searching, so only multi-word and any-word searches
            # have it applied here.
            if func.__name__ in ['multiword_search', 'anyword_search', 
                                 'partial_word_search']:
                if range_set:
                    found_set.intersection_update(range_set)
            return found_set

        # Return wrapper function.
        return wrapper

    @_process_search
    def combined_search(self, search_terms, strongs=False, morph=False,
                        added=True, case_sensitive=False, range_str=''):
        """ combined_search(self, search_terms, strongs=False, morph=False,
                        case_sensitive=False, range_str=''): ->
        Perform a combined search.  Search terms could be
        'created NOT (and OR but)' and it would find all verses with the word
        'created' in them and remove any verse that had either 'and' or 'but.'

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for '%s'..." % search_terms, tag=1)

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
                               added=True, case_sensitive=False, range_str=''):
        """ combined_phrase_search(self, search_terms, strongs=False,
                morph=False, case_sensitive=False, range_str=''): ->
        Perform a combined phrase search.  Search terms could be
        'created NOT (and AND but)' and it would find all verses with the word
        'created' in them and remove any verse that had the phrase 'and but.'

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for '%s'..." % search_terms, tag=1)

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
    def multiword_search(self, search_terms, strongs=False, morph=False,
                         added=True, case_sensitive=False, range_str=''):
        """ multiword_search(self, search_terms, strongs=False, morph=False,
                  case_sensitive=False, range_str='') -> 
        Perform a multiword search using the search_terms.

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for verses with all these words '%s'..." % ', '.join(search_terms.split()), tag=1)

        # All that needs to be done is find all references with all the
        # searched words in them.
        found_set = self._index_dict.value_intersect(search_terms.split(), 
                                                     case_sensitive)

        return found_set

    @_process_search
    def eitheror_search(self, search_terms, strongs=False, morph=False,
                        added=True, case_sensitive=False, range_str=''):
        """ eitheror_search(self, search_terms, strongs=False, morph=False,
                case_sensitive=False, range_str='') -> 
        Perform a search returning any verse with one and only one of the terms
        searched for.

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for verses with one and not all of these words '%s'..." % ', '.join(search_terms.split()), tag=1)

        # Any verse with one and only one of the searched words.
        found_set = self._index_dict.value_sym_diff(search_terms.split(), 
                                                    case_sensitive)

        return found_set

    @_process_search
    def anyword_search(self, search_terms, strongs=False, morph=False,
                       added=True, case_sensitive=False, range_str=''):
        """ anyword_search(self, search_terms, strongs=False, morph=False,
                case_sensitive=False, range_str='') -> 
        Perform a search returning any verse with one or more of the search
        terms.

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for verses with any of these words '%s'..." % ', '.join(search_terms.split()), tag=1)

        # Any verse with one or more of the searched words.
        found_set = self._index_dict.value_union(search_terms.split(), 
                                                 case_sensitive)

        return found_set

    @_process_search
    def partial_word_search(self, search_terms, strongs=False, morph=False,
                           added=True, case_sensitive=False, range_str=''):
        """ partial_word_search(self, search_terms, strongs=False, morph=False,
                case_sensitive=False, range_str='') -> 
        Perform a search returning any verse with one or more words matching
        the partial words given in the search terms.  Partial words are markes
        tih *'s (e.g. '*guil*' will match any word with 'guil' in it such as
        'guilt' or 'beguile.'

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for verses with any of these partial words '%s'..." % ', '.join(search_terms.split()), tag=1)

        #found_set = self._index_dict.value_union(
                #self._words_from_partial(search_terms, case_sensitive), 
                #case_sensitive)
        search_list = search_terms.split()
        found_set = self._index_dict.from_partial(search_list, case_sensitive)

        return found_set

    def _words_from_partial(self, partial_word_list, case_sensitive=False):
        """ Search through a list of partial words and yield words that match.

        """

        flags = re.I if not case_sensitive else 0

        # Split the search terms and search through each word key in the index
        # for any word that contains the partial word.
        word_list = partial_word_list.split()
        for word in self._index_dict['_words_']:
            for partial_word in word_list:
                # A Regular expression that matches any number of word
                # characters for every '*' in the term.
                reg_str = '\\b%s\\b' % partial_word.replace('*', '\w*')
                word_regx = re.compile(reg_str, flags)
                if word_regx.match(word):
                    yield word

    def _process_phrase(func):
        """ Returns a wrapper function for wrapping phrase like searches.

        """

        @wraps(func)
        def wrapper(self, search_terms, strongs=False, morph=False,
                    added=True, case_sensitive=False, range_str=''):
            """ Gets a regular expression from the wrapped function, then
            builds a set of verse references to search, finally it calls the
            searching function with the regular expression and the verse
            reference iterator, and returns the resulting set of references.

            """

            search_regx = func(self, search_terms, strongs, morph, added,
                               case_sensitive, range_str)

            # First make sure we are only searching verses that have all the
            # search terms in them.
            search_list = search_terms.split()
            if '*' in search_terms:
                ref_set = self._index_dict.from_partial(search_list,
                                                        case_sensitive,
                                                        common_limit=500)
            else:
                ref_set = self._index_dict.value_intersect(search_list, 
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

            # Disable Strong's and Morphological if only words are used.
            strongs = bool(self._strongs_regx.search(search_terms))
            morph = bool(self._morph_regx.search(search_terms))

            return self.find_from_regex(ref_iter, search_regx, strongs, morph)

        return wrapper

    @_process_search
    @_process_phrase
    def ordered_multiword_search(self, search_terms, strongs=False,
                                 morph=False, added=True, case_sensitive=False,
                                 range_str=''):
        """ ordered_multiword_search(self, search_terms, strongs=False,
            morph=False, case_sensitive=False, range_str='') -> 
        Perform an ordered multiword search.  Like a multiword search, but all
        the words have to be in order.
                
            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for verses with these words in order '%s'..." % search_terms, tag=1)

        return self.search_terms_to_regex(search_terms, case_sensitive,
                                          sloppy=True)

    @_process_search
    @_process_phrase
    def phrase_search(self, search_terms, strongs=False, morph=False, 
                      added=True, case_sensitive=False, range_str=''):
        """ phrase_search(self, search_terms, strongs=False, morph=False,
               case_sensitive=False, range_str='') -> 
        Perform a phrase search.
                
            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for verses with this phrase '%s'..." % search_terms, tag=1)

        # Make all the terms the same case if case doesn't matter.
        flags = re.I if not case_sensitive else 0

        if strongs:
            # Match strongs phrases.
            search_reg_str = search_terms.replace(' ', r'[^<]*')
        elif morph:
            # Match morphological phrases.
            search_reg_str = search_terms.replace(' ', r'[^\{]*')
        else:
            # Match word phrases
            search_reg_str = '\\b%s\\b' % search_terms.replace(' ', 
                    r'\b(<[^>]*>|\{[^\}]*\}|\W)*\b')
        
        # Make a regular expression from the search terms.
        return re.compile(search_reg_str, flags)

    @_process_search
    @_process_phrase
    def mixed_phrase_search(self, search_terms, strongs=False, morph=False, 
                            added=True, case_sensitive=False, range_str=''):
        """ mixed_phrase_search(self, search_terms, strongs=False, morph=False,
        case_sensitive=False, range_str='') -> 
        Perform a phrase search.
                
            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for verses with this phrase '%s'..." % search_terms, tag=1)

        # Make a regular expression from the search terms.
        return self.search_terms_to_regex(search_terms, case_sensitive)

    @_process_search
    def regex_search(self, search_terms, strongs=False, morph=False,
                     added=True, case_sensitive=False, range_str=''):
        """ regex_search(self, search_terms, strongs=False, morph=False,
              case_sensitive=False, range_str='') -> 
        Perform a regular expression search.

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for regular expression '%s'..." % search_terms,
                   tag=1)

        # re.I is case insensitive.
        flags = re.I if not case_sensitive else 0

        try:
            # Make a regular expression from the search_terms.
            search_regx = re.compile(r'%s' % search_terms, flags)
        except Exception as err:
            print('There is a problem with the regular expression "%s": %s' % \
                    (search_terms, err), file=sys.stderr)
            exit()

        if range_str:
            # Only search through the supplied range.
            ref_iter = self._sorted_iter(range_str)
        else:
            # Search the entire Bible.
            ref_iter = VerseIter('Genesis 1:1')

        return self.find_from_regex(ref_iter, search_regx, strongs, morph,
                                    tag=1, try_clean=True)

    def find_from_regex(self, ref_iter, search_regex, strongs=False,
                        morph=False, added=True, tag=3, try_clean=False):
        """ Iterates through all the verses in the ref iter iterator and
        returns a list of verses whose text matches search_regx.

        """

        # Get an iterator that will return tuples
        # (verse_reference, verse_text).
        verse_iter = IndexedVerseTextIter(ref_iter, strongs=strongs,
                                          morph=morph, added=added,
                                          module=self._module_name)

        found_set = set()
        for verse_ref, verse_text in verse_iter:
            info_print('\033[%dD\033[KSearching...%s' % \
                       (len(verse_ref) + 20, verse_ref), end='', tag=tag)

            # Search for matches in the verse text.
            if search_regex.search(verse_text):
                found_set.add(verse_ref)
            elif try_clean and not strongs and not morph:
                # Should we do this or should we trust the user knows what
                # puctuation are in the verses?
                clean_verse_text = self._clean_text(verse_text)
                if search_regex.search(clean_verse_text):
                    found_verses.add(verse_ref)
        
        info_print("...Done.", tag=tag)

        return found_set

    def mixed_search(self, search_terms, strongs=False, morph=False, 
                     added=True, case_sensitive=False, range_str=''):
        """ mixed_search(self, search_terms, strongs=False, morph=False,
               case_sensitive=False, range_str='') -> 
        Perform a mixed search.
                
            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        found_set = set()
        not_set = set()
        and_set = set()
        or_set = set()
        xor_set = set()

        combine_dict = {
                '!' : not_set.update,
                '+' : and_set.intersection_update,
                '|' : or_set.update,
                '^' : xor_set.symmetric_difference_update,
                }

        for term in search_terms:
            if term[0] in '!+^|':
                # Set the correct combining function, and cleanup the item.
                if term[0] == '+' and not and_set:
                    # All of these verses go in the output.
                    combine_func = and_set.update
                else:
                    combine_func = combine_dict[term[0]]
                term = term[1:]
            else:
                if self._multi and found_set:
                    # If multiword is default and found_set is not empty
                    # make all search terms appear in the output.
                    combine_func = found_set.intersection_update
                else:
                    # Any of these verses could be in the output
                    combine_func = found_set.update

            if term.startswith('&'):
                # Allow regular expression searching.
                term = term[1:]
                search_func = self.regex_search
            elif ' ' in term:
                # Search term is a quoted string, so treat it like a phrase.
                if term.startswith('~'):
                    # ~'s trigger ordered multiword or sloppy phrase search.
                    term = term[1:]
                    search_func = self.ordered_multiword_search
                else:
                    search_func = self.mixed_phrase_search
            elif '*' in term:
                # Search for partial words.
                search_func = self.partial_word_search
            else:
                # A single word should be (multi/any)-word.
                search_func = self.multiword_search

            # Perform a strongs search.
            strongs = bool(self._strongs_regx.match(term.upper()))
            # Perform a morpholagical search.
            morph = bool(self._morph_regx.match(term.upper()))

            # Search for words or phrases.
            temp_set = search_func(term, strongs, morph, added, case_sensitive,
                                   range_str)

            # Add the results to the correct set.
            combine_func(temp_set)

        # Update the result set.
        found_set.update(or_set)
        found_set.update(xor_set)

        if and_set and found_set:
            # Make sure all the verses that are in the output have the words
            # or phrases that hade a '+' in front of them.
            found_set = and_set.union(found_set.intersection(and_set))
        elif and_set:
            # Found set must be empty to fill it with and_set's contents.
            found_set.update(and_set)

        # Finally remove all the verses that are in the not_set.
        found_set.difference_update(not_set)

        return found_set

    def sword_search(self, search_terms, strongs=False, morph=False,
                     added=True, case_sensitive=False, range_str='',
                     search_type='lucene'):
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

        info_print("Searching using the Sword library for '%s'..." % search_terms, tag=1)
        
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

            # Set the search type based on the search_type argument.
            search_type = search_type_dict.get(search_type.lower(), -4)

            # Make sure we can search like this.
            if not module.isSearchSupported(search_terms, search_type):
                print("Search not supported", file=sys.stderr)
                return found_set()

            # Get the range key.
            if not range_str:
                range_str = 'Genesis-Revelation'
            range_k = Sword.VerseKey().ParseVerseList(range_str, 'Genesis 1:1',
                                                      True)

            flags = re.I if not case_sensitive else 0

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
            print("There was a problem while searching: %s" % err, 
                  file=sys.stderr)

        found_set.discard('')

        return found_set

    @_process_search
    def test_search(self, search_terms, strongs=False, morph=False,
                    added=True, case_sensitive=False, range_str=''):
        """ A Test.

        """

        ref_set = self._index_dict.value_union(search_terms.split(), 
                                                 case_sensitive)
        if range_str:
            # Only search through the supplied range.
            ref_set.intersection_update(range_str)

        ref_list = sorted(ref_set, key=sort_key)

        term_dict = defaultdict(list)
        raw_dict = RawDict(iter(ref_list), self._module_name)
        words_len = 0
        for verse_ref, (verse_text, verse_dict) in raw_dict:
            for term in search_terms.split():
                if self._strongs_regx.match(term):
                    num = self._strongs_regx.sub('\\1', term)
                    words = set(verse_dict[num.upper()])
                    if words:
                        term_dict[num.upper()].append({verse_ref:words})
                elif self._morph_regx.match(term):
                    tag = self._morph_regx.sub('\\1', term)
                    words = set(verse_dict[tag.upper()])
                    if words:
                        term_dict[tag.upper()].append({verse_ref:words})
                else:
                    for key, value in verse_dict['_words'][0].items():
                        if ' %s ' % term.lower() in ' %s ' %  key.lower():
                            attr_dict = value[0]
                            if strongs and 'strongs' in attr_dict:
                                attr_list = attr_dict['strongs']
                                attr_list.append(key)
                                term_dict[term].append({verse_ref:attr_list})
                            if morph and 'morph' in attr_dict:
                                attr_list = attr_dict['morph']
                                attr_list.append(key)
                                words_len = max(len(attr_list), words_len)
                                term_dict[term].append({verse_ref:attr_list})
        len_longest_ref = len(max(ref_set, key=len))
        for key, value in term_dict.items():
            words_len = max([len(i) for d in value for i, v in d.items()])
            print('%s:' % key)
            for dic in value:
                ref, words = tuple(dic.items())[0]
                if isinstance(words, list):
                    w_str = '"%s"' % '", "'.join(words[:-1])
                    l_str = '"%s"' % words[-1]
                    words_str = '{0:{2}}: {1}'.format(w_str, l_str, words_len)
                else:
                    words_str = '"%s"' % '", "'.join(words)
                print('\t{0:{1}}: {2}'.format(ref, len_longest_ref, words_str))
                    #print('\t{0:{1}}: "{2}"'.format(ref, len_longest_ref, '", "'.join(words)))
        exit()

    @_process_search
    def test2_search(self, search_terms, strongs=False, morph=False,
                     added=True, case_sensitive=False, range_str=''):
        """ A Test.

        """

        ref_set = self._index_dict.value_union(search_terms.split(), 
                                                 case_sensitive)
        if range_str:
            # Only search through the supplied range.
            ref_set.intersection_update(range_str)

        ref_iter = iter(sorted(ref_set, key=sort_key))
        # Get an iterator that will return tuples
        # (verse_reference, verse_text).
        verse_iter = IndexedVerseTextIter(ref_iter, strongs=True,
                                          morph=morph, added=added,
                                          module=self._module_name)

        # This will skip words.
        not_words_str = r'\b\w+\b'
        # This will skip Strong's Numbers.
        not_strongs_str = r'<[^>]*>'
        # This wil skip Morphological Tags.
        not_morph_str = r'\{[^\}]*\}'
        # This will skip all punctuation.  Skipping ()'s is a problem for
        # searching Morphological Tags, but it is necessary for the
        # parenthesized words.  May break highlighting.
        not_punct_str = r'[\s,\?\!\.;:\\/_\(\)\[\]"\'-]'
        max_ref_len = len(max(ref_set, key=len))
        found_set = set()
        term_dict = defaultdict(list)
        for verse_ref, verse_text in verse_iter:
            for term in search_terms.split():
                if self._strongs_regx.match(term):
                    test_regx = re.compile(r'\s((?:\b\w+\b|[\s,\?\!\.;:\\/_\(\)\[\]"\'-])+)\s((?:%s)+)' % term, re.I)
                elif self._morph_regx.match(term):
                    test_regx = re.compile(r'\s((?:\b\w+\b|[\s,\?\!\.;:\\/_\(\)\[\]"\'-])+)(?:<[^>]*>|\s)+((?:%s)+)' % term, re.I)
                else:
                    test_regx = re.compile(r'((?:\b\w+\b|[\s,\?\!\.;:\\/_\(\)\[\]"\'-])*?%s(?:\b\w+\b|[\s,\?\!\.;:\\/_\(\)\[\]"\'-])+)+((?:<[^>]*>|\{[^\}]*\}|\s)+)' % term, re.I)
                for match in test_regx.finditer(verse_text):
                    phrase, num = match.groups()
                    phrase = phrase.strip(',').strip('.').strip()
                    phrase = phrase.strip(';').strip('?').strip(':').strip()
                    num = num.replace('<', '').replace('>', '')
                    num = num.replace('{', '').replace('}', '')
                    if not phrase or not num.strip():
                        if not strongs:
                            break
                        print(verse_ref, verse_text)
                        print(match.group(), match.groups())
                        exit()
                    num = '"%s"' % '", "'.join(num.split()) 
                    term_dict[term].append('\t{0:{1}}: {2:{4}}: "{3}"'.format(verse_ref, max_ref_len, num, phrase, 18))
        for term, lst in term_dict.items():
            term = term.replace('<', '').replace('>', '')
            term = term.replace('{', '').replace('}', '')
            print('%s:\n%s' % (term, '\n'.join(lst)))
        exit()

    @_process_search
    def test3_search(self, search_terms, strongs=False, morph=False,
                     added=True, case_sensitive=False, range_str=''):
        """ A Test.

        """

        ref_set = self._index_dict.value_union(search_terms.split(), 
                                                 case_sensitive)
        if range_str:
            # Only search through the supplied range.
            ref_set.intersection_update(range_str)

        if not ref_set:
            exit()

        ref_iter = iter(sorted(ref_set, key=sort_key))
        # Get an iterator that will return tuples
        # (verse_reference, verse_text).
        verse_iter = VerseTextIter(ref_iter, strongs=strongs,
                                   morph=morph, render='raw',
                                   module=self._module_name)

        found_set = set()
        strong_regx = re.compile(r'strong:([GH]\d+)', re.I)
        morph_regx = re.compile(r'(?:Morph|robinson):([\w-]*)', re.I)
        tag_regx = re.compile(r'''
                ([^<]*)                             # Before tag.
                <(?P<tag>q|w|transChange|note)      # Tag name.
                ([^>]*)>                            # Tag attributes.
                ([\w\W]*?)</(?P=tag)>               # Tag text and end.
                ([^<]*)                             # Between tags. 
                ''', re.I|re.X)
        divname_regx = re.compile(r'(?:<seg>)?<(?:divineName)>+([^<]*?)([\'s]*)</(?:divineName)>(?:</seg>)?', re.I)
        xadded_regx = re.compile(r'<seg subType="x-added"[^>]*>([^<]*)</seg>', re.I)
        div_upper = lambda m: m.group(1).upper() + m.group(2)
        marker_regx = re.compile(r'.*marker="(.)".*', re.I)
        term_dict = defaultdict(list)
        len_attrs = 0

        for verse_ref, verse_text in verse_iter:
            #print(render_raw(verse_text, strongs, morph))
            #print(render_raw2(verse_text, strongs, morph))
            #continue
            for term in search_terms.split():
                term = term.replace('<', '').replace('>', '')
                term = term.replace('{', '').replace('}', '')
                v_text = ''
                info_print('%s\n' % verse_text, tag=4)
                term_regx = re.compile('\\b%s\\b' % term, re.I)
                for match in tag_regx.finditer(verse_text):
                    opt, tag_name, tag_attr, tag_text, punct = match.groups()
                    tag_text = xadded_regx.sub('\\1', tag_text)
                    if match.re.search(tag_text):
                        match_list = match.re.findall(tag_text + punct)
                    else:
                        match_list = [match.groups()]
                    for tag_tup in match_list:
                        opt, tag_name, tag_attr, tag_text, punct = tag_tup
                        info_print(tag_tup, tag=4)
                        value_list = []
                        attr_list = []
                        strongs_list = []
                        morph_list = []
                        tag_text = divname_regx.sub(div_upper, tag_text)
                        v_text += marker_regx.sub('\\1 ', opt) + tag_text + punct
                        if term.upper() in tag_attr:
                            attr_list = [term.upper()]
                        elif term_regx.search(tag_text):
                            if strongs or not morph:
                                strongs_list = strong_regx.findall(tag_attr)
                            if morph:
                                morph_list = morph_regx.findall(tag_attr)

                        for lst in (strongs_list, morph_list, attr_list):
                            if lst:
                                attr_str = '%s"' % '", "'.join(lst)
                                value_list = [attr_str, tag_text.strip()]
                                term_dict[term].append({verse_ref:value_list})
                                len_attrs = max(len(attr_str), len_attrs)
                info_print(v_text, tag=4)
        max_len_ref = len(max(ref_set, key=len))
        for term, lst in term_dict.items():
            print('%s:' % term)
            for dic in lst:
                ref, (attrs, s) = list(dic.items())[0]
                s_l = '{1:{0}}: "{2}'.format(len_attrs, attrs, s)
                print('\t{0:{1}}: "{2}"'.format(ref, max_len_ref, s_l))
                

        exit()

    @_process_search
    def test4_search(self, search_terms, strongs=False, morph=False,
                     added=True, case_sensitive=False, range_str=''):
        """ A Test.

        """

        ref_set = self._index_dict.value_union(search_terms.split(), 
                                                 case_sensitive)
        if range_str:
            # Only search through the supplied range.
            ref_set.intersection_update(range_str)

        if not ref_set:
            exit()

        ref_iter = iter(sorted(ref_set, key=sort_key))
        # Get an iterator that will return tuples
        # (verse_reference, verse_text).
        verse_iter = VerseTextIter(ref_iter, strongs=strongs,
                                   morph=morph, render='raw',
                                   module=self._module_name)

        found_set = set()
        strong_regx = re.compile(r'strong:([GH]\d+)', re.I)
        morph_regx = re.compile(r'(?:Morph|robinson):([\w-]*)', re.I)
        tag_regx = re.compile(r'''
                ([^<]*)                             # Before tag.
                <(?P<tag>seg|q|w|transChange|note)  # Tag name.
                ([^>]*)>                            # Tag attributes.
                ([\w\W]*?)</(?P=tag)>               # Tag text and end.
                ([^<]*)                             # Between tags. 
                ''', re.I|re.X)
        divname_regx = re.compile(r'<(?:divineName)>([^<]*?)([\'s]*)</(?:divineName)>', re.I)
        div_upper = lambda m: m.group(1).upper() + m.group(2)
        marker_regx = re.compile(r'.*marker="(.)".*', re.I)
        term_dict = defaultdict(list)
        len_attrs = 0
        def recurse_tag(text, term, verse_ref, ctag_attr=''):
            """ Recursively parse raw verse text using regular expressions, and
            returns the correctly formatted text.

            """

            term_list = []
            for match in tag_regx.finditer(text):
                value_list = []
                attr_list = []
                strongs_list = []
                morph_list = []
                opt, tag_name, tag_attr, tag_text, punct = match.groups()
                if match.re.search(tag_text):
                    term_list.extend(recurse_tag(tag_text, term, verse_ref, tag_attr))
                else:
                    info_print((opt, tag_name, tag_attr, tag_text, punct), tag=4)
                    if marker_regx.match(opt):
                        opt = ''
                    tag_text = opt + divname_regx.sub(div_upper, tag_text) + punct
                    if term.upper() in tag_attr or term.upper() in ctag_attr:
                        attr_list = [term.upper()]
                    elif term_regx.search(tag_text):
                        if strongs or not morph:
                            strongs_list.extend(strong_regx.findall(tag_attr))
                            strongs_list.extend(strong_regx.findall(ctag_attr))
                        if morph:
                            morph_list.extend(morph_regx.findall(tag_attr))
                            morph_list.extend(morph_regx.findall(ctag_attr))
                    for lst in (strongs_list, morph_list, attr_list):
                        if lst:
                            a_str = '%s"' % '", "'.join(lst)
                            value_list = [a_str, tag_text.strip()]
                            term_list.append({verse_ref:value_list})
            return term_list

        for verse_ref, verse_text in verse_iter:
            #print(render_raw(verse_text, strongs, morph))
            #print(render_raw2(verse_text, strongs, morph))
            #continue
            for term in search_terms.split():
                term = term.replace('<', '').replace('>', '')
                term = term.replace('{', '').replace('}', '')
                v_text = ''
                info_print('%s\n' % verse_text, tag=4)
                term_regx = re.compile('\\b%s\\b' % term, re.I)
                value_list = recurse_tag(verse_text, term, verse_ref)
                if value_list:
                    for i in value_list:
                        len_attrs = max(len(i[verse_ref][0]), len_attrs)
                    term_dict[term].extend(value_list)

        max_len_ref = len(max(ref_set, key=len))
        for term, lst in term_dict.items():
            print('%s:' % term)
            for dic in lst:
                ref, (attrs, s) = list(dic.items())[0]
                s_l = '{1:{0}}: "{2}'.format(len_attrs, attrs, s)
                print('\t{0:{1}}: "{2}"'.format(ref, max_len_ref, s_l))
                

        exit()
            


def main(arg_list, **kwargs):
    """ Takes a string of arguments, and a bunch of keyword arguments.

    """

    info_print("\nProcessing arguments...\n", tag=2)

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
    search_added = kwargs['search_added']
    case_sensitive = kwargs['case_sensitive']
    search_range = kwargs['search_range']

    # Get the lookup related arguments
    lookup = kwargs['verse_reference']
    define_strongs = kwargs['numbers']
    define_morph = kwargs['tags']
    define_word = kwargs['words']
    define_kjv_word = kwargs['kjv_words']
    daily = kwargs['day']

    # Set the highlight to nothing.
    highlight_list = []

    if kwargs['raw']:
        raw_lookup = Lookup()
        strongs = 'On' if kwargs['show_numbers'] else 'Off'
        morph = 'On' if kwargs['show_tags'] else 'Off'
        raw_lookup._library.setGlobalOption("Strong's Numbers", strongs)
        raw_lookup._library.setGlobalOption("Morphological Tags", morph)
        for i in sorted(parse_verse_range(arg_list), key=sort_key):
            info_print('%s\n' % raw_lookup.get_raw_text(i))
            print('%s\n' % raw_lookup.get_text(i))
        exit()
    elif lookup:
        # Lookup verses in the argument string.
        results = parse_verse_range(lookup)
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
        # only lookup Greek ones in 'Robinson.'
        print('%s\n' % mod_lookup('Robinson', define_morph.upper()))
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

        # Use the Sword modules search capabilities.
        if search_type.startswith('sword_'):
            extras = (search_type[6:],)
            search_type = search_type[:5]
            highlight_list = arg_list

        try:
            # Get the search function asked for.
            search_func = getattr(search, '%s_search' % search_type)
        except AttributeError as err:
            # An invalid search type was specified.
            print("Invalid search type: %s" % search_type, file=sys.stderr)
            exit()

        # Search.
        results = search_func(arg_list, strongs_search, morph_search,
                              search_added, case_sensitive, search_range,
                              *extras)

        
    count = len(results)
    info_print("\nFound %s verse%s.\n" % (count, 's' if count != 1 else ''), 
               tag=-10)

    if kwargs['quiet']:
        # Only the verse count was given.
        exit()
    elif kwargs['list_only']:
        # Print a sorted list of references.
        print('\n'.join(sorted(results, key=sort_key)))
        exit()
    else:
        if search_type in ['combined', 'combined_phrase']:
            # Combined searches are complicated.
            # Parse the search argument and build a highlight string from the
            # result.
            arg_parser = CombinedParse(arg_str)
            parsed_args = arg_parser.word_list
            not_l = arg_parser.not_list
            # Remove any stray '+'s.
            #highlight_str = highlight_str.replace('|+', ' ')
            if search_type == 'combined_phrase':
                # A phrase search needs to highlight phrases.
                highlight_list = parsed_args
            else:
                highlight_list = ' '.join(parsed_args).split()
        # Build the highlight string for the other searches.
        elif search_type in ['anyword', 'multiword', 'eitheror', 
                             'partial_word']:
            # Highlight each word separately.
            highlight_list = arg_str.split()
        elif search_type == 'mixed':
            # In mixed search phrases are in quotes so the arg_list should be
            # what we want, but don't include any !'ed words.
            highlight_list = [i for i in arg_list if not i.startswith('!')]
        elif search_type in ['phrase', 'mixed_phrase', 'ordered_multiword']:
            # Phrases should highlight phrases.
            highlight_list = [arg_str]
        #elif search_type == 'partialword':
            #for part in arg_str.split():
                #highlight_list.append('\w*%s\w' % part)

        if lookup:
            # Highlight anything else the user typed in.
            highlight_list = arg_list

        # Don't modify regular expression searches.
        if search_type != 'regex':
            regx_list = build_highlight_regx(highlight_list, case_sensitive,
                        (search_type == 'ordered_multiword'))
            if kwargs['context']:
                regx_list.extend(build_highlight_regx(results, case_sensitive))
        else:
            regx_list = [re.compile(arg_str, re.I if case_sensitive else 0)]

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
        verse_gen = render_verses_with_italics(context_results, 
                                               not kwargs['one_line'],
                                               show_strongs, show_morph, 
                                               search_added,
                                               kwargs['show_notes'],
                                               highlight_search_terms,
                                               regx_list, flags)
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
    parser.add_option('-s', '--search-type', action='store', default='mixed',
            help='Valid search types are: phrase, multiword, anyword, eitheror, mixed, mixed_phrase, ordered_multiword, regex, combined, combined_phrase, sword, sword_phrase, sword_multiword, sword_entryattrib, and sword_lucene. (default: phrase)',
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
    parser.add_option('-x', '--raw', action='store_true', default=False,
                        help='Get the raw text of verses by reference.',
                        dest='raw')
    parser.add_option('-l', '--lookup', action='store', default='',
                        help='Lookup a comma seperated list of verse references.',
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
    parser.add_option('-a', '--added', action='store_false', default=True,
                        help="Show/search the added text (italics) default is \
                                True.",
                              dest='search_added')
    parser.add_option('', '--notes', action='store_true', default=False,
                        help="Show study notes.", dest='show_notes')
    parser.add_option('-n', '--numbers', action='store_true', default=False,
                        help="Include the Strong's numbers in the verse \
                              output.", dest='show_numbers')
    parser.add_option('-t', '--tags', action='store_true', default=False,
                        help="Include the Morphological tags in the verse \
                              output.", dest='show_tags')
    parser.add_option('-r', '--verse_ref', action='store_true', default=False,
                        help='Show only a sorted list of references', 
                        dest='list_only')
    parser.add_option('-c', '--color_output', action='store', default=3,
                        help='How much to color. (-1 == nothing, 0 == verse references, 1 == italics, 2 == attributes, 3 == highlight)',
                        dest='color_level')
    parser.add_option('-q', '--quiet', action='store_true', default=False,
                        help='Only print the number of verses found.', 
                        dest='quiet')
    parser.add_option('-v', '--verbose', action='store', default=1,
                        help='Print more information.', 
                        dest='verbose_level')

    options, args = parser.parse_args()
    try:
        VERBOSE_LEVEL = int(options.verbose_level)
    except Exception as err:
        print("Invalid verbose level '%s': %s" % (options.verbose_level, err),
              file=sys.stderr)
        VERBOSE_LEVEL = 1
    try:
        COLOR_LEVEL = int(options.color_level)
    except Exception as err:
        print("Invalid color level '%s': %s" % (options.verbose_level, err),
              file=sys.stderr)
        COLOR_LEVEL = 3

    def stdout_to_stderr(data):
        """ Write data to stderr.

        """

        sys.stderr.write(data)
        sys.stderr.flush()

    #with StdoutRedirect(stdout_to_stderr):
    main(args, **options.__dict__)
    re.purge()
