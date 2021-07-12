#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pysymbolscanner
  Copyright 2019 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import re
from setuptools import setup, find_packages

EXCLUDE_FROM_PACKAGES = ['test', 'test.*', 'test*']

VERSION = '0.0.0'

with open("README.md", "r") as fh:
    long_description = fh.read()

INSTALL_REQUIRES = [
    'PyYAML==5.4.1',
    'wptools==0.4.17',
    'wikipedia==1.4.0',
    'pandas==1.2.4',
    'pycountry==20.7.3',
    'Unidecode==1.2.0',
    'uplink==0.9.4',
    'pytickersymbols>=1.6.0',
    'toolz==0.11.1'
]

with open('src/pysymbolscanner/__init__.py', 'r') as fd:
    VERSION = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

setup(
    name="pysymbolscanner",
    version=VERSION,
    author="Slash Gordon",
    author_email="slash.gordon.dev@gmail.com",
    py_modules=['pysymbolscanner'],
    package_dir={'': 'src'},
    description='The lib scans wiki pages and'
    ' updates symbol source of pytickersymbols',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/portfolioplus/pysymbolscanner",
    packages=find_packages('src', exclude=EXCLUDE_FROM_PACKAGES),
    install_requires=INSTALL_REQUIRES,
    entry_points={'console_scripts': [
            'pysymbolscanner = pysymbolscanner.command_line:symbolscanner_app',
    ]},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial :: Investment',
    ],
)
