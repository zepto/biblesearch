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

"""Utility functions and classes."""

import dbm
import json
import locale
import os
import re
import sys
from fcntl import ioctl
from os.path import join
from struct import unpack
from termios import TIOCGWINSZ
from typing import Any, Generator

VERBOSE_LEVEL = 1

# Setup the index path to '/userhome/.biblesearch', and if that doesn't exist
# use the current working directory.
INDEX_PATH = ''
home_path = os.getenv('HOME')
if home_path:
    INDEX_PATH = os.path.join(home_path, '.biblesearch')

if not os.path.isdir(INDEX_PATH):
    INDEX_PATH = os.getcwd()


def info_print(data, end: str = '\n', tag: int = 0):
    """Print the data to stderr as info."""
    if tag <= VERBOSE_LEVEL:
        print(data, end=end, file=sys.stderr)
        sys.stderr.flush()


def get_encoding() -> str:
    """Figure out the encoding to use for strings."""
    # Hopefully get the correct encoding to use.
    lang, enc = locale.getlocale()
    if not lang or lang == 'C':
        encoding = 'ascii'
    else:
        encoding = enc

    return encoding


def screen_size() -> tuple[Any, ...]:
    """Get screen size.

    Returns a tuple containing the hight and width of the screen in
    characters (i.e. (25, 80)).
    """
    get_size = lambda fd: unpack("hh", ioctl(fd, TIOCGWINSZ, '0000'))
    try:
        for i in [0, 1, 2]:
            return get_size(i)
    except Exception:
        try:
            term_fd = os.open(os.ctermid(), os.O_RDONLY)
            size = get_size(term_fd)
            os.close(term_fd)
            return size
        except Exception:
            pass
    return (25, 80)


