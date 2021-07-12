from pysymbolscanner.utils import filter_duplicate_dicts_in_list


class Stock:
    def __init__(
        self,
        name,
        wiki_name,
        link,
        link_lang,
        main_symbol,
        loc,
        indices,
        industry,
        symbols,
        isins,
        founded,
        employees,
    ):
        self.data = {
            'name': name,
            'wiki_name': wiki_name,
            'link': link,
            'link_lang': link_lang,
            'symbol': main_symbol,
            'country': loc,
            'indices': indices,
            'industries': industry,
            'symbols': symbols,
            'isins': isins,
            'metadata': {'founded': founded, 'employees': employees},
        }

    @classmethod
    def from_wiki(cls, indices, wiki_name, link, link_lang, symbol):
        return cls(
            wiki_name,
            wiki_name,
            link,
            link_lang,
            symbol,
            '',
            indices,
            [],
            [],
            [],
            0,
            0,
        )

    @classmethod
    def from_pyticker(cls, stock):
        return cls(
            stock.get('name', ''),
            stock.get('wiki_name', ''),
            '',
            '',
            stock.get('symbol', ''),
            stock.get('country', ''),
            stock.get('indices', []),
            stock.get('industries', []),
            stock.get('symbols', []),
            stock.get('isins', []),
            stock.get('metadata', {}).get('founded', 0),
            stock.get('metadata', {}).get('employees', 0)
        )

    def to_pyticker_symbol(self):
        sym = self.symbol
        symbols = self.get_symbols(self.symbols)
        if self.yahoo_symbols:
            symbols += self.yahoo_symbols
            symbols = filter_duplicate_dicts_in_list(symbols)

        if not sym:
            sym = next(map(lambda x: x['yahoo'], symbols), None)

        if sym and '.' in sym:
            sym = sym.split('.')[0]

        return {
            'name': self.name,
            'wiki_name': self.wiki_name,
            'symbol': sym if sym else self.get_symbol(self.symbols),
            'country': self.country,
            'indices': self.indices,
            'industries': self.industries,
            'symbols': symbols,
            'isins': self.isins,
            'metadata': self.metadata,
        }

    @property
    def name(self):
        return self.data['name']

    @name.setter
    def name(self, name):
        self.data['name'] = name

    @property
    def wiki_name(self):
        return self.data['wiki_name']

    @wiki_name.setter
    def wiki_name(self, wiki_name):
        self.data['wiki_name'] = wiki_name

    @property
    def symbol(self):
        return self.data['symbol']

    @symbol.setter
    def symbol(self, symbol):
        self.data['symbol'] = symbol

    @property
    def yahoo_symbols(self):
        return self.data['yahoo_symbols']

    @yahoo_symbols.setter
    def yahoo_symbols(self, symbols):
        self.data['yahoo_symbols'] = symbols

    @property
    def link(self):
        return self.data['link']

    @link.setter
    def link(self, link):
        self.data['link'] = link

    @property
    def link_lang(self):
        return self.data['link_lang']

    @link_lang.setter
    def link_lang(self, lang):
        self.data['link_lang'] = lang

    @property
    def country(self):
        return self.data['country']

    @country.setter
    def country(self, country):
        self.data['country'] = country

    @property
    def industries(self):
        return self.data['industries']

    @industries.setter
    def industries(self, industries):
        self.data['industries'] = industries

    @property
    def indices(self):
        return self.data['indices']

    @indices.setter
    def indices(self, indices):
        self.data['indices'] = indices

    @property
    def symbols(self):
        return self.data['symbols']

    @symbols.setter
    def symbols(self, symbols):
        self.data['symbols'] = symbols

    @property
    def isins(self):
        return self.data['isins']

    @isins.setter
    def isins(self, isins):
        self.data['isins'] = isins

    @property
    def metadata(self):
        return self.data['metadata']

    @metadata.setter
    def metadata(self, metadata):
        self.data['metadata'] = metadata

    @property
    def metadata_founded(self):
        return self.data['metadata']['founded']

    @metadata_founded.setter
    def metadata_founded(self, founded):
        if not isinstance(founded, int):
            raise ValueError('founded must be of type int')
        self.data['metadata']['founded'] = founded

    @property
    def metadata_employees(self):
        return self.data['metadata']['employees']

    @metadata_employees.setter
    def metadata_employees(self, employees):
        if not isinstance(employees, int):
            raise ValueError('employees must be of type int')
        self.data['metadata']['employees'] = employees

    @staticmethod
    def get_symbol(symbols):
        if not symbols:
            return None
        return min(map(lambda x: x.split('|')[-1], symbols))

    @staticmethod
    def get_symbols(symbols):
        # skip if allready transformed
        if all(map(lambda x: isinstance(x, dict), symbols)):
            return symbols
        if not symbols:
            return []
        result = []
        for exchange, sym in filter(
            lambda x: len(x) == 2, map(lambda x: x.split('|'), symbols)
        ):
            exc = exchange.upper().strip()
            if exc == 'FWB':
                result.append(
                    {
                        'yahoo': f'{sym}.F',
                        'google': f'FRA:{sym}',
                        'currency': 'EUR',
                    }
                )
            elif exc in ['NASDAQ', 'NASDAQSYMBOL']:
                result.append(
                    {
                        'yahoo': sym,
                        'google': f'NASDAQ:{sym}',
                        'currency': 'USD',
                    }
                )
            elif exc in ['NYSE', 'NEW YORK STOCK EXCHANGE']:
                result.append(
                    {'yahoo': sym, 'google': f'NYSE:{sym}', 'currency': 'USD'}
                )
            elif exc == 'Euronext':
                continue
            elif exc == 'LSE':
                continue
            elif exc == 'ASX':
                continue
            elif exc in ['BMAD', 'BMV']:
                continue
            elif exc == 'ISE':
                continue
            elif exc == 'MICEX-RTS':
                result.append(
                    {
                        'yahoo': f'{sym}.ME',
                        'google': f'MCX:{sym}',
                        'currency': 'RUB',
                    }
                )
        return result
