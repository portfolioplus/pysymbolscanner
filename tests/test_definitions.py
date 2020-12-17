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


class TestDefinitions(unittest.TestCase):
    def test_indices_count(self):
        """
        Test if all urls pressent for each index in pytickersymbols
        :return:
        """
        stock_data = PyTickerSymbols()
        indices = stock_data.get_all_indices()
        is_url_list_complete = all(
            map(lambda x: x in Indices.symbol_source_dict, indices)
        )
        self.assertTrue(is_url_list_complete)


if __name__ == "__main__":
    unittest.main()
