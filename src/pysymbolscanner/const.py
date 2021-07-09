#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pysymbolscanner
  Copyright 2020 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import re

most_common_endings = [
    'GmbH & Co. Kommanditgesellschaft auf Aktien',
    'Compagnie Générale des Établissements',
    'Compagnie Générale des établissements',
    ', Société Européenne',
    'Société Européenne',
    ' - ',
    'GmbH & Co. KGaA',
    'AG & Co. KGaA',
    'SE & Co. KGaA',
    'Aktiengesellschaft',
    'Аэрофлот',
    'PAO',
    'SA',
    'S.A.',
    'AG',
    'Ag',
    'ag',
    'SE',
    'S.E.',
    'plc',
    'Plc',
    'PLC',
    'GmbH',
    'KGaA',
    'Corp.',
    'Corp',
    'Co.',
    'Inc.',
    '(Class C)',
    '(Class B)',
    '(Class A)',
    '(A)',
    '(B)',
    '(C)',
    'OJSC',
    'PJSC',
    'S.p.A.',
    'Oyj',
    '(Unternehmen)',
    '(Company)',
]

blocklist_search = ['SDAX', 'MDAX', 'TecDAX', 'S&P 500', 'IBEX 35']

locations = {
    'OMX Helsinki 25': 'Finland',
    'SDAX': 'Germany',
    'MOEX': 'Russian Federation',
    'FTSE 100': 'United Kingdom',
    'S&P 100': 'United States',
    'IBEX 35': 'Finland',
    'DOW JONES': 'United States',
    'DAX': 'Germany',
    'CAC Mid 60': 'France',
    'TECDAX': 'Germany',
    'NASDAQ 100': 'United States',
    'Switzerland 20': 'Switzerland',
    'CAC 40': 'France',
    'S&P 500': 'United States',
    'OMX Stockholm 30': 'Sweden',
    'BEL 20': 'Belgium',
    'MDAX': 'Germany',
    'AEX': 'Netherlands',
}


def fallback_location(index, loc):
    if (loc is None or loc == '') and len(index) > 0:
        loc = locations.get(f'{index[0]}'.upper(), '')
    return loc


def remove_most_common_endings(company):
    for end in most_common_endings:
        company = company.replace(f' {end}', '')
    return company.replace(',', '')


def long_to_short(name):
    result = name.replace('Aktiengesellschaft', 'AG')
    result = result.replace(', Inc.', ' Inc.')
    result = re.sub(r' \(.+\)$', '', result)
    if not result or not result.strip():
        raise RuntimeError(f'Error during name processing {name}')
    return result
