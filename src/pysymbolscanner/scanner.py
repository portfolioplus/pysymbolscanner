#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pysymbolscanner
  Copyright 2020 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

import logging
import os
import pickle
import sys
import pandas as pd
import multiprocessing
from pysymbolscanner.index_definitions import Indices
from pysymbolscanner.wiki import get_merged_infobox
from pysymbolscanner.stock import Stock
from pysymbolscanner.word_score import get_best_match


class SymbolScanner:
    MAX_PROCESSES = 8
    PICKLE_FILE = 'index_data.pickle'

    def __init__(self, cache):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        self.log = logging.getLogger('symbol scanner')
        self.data = None
        self.cache = cache

    def start(self):
        if self.cache and os.path.isfile(SymbolScanner.PICKLE_FILE):
            with open(SymbolScanner.PICKLE_FILE, 'rb') as handle:
                self.data = pickle.load(handle)
        else:
            self.data = self.start_index()
            self.data = self.start_metadata()
            with open(SymbolScanner.PICKLE_FILE, 'wb') as handle:
                pickle.dump(
                    self.data, handle, protocol=pickle.HIGHEST_PROTOCOL
                )

    def sync_pytickersymbols(self, stocks):

        pyticker_names = [
            stock['name']
            for stock_list in map(
                lambda index: stocks.get_stocks_by_index(index),
                stocks.get_all_indices(),
            )
            for stock in stock_list
        ]
        if not self.data:
            return
        for index in self.data:
            for idx, stock in enumerate(self.data[index]):
                pyticker_id, _ = get_best_match(
                    stock.data['short_name'], pyticker_names
                )
                self.data[index][idx].data['name'] = pyticker_names[
                    pyticker_id
                ]

    def start_metadata(self):
        result = {}
        with multiprocessing.Pool(processes=self.MAX_PROCESSES) as pool:
            for index in self.data:
                args = map(
                    lambda stock, idx=index: (
                        stock,
                        Indices.symbol_source_dict[idx].PAGE_LANGS,
                    ),
                    self.data[index],
                )
                stocks_with_metadata = pool.map(self.worker_metadata, args)
                result[index] = stocks_with_metadata
        return result

    def worker_metadata(self, args):
        stock, langs = args
        infobox = get_merged_infobox(stock.data['short_name'], langs)
        if not infobox:
            self.log.warn(
                'Did not find any wikipedia data'
                f'for {stock.data["short_name"]}'
            )
            return stock
        return infobox.to_stock(stock.data['indices'])

    def start_index(self):
        with multiprocessing.Pool(processes=self.MAX_PROCESSES) as pool:
            items = list(
                map(lambda x: (x[0], x[1]), Indices.symbol_source_dict.items())
            )
            index_results = pool.map(self.worker_index, items, chunksize=1)
            result = dict(map(lambda val: list(val.items())[0], index_results))
            return result

    def worker_index(self, args):
        key, index_source = args
        self.log.info(f'________________ parse {index_source.TITLE}')
        wiki_url = (
            f'https://{index_source.LANG}.wikipedia.org/wiki/'
            f'{index_source.TITLE}#{index_source.SECTION}'
        )
        dfs = pd.read_html(wiki_url)
        df = dfs[index_source.TABLE_ID]
        if index_source.COL_NAME_SYMBOL is not None:
            df = df.rename(
                columns={
                    index_source.COL_NAME_COMPANY: 'name',
                    index_source.COL_NAME_SYMBOL: 'symbol',
                }
            )[['name', 'symbol']]
        else:
            df = df.rename(columns={index_source.COL_NAME_COMPANY: 'name'})
            df['symbol'] = None
            df = df[['name', 'symbol']]
        result = {key: []}
        for wiki_name, symbol in zip(df.name, df.symbol):
            stock = Stock.from_wiki(key, wiki_name, symbol)
            result[key].append(stock)
        return result
