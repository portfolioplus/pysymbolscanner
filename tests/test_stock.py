#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pysymbolscanner
  Copyright 2020 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import unittest
from pysymbolscanner.stock import Stock


class TestStock(unittest.TestCase):

    def test_get_symbol(self):
        symbols = [
            'lse|ULVR',
            'LSE|ULVR',
            'Euronext|UNA',
            'nyse|UN',
            'nyse|UL',
        ]
        result = Stock.get_symbol(symbols)
        self.assertEqual('UL', result)
