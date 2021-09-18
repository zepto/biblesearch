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

"""Bible verse objects and functions."""

import gzip
import json
import re
import sys
from collections import defaultdict
from difflib import get_close_matches
from os.path import dirname as os_dirname
from os.path import join as os_join
from textwrap import fill
from typing import Any, Generator, Iterator, Union
from xml.dom.minidom import parseString

from .utils import INDEX_PATH, DbmDict, IndexDbm, info_print, screen_size

data_path = os_join(os_dirname(__file__), 'data')


class Verse(object):
    """Bible references.

    An index object of Bible references that can increment and decrement a
    reference.
    """

    # This information came from the sword libraries canon.h
    _books_tup = (
        ("Genesis", "Gen", "Gen", 50),
        ("Exodus", "Exod", "Exod", 40),
        ("Leviticus", "Lev", "Lev", 27),
        ("Numbers", "Num", "Num", 36),
        ("Deuteronomy", "Deut", "Deut", 34),
        ("Joshua", "Josh", "Josh", 24),
        ("Judges", "Judg", "Judg", 21),
        ("Ruth", "Ruth", "Ruth", 4),
        ("I Samuel", "1Sam", "1Sam", 31),
        ("II Samuel", "2Sam", "2Sam", 24),
        ("I Kings", "1Kgs", "1Kgs", 22),
        ("II Kings", "2Kgs", "2Kgs", 25),
        ("I Chronicles", "1Chr", "1Chr", 29),
        ("II Chronicles", "2Chr", "2Chr", 36),
        ("Ezra", "Ezra", "Ezra", 10),
        ("Nehemiah", "Neh", "Neh", 13),
        ("Esther", "Esth", "Esth", 10),
        ("Job", "Job", "Job", 42),
        ("Psalms", "Ps", "Ps", 150),
        ("Proverbs", "Prov", "Prov", 31),
        ("Ecclesiastes", "Eccl", "Eccl", 12),
        ("Song of Solomon", "Song", "Song", 8),
        ("Isaiah", "Isa", "Isa", 66),
        ("Jeremiah", "Jer", "Jer", 52),
        ("Lamentations", "Lam", "Lam", 5),
        ("Ezekiel", "Ezek", "Ezek", 48),
        ("Daniel", "Dan", "Dan", 12),
        ("Hosea", "Hos", "Hos", 14),
        ("Joel", "Joel", "Joel", 3),
        ("Amos", "Amos", "Amos", 9),
        ("Obadiah", "Obad", "Obad", 1),
        ("Jonah", "Jonah", "Jonah", 4),
        ("Micah", "Mic", "Mic", 7),
        ("Nahum", "Nah", "Nah", 3),
        ("Habakkuk", "Hab", "Hab", 3),
        ("Zephaniah", "Zeph", "Zeph", 3),
        ("Haggai", "Hag", "Hag", 2),
        ("Zechariah", "Zech", "Zech", 14),
        ("Malachi", "Mal", "Mal", 4),
        ("Matthew", "Matt", "Matt", 28),
        ("Mark", "Mark", "Mark", 16),
        ("Luke", "Luke", "Luke", 24),
        ("John", "John", "John", 21),
        ("Acts", "Acts", "Acts", 28),
        ("Romans", "Rom", "Rom", 16),
        ("I Corinthians", "1Cor", "1Cor", 16),
        ("II Corinthians", "2Cor", "2Cor", 13),
        ("Galatians", "Gal", "Gal", 6),
        ("Ephesians", "Eph", "Eph", 6),
        ("Philippians", "Phil", "Phil", 4),
        ("Colossians", "Col", "Col", 4),
        ("I Thessalonians", "1Thess", "1Thess", 5),
        ("II Thessalonians", "2Thess", "2Thess", 3),
        ("I Timothy", "1Tim", "1Tim", 6),
        ("II Timothy", "2Tim", "2Tim", 4),
        ("Titus", "Titus", "Titus", 3),
        ("Philemon", "Phlm", "Phlm", 1),
        ("Hebrews", "Heb", "Heb", 13),
        ("James", "Jas", "Jas", 5),
        ("I Peter", "1Pet", "1Pet", 5),
        ("II Peter", "2Pet", "2Pet", 3),
        ("I John", "1John", "1John", 5),
        ("II John", "2John", "2John", 1),
        ("III John", "3John", "3John", 1),
        ("Jude", "Jude", "Jude", 1),
        ("Revelation of John", "Rev", "Rev", 22),
    )

    _verse_count = (
        # Genesis
        (31, 25, 24, 26, 32, 22, 24, 22, 29, 32, 32, 20, 18, 24, 21, 16, 27,
            33, 38, 18, 34, 24, 20, 67, 34, 35, 46, 22, 35, 43, 55, 32, 20, 31,
            29, 43, 36, 30, 23, 23, 57, 38, 34, 34, 28, 34, 31, 22, 33, 26),
        # Exodus
        (22, 25, 22, 31, 23, 30, 25, 32, 35, 29, 10, 51, 22, 31, 27, 36, 16,
            27, 25, 26, 36, 31, 33, 18, 40, 37, 21, 43, 46, 38, 18, 35, 23, 35,
            35, 38, 29, 31, 43, 38),
        # Leviticus
        (17, 16, 17, 35, 19, 30, 38, 36, 24, 20, 47, 8, 59, 57, 33, 34, 16, 30,
            37, 27, 24, 33, 44, 23, 55, 46, 34),
        # Numbers
        (54, 34, 51, 49, 31, 27, 89, 26, 23, 36, 35, 16, 33, 45, 41, 50, 13,
            32, 22, 29, 35, 41, 30, 25, 18, 65, 23, 31, 40, 16, 54, 42, 56, 29,
            34, 13),
        # Deuteronomy
        (46, 37, 29, 49, 33, 25, 26, 20, 29, 22, 32, 32, 18, 29, 23, 22, 20,
            22, 21, 20, 23, 30, 25, 22, 19, 19, 26, 68, 29, 20, 30, 52, 29,
            12),
        # Joshua
        (18, 24, 17, 24, 15, 27, 26, 35, 27, 43, 23, 24, 33, 15, 63, 10, 18,
            28, 51, 9, 45, 34, 16, 33),
        # Judges
        (36, 23, 31, 24, 31, 40, 25, 35, 57, 18, 40, 15, 25, 20, 20, 31, 13,
            31, 30, 48, 25),
        # Ruth
        (22, 23, 18, 22),
        # I Samuel
        (28, 36, 21, 22, 12, 21, 17, 22, 27, 27, 15, 25, 23, 52, 35, 23, 58,
            30, 24, 42, 15, 23, 29, 22, 44, 25, 12, 25, 11, 31, 13),
        # II Samuel
        (27, 32, 39, 12, 25, 23, 29, 18, 13, 19, 27, 31, 39, 33, 37, 23, 29,
            33, 43, 26, 22, 51, 39, 25),
        # I Kings
        (53, 46, 28, 34, 18, 38, 51, 66, 28, 29, 43, 33, 34, 31, 34, 34, 24,
            46, 21, 43, 29, 53),
        # II Kings
        (18, 25, 27, 44, 27, 33, 20, 29, 37, 36, 21, 21, 25, 29, 38, 20, 41,
            37, 37, 21, 26, 20, 37, 20, 30),
        # I Chronicles
        (54, 55, 24, 43, 26, 81, 40, 40, 44, 14, 47, 40, 14, 17, 29, 43, 27,
            17, 19, 8, 30, 19, 32, 31, 31, 32, 34, 21, 30),
        # II Chronicles
        (17, 18, 17, 22, 14, 42, 22, 18, 31, 19, 23, 16, 22, 15, 19, 14, 19,
            34, 11, 37, 20, 12, 21, 27, 28, 23, 9, 27, 36, 27, 21, 33, 25, 33,
            27, 23),
        # Ezra
        (11, 70, 13, 24, 17, 22, 28, 36, 15, 44),
        # Nehemiah
        (11, 20, 32, 23, 19, 19, 73, 18, 38, 39, 36, 47, 31),
        # Esther
        (22, 23, 15, 17, 14, 14, 10, 17, 32, 3),
        # Job
        (22, 13, 26, 21, 27, 30, 21, 22, 35, 22, 20, 25, 28, 22, 35, 22, 16,
            21, 29, 29, 34, 30, 17, 25, 6, 14, 23, 28, 25, 31, 40, 22, 33, 37,
            16, 33, 24, 41, 30, 24, 34, 17),
        # Psalms
        (6, 12, 8, 8, 12, 10, 17, 9, 20, 18, 7, 8, 6, 7, 5, 11, 15, 50, 14, 9,
            13, 31, 6, 10, 22, 12, 14, 9, 11, 12, 24, 11, 22, 22, 28, 12, 40,
            22, 13, 17, 13, 11, 5, 26, 17, 11, 9, 14, 20, 23, 19, 9, 6, 7, 23,
            13, 11, 11, 17, 12, 8, 12, 11, 10, 13, 20, 7, 35, 36, 5, 24, 20,
            28, 23, 10, 12, 20, 72, 13, 19, 16, 8, 18, 12, 13, 17, 7, 18, 52,
            17, 16, 15, 5, 23, 11, 13, 12, 9, 9, 5, 8, 28, 22, 35, 45, 48, 43,
            13, 31, 7, 10, 10, 9, 8, 18, 19, 2, 29, 176, 7, 8, 9, 4, 8, 5, 6,
            5, 6, 8, 8, 3, 18, 3, 3, 21, 26, 9, 8, 24, 13, 10, 7, 12, 15, 21,
            10, 20, 14, 9, 6),
        # Proverbs
        (33, 22, 35, 27, 23, 35, 27, 36, 18, 32, 31, 28, 25, 35, 33, 33, 28,
            24, 29, 30, 31, 29, 35, 34, 28, 28, 27, 28, 27, 33, 31),
        # Ecclesiastes
        (18, 26, 22, 16, 20, 12, 29, 17, 18, 20, 10, 14),
        # Song of Solomon
        (17, 17, 11, 16, 16, 13, 13, 14),
        # Isaiah
        (31, 22, 26, 6, 30, 13, 25, 22, 21, 34, 16, 6, 22, 32, 9, 14, 14, 7,
            25, 6, 17, 25, 18, 23, 12, 21, 13, 29, 24, 33, 9, 20, 24, 17, 10,
            22, 38, 22, 8, 31, 29, 25, 28, 28, 25, 13, 15, 22, 26, 11, 23, 15,
            12, 17, 13, 12, 21, 14, 21, 22, 11, 12, 19, 12, 25, 24),
        # Jeremiah
        (19, 37, 25, 31, 31, 30, 34, 22, 26, 25, 23, 17, 27, 22, 21, 21, 27,
            23, 15, 18, 14, 30, 40, 10, 38, 24, 22, 17, 32, 24, 40, 44, 26, 22,
            19, 32, 21, 28, 18, 16, 18, 22, 13, 30, 5, 28, 7, 47, 39, 46, 64,
            34),
        # Lamentations
        (22, 22, 66, 22, 22),
        # Ezekiel
        (28, 10, 27, 17, 17, 14, 27, 18, 11, 22, 25, 28, 23, 23, 8, 63, 24, 32,
            14, 49, 32, 31, 49, 27, 17, 21, 36, 26, 21, 26, 18, 32, 33, 31, 15,
            38, 28, 23, 29, 49, 26, 20, 27, 31, 25, 24, 23, 35),
        # Daniel
        (21, 49, 30, 37, 31, 28, 28, 27, 27, 21, 45, 13),
        # Hosea
        (11, 23, 5, 19, 15, 11, 16, 14, 17, 15, 12, 14, 16, 9),
        # Joel
        (20, 32, 21),
        # Amos
        (15, 16, 15, 13, 27, 14, 17, 14, 15),
        # Obadiah
        (21,),
        # Jonah
        (17, 10, 10, 11),
        # Micah
        (16, 13, 12, 13, 15, 16, 20),
        # Nahum
        (15, 13, 19),
        # Habakkuk
        (17, 20, 19),
        # Zephaniah
        (18, 15, 20),
        # Haggai
        (15, 23),
        # Zechariah
        (21, 13, 10, 14, 11, 15, 14, 23, 17, 12, 17, 14, 9, 21),
        # Malachi
        (14, 17, 18, 6),
        # -----------------------------------------------------------------
        # Matthew
        (25, 23, 17, 25, 48, 34, 29, 34, 38, 42, 30, 50, 58, 36, 39, 28, 27,
            35, 30, 34, 46, 46, 39, 51, 46, 75, 66, 20),
        # Mark
        (45, 28, 35, 41, 43, 56, 37, 38, 50, 52, 33, 44, 37, 72, 47, 20),
        # Luke
        (80, 52, 38, 44, 39, 49, 50, 56, 62, 42, 54, 59, 35, 35, 32, 31, 37,
            43, 48, 47, 38, 71, 56, 53),
        # John
        (51, 25, 36, 54, 47, 71, 53, 59, 41, 42, 57, 50, 38, 31, 27, 33, 26,
            40, 42, 31, 25),
        # Acts
        (26, 47, 26, 37, 42, 15, 60, 40, 43, 48, 30, 25, 52, 28, 41, 40, 34,
            28, 41, 38, 40, 30, 35, 27, 27, 32, 44, 31),
        # Romans
        (32, 29, 31, 25, 21, 23, 25, 39, 33, 21, 36, 21, 14, 23, 33, 27),
        # I Corinthians
        (31, 16, 23, 21, 13, 20, 40, 13, 27, 33, 34, 31, 13, 40, 58, 24),
        # II Corinthians
        (24, 17, 18, 18, 21, 18, 16, 24, 15, 18, 33, 21, 14),
        # Galatians
        (24, 21, 29, 31, 26, 18),
        # Ephesians
        (23, 22, 21, 32, 33, 24),
        # Philippians
        (30, 30, 21, 23),
        # Colossians
        (29, 23, 25, 18),
        # I Thessalonians
        (10, 20, 13, 18, 28),
        # II Thessalonians
        (12, 17, 18),
        # I Timothy
        (20, 15, 16, 16, 25, 21),
        # II Timothy
        (18, 26, 17, 22),
        # Titus
        (16, 15, 15),
        # Philemon
        (25,),
        # Hebrews
        (14, 18, 19, 16, 14, 20, 28, 13, 28, 39, 40, 29, 25),
        # James
        (27, 26, 18, 17, 20),
        # I Peter
        (25, 25, 22, 19, 14),
        # II Peter
        (21, 22, 18),
        # I John
        (10, 29, 24, 21, 21),
        # II John
        (13,),
        # III John
        (14,),
        # Jude
        (25,),
        # Revelation of John
        (20, 29, 22, 11, 14, 17, 17, 13, 21, 11, 19, 17, 18, 20, 8, 21, 18, 24,
            21, 15, 27, 21)
    )

    _book_offsets = []
    _chapter_offsets = []
    _ref_list = []

    # \b(?P<book>(?:I{1,3}|[1-3])?\s?\w+)
    _ref_regx = re.compile(r'''
        \b(?P<book>(?:I{1,3}|[1-3])?[^\d,-:]+)
        (?:\s*)?
        (?P<chap>\d{0,3})
        (?:\s*:\s*
        (?P<verse>\d{1,3}))?
        ''', re.X | re.IGNORECASE)

    def __init__(self, reference: str = "Genesis 1:1"):
        """Extract reference parts.

        Get the book, chapter, and verse of the reference so it can be
        incremented and decremented.
        """
        # Initialize the class offsets lists on the first instance, so
        # all other instances can use them.
        if not self._book_offsets or not self._chapter_offsets:
            self._build_offsets()

        # Load the reference list if it is empty.
        if not self._ref_list:
            self._load_reflist()

        # Get the total number of chapters.
        self._chapter_count = len(self._chapter_offsets)

        # Get the total number of books.
        self._book_count = len(self._books_tup) - 1

        self._book = 0
        self._chapter = 1
        self._verse = 1

        self._verse_offset = self._get_valid(reference)

    def __str__(self) -> str:
        """Return string representation of this verse."""
        return self.get_text()

    def __repr__(self) -> str:
        """Return a python expression to recreate this instance."""
        return f"{self.__class__.__name__}(reference={self.get_text()})"

    def __hash__(self) -> int:
        """Return a hash of this Verse."""
        return hash(repr(self))

    def __eq__(self, other: 'Verse') -> bool:
        """Return True if both have equal verse offsets."""
        return self._verse_offset == other._verse_offset

    def __ne__(self, other: 'Verse') -> bool:
        """Return True if both have not equal verse offsets."""
        return self._verse_offset != other._verse_offset

    def __lt__(self, other: 'Verse') -> bool:
        """Return True if the verse offset is less than that of other."""
        return self._verse_offset < other._verse_offset

    def __gt__(self, other: 'Verse') -> bool:
        """Return True if the verse offset is greater than that of other."""
        return self._verse_offset > other._verse_offset

    def __ge__(self, other: 'Verse') -> bool:
        """Return true if self is greater than or equal to other."""
        return self._verse_offset >= other._verse_offset

    def __le__(self, other: 'Verse') -> bool:
        """Return True when self is less than or equal to other."""
        return self._verse_offset <= other._verse_offset

    def __int__(self) -> int:
        """Return the verse offset."""
        return self._verse_offset

    def __add__(self, other: Union['Verse', int]) -> 'Verse':
        """Return the sum of the verse_offset and other."""
        verse_offset = self._verse_offset + int(other)

        if verse_offset >= self._chapter_offsets[-1]:
            verse_offset = self._chapter_offsets[-1] - 1

        return Verse(self._ref_list[verse_offset])

    def __iadd__(self, other: Union['Verse', int]) -> 'Verse':
        """Add other to the verse offset if it is an int."""
        self = self + other
        return self

    def __sub__(self, other: Union['Verse', int]) -> 'Verse':
        """Return the difference of the verse offset and other."""
        verse_offset = self._verse_offset - int(other)
        verse_ref = self._ref_list[0 if verse_offset < 0 else verse_offset]
        return Verse(verse_ref)

    def __isub__(self, other: Union['Verse', int]) -> 'Verse':
        """Subtract other from self."""
        self = self - other
        return self

    def __mul__(self, other: Union['Verse', int]) -> 'Verse':
        """Return the product of the verse offset and other."""
        verse_offset = self._verse_offset * int(other)

        if verse_offset >= self._chapter_offsets[-1]:
            verse_offset = self._chapter_offsets[-1] - 1

        return Verse(self._ref_list[verse_offset])

    def __imul__(self, other: Union['Verse', int]) -> 'Verse':
        """Multiply other to the verse offset."""
        self = self * other
        return self

    def __floordiv__(self, other: Union['Verse', int]) -> 'Verse':
        """Return the quotient of the verse offset and other."""
        verse_offset = self._verse_offset // int(other)
        verse_ref = self._ref_list[0 if verse_offset < 0 else verse_offset]
        return Verse(verse_ref)
    __truediv__ = __floordiv__

    def __ifloordiv__(self, other: Union['Verse', int]) -> 'Verse':
        """Divide the verse offset by other."""
        self = self // other
        return self
    __itruediv__ = __ifloordiv__

    def _get_valid(self, reference: str, default: str = "Genesis 1:1") -> int:
        """Return the verse offset of a valid verse."""
        match = self._ref_regx.search(reference)

        # Return the default reference if this one doesn't look like
        # one.
        if not match:
            reference = default
            match = self._ref_regx.search(reference)

        if match:
            book, chapter, verse = match.groups()
        else:
            book, chapter, verse = 'Genesis', 1, 1

        # Make the chapter and verse default to 1.
        chapter = int(chapter or 1)
        verse = int(verse or 1)
        book = book.strip()

        book_index = self._get_book_index(book)

        if reference in self._ref_list:
            self._book = book_index
            self._chapter = chapter
            self._verse = verse
            return self._ref_list.index(reference)

        book_index, chapter, verse = self._abs_verse(book_index, chapter,
                                                     verse)
        self._book = book_index
        self._chapter = chapter
        self._verse = verse

        # ref = "%s %s:%s" % (self._books_tup[book_index][0], chapter, verse)

        verse_offset = self._get_verse_offset(book_index, chapter, verse)

        return verse_offset

    def _get_book_index(self, book: str) -> int:
        """Get the index in the Bible of the book."""
        name_list = []
        book = book.lower()
        for index, (name, abv1, abv2, _) in enumerate(self._books_tup):
            name = name.lower()
            abv1 = abv1.lower()
            abv2 = abv2.lower()
            name_list.extend((name, abv1, abv2))
            if book in (name, abv1, abv2):
                return index
            elif (name.startswith(book) or abv1.startswith(book) or
                  abv2.startswith(book)):
                return index

        match_list = get_close_matches(book, name_list, cutoff=0.6)
        if match_list:
            return name_list.index(match_list[0]) // 3

        # Default to Genesis
        return 0

    def _abs_chapter(self, book_index: int, chapter: int) -> tuple[int, int]:
        """Get the absolute location of the chapter.

        Returns the absolute location in the Bible of the chapter, based on the
        book_index.
        """
        while chapter <= 0:
            book_index -= 1
            if book_index >= 0:
                chapter += self._books_tup[book_index][-1]
            else:
                return 0, 1

        book_num, chapter_list = 0, []
        for (book_num,
             chapter_list) in enumerate(self._verse_count[book_index:]):
            if chapter <= len(chapter_list):
                break
            if book_index + book_num >= self._book_count:
                return self._book_count, self._books_tup[-1][-1]
            chapter -= len(chapter_list)

        if chapter > len(chapter_list):
            chapter = len(chapter_list)

        book_index = book_index + book_num

        return book_index, chapter

    def _abs_verse(self, book_index: int, chapter: int,
                   verse: int) -> tuple[int, int, int]:
        """Get absolute reference.

        Calculate the absolute reference given a book index, chapter, and
        verse.
        """
        # First make sure the book and chapters are valid.
        book_index, chapter = self._abs_chapter(book_index, chapter)

        # Make sure the verse and chapter are positive.
        while verse <= 0 or chapter <= 0:
            # Stop if the book and chapter reach the start of the Bible.
            if book_index == 0 and chapter == 1:
                verse = 1
                break

            # If the verse is still negative, then the valid verse is
            # atleast before this chapter.
            chapter -= 1

            # Only try to increment the verse if the chapter is
            # positive.
            if chapter > 0:
                verse += self._verse_count[book_index][chapter - 1]

            # After every verse change, make the chapter and book valid
            # again.
            book_index, chapter = self._abs_chapter(book_index, chapter)

        verse_count = self._verse_count[book_index][chapter - 1]

        # Loop until the verse is valid.
        while verse > verse_count:
            # If the book_index and chapter exceed the maximum, then the
            # end of the Bible is reached so stop.
            if book_index >= self._book_count:
                if chapter >= self._books_tup[book_index][-1]:
                    break

            # Decrement the verse by the number of verses in the current
            # chapter.
            verse -= verse_count

            # Make sure the book and chapter are valid.
            book_index, chapter = self._abs_chapter(book_index, chapter + 1)

            # Get the number of verses in this chapter.
            verse_count = self._verse_count[book_index][chapter - 1]

        # If the verse still exceeds the maximum then it has to be the
        # last verse of the Bible.
        if verse > verse_count:
            verse = verse_count

        return book_index, chapter, verse

    def _get_verse_offset(self, book: int, chapter: int, verse: int) -> int:
        """Get verse offset from the start of the Bible."""
        chapter_offset = ((self._book_offsets[book] - 1) + chapter)

        if chapter_offset >= self._chapter_count:
            chapter_offset = self._chapter_count - 2
        if chapter_offset < 0:
            chapter_offset = 0

        verse_offset = self._chapter_offsets[chapter_offset] + verse - 1

        if verse_offset >= self._chapter_offsets[-1]:
            verse_offset = self._chapter_offsets[-1] - 1

        return verse_offset

    @classmethod
    def _build_offsets(cls):
        """Build the book and chapter offsets lists.

        The book offsets are the number of chapters before that book, and the
        chapter offsets are the number of verses before that chapter.
        """
        # Modify the class variables, so this is only run once and they
        # will be used by all instances of this class.
        cls._book_offsets.append(0)
        cls._chapter_offsets.append(0)

        for book in cls._verse_count:
            cls._book_offsets.append(cls._book_offsets[-1] + len(book))
            for chapter in book:
                cls._chapter_offsets.append(cls._chapter_offsets[-1] + chapter)

    @classmethod
    def _load_reflist(cls):
        """Load the reference list."""
        filename = os_join(data_path, 'ref_list.json.gz')
        with gzip.open(filename, 'rb') as reflist:
            cls._ref_list = json.loads(reflist.read().decode())

    def copy(self) -> 'Verse':
        """Return a unique copy of self."""
        return Verse(str(self))

    def get_text(self) -> str:
        """Return a string representation of the verse."""
        return self._ref_list[self._verse_offset]

    def get_max_verse(self) -> 'Verse':
        """Return a Verse object of the last verse in the chapter."""
        max_verse = self._verse_count[self._book][self._chapter - 1]
        book_name = self._books_tup[self._book][0]
        reference = f"{book_name} {self._chapter}:{max_verse}"

        return Verse(reference)

    def get_max_chapter(self) -> 'Verse':
        """Return a Verse object of the last chapter of the book."""
        max_chapter = self._books_tup[self._book][-1]
        book_name = self._books_tup[self._book][0]
        reference = f"{book_name} {max_chapter}:1"
        return Verse(reference)

    def get_book_name(self) -> str:
        """Return the book name as a string."""
        return self._books_tup[self._book][0]

    def get_chapter_number(self) -> int:
        """Return the number."""
        return self._chapter

    def get_verse_number(self) -> int:
        """Return the verse number."""
        return self._verse


