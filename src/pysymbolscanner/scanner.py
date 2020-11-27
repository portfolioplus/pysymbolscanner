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
import wikipedia as wp
import wptools
from difflib import SequenceMatcher
import multiprocessing
from pysymbolscanner.index_definitions import Indices
from pysymbolscanner.wiki import get_infobox


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
            manager = multiprocessing.Manager()
            return_dict = manager.dict()
            jobs = []
            for key, index_source in Indices.symbol_source_dict.items():
                p = multiprocessing.Process(
                    target=self.worker, args=(key, index_source, return_dict)
                )
                jobs.append(p)
                p.start()

            for proc in jobs:
                proc.join()
            self.data = dict(return_dict)
            with open(SymbolScanner.PICKLE_FILE, 'wb') as handle:
                pickle.dump(
                    self.data, handle, protocol=pickle.HIGHEST_PROTOCOL
                )

    def start_metadata(self, indices):
        result = {}
        with multiprocessing.Pool(processes=MAX_PROCESSES) as pool:
            for index in indices:
                _, stocks_with_metadata = zip(*pool.map(self.worker_metadata, indices[index]))
                result[index] = stocks_with_metadata
        return result

    def worker_metadata(self, stock):
        pass


    def start_index(self, stocks):
        pass

    def worker_index(self, key, index_source, result):
        self.log.info(f'________________ parse {index_source.TITLE}')
        wiki_url = f'https://{index_source.LANG}.wikipedia.org/wiki/{index_source.TITLE}#{index_source.SECTION}'
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
        result[key] = []
        for wiki_name, symbol in df[['name', 'symbol']]:
            stock = {
                'name': '',
                'short_name': wiki_name,
                'symbol': symbol,
                'indices': [key],
                'industries': [],
                'symbols': [],
                'metadata': {}
            }
            result[key].append(stock)


    def worker(self, key, index_source, result):
        self.log.info(f'________________ parse {index_source.TITLE}')
        wiki_url = f'https://{index_source.LANG}.wikipedia.org/wiki/{index_source.TITLE}#{index_source.SECTION}'
        dfs = pd.read_html(wiki_url)
        df = dfs[index_source.TABLE_ID]
        try:
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
            # fix names
            for wiki_name in df['name']:
                infobox = get_infobox(wiki_name)
                if infobox and 'name' in infobox:
                    wiki_name_page = infobox['name']
                    self.log.info(f'Change {wiki_name} with {wiki_name_page}')
                    df['name'] = df['name'].replace(
                        [wiki_name], wiki_name_page
                    )
                else:
                    self.log.warn(
                        f'Could not extract info box name from {wiki_name}'
                    )
        except:
            self.log.error(f'Could not extract index table from {wiki_url}')
        result[key] = df
