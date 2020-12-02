#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pysymbolscanner
  Copyright 2020 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import logging

import argparse
from pytickersymbols import PyTickerSymbols
from pysymbolscanner.scanner import SymbolScanner
from pysymbolscanner.word_score import get_word_list_diff

logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

__VERSION__ = "1.0.0"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='SymbolScanner CLI'
    )
    parser.add_argument('--cache', action="store_true", default=False)
    args = parser.parse_args()
    scanner = SymbolScanner(args.cache)
    stock_data = PyTickerSymbols()
    indices = stock_data.get_all_indices()
    # missing stocks in index
    for index in indices:
        stocks = stock_data.get_stocks_by_index(index)
        py_stocks = list(map(lambda x: x['name'], stocks))
        wiki_stocks = [
            wiki_stock.data['short_name'] for wiki_stock in scanner.data[index]
        ]
        missing_stocks = get_word_list_diff(wiki_stocks, py_stocks)
        scanner.log.info(f'-------missing stocks of {index}---------')
        for stock in missing_stocks:
            scanner.log.info(stock)
        scanner.log.info(f'-------wrong stocks of {index}---------')
        old_stocks = get_word_list_diff(py_stocks, wiki_stocks)
        for stock in old_stocks:
            scanner.log.info(stock)
