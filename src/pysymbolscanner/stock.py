class Stock:
    def __init__(
        self,
        name,
        wiki_name,
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
            'symbol': main_symbol,
            'country': loc,
            'indices': indices,
            'industries': industry,
            'symbols': symbols,
            'isins': isins,
            'metadata': {'founded': founded, 'employees': employees},
        }

    @classmethod
    def from_wiki(cls, indices, wiki_name, symbol):
        return cls('', wiki_name, symbol, '', indices, [], [], [], 0, 0)

    def to_pyticker_symbol(self):
        return {
            'name': self.name,
            'symbol': self.symbol,
            'country': self.country,
            'indices': self.indices,
            'industries': self.industries,
            'symbols': self.symbols,
            'isins': self.isins,
            'metadata': self.metadata
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
