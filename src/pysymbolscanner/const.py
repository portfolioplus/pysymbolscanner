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
    'GmbH & Co. KGaA',
    'AG & Co. KGaA',
    'Aktiengesellschaft',
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

blocklist_search = ['SDAX', 'MDAX', 'TecDAX', 'S&P 500']


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