class VerseRange(object):
    """A verse range object."""

    _ref_regx = re.compile(r'''
        \b(?P<book>(?:I{1,3}|[1-3])?[^\d,-:]+)
        (?:\s*)?
        (?P<chap>\d{0,3})
        (?:\s*:\s*
        (?P<verse>\d{1,3}))?
        (?:\s*-\s*
        (?P<end_book>(?:I{1,3}|[1-3])?[^\d,-:]+)?
        (?P<end_chap>\d{1,3}(?=\s*:\s*))?
        (?:\s*:\s*)?
        (?P<end_verse>\d{1,3})?)?
        ''', re.X | re.IGNORECASE)

    def __init__(self, start: str = "Genesis 1:1",
                 end: str = "Revelation 22:21"):
        """Create a range of verses."""
        self._lower = start if type(start) is Verse else Verse(str(start))
        self._upper = end if type(end) is Verse else Verse(str(end))

        if self._lower > self._upper:
            self._upper = self._lower.copy()

    @property
    def upper(self) -> Verse:
        """Get the upper verse in the range."""
        return self._upper

    @property
    def lower(self) -> Verse:
        """Get the lower verse in the range."""
        return self._lower

    def __str__(self) -> str:
        """Return string representation of this verse."""
        return f"{self._lower}-{self._upper}"

    def __repr__(self) -> str:
        """Return a python expression to recreate this instance."""
        return (f"{self.__class__.__name__}(start={self._lower}, "
                f"end={self._upper})")

    def __contains__(self, item: Verse) -> bool:
        """Return True if item is in the range."""
        return self._lower <= item and item <= self._upper

    def __iter__(self) -> Generator[Verse, None, None]:
        """Create a Generator over all the verses in the range."""
        temp = self._lower.copy()
        while temp < self._upper:
            yield temp
            temp += 1
        yield temp

    def __len__(self) -> int:
        """Return the length of the range."""
        return int(self._upper) - int(self._lower) + 1

    def __getitem__(self, key: int) -> Union['VerseRange', Verse]:
        """Return the key'th verse in the range."""
        if type(key) is slice:
            start = key.start if key.start else 0
            stop = key.stop if key.stop else 0
            if abs(start + stop) > len(self):
                return self
            if start >= 0:
                lower = self._lower + start
            else:
                lower = self._upper + start + 1
            if stop >= 0:
                upper = self._lower + stop
            else:
                upper = self._upper + stop + 1
            return VerseRange(str(lower), str(upper))
        else:
            if key >= len(self):
                raise(IndexError(f"Index out of range: {key}"))
            if key >= 0:
                return self._lower + key
            else:
                return self._upper + key + 1

    def index(self, item: Verse) -> int:
        """Return the index of item."""
        if item in self:
            return int(item - self._lower)
        else:
            raise(ValueError(f"{item} not in range"))

    def expand(self) -> set:
        """Get a set of all verse references in the range.

        Expands this range into a set containing all the verse references in
        this range.
        """
        return {str(i) for i in self}

    @classmethod
    def parse_range(cls, ref_str: str, default_book: str = 'Genesis',
                    default_chapter: int = 1
                    ) -> set[Union[Verse, "VerseRange"]]:
        """Parse a range string into a set of verses."""
        ref_list = cls._ref_regx.findall(ref_str)

        if not ref_list:
            if ':' in ref_str:
                ref_str = f'{default_book} {ref_str}'
            else:
                ref_str = f'{default_book} {default_chapter}:{ref_str}'
            ref_list = cls._ref_regx.findall(ref_str)

        ref_set = set()
        for (start_book, start_chapter, start_verse, end_book, end_chapter,
             end_verse) in ref_list:
            first_verse = Verse(f'{start_book} {start_chapter}:{start_verse}')

            if not start_verse and not end_chapter:
                # This covers cases with references such as Gen1-4.
                if end_verse:
                    # If end_book is None the range is in the same book.
                    if not end_book:
                        end_book = start_book

                    # The end_verse is actually the end_chapter
                    end_chapter = end_verse

                    # Include the entire chapter.
                    tmp_verse = Verse(f'{end_book} {end_chapter}:1')
                    end_verse = tmp_verse.get_max_verse()._verse

                elif end_book == start_book or not end_book:
                    # end_book is None so the range is in the start_book.
                    end_book = start_book

                    if start_chapter:
                        # This covers cases with references such as Gen1.  It
                        # returns the entire chapter.
                        end_chapter = start_chapter
                        end_verse = first_verse.get_max_verse()._verse
                    else:
                        # This coverse ranges such as gen.  It returns the
                        # entire book.
                        tmp_verse = first_verse.get_max_chapter()
                        end_chapter = tmp_verse._chapter
                        end_verse = tmp_verse.get_max_verse()._verse

            if start_verse and not end_chapter:
                if end_verse and not end_book:
                    # A range like Gen3:4-10
                    end_book = start_book
                    end_chapter = start_chapter
                elif end_verse:
                    # A range like Gen 3:4-John5'
                    end_chapter = end_verse
                    tmp_verse = Verse(f'{end_book} {end_chapter}:1')
                    end_verse = tmp_verse.get_max_verse()._verse

            # The end verse is in the same book as the start.
            if not end_book:
                end_book = start_book

            last_verse = Verse(f'{end_book} {end_chapter}:{end_verse}')

            if last_verse > first_verse:
                ref_set.add(VerseRange(str(first_verse), str(last_verse)))
            else:
                ref_set.add(first_verse)

        return ref_set

    def get_refs_list(self) -> list[str]:
        """Return a list of all the references in the range."""
        return Verse._ref_list[int(self._lower): int(self._upper) + 1]

    # args: verse_list, default_key, expand_range, chapter_as_verse?
    def parse_verse_list(self, verse_list: list, default_key: int,
                         expand_range: bool,
                         chapter_as_verse: bool) -> 'VerseRange':
        """Try to do what the Sword VerseKey.ParseVerseList does."""
        return self

    def getRangeText(self) -> str:
        """Return the range text."""
        return str(self)


