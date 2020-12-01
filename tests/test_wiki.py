#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pysymbolscanner
  Copyright 2020 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import unittest

from pytickersymbols import PyTickerSymbols
from pysymbolscanner.wiki import (
    get_infobox_items,
    get_country,
    get_merged_infoboxes,
)


class TestWiki(unittest.TestCase):
    def test_infobox(self):
        """
        Test wiki infobox
        :return:
        """
        items_google = get_infobox_items('Alphabet')
        self.assertEqual(len(items_google), 7)
        items_basf = get_infobox_items('BASF')
        self.assertEqual(len(items_basf), 7)
        items_bmw = get_infobox_items('BMW')
        self.assertEqual(len(items_bmw), 7)

    def test_merged_infoboxes(self):
        """
        Test wiki infobox
        :return:
        """
        items_bmw = get_merged_infoboxes('BMW', ['de', 'en'])
        self.assertEqual(len(items_bmw), 7)

    def test_get_country(self):
        """
        Test country detection
        :return:
        """
        country = get_country('en', None)
        self.assertIsNone(country)
        country = get_country('en', 'Deutschland')
        self.assertIsNone(country)
        country = get_country('en', 'Berlin, Germany')
        self.assertIsNotNone(country)
        self.assertEqual(len(country), 2)
        country, code = country
        self.assertEqual(country, 'Germany')
        self.assertEqual(code, 'DE')
        country = get_country('de', 'Berlin, Deutschland')
        self.assertIsNotNone(country)
        self.assertEqual(len(country), 2)
        country, code = country
        self.assertEqual(country, 'Germany')
        self.assertEqual(code, 'DE')


if __name__ == "__main__":
    unittest.main()