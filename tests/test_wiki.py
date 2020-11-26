#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" symbol_Scanner
  Copyright 2020 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import unittest

from pytickersymbols import PyTickerSymbols
from symbol_scanner.wiki import get_infobox_items

class TestWiki(unittest.TestCase):

    def test_infobox(self):
        """
        Test wiki infobox
        :return:
        """
        items_google = get_infobox_items('google')
        self.assertEqual(len(items_google), 5)
        items_bmw = get_infobox_items('BMW')
        self.assertEqual(len(items_bmw), 5)
        items_basf = get_infobox_items('BASF')
        self.assertEqual(len(items_basf), 5)


if __name__ == "__main__":
    unittest.main()