#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pysymbolscanner
  Copyright 2020 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import unittest

from pysymbolscanner.utils import filter_duplicate_dicts_in_list
from pysymbolscanner.utils import is_isin, is_not_isin

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

    def test_is_isin(self):
        self.assertTrue(is_isin('US0378331005'))
        self.assertTrue(is_isin('DE0378331005.F'))
        self.assertTrue(is_isin('US2042803096'))
        self.assertTrue(is_isin('US2042803096.F'))
        self.assertFalse(is_isin('US037833100'))
        self.assertFalse(is_isin('U10378331001'))

    def test_is_not_isin(self):
        self.assertFalse(is_not_isin('US0378331005'))
        self.assertTrue(is_not_isin('US037833100'))
        self.assertTrue(is_not_isin('U10378331001'))


if __name__ == "__main__":
    unittest.main()