VerseKey = VerseRange


class VerseIter(object):
    """Iterator of verse references."""

    def __init__(self, start: str, end: str = 'Revelation of John 22:21'):
        """Create an iter over the range(strt, end)."""
        # Make sure the range is in order.
        start_verse, end_verse = sorted([Verse(start), Verse(end)])
        self._verse_iter = iter(VerseRange(str(start_verse), str(end_verse)))

        self._verse_ref = ''

    def __next__(self) -> str:
        """Return the next verse reference."""
        # Return only the reference.
        return str(next(self._verse_iter))

    def __iter__(self) -> 'VerseIter':
        """Return an iterator of self."""
        return self

    def next(self) -> str:
        """Return the next verse reference."""
        return self.__next__()


class ChapterIter(VerseIter):
    """Iterates over just one chapter."""

    def __init__(self, book: str = 'Genesis', chapter: int = 1):
        """Crate iterator over all the verses in a chapter."""
        start = Verse(f"{book} {chapter}:1")
        end = start.get_max_verse()

        super(ChapterIter, self).__init__(start.get_text(), end.get_text())


class BookIter(VerseIter):
    """Iterates over just one book."""

    def __init__(self, book='Genesis'):
        """Create iterator over an entire book."""
        start = Verse(f"{book} 1:1")
        end = start.get_max_chapter().get_max_verse()

        super(BookIter, self).__init__(start.get_text(), end.get_text())


