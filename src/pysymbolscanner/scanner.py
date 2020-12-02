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


class SymbolScanner:
    MAX_PROCESSES = 8
    PICKLE_FILE = 'index_data.pickle'

    def __init__(self, cache):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        self.log = logging.getLogger('symbol scanner')
        self.data = None
        if cache and os.path.isfile(SymbolScanner.PICKLE_FILE):
            with open(SymbolScanner.PICKLE_FILE, 'rb') as handle:
                self.data = pickle.load(handle)
        else:
            self.data = self.start_index()
            self.data = self.start_metadata()
            with open(SymbolScanner.PICKLE_FILE, 'wb') as handle:
                pickle.dump(
                    self.data, handle, protocol=pickle.HIGHEST_PROTOCOL
                )

    def start_metadata(self):
        result = {}
        with multiprocessing.Pool(processes=self.MAX_PROCESSES) as pool:
            for index in self.data:
                stocks_with_metadata = pool.map(
                    self.worker_metadata, self.data[index]
                )
                result[index] = stocks_with_metadata
        return result

    def worker_metadata(self, stock):
        infobox = get_merged_infobox(stock.data['short_name'])
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
