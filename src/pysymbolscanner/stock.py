class Stock:
    def __init__(
        self,
        name,
        short_name,
        main_symbol,
        loc,
        index,
        industry,
        symbols,
        isins,
        founded,
        employees,
    ):
        self.data = {
            'name': name,
            'short_name': short_name,
            'symbol': main_symbol,
            'country': loc,
            'indices': index,
            'industries': industry,
            'symbols': symbols,
            'isins': isins,
            'metadata': {'founded': founded, 'employees': employees},
        }

    @classmethod
    def from_wiki(cls, index, short_name, symbol):
        return cls('', short_name, symbol, '', index, [], [], [], 0, 0)
