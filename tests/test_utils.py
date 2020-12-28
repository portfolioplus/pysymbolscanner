#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pysymbolscanner
  Copyright 2020 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import unittest

from pysymbolscanner.utils import filter_duplicate_dicts_in_list


class TestUtils(unittest.TestCase):
    def test_filter_duplicate_dicts_in_list(self):
        """
        Test filter duplicate dicts in list
        :return:
        """
        result = filter_duplicate_dicts_in_list(
            [{'a': 2}, {'a': 2, 'b': 2}, {'a': 3}, {'a': 2}]
        )
        self.assertEqual(len(result), 3)


if __name__ == "__main__":
    unittest.main()
