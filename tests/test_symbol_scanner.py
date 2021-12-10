import unittest
import os

from pysymbolscanner.scanner import SymbolScanner
from pytickersymbols import Statics
from pysymbolscanner.index_definitions import Indices
from parameterized import parameterized
import collections


class TestSymbolScanner(unittest.TestCase):
    def _get_text(self, filename):
        dow_path = os.path.join(os.path.dirname(__file__), filename)
        with open(dow_path) as f:
            html = f.read()
        return html

    @parameterized.expand(
        [
            ['data/index/dow.dat', Statics.Indices.US_DOW, 0],
            ['data/index/sp100.dat', Statics.Indices.US_SP_100, 1],
            ['data/index/estoxx50.dat', Statics.Indices.EU_50, 0],
        ]
    )
    def test_parse_index(self, filename, index, duplicates_allowed=False):
        dow_text = self._get_text(filename)
        scanner = SymbolScanner(None)
        result = scanner.parse_index(
            dow_text,
            index,
            Indices.symbol_source_dict[index],
        )
        self.assertIsNotNone(result)
        all_links = result['link'].values.tolist()
        duplicates = len(all_links) - len(set(all_links))
        self.assertEqual(
            duplicates,
            duplicates_allowed,
            'Duplicate links: '
            + ', '.join(
                [
                    item
                    for item, count in collections.Counter(all_links).items()
                    if count > 1
                ]
            ),
        )
