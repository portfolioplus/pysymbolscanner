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
import os
import yaml
from collections import OrderedDict

logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)


yaml.add_representer(
    OrderedDict,
    lambda self, data: self.represent_mapping(
        'tag:yaml.org,2002:map', data.items()
    ),
)


def is_valid_file(parser, arg):
    """
    Check if file exists
    :param parser: parser instance
    :param arg: path to file
    :return: return the path if exists otherwise None
    """
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
        return None
    return arg


def get_missing_objects(index, scanner, stock_data):
    missing_stocks = list(
        filter(
            lambda x: x['name']
            not in map(
                lambda x: x['name'], stock_data.get_stocks_by_index(index)
            ),
            map(lambda y: y.to_pyticker_symbol(), scanner.data[index]),
        )
    )
    return missing_stocks


def get_wrong_objects(index, scanner, stock_data):
    wrong_stocks = list(
        filter(
            lambda x: x['name']
            not in map(lambda y: y.name, scanner.data[index]),
            map(lambda y: y, stock_data.get_stocks_by_index(index)),
        )
    )
    return wrong_stocks


def fix_missing(missings, index, stocks_yaml):
    for missing in missings:
        not_exists = True
        for stock in stocks_yaml['companies']:
            if (
                stock['name'] == missing['name']
                and index not in stock['indices']
            ):
                stock['indices'].append(index)
                stock['isins'] = missing['isins']
                stock['metadata'] = missing['metadata']
                for symbol in missing['symbols']:
                    if symbol not in stock['symbols']:
                        stock['symbols'].append(symbol)
                not_exists = False
                break
        if not_exists:
            stocks_yaml['companies'].append(missing)
    return stocks_yaml


def fix_wrong(wrongs, index, stocks_yaml):
    for wrong in wrongs:
        for stock in stocks_yaml['companies']:
            if stock['name'] == wrong['name'] and index in stock['indices']:
                stock['indices'].remove(index)
    return stocks_yaml


def symbolscanner_app():
    """
    Main entry point for symbolscanner application
    :return:
    """
    parser = argparse.ArgumentParser(description='SymbolScanner CLI')
    parser.add_argument('--cache', action='store_true', default=False)
    parser.add_argument(
        '-i',
        '--input',
        dest='input',
        action='store',
        help='Path to the input file.',
        type=lambda x: is_valid_file(parser, x),
    )
    parser.add_argument(
        '-o',
        '--output',
        dest='output',
        action='store',
        help='Path to the output file.',
    )
    args = parser.parse_args()
    stock_data = PyTickerSymbols()
    scanner = SymbolScanner(args.cache)
    scanner.start()
    indices = stock_data.get_all_indices()
    stocks_yaml = None
    with open(args.input, 'r') as in_file:
        stocks_yaml = yaml.safe_load(in_file)
        for index in indices:
            missing = get_missing_objects(index, scanner, stock_data)
            wrong = get_wrong_objects(index, scanner, stock_data)
            stocks_yaml = fix_wrong(wrong, index, stocks_yaml)
            stocks_yaml = fix_missing(missing, index, stocks_yaml)
    with open(args.output, 'w', encoding='latin1') as out_file:
        yaml.dump(stocks_yaml, out_file, sort_keys=False)
