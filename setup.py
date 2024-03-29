#!/usr/bin/env python
# vim: sw=4:ts=4:sts=4:fdm=indent:fdl=0:
# -*- coding: UTF8 -*-
#
# Build biblesearch package.
# Copyright (C) 2012 Josiah Gordon <josiahg@gmail.com>
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


"""Build biblesearch package."""

from distutils.core import setup

# from distutils.command.install import INSTALL_SCHEMES
#
# for scheme in INSTALL_SCHEMES.values():
#     scheme['data'] = scheme['purelib']

setup(
    name='biblesearch',
    packages=['sword_search'],
    package_dir={'sword_search': 'sword_search'},
    package_data={'sword_search': ['data/*.gz']},
    scripts=['scripts/biblesearch'],
    version='1.0.0',
    description='Bible searching module using sword.',
    long_description=open('README.mkd').read(),
    requires=["Sword (>=1.6.2)"],
    author='Josiah Gordon',
    author_email='josiahg@gmail.com',
    url='http://www.github.com/zepto/biblesearch',
    download_url='http://www.github.com/zepto/biblesearch/downloads',
    license='LICENSE.txt',
    keywords=['sword', 'bible', 'search'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development  Status :: 4 - Beta',
        'Environment :: Console Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL3)',
        'Operating System :: Linux',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Bible Searching/Indexing',
    ],
)
