#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pysymbolscanner
  Copyright 2020 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

import logging
import multiprocessing
import os
import pickle
import sys

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pytickersymbols import PyTickerSymbols

from pysymbolscanner.const import most_common_endings
from pysymbolscanner.index_definitions import Indices
from pysymbolscanner.stock import Stock
from pysymbolscanner.wiki import get_merged_infobox, get_wiki_url
from pysymbolscanner.word_score import deep_search, get_best_match
from pysymbolscanner.yahoo import YahooSearch
from pysymbolscanner.const import fallback_location


class SymbolScanner:
    MIN_WORD_OCCURRENCE = 5
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
            self.data = self.start_yahoo()
            self.data = self.start_sync()
            with open(SymbolScanner.PICKLE_FILE, 'wb') as handle:
                pickle.dump(
                    self.data, handle, protocol=pickle.HIGHEST_PROTOCOL
                )

    def start_yahoo(self):
        result = {}
        with multiprocessing.Pool(processes=self.MAX_PROCESSES * 4) as pool:
            for index in self.data:
                args = map(
                    lambda stock: stock,
                    self.data[index],
                )
                stocks_with_yahoo_symbols = pool.map(self.worker_yahoo, args)
                result[index] = stocks_with_yahoo_symbols
        return result

    def worker_yahoo(self, stock):
        search = YahooSearch()
        if not stock.name:
            self.log.warn(
                f'Item without name {stock}'
            )
            return stock
        symbols = search.get_symbols(stock.name)
        stock.yahoo_symbols = symbols
        return stock

    def start_sync(self):
        stocks = PyTickerSymbols()
        if not self.data:
            return

        stocks_py = stocks.get_all_stocks()

        names_py = list(set([stock['name'] for stock in stocks_py]))

        names_wiki = list(
            set(
                [
                    stock.wiki_name
                    for stock_list in map(
                        lambda index: self.data[index],
                        Indices.symbol_source_dict,
                    )
                    for stock in stock_list
                ]
            )
        )

        names = names_py + names_wiki
        endings = list(
            map(lambda x: ' ' + x, self.get_most_common_endings(names))
        )
        occurrences = list(
            set(
                list(self.get_most_common_occurrences(names))
                + most_common_endings
                + endings
            )
        )

        occurrences.sort(key=len, reverse=True)
        endings.sort(key=len, reverse=True)
        with multiprocessing.Pool(processes=self.MAX_PROCESSES) as pool:
            items = list(
                map(
                    lambda index: (index, endings, occurrences, stocks_py),
                    Indices.symbol_source_dict,
                )
            )
            sync_results = pool.map(self.worker_sync, items)
            result = dict(map(lambda val: list(val.items())[0], sync_results))
            return result

    @staticmethod
    def find_by_symbol(stock, py_stocks):
        for idx, py_stock in enumerate(py_stocks):
            for py_symbol in py_stock['symbols']:
                for symbol in stock['symbols']:
                    if symbol['yahoo'] == py_symbol['yahoo']:
                        return idx
        return -1

    @staticmethod
    def find_by_symbol_and_country(stock, py_stocks):
        for idx, py_stock in enumerate(py_stocks):
            if (
                stock['symbol'] == py_stock['symbol']
                and stock['country'] == py_stock['country']
                and stock['metadata'] == py_stock['metadata']
            ):
                return idx
        return -1

    def worker_sync(self, args):
        index, endings, occurrences, stocks = args
        wiki_stocks = self.data[index].copy()
        for idx, wiki_stock in enumerate(wiki_stocks):
            stock = wiki_stock.to_pyticker_symbol()
            names = [stock['name'] for stock in stocks]
            names_wiki = [stock.get('wiki_name', '') for stock in stocks]
            name_id = self.find_by_symbol(stock, stocks)

            if name_id != -1:
                wiki_stocks[idx].name = names[name_id]
                continue

            name_id = self.find_by_symbol_and_country(stock, stocks)
            if name_id != -1:
                wiki_stocks[idx].name = names[name_id]
                continue

            wiki_stock_name = stock['wiki_name']
            name_id, max_score = get_best_match(
                wiki_stock_name,
                names,
                word_filter=occurrences,
            )

            if max_score < 0.9:
                name_id, max_score = get_best_match(
                    wiki_stock_name,
                    names_wiki,
                    word_filter=occurrences,
                )

            if max_score > 0.9:
                self.log.warn(
                    f'Sync by word score. {wiki_stocks[idx].wiki_name} =='
                    f' {names[name_id]} = {max_score}'
                )
                wiki_stocks[idx].name = names[name_id]
                continue

            name_id, max_score = deep_search(
                wiki_stock_name, names, occurrences
            )

            if max_score > 0.9:
                self.log.warn(
                    f'Sync by deep search. {wiki_stocks[idx].wiki_name} =='
                    f' {names[name_id]} = {max_score}'
                )
                wiki_stocks[idx].name = names[name_id]
            else:
                self.log.warn(
                    f'Did not find any match for {index} - {wiki_stock_name}'
                )
                wiki_stocks[idx].name = wiki_stocks[idx].wiki_name
        return {index: wiki_stocks}

    def get_most_common_endings(self, names):
        most_words = {}
        for name in names:
            if not name.split():
                continue
            word = name.split()[-1]
            most_words[word] = most_words.get(word, 0) + 1

        items_list = [word for word in most_words.items()]
        items_list.sort(key=lambda tup: tup[1])
        return map(
            lambda x: x[0],
            filter(lambda f: f[1] >= self.MIN_WORD_OCCURRENCE, items_list),
        )

    def get_most_common_occurrences(self, names):
        most_words = {}
        for name in names:
            if not name.split():
                continue
            words = name.split()
            for word in words:
                most_words[word] = most_words.get(word, 0) + 1

        items_list = [word for word in most_words.items()]
        items_list.sort(key=lambda tup: tup[1])
        return map(
            lambda x: x[0],
            filter(lambda f: f[1] >= self.MIN_WORD_OCCURRENCE, items_list),
        )

    def start_metadata(self):
        result = {}
        with multiprocessing.Pool(processes=self.MAX_PROCESSES * 4) as pool:
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
        infobox = get_merged_infobox(
            stock.wiki_name, stock.link, stock.link_lang, langs
        )
        if not infobox:
            self.log.warn(
                f'Did not find any wikipedia data for {stock.wiki_name}'
            )
            stock.country = fallback_location(stock.indices, stock.country)
            return stock
        return infobox.to_stock(stock.indices, stock.symbol)

    def start_index(self):
        with multiprocessing.Pool(processes=self.MAX_PROCESSES) as pool:
            items = list(
                map(lambda x: (x[0], x[1]), Indices.symbol_source_dict.items())
            )
            index_results = pool.map(self.worker_index, items)
            result = dict(map(lambda val: list(val.items())[0], index_results))
            return result

    def worker_index(self, args):
        key, index_source = args
        self.log.info(f'________________ parse {index_source.TITLE}')
        wiki_url = get_wiki_url(index_source.LANG, index_source.TITLE)
        response = requests.get(wiki_url)
        dfs = pd.read_html(response.text)
        table_id = self.get_table_id(dfs, index_source.ITEMS)
        if table_id == -1:
            raise RuntimeError(f'Could not find index table for {key}')
        df = dfs[table_id]
        try:
            links = self.get_wiki_links(
                response.text, table_id, index_source.COL_NAME_COMPANY
            )
        except TypeError:
            raise RuntimeError(f'Could not find company links {key} table')
        df['link'] = links
        if index_source.COL_NAME_SYMBOL is not None:
            df = df.rename(
                columns={
                    index_source.COL_NAME_COMPANY: 'name',
                    index_source.COL_NAME_SYMBOL: 'symbol',
                }
            )[['name', 'symbol', 'link']]
        else:
            df = df.rename(columns={index_source.COL_NAME_COMPANY: 'name'})
            df['symbol'] = None
            df = df[['name', 'symbol', 'link']]
        result = {key: []}
        for wiki_name, symbol, link in zip(df.name, df.symbol, df.link):
            stock = Stock.from_wiki(
                [key], wiki_name, link, index_source.LANG, symbol
            )
            result[key].append(stock)
        return result

    @staticmethod
    def get_table_id(dfs, columns):
        table_id = -1
        for idx, df in enumerate(dfs):
            if all(col in df.columns for col in columns):
                if table_id != -1:
                    raise RuntimeError(
                        'Could not detect table because of multiple matches'
                    )
                table_id = idx
        return table_id

    @staticmethod
    def get_wiki_links(html, table_id, col_name):
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.findAll('table')[table_id]
        links = []
        index = -1
        for row in table.findAll('tr'):
            column_names = row.findAll('th')
            if index == -1:
                index = SymbolScanner._get_col_id(col_name, column_names)
                continue
            tr = row.findAll('td')[index]
            try:
                link = tr.find('a')['href']
                if 'action=edit' not in link:
                    links.append(link)
                else:
                    links.append('')
            except (KeyError, TypeError):
                links.append('')
        return links

    @staticmethod
    def _get_col_id(col_name, column_names):
        index = next(
            iter(
                [
                    i
                    for i, s in enumerate(column_names)
                    if col_name in s.getText()
                ]
            ),
            None,
        )
        return index
