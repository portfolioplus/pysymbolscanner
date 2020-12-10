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
    SECTION: str
    LANG: str
    TABLE_ID: int
    COL_NAME_SYMBOL: str
    COL_NAME_COMPANY: str
    PAGE_LANGS: []


class Indices:

    symbol_source_dict = {
        Statics.Indices.DE_SDAX: IndexSource(
            'SDAX', 'Companies', 'en', 2, None, 'Name', ['de', 'en']
        ),
        Statics.Indices.RU_MOEX: IndexSource(
            'RTS_Index',
            'Zusammensetzung',
            'de',
            8,
            None,
            'Unternehmen',
            ['en', 'de'],
        ),
        Statics.Indices.GB_FTSE: IndexSource(
            'FTSE_100_Index',
            'Constituents_in_September_2020',
            'en',
            3,
            'EPIC',
            'Company',
            ['en', 'de'],
        ),
        Statics.Indices.FI_OMX_25: IndexSource(
            'OMX_Helsinki_25',
            'Components',
            'en',
            0,
            'Ticker symbol',
            'Company',
            ['en', 'de'],
        ),
        Statics.Indices.EU_50: IndexSource(
            'EURO_STOXX_50',
            'Composition',
            'en',
            2,
            'Main listing',
            'Name',
            ['en', 'de', 'fr'],
        ),
        Statics.Indices.US_SP_100: IndexSource(
            'S%26P_100', 'Components', 'en', 2, 'Symbol', 'Name', ['en']
        ),
        Statics.Indices.ES_IBEX_35: IndexSource(
            'IBEX_35', 'Components', 'en', 1, 'Ticker', 'Company', ['en', 'es']
        ),
        Statics.Indices.US_DOW: IndexSource(
            'Dow_Jones_Industrial_Average',
            'Components',
            'en',
            1,
            'Symbol',
            'Company',
            ['en'],
        ),
        Statics.Indices.DE_DAX: IndexSource(
            'DAX',
            'Components',
            'en',
            3,
            'Ticker symbol',
            'Company',
            ['de', 'en'],
        ),
        Statics.Indices.FR_CAC_60: IndexSource(
            'CAC_Mid_60',
            'Zusammensetzung',
            'de',
            0,
            None,
            'Unternehmen',
            ['fr', 'en', 'de'],
        ),
        Statics.Indices.DE_TECDAX: IndexSource(
            'TecDAX',
            'Zusammensetzung',
            'de',
            5,
            'Symbol[11]',
            'Name',
            ['de', 'en'],
        ),
        Statics.Indices.US_NASDAQ: IndexSource(
            'NASDAQ-100', 'Components', 'de', 4, 'Symbol', 'Name (A–Z)', ['en']
        ),
        Statics.Indices.CH_20: IndexSource(
            'Swiss_Market_Index',
            'SMI_constituents',
            'en',
            1,
            'Ticker',
            'Name',
            ['en', 'de', 'fr'],
        ),
        Statics.Indices.FR_CAC_40: IndexSource(
            'CAC_40',
            'Composition',
            'en',
            3,
            'Ticker',
            'Company',
            ['fr', 'en', 'de'],
        ),
        Statics.Indices.US_SP_500: IndexSource(
            'List_of_S%26P_500_companies',
            'Selected_changes_to_the_list_of_S&P_500_components',
            'en',
            0,
            'Symbol',
            'Security',
            ['en'],
        ),
        Statics.Indices.SE_OMX_30: IndexSource(
            'OMX_Stockholm_30',
            'Zusammensetzung',
            'de',
            6,
            None,
            'Name',
            ['en', 'de'],
        ),
        Statics.Indices.BE_20: IndexSource(
            'BEL_20',
            'Constituents',
            'en',
            2,
            'Ticker symbol',
            'Company',
            ['fr', 'en', 'de'],
        ),
        Statics.Indices.DE_MDAX: IndexSource(
            'MDAX', 'Companies', 'en', 1, None, 'Name', ['de', 'en']
        ),
        Statics.Indices.NL_AEX: IndexSource(
            'AEX_index',
            'Composition',
            'en',
            2,
            'Ticker symbol',
            'Company',
            ['en', 'de'],
        ),
    }
