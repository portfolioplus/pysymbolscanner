#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

""" pysymbolscanner
  Copyright 2020 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""


def filter_duplicate_dicts_in_list(items):
    return [dict(t) for t in {tuple(d.items()) for d in items}]


def flat_list(my_list):
    return [item for sublist in my_list for item in sublist]


def get_wiki_url(lang, title):
    return f'https://{lang}.wikipedia.org/wiki/{title}'


def get_wiki_page_title_and_links(link, lang_codes):
    get_url = requests.get(link)
    get_text = get_url.text
    soup = BeautifulSoup(get_text, "html.parser")
    company = soup.find('h1').text
    links = soup.findAll(
        'a', href=True, attrs={'class': 'interlanguage-link-target'}
    )
    links = list(
        filter(
            lambda x: x[1] in lang_codes,
            map(lambda x: (x['href'], x['lang']), links),
        )
    )
    return company, links


def is_isin(isin_str):
    """Check if string is a valid ISIN like 'US0378331005'
    :param isin_str: string to check
    :return: True if valid, False otherwise
    """
    if (
        (len(isin_str) == 12 or (len(isin_str) >= 13 and isin_str[12] == '.'))
        and isin_str[:2].isalpha()
        and isin_str[2:12].isalnum()
    ):
        return True
    return False


def is_not_isin(isin_str):
    """Check if string is not a valid ISIN
    :param isin_str: string to check
    :return: True if not valid, False otherwise
    """
    return not is_isin(isin_str)