class IndexDbm(object):
    """A dbm database writer."""

    def __init__(self, name: str = '', mode: Any = 'r'):
        """Create a databse."""
        self._dbm = dbm.open(name, mode)

    def __setitem__(self, key: str, item: Any) -> int:
        """Add item assignment to this dict."""
        return self.set(key, item)

    def _encoding(self) -> str:
        """Figure out the encoding to use for strings."""
        # Hopefully get the correct encoding to use.
        lang, enc = locale.getlocale()
        if not lang or lang == 'C':
            encoding = 'ascii'
        else:
            encoding = enc

        return encoding

    def firstkey(self) -> Any:
        """Return the first key."""
        key = self._dbm.firstkey()
        if key:
            key = key.decode(self._encoding(), 'replace')
        return key

    def nextkey(self, key: str) -> Any:
        """Return the next key from key."""
        key_b = key.encode(self._encoding(), 'replace')
        return_key = self._dbm.nextkey(key_b)
        if return_key:
            return_key = return_key.decode(self._encoding(), 'replace')
        return return_key

    def set(self, key: str, value: Any) -> int:
        """Write the list database under the given name."""
        # Encode the buffer into bytes.
        byte_buffer = json.dumps(value).encode(self._encoding(), 'replace')

        # Write buffer to tar file.
        self._dbm[key] = byte_buffer

        return len(byte_buffer)

    def get(self, key: str, default: list = []) -> Any:
        """Read the named list out of the database."""
        try:
            str_buffer = self._dbm[key].decode(self._encoding(), 'replace')
            return json.loads(str_buffer)
        except Exception as err:
            print(f"Error reading {key}: {err}", file=sys.stderr)
            return default

    def update(self, dic: dict) -> int:
        """Write a dictionary to the database."""
        for k, v in dic.items():
            self.set(k, v)

        return len(dic)

    def read_dict(self) -> dict:
        """Read out the entire dictionary."""
        temp_dict = {}
        key = self._dbm.firstkey()
        while key:
            temp_dict[key] = self._dbm[key]
            key = self._dbm.nextkey(key)

        return temp_dict

    def __enter__(self) -> "IndexDbm":
        """Add the functionality to use pythons with statement."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        """Close the file and exit."""
        try:
            self._dbm.close()
            if exc_type:
                return False
            return True
        except Exception as err:
            print(f"Error in __exit__: {err}", file=sys.stderr)
            return False


class IndexDict(dict):
    """Bible index container.

    A Bible index container, that provides on-demand loading of indexed items.
    """

    def __init__(self, name: str = '', path: str = ''):
        """Initialize the index."""
        path = path if path else INDEX_PATH

        self._non_key_text_regx = re.compile(r'[<>\{\}]')

        self._name = name
        self._path = path

        dbm_name = f"{path}/{name}_index_i.dbm"
        self._dbm_dict = IndexDbm(dbm_name, 'r')

        self._lower_case = self.get("lower_case", {})

        super(IndexDict, self).__init__()

    # In case we need to access the name externally we don't want it changed.
    name = property(lambda self: self._name)

    def __getitem__(self, key: Any) -> Any:
        """Get item associated with key.

        If a filename was given then use it to retrieve keys when they are
        needed.
        """
        # Cleanup Strong's and Morphology
        key = self._non_key_text_regx.sub('', key).strip()
        if self._name and (key not in self):
            # Load the value from the database if we don't have it.
            try:
                # dbm_name = '%s/%s_index_i.dbm' % (self._path, self._name)
                # with IndexDbm(dbm_name, 'r') as dbm_dict:
                self[key] = self._dbm_dict.get(key)
            except Exception as err:
                print("The index is either broken or missing.",
                      file=sys.stderr)
                print("Please fix it.  Re-build the index.", file=sys.stderr)
                print(f"The error was: {err}", file=sys.stderr)
                sys.exit()

        return super(IndexDict, self).__getitem__(key)

    def get(self, key: Any, default: Any = []) -> Any:
        """Return the value associated with key, or default."""
        value = self[key]
        return value if value else default

    def keys(self) -> Generator[Any, None, None]:
        """Yield each key."""
        # dbm_name = '%s/%s_index_i.dbm' % (self._path, self._name)
        # with IndexDbm(dbm_name, 'r') as dbm_dict:
        key = self._dbm_dict.firstkey()
        while key:
            yield key
            key = self._dbm_dict.nextkey(key)

    def value_intersect(self, key_list: list,
                        case_sensitive: bool = False) -> set[str]:
        """Get a set of verses containing words in key_list.

        Return a set with only the verses that contain all the items in
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

    def value_sym_diff(self, key_list: list,
                       case_sensitive: bool = False) -> set:
        """Get verses with either or key_list.

        Finds the symmetric difference of all the references that contain the
        keys in key_list.  (only a set with either or not both keys)
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

    def value_union(self, key_list: list, case_sensitive:
                    bool = False) -> set[str]:
        """Verses that contain each in key_list.

        Returns a set with all the verses that contain each item in
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

    def from_partial(self, partial_list: list, case_sensitive=False,
                     common_limit: int = 31103) -> set[str]:
        """Partial word search.

        Returns a set of verses that have any the partial words in the list.
        """
        flags = re.I if not case_sensitive else 0
        verse_set = set()

        # Search through each word key in the index for any word that contains
        # the partial word.
        for word in self['_words_']:
            for partial_word in partial_list:
                # A Regular expression that matches any number of word
                # characters for every '*' in the term.
                reg_str = '\\b%s\\b' % partial_word.replace('*', r'\w*')
                try:
                    word_regx = re.compile(reg_str, flags)
                except Exception as err:
                    print(f"There is a problem with the regular "
                          f"expression {reg_str}: {err}", file=sys.stderr)
                    sys.exit()
                if word_regx.match(word):
                    temp_list = self[word]
                    if len(temp_list) < common_limit:
                        verse_set.update(temp_list)

        return verse_set


class DbmDict(dict):
    """A dbm dictionary."""

    def __init__(self, name: str = '', path: str = ''):
        """Initialize the dbm."""
        path = path if path else INDEX_PATH

        self._non_key_text_regx = re.compile(r'[<>\{\}]')

        self._name = f"{name}.dbm"
        self._path = path

        dbm_name = join(path, f"{name}.dbm")
        self._dbm_dict = IndexDbm(dbm_name, 'r')

        super(DbmDict, self).__init__()

    # In case we need to access the name externally we don't want it changed.
    name = property(lambda self: self._name)

    def __getitem__(self, key: Any) -> Any:
        """Get the item associated with key.

        If a filename was given then use it to retrieve keys when they are
        needed.
        """
        # Cleanup Strong's and Morphology
        key = self._non_key_text_regx.sub('', key).strip()
        if self._name and (key not in self):
            # Load the value from the database if we don't have it.
            try:
                # dbm_name = join(self._path, self._name)
                # with IndexDbm(dbm_name, 'r') as dbm_dict:
                self[key] = self._dbm_dict.get(key)
            except Exception as err:
                print(f"The error was: {err}", file=sys.stderr)

        return super(DbmDict, self).__getitem__(key)

    def get(self, key: str, default: Any = []) -> Any:
        """Return the value associated with key, or default."""
        value = self[key]
        return value if value else default

    def keys(self) -> Generator[Any, None, None]:
        """Yield each key."""
        # dbm_name = join(self._path, self._name)
        # with IndexDbm(dbm_name, 'r') as dbm_dict:
        key = self._dbm_dict.firstkey()
        while key:
            yield key
            key = self._dbm_dict.nextkey(key)
