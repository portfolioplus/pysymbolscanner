from json import JSONDecodeError

from uplink import Consumer, Query, get, returns, headers

from pysymbolscanner.const import remove_most_common_endings, long_to_short
from pysymbolscanner.word_score import get_score
from pysymbolscanner.utils import filter_duplicate_dicts_in_list


class YahooSearch(Consumer):

    BASE_URL = 'https://query1.finance.yahoo.com/'

    def __init__(self):
        super().__init__(base_url=YahooSearch.BASE_URL)

    @headers(
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/75.0.3770.142 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'Accept': '*/*',
            'Connection': 'keep-alive',
        }
    )
    @returns.json()
    @get('/v1/finance/search')
    def search(
        self,
        search: Query('q'),
        lang: Query('lang') = 'en-US',
        quotes_count: Query('quotesCount') = 15,
        news_count: Query('newsCount') = 0,
    ):
        """returns ticker symbols by search token"""

    @staticmethod
    def item_sort(item):
        return {
            'EUR': 1,
            'USD': 2,
            'RUB': 3,
            'GBP': 4,
        }.get(item['currency'], 99)

    def _search_symbols(self, search, isins=[]):
        search1 = search
        search2 = remove_most_common_endings(search)
        search3 = long_to_short(search)
        data = []
        for search_item in [search1, search2, search3] + isins:
            try:
                search_result = self.search(search_item)
                if 'quotes' not in search_result:
                    continue
                data += search_result['quotes']
            except JSONDecodeError:
                continue
        return data

    @staticmethod
    def _get_scored_quotes(search, data):
        search = remove_most_common_endings(search)
        # filter by word  score
        quotes = list(
            filter(
                lambda x: 'exchange' in x
                and (
                    (
                        'longname' in x
                        and get_score(
                            search, remove_most_common_endings(x['longname'])
                        )
                        > 0.8
                    )
                    or (
                        'shortname' in x
                        and get_score(
                            search, remove_most_common_endings(x['shortname'])
                        )
                        > 0.8
                    )
                ),
                data,
            )
        )
        exchanges = set(map(lambda x: x['exchange'], quotes))
        scored_quotes = list(
            map(
                lambda exchange: max(
                    filter(
                        lambda y, exc=exchange: y['exchange'] == exc,
                        quotes,
                    ),
                    key=lambda x: x['score'],
                ),
                exchanges,
            )
        )
        return scored_quotes

    @staticmethod
    def _get_symbol(sym, google_prefix, yahoo_suffix, currency):
        return {
            'yahoo': f'{sym}.{yahoo_suffix}' if yahoo_suffix else sym,
            'google': f'{google_prefix}:{sym}',
            'currency': currency,
        }

    @staticmethod
    def _get_pyticker_symbol(exchange, symbol):
        sym = symbol.split('.')[0] if symbol.split('.') else symbol
        return {
            'FRA': lambda x: YahooSearch._get_symbol(x, 'FRA', 'F', 'EUR'),
            'GER': lambda x: YahooSearch._get_symbol(x, 'FRA', 'F', 'EUR'),
            'BER': lambda x: YahooSearch._get_symbol(x, 'FRA', 'F', 'EUR'),
            'STU': lambda x: YahooSearch._get_symbol(x, 'FRA', 'F', 'EUR'),
            'HAN': lambda x: YahooSearch._get_symbol(x, 'FRA', 'F', 'EUR'),
            'MUN': lambda x: YahooSearch._get_symbol(x, 'FRA', 'F', 'EUR'),
            'AMS': lambda x: YahooSearch._get_symbol(x, 'AMS', 'AS', 'EUR'),
            'MCE': lambda x: YahooSearch._get_symbol(x, 'BME', 'MC', 'EUR'),
            'LSE': lambda x: YahooSearch._get_symbol(x, 'LON', 'L', 'GBP'),
            'NMS': lambda x: YahooSearch._get_symbol(x, 'NASDAQ', None, 'USD'),
            'PNK': lambda x: YahooSearch._get_symbol(
                x, 'OTCMKTS', None, 'USD'
            ),
            'NYQ': lambda x: YahooSearch._get_symbol(x, 'NYSE', None, 'USD'),
            'MCX': lambda x: YahooSearch._get_symbol(x, 'MCX', 'ME', 'RUB'),
        }.get(exchange, lambda x: None)(sym)

    def get_symbols(self, search, isins=[]):
        data = self._search_symbols(search, isins)

        if not data:
            return None

        scored_quotes = self._get_scored_quotes(search, data)
        result = []
        for quote in scored_quotes:
            exchange = quote.get('exchange', '')
            symbol = quote.get('symbol', '')
            if not symbol or not exchange:
                continue
            pyticker_symbol = self._get_pyticker_symbol(exchange, symbol)
            if pyticker_symbol:
                result.append(pyticker_symbol)
        result = filter_duplicate_dicts_in_list(result)
        result.sort(key=self.item_sort)
        return result