class Lookup(object):
    """A generic object to lookup refrences in differend sword modules."""

    def __init__(self, module_name: str = 'KJV', markup: int = 0):
        """Open database to lookup information in."""
        self._dbm_dict = DbmDict(module_name, INDEX_PATH)

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

    def get_text(self, key: str) -> str:
        """Get the text at the given key in the module.

        i.e. get_text('3778') returns the greek strongs.
        """
        item_text = self._dbm_dict[key]
        if not item_text:
            return ''
        return fill(item_text, screen_size()[1])

    def get_raw_text(self, key: str) -> str:
        """Get the text at the given key in the module.

        i.e. get_raw_text('3778') returns the greek strongs.
        """
        item_text = self._dbm_dict[key]
        if not item_text:
            return ''
        return item_text

    def get_formatted_text(self, key: str) -> str:
        """Return the formated raw text of the specified key."""
        text = self._dbm_dict[key]
        if not text:
            return ''

        # Format and highlight the text.
        text = self._bold_regx.sub('\033[1m\\1\033[m', text)
        text = self._italic_regx.sub('\033[36m\\1\033[m', text)
        text = self._br_regx.sub('\n', text)
        text = self._bracket_regx.sub('[\\1\033[33m\\2\033[m\\3]', text)
        text = self._brace_regx.sub('{\\1\033[35m\\2\033[m\\3}', text)
        text = self._parenthesis_regx.sub('(\\1\033[32m\\2\033[m\\3)', text)
        text = self._verse_ref_regx.sub('\033[32m\\1\033[m', text)
        text = self._cleanup_regx.sub('', text)

        return text


