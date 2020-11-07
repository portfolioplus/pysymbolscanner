#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" symbol_scanner
  Copyright 2019 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import logging
import os
import pickle
import sys
from dataclasses import dataclass
import argparse
import pandas as pd
import wikipedia as wp
from pytickersymbols import PyTickerSymbols, Statics

logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

@dataclass
class IndexSource:
    TITLE: str
    SECTION: str
    LANG: str
    TABLE_ID: int
    COL_NAME_SYMBOL: str
    COL_NAME_COMPANY: str

symbol_source_dict = {
   Statics.Indices.DE_SDAX: IndexSource('SDAX', 'Companies', 'en', 2, None, 'Name'),
   Statics.Indices.RU_MOEX: IndexSource('RTS_Index', 'Components', 'en', 1, 'Ticker symbol', 'Company'),
   Statics.Indices.GB_FTSE: IndexSource('FTSE_100_Index', 'Constituents_in_September_2020', 'en', 3, 'EPIC', 'Company'),
   Statics.Indices.FI_OMX_25: IndexSource('OMX_Helsinki_25', 'Components', 'en', 0, 'Ticker symbol', 'Company'),
   Statics.Indices.EU_50: IndexSource('EURO_STOXX_50', 'Composition', 'en', 2, 'Main listing', 'Name'),
   Statics.Indices.US_SP_100: IndexSource('S%26P_100', 'Components', 'en', 2, 'Symbol', 'Name'),
   Statics.Indices.ES_IBEX_35: IndexSource('IBEX_35', 'Components', 'en', 1, 'Ticker', 'Company'),
   Statics.Indices.US_DOW: IndexSource('Dow_Jones_Industrial_Average', 'Components', 'en', 1, 'Symbol', 'Company'),
   Statics.Indices.DE_DAX: IndexSource('DAX', 'Components', 'en', 3, 'Ticker symbol', 'Company'),
   Statics.Indices.FR_CAC_60: IndexSource('CAC_Mid_60', 'Zusammensetzung', 'de', 0, None, 'Unternehmen'),
   Statics.Indices.DE_TECDAX: IndexSource('TecDAX', 'Zusammensetzung', 'de', 5, 'Symbol[11]', 'Name'),
   Statics.Indices.US_NASDAQ: IndexSource('NASDAQ-100', 'Components', 'de', 4, 'Symbol', 'Name (A–Z)'),
   Statics.Indices.CH_20: IndexSource('Swiss_Market_Index', 'SMI_constituents', 'en', 1, 'Ticker', 'Name'),
   Statics.Indices.FR_CAC_40: IndexSource('CAC_40', 'Composition', 'en', 3, 'Ticker', 'Company'),
   Statics.Indices.US_SP_500: IndexSource(
      'List_of_S%26P_500_companies',
      'Selected_changes_to_the_list_of_S&P_500_components',
      'en',
      0,
      'Symbol',
      'Security'
   ),
   Statics.Indices.SE_OMX_30: IndexSource('OMX_Stockholm_30', 'Zusammensetzung', 'de',  6, None, 'Name',),
   Statics.Indices.BE_20: IndexSource('BEL_20', 'Constituents', 'en', 2, 'Ticker symbol', 'Company'),
   Statics.Indices.DE_MDAX: IndexSource('MDAX', 'Companies', 'en', 1, None, 'Name',),
   Statics.Indices.NL_AEX: IndexSource('AEX_index', 'Composition', 'en', 2, 'Ticker symbol', 'Company'),
}


class SymbolScanner:

   def __init__(self, cache):
      logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
      self.log = logging.getLogger('symbol scanner')
      self.data = None
      if cache and os.path.isfile('index_data.pickle'):
         with open('index_data.pickle', 'rb') as handle:
            self.data = pickle.load(handle)
      else:
         self.data = self._get_index_tables()
         with open('index_data.pickle', 'wb') as handle:
            pickle.dump(self.data, handle, protocol=pickle.HIGHEST_PROTOCOL)


   def _get_index_tables(self):
      result = {}
      for key, index_source in symbol_source_dict.items():
         self.log.info(f'________________ parse {index_source.TITLE}')
         wiki_url = f'https://{index_source.LANG}.wikipedia.org/wiki/{index_source.TITLE}#{index_source.SECTION}'
         try:
               dfs = pd.read_html(wiki_url)
               df = dfs[index_source.TABLE_ID]
               if index_source.COL_NAME_SYMBOL is not None:
                  result[key] = df.rename(columns={index_source.COL_NAME_COMPANY: 'name', index_source.COL_NAME_SYMBOL: 'symbol'})[['name', 'symbol']]
               else:
                  myNewdf = df.rename(columns={index_source.COL_NAME_COMPANY: 'name'})
                  myNewdf['symbol'] = None
                  result[key] = myNewdf[['name', 'symbol']]
         except:
               self.log.error(f'Could not extract index table from {wiki_url}')
               pass
      return result

   def get_missing_stocks_of_index(self, index, stocks):
      result =list(
         filter(
            lambda x: x.lower() not in map(lambda y: y['name'].lower(), stocks),
            self.data[index]['name']
         )
      )
      return result

if __name__ == "__main__":
   parser = argparse.ArgumentParser(description='This is a PyMOTW sample program')
   parser.add_argument('--cache', action="store_true", default=False)
   args = parser.parse_args()
   scanner = SymbolScanner(args.cache)
   stock_data = PyTickerSymbols()
   indices = stock_data.get_all_indices()

   # check if all urls pressent for each index in pytickersymbols
   is_url_list_complete = all(map(lambda x: x in symbol_source_dict, indices))
   if not is_url_list_complete:
      scanner.log.error('URL lookup table is not complete.')
      sys.exit(1)

   # check if all urls are reachable
   is_table_dict_complete = all(map(lambda x: x in scanner.data, indices))

   if not is_table_dict_complete:
      scanner.log.error('Table dict is not complete.')
      sys.exit(1)

   # missing stocks in index
   for index in  indices:
      stocks = stock_data.get_stocks_by_index(index)
      missing_stocks = scanner.get_missing_stocks_of_index(index, stocks)
      scanner.log.info(f'missing stocks of {index}:')
      for stock in missing_stocks:
         scanner.log.info(stock)

