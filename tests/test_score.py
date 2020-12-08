#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pysymbolscanner
  Copyright 2020 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import unittest
from pysymbolscanner.word_score import get_best_match, get_score, get_word_list_diff


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

    def test_word_score(self):
        score = get_score('Telia', 'Tesla')
        self.assertEqual(score, 0.8)
        score = get_score('Tesli', 'Tesla')
        self.assertEqual(score, 0.8)

    def test_best_match(self):
        """
        Test best match scoring
        :return:
        """
        test_value = (
            'test AG',
            [
                'test Aktiengeselschaft',
                'testing AG',
                'the test Aktiengeselschaft',
            ],
        )

        result = get_best_match(*test_value)
        self.assertEqual(result[0], 1)
        result = get_best_match(
            *test_value, word_filter=[' Aktiengeselschaft', ' AG']
        )
        self.assertEqual(result[0], 0)


if __name__ == "__main__":
    unittest.main()