class VerseTextIter(object):
    """A verse text itorator.

    An iterable object for accessing verses in the Bible.  Maybe it will be
    easier maybe not.
    """

    def __init__(self, reference_iter: Iterator[str], strongs: bool = False,
                 morph: bool = False, module: str = 'KJV', markup: int = 0,
                 render: str = ''):
        """Initialize."""
        self._module = Lookup(module)

        if render.lower() == 'raw':
            self._render_func = self._module.get_raw_text
        elif render.lower() == 'render_raw':
            self._fix_space_regx = re.compile(r'([^\.:\?!])\s+')
            self._fix_end_regx = re.compile(r'\s+([\.:\?!,;])')
            self._fix_start_tag_regx = re.compile(r'(<[npi]>)\s*')
            self._fix_end_tag_regx = re.compile(r'\s*(</[npi]>)')
            self._upper_divname_regx = re.compile(r'(\w+)([\'s]*)')
            self._render_func = \
                lambda ref: self._parse_raw(self._module.get_raw_text(ref),
                                            strongs, morph)
        else:
            self._render_func = self._module.get_text

        self._ref_iter = reference_iter

    def next(self) -> tuple[str, str]:
        """Return the next verse reference and text."""
        return self.__next__()

    def __next__(self) -> tuple[str, str]:
        """Return a tuple of the next verse reference and text."""
        # Retrieve the next reference.
        verse_ref = next(self._ref_iter)

        # Set the verse and render the text.
        verse_text = self._get_text(verse_ref)

        return (verse_ref, verse_text)

    def __iter__(self) -> 'VerseTextIter':
        """Return an iterator of self."""
        return self

    def _get_text(self, verse_ref: str) -> str:
        """Return the verse text.

        Override this to produce formatted verse text.
        """
        verse_text = self._render_func(verse_ref)

        return verse_text

    def _parse_xml(self, xml_dom: Any, strongs: bool = False,
                   morph: bool = False) -> str:
        """Build verse text from xml.

        Recursively parse all the childNodes in a xml minidom, and build the
        verse text.
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
                verse_text += \
                    ' %s' % self._upper_divname_regx.sub(
                        lambda m: m.group(1).upper() + m.group(2),
                        child_s)
            else:
                verse_text += ' %s' % child_s

        if xml_dom.attributes:
            return italic_str % note_str % "%s%s%s" % (verse_text, strongs_str,
                                                       morph_str)
        if hasattr(xml_dom, 'data'):
            info_print(xml_dom.data, tag=4)
            return xml_dom.data
        return verse_text.strip()

    def _parse_raw(self, raw_text: str, strongs: bool = False,
                   morph: bool = False) -> str:
        """Parse raw verse text and return a formated version."""
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
    """Raw verse.

    Parse raw verse text into a dictionary so it can easly be found out how
    words are translated and how Strong's numbers are used.
    """

    def __init__(self, reference_iter: Iterator[str], module: str = 'KJV'):
        """Initialize the sword module."""
        self._module = Lookup(module)

        self._ref_iter = reference_iter

        self._fix_space_regx = re.compile(r'([^\.:\?!])\s+')
        self._fix_end_regx = re.compile(r'\s+([\.:\?!,;])')
        self._remove_tag_regx = re.compile(r'(<i>\s?|\s?</i>)')
        self._fix_start_tag_regx = re.compile(r'(<i>)\s*')
        self._fix_end_tag_regx = re.compile(r'\s*(</i>)')

    def next(self) -> tuple[str, tuple[str, dict]]:
        """Return the next verse reference and text."""
        return self.__next__()

    def __next__(self) -> tuple[str, tuple[str, dict]]:
        """Return a tuple of the next verse reference and text."""
        # Retrieve the next reference.
        verse_ref = next(self._ref_iter)

        # Set the verse and render the text.
        verse_dict = self.get_dict(verse_ref)

        return (verse_ref, verse_dict)

    def __iter__(self) -> 'RawDict':
        """Return an iterator of self."""
        return self

    def get_dict(self, verse_reference: str) -> tuple[str, dict]:
        """Get a dictionary from verse_reference.

        Lookup the verse reference in the sword module specified and return a
        dictionary from it.
        """
        raw_text = self._module.get_raw_text(verse_reference)

        return self._get_parsed_dict(raw_text, True, True)

    def _raw_to_dict(self, xml_dom: Any, strongs: bool = False,
                     morph: bool = False) -> tuple[str, dict]:
        """Parse xml.

        Recursively parse all the childNodes in a xml minidom, and build a
        dictionary to use for telling what strongs numbers go to what words and
        vise versa.
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
                verse_text += f" {child_s.upper()}"
            else:
                verse_text += f" {child_s}"
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
                            strongs_str += f" <{num}> "
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
                            morph_str += f" {{{tag}}} "
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
                verse_dict[f"_{attr_dict['xmlns']}"].append(verse_text)

            # Build up the verse string.
            temp_str = f"{verse_text}{strongs_str}{morph_str}"
            verse_text = italic_str % temp_str
        if hasattr(xml_dom, 'data'):
            return xml_dom.data, verse_dict

        return verse_text, verse_dict

    def _get_parsed_dict(self, raw_text: str, strongs: bool = False,
                         morph: bool = False) -> tuple[str, dict]:
        """Parse raw verse text and return a formated version."""
        info_print(raw_text, tag=31)

        # A hack to make the raw text parse as xml.
        xml_text = f'''<?xml version="1.0"?>
        <root xmlns="{'verse_text'}">
        {raw_text}
        </root>'''

        # It works now we can parse the xml dom.
        try:
            parsed_xml = parseString(xml_text)
            return self._raw_to_dict(parsed_xml, strongs, morph)
        except Exception as err:
            info_print(f"Error {err} while processing {raw_text}.\n", tag=31)
            return raw_text, {'_verse_text': [raw_text],
                              '_words': [defaultdict(list)]}


