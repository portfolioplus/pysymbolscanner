#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pysymbolscanner
  Copyright 2020 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""


def filter_duplicate_dicts_in_list(items):
    return [dict(t) for t in {tuple(d.items()) for d in items}]
