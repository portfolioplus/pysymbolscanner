#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pysymbolscanner
  Copyright 2020 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
from dataclasses import dataclass
from pytickersymbols import Statics


@dataclass
class IndexSource:
    TITLE: str
    ITEMS: []
    LANG: str
    COL_NAME_SYMBOL: str
    COL_NAME_COMPANY: str
    PAGE_LANGS: []


class Indices:

    symbol_source_dict = {
        Statics.Indices.DE_SDAX: IndexSource(
            'SDAX',
            ['Logo', 'Name', 'Branche'],
            'de',
            None,
            'Name',
            ['de', 'en'],
        ),
        Statics.Indices.RU_MOEX: IndexSource(
            'RTS_Index',
            ['Logo', 'Unternehmen', 'Branche'],
            'de',
            None,
            'Unternehmen',
            ['de', 'en'],
        ),
        Statics.Indices.GB_FTSE: IndexSource(
            'FTSE_100_Index',
            ['Company', 'EPIC'],
            'en',
            'EPIC',
            'Company',
            ['en', 'de'],
        ),
        Statics.Indices.FI_OMX_25: IndexSource(
            'OMX_Helsinki_25',
            ['Company', 'Ticker symbol'],
            'en',
            'Ticker symbol',
            'Company',
            ['en', 'de'],
        ),
        Statics.Indices.EU_50: IndexSource(
            'EURO_STOXX_50',
            ['Name', 'Main listing', 'Ticker', 'Industry'],
            'en',
            'Ticker',
            'Name',
            ['en', 'de', 'fr'],
        ),
        Statics.Indices.US_SP_100: IndexSource(
            'S%26P_100',
            ['Name', 'Symbol'],
            'en',
            'Symbol',
            'Name',
            ['en'],
        ),
        Statics.Indices.ES_IBEX_35: IndexSource(
            'IBEX_35',
            ['Company', 'Ticker', 'Sector'],
            'en',
            'Ticker',
            'Company',
            ['en', 'es'],
        ),
        Statics.Indices.US_DOW: IndexSource(
            'Dow_Jones_Industrial_Average',
            ['Symbol', 'Company', 'Industry'],
            'en',
            'Symbol',
            'Company',
            ['en'],
        ),
        Statics.Indices.DE_DAX: IndexSource(
            'DAX',
            ['Logo', 'Name', 'Branche', 'Symbol'],
            'de',
            'Symbol',
            'Name',
            ['de', 'en'],
        ),
        Statics.Indices.FR_CAC_60: IndexSource(
            'CAC_Mid_60',
            ['Unternehmen', 'Branche', 'Logo'],
            'de',
            None,
            'Unternehmen',
            ['de', 'en', 'fr'],
        ),
        Statics.Indices.DE_TECDAX: IndexSource(
            'TecDAX',
            ['Logo', 'Name', 'Branche'],
            'de',
            'Symbol[11]',
            'Name',
            ['de', 'en'],
        ),
        Statics.Indices.US_NASDAQ: IndexSource(
            'NASDAQ-100',
            ['Company', 'Ticker'],
            'en',
            'Ticker',
            'Company',
            ['en'],
        ),
        Statics.Indices.CH_20: IndexSource(
            'Swiss_Market_Index',
            ['Name', 'Industry', 'Ticker'],
            'en',
            'Ticker',
            'Name',
            ['en', 'de', 'fr'],
        ),
        Statics.Indices.FR_CAC_40: IndexSource(
            'CAC_40',
            ['Company', 'Sector', 'Ticker'],
            'en',
            'Ticker',
            'Company',
            ['en', 'fr', 'de'],
        ),
        Statics.Indices.US_SP_500: IndexSource(
            'List_of_S%26P_500_companies',
            ['Symbol', 'Security', 'Founded', 'Headquarters Location'],
            'en',
            'Symbol',
            'Security',
            ['en'],
        ),
        Statics.Indices.SE_OMX_30: IndexSource(
            'OMX_Stockholm_30',
            ['Logo', 'Name', 'Branche'],
            'de',
            None,
            'Name',
            ['de', 'en'],
        ),
        Statics.Indices.BE_20: IndexSource(
            'BEL_20',
            ['Logo', 'Name', 'Branche'],
            'de',
            None,
            'Name',
            ['de', 'en', 'fr'],
        ),
        Statics.Indices.DE_MDAX: IndexSource(
            'MDAX',
            ['Logo', 'Name', 'Branche'],
            'de',
            None,
            'Name',
            ['de', 'en'],
        ),
        Statics.Indices.NL_AEX: IndexSource(
            'AEX_index',
            ['Company', 'Ticker symbol'],
            'en',
            'Ticker symbol',
            'Company',
            ['en', 'de'],
        ),
    }