class IndexBible(object):
    """Index the bible by Strong's Numbers, Morphological Tags, and words."""

    def __init__(self, module: str = 'KJV', path: str = ''):
        """Initialize the index dicts."""
        self._module_name = module
        self._path = path if path else INDEX_PATH

        # Remove morphological and strongs information.
        self._cleanup_regx = re.compile(r'\s*(<([GH]\d*)>|\{([A-Z\d-]*)\})')
        # Note removal regular expression.
        self._remove_notes_regex = re.compile(r'\s?<n>\s?(.*?)\s?</n>', re.S)
        self._remove_tags_regex = re.compile(r'<[/]?[pin]>')

        self._non_alnum_regx = re.compile(r'\W')
        self._fix_regx = re.compile(r'\s\s+')
        self._strongs_regx = re.compile(r'\s<([GH]\d+)>', re.I)
        self._morph_regx = re.compile(r'\s\{([\w-]+)\}', re.I)

        self._module_dict = defaultdict(list)
        # lower_case is used to store lower_case words case sensitive
        # counterpart.  _Words_ is for easy key lookup for partial words.
        self._words_set = set()
        self._strongs_set = set()
        self._morph_set = set()
        self._module_dict.update({'lower_case': defaultdict(list)})

        self._index_dict = {f"{self._module_name}_index_i": self._module_dict}

        self._index_built = False

    def _index_strongs(self, verse_ref: str, verse_text: str):
        """Update the modules strongs dictionary from the verse text."""
        strongs_list = set(self._strongs_regx.findall(verse_text))
        for strongs_num in strongs_list:
            self._strongs_set.add(strongs_num)
            self._module_dict[strongs_num].append(verse_ref)

    def _index_morph(self, verse_ref: str, verse_text: str):
        """Update the modules mophological dictionary from the verse text."""
        morph_list = set(self._morph_regx.findall(verse_text))
        for morph_num in morph_list:
            self._morph_set.add(morph_num)
            self._module_dict[morph_num].append(verse_ref)

    def _index_words(self, verse_ref: str, verse_text: str):
        """Update the modules word dictionary from the verse text."""
        # Remove all the morphological and strongs stuff.
        clean_text = self._cleanup_regx.sub(' ', verse_text)
        # Remove any non-alpha-numeric stuff.
        clean_text = self._non_alnum_regx.sub(' ', clean_text)
        # Replace runs of one or more spaces with just a single space.
        clean_text = self._fix_regx.sub(' ', clean_text).strip()

        # Remove the strongs and morphological stuff in such a way that
        # split words are still split (i.e. where in, instead of wherein).
        # So there are split versions and non-split versions just to be sure
        # that the correct one is in there.
        verse_text = self._strongs_regx.sub(' ', verse_text)
        verse_text = self._morph_regx.sub(' ', verse_text)

        # Strip out all unicode so we can search correctly.
        verse_text_b = verse_text.encode('ascii', 'ignore')
        verse_text = verse_text_b.decode('ascii', 'ignore')
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

    def _index_book(self, book_name: str = "Genesis"):
        """Create indexes for strongs, morphology and words."""
        book_iter = BookIter(book_name)
        verse_iter = VerseTextIter(book_iter, True, True, self._module_name,
                                   render='render_raw')

        for verse_ref, verse_text in verse_iter:
            info_print(f"\033[{len(verse_ref) + 20}D\033[KIndexing..."
                       f"{verse_ref}", end='')

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
        """Create index.

        Create index files of the bible for strongs numbers, morphological
        tags, and case (in)sensitive words.
        """
        info_print(f"Indexing {self._module_name} could take a while...")
        try:
            for book in book_gen():
                self._index_book(book)
        except Exception:
            pass
        self._module_dict['_words_'].extend(self._words_set)
        self._module_dict['_strongs_'].extend(self._strongs_set)
        self._module_dict['_morph_'].extend(self._morph_set)

        info_print("\nDone.")

        self._index_built = True

    def write_index(self):
        """Write the index to disk.

        Write all the index dictionaries to their respective files.  If Any of
        the dictionaries is empty, then build the index.

        The indexes are just json-ed dictionaries.  The keys are the indexed
        items and the values are the verse references that contain the key.
        """
        if not self._index_built:
            self.build_index()
        # Build the index if it's not already built.
        for name, dic in self._index_dict.items():
            info_print(f"Writing {name}.dbm...")
            # Save as just a plain text file.  Has to be loaded all at once,
            # so it is really slow.
        #     with open(name, 'w') as index_file:
        #         json.dump(dic, index_file, indent=4)
        # return
            # Save a dbm database that we can access without loading it all
            # into memeory so it is fast.
            dbm_name = f"{self._path}/{name}.dbm"
            with IndexDbm(dbm_name, 'nf') as index_file:
                # with open(name, 'r') as i_file:
                #     dic =json.load(i_file)
                index_file.update(dic)


