#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pysymbolscanner
  Copyright 2020 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import unittest

from pysymbolscanner.yahoo import YahooSearch


class TestYahooSearch(unittest.TestCase):
    def test_yahoo_search(self):
        """
        Test the yahoo search
        :return:
        """
        search = YahooSearch()
        result = search.get_symbols('INDUS Holding Aktiengesellschaft')
        self.assertTrue(result)
        result2 = search.get_symbols('Borussia Dortmund GmbH & Co. KGaA')
        self.assertTrue(result2)


if __name__ == "__main__":
    unittest.main()
