#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pysymbolscanner
  Copyright 2020 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import unittest

from pytickersymbols import PyTickerSymbols
from pysymbolscanner.index_definitions import Indices
from pysymbolscanner.word_score import get_word_list_diff

class TestWordScore(unittest.TestCase):

    def test_score(self):
        """
        Test score
        :return:
        """
        words_a = ['test ag', 'test co kg', 'test S.E.', 'unknown']
        words_b = ['test', 'test', 'test', 'bibo']
        result = get_word_list_diff(words_a, words_b)
        self.assertEqual(len(result), 1)
        self.assertIn('unknown', result)
        result = get_word_list_diff(words_b, words_a)
        self.assertEqual(len(result), 1)
        self.assertIn('bibo', result)


if __name__ == "__main__":
    unittest.main()