def parse_verse_range(verse_list: Union[list, str]) -> set[str]:
    """Return a set of verse references.

    Return a set of all the verses in the ranges represented by verse_list.
    """
    if not verse_list:
        return set()

    # Make the argument a list.
    if isinstance(verse_list, str):
        verse_list = verse_list.split(',')

    verse_set = set()
    book = 'Genesis'
    chapter = 1

    for verse_str in verse_list:
        verse_range = VerseRange.parse_range(verse_str, default_book=book,
                                             default_chapter=chapter)
        for i in verse_range:
            if type(i) is VerseRange:
                verse_set.update(i.get_refs_list())
                last_verse = i.upper
            else:
                verse_set.add(str(i))
                last_verse = i
            book = last_verse.get_book_name()
            chapter = last_verse.get_chapter_number()

    return verse_set


def add_context(ref_set: set[str], count: int = 0,
                chapter: bool = False) -> set[str]:
    """Add context refereneces to ref_st.

    Add count number of verses before and after reference and return a set of
    those references.
    """
    if count == 0 and not chapter:
        return ref_set

    # Make the argument a parseable string.
    reference = ','.join(ref_set)

    verse_set = VerseRange.parse_range(reference)
    return_set = set()
    for i in verse_set:
        return_set.update(str(j) for j in VerseRange(i - count, i + count))

    if chapter:
        for i in verse_set:
            chap_ref = f'{i.get_book_name()} {i._chapter}'
            return_set.update(parse_verse_range(chap_ref))

    return return_set


def book_gen() -> Generator[str, None, None]:
    """Create a Generator function that yields book names in order."""
    for book in Verse._books_tup:
        yield book[0]


book_list = list(book_gen())


# Key function used to sort a list of verse references.
def sort_key(ref):
    """Sort verses by book."""
    try:
        book, chap_verse = ref.rsplit(' ', 1)
        chap, verse = chap_verse.split(':')
        val = f"{int(book_list.index(book)):02}{int(chap):03}{int(verse):03}"
        return val
    except Exception as err:
        print(f"Error sorting \"{ref}\": {err}", file=sys.stderr)
        sys.exit()
