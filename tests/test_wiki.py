#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pysymbolscanner
  Copyright 2020 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import unittest
from unittest import mock
from pysymbolscanner.wiki import (
    get_infobox,
    get_merged_infobox,
    get_wiki_infobox,
)
from pysymbolscanner.infobox import get_country
import json
import os


def create_test_data():
    infobox_dict = {
        'Alphabet': {
            'en': None,
            'de': None,
            'fr': None,
            'es': None,
        },
        'BASF': {
            'en': None,
            'de': None,
            'fr': None,
            'es': None,
        },
        'BMW': {
            'en': None,
            'de': None,
            'fr': None,
            'es': None,
        },
        'CaixaBank': {
            'es': None,
        },
    }
    for page in infobox_dict:
        for lang in infobox_dict[page]:
            infobox = get_wiki_infobox(page, [lang])
            infobox_dict[page][lang] = infobox[0] if infobox else None
    with open('tests/test_data.json', 'w') as fp:
        json.dump(infobox_dict, fp)


def mock_get_wiki_info_box(page, lang_codes=['en', 'de', 'es', 'fr']):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, 'test_data.json')) as json_file:
        data = json.load(json_file)
        if page not in data:
            return None
        wiki_page = data[page]
        for lang in lang_codes:
            if lang in wiki_page:
                return wiki_page[lang], lang
    return None


class TestWiki(unittest.TestCase):

    @mock.patch(
        'pysymbolscanner.wiki.get_wiki_infobox',
        side_effect=mock_get_wiki_info_box,
    )
    def test_infobox(self, mock_func):
        """
        Test wiki infobox
        :return:
        """
        items_google = get_infobox('Alphabet')
        self.assertEqual(items_google.name, 'Alphabet Inc.')
        self.assertEqual(items_google.founded, 2015)
        self.assertEqual(items_google.employees, 127498)
        self.assertEqual(items_google.location, 'United States')
        self.assertEqual(len(items_google.isins), 2)
        self.assertEqual(len(items_google.symbols), 2)
        self.assertIn('Conglomerate', items_google.industry)
        items_basf = get_infobox('BASF')
        self.assertEqual(items_basf.name, 'BASF SE')
        self.assertEqual(items_basf.founded, 1865)
        self.assertEqual(items_basf.employees, 117628)
        self.assertEqual(items_basf.location, 'Germany')
        self.assertEqual(len(items_basf.isins), 0)
        self.assertEqual(len(items_basf.symbols), 1)
        self.assertIn('Chemicals', items_basf.industry)
        items_bmw = get_infobox('BMW')
        self.assertEqual(items_bmw.name, 'Bayerische Motoren Werke AG')
        self.assertEqual(items_bmw.founded, 1916)
        self.assertEqual(items_bmw.employees, 133778)
        self.assertEqual(items_bmw.location, 'Germany')
        self.assertEqual(len(items_bmw.isins), 0)
        self.assertEqual(len(items_bmw.symbols), 1)
        self.assertIn('Automotive', items_bmw.industry)

    @mock.patch(
        'pysymbolscanner.wiki.get_wiki_infobox',
        side_effect=mock_get_wiki_info_box,
    )
    def test_merged_infoboxes(self, mock_func):
        """
        Test wiki infobox
        :return:
        """
        items_caixa = get_merged_infobox('CaixaBank', ['es'])
        self.assertEqual(items_caixa.name, 'CaixaBank, S.A.')
        self.assertEqual(items_caixa.founded, 2011)
        self.assertEqual(items_caixa.employees, 37440)
        self.assertEqual(items_caixa.location, 'Spain')
        self.assertEqual(len(items_caixa.isins), 1)
        items_bmw = get_merged_infobox('BMW', ['de', 'en'])
        self.assertEqual(items_bmw.name, 'Bayerische Motoren Werke AG')
        self.assertEqual(items_bmw.founded, 1916)
        self.assertEqual(items_bmw.employees, 133778)
        self.assertEqual(items_bmw.location, 'Germany')
        self.assertEqual(len(items_bmw.isins), 1)
        self.assertEqual(len(items_bmw.symbols), 1)
        self.assertIn('Automotive', items_bmw.industry)

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
        self.assertEqual(len(country), 3)
        country, code, code2 = country
        self.assertEqual(country, 'Germany')
        self.assertEqual(code, 'DE')
        self.assertEqual(code2, 'DEU')
        country = get_country('de', 'Berlin, Deutschland')
        self.assertIsNotNone(country)
        self.assertEqual(len(country), 3)
        country, code, code2 = country
        self.assertEqual(country, 'Germany')
        self.assertEqual(code, 'DE')
        self.assertEqual(code2, 'DEU')


if __name__ == "__main__":
    unittest.main()
