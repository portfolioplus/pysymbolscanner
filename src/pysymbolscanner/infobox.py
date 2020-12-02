import re
import pycountry
import gettext
from pysymbolscanner.stock import Stock


class Infobox:
    def __init__(
        self, name, founded, employees, loc, industry, symbols, isins
    ):
        self.name = name
        self.founded = founded
        self.employees = employees
        self.location = loc
        self.industry = industry
        self.symbols = symbols
        self.isins = isins

    @classmethod
    def from_wiki_infobox(cls, infobox, lang):
        if not infobox:
            return None
        infobox_items = parse_infobox(infobox, lang)
        if not infobox_items:
            return None
        return cls(*infobox_items)

    def to_stock(self, index):
        return Stock(
            '',
            self.name,
            '' if not self.symbols else self.symbols[0],
            self.location,
            index,
            self.industry,
            self.symbols,
            self.isins,
            self.employees,
            self.founded,
        )


def get_value(infobox, keys):
    return next(
        filter(
            lambda x: x is not None,
            map(lambda key: infobox.get(key, None), keys),
        ),
        '',
    )


def get_location(
    infobox,
    lang,
    keys=['location_country', 'hq_location_country', 'location', 'sitz'],
):
    loc = get_value(infobox, keys)
    loc_translated = get_country(lang, loc if loc else str(infobox))
    if loc_translated:
        loc = loc_translated[0]
    return loc


def get_foundation_date(
    infobox,
    keys=['foundation', 'founded', 'gründungsdatum'],
):
    founded = get_value(infobox, keys)
    if founded:
        founded = re.findall(r'\d{4}', founded)
        if founded:
            return int(min(founded))
    return ''


def get_employees(infobox, keys=['num_employees', 'mitarbeiterzahl']):
    employees = get_value(infobox, keys)
    employees = employees.replace(',', '').replace('.', '')
    employees_items = re.findall(r'\d+', employees)
    if employees_items:
        employees = int(employees_items[0])
    return employees


def get_country(loc, mystr):
    if not mystr:
        return None

    mystr = re.sub('[^0-9a-zA-Z _\-]+', '', mystr)

    if loc != 'en':
        # load language of wiki page
        lang = gettext.translation(
            'iso3166', pycountry.LOCALES_DIR, languages=[loc]
        )
        lang.install()
        _ = lang.gettext
        translate = dict(
            map(
                lambda x: (_(x.name), (x.name, x.alpha_2, x.alpha_3)),
                pycountry.countries,
            )
        )
    else:
        translate = dict(
            map(
                lambda x: (x.name, (x.name, x.alpha_2, x.alpha_3)),
                pycountry.countries,
            )
        )

    # find by name
    country = next(
        filter(
            lambda key: key.lower() in mystr.lower(),
            translate,
        ),
        None,
    )

    # find by alpha 2 or alpha 3 code
    for word_length in [2, 3]:
        if country:
            break
        extract = list(
            filter(
                lambda x, length=word_length: len(x) == length,
                mystr.lower().replace('.', '').split(' '),
            )
        )
        if extract:
            word = extract[-1]
            country = next(
                filter(
                    lambda key, length=word_length, alpha=word: translate[key][
                        length - 1
                    ].lower()
                    == alpha,
                    translate,
                ),
                None,
            )
    if country:
        country = translate[country]
    return country


def parse_infobox(infobox, lang):
    if infobox is None:
        return None
    name = infobox.get('name', '')
    loc = get_location(infobox, lang)
    founded = get_foundation_date(infobox)
    employees = get_employees(infobox)

    industry = []
    if lang == 'en':
        industry = re.findall(
            r'\[[a-zA-Z_ ()]+\|([a-zA-Z_ ]+)\]', infobox.get('industry', '')
        )
        if not industry:
            industry = re.findall(
                r'\[\[([a-zA-Z_ ]+)\]\]', infobox.get('industry', '')
            )
    symbols = re.findall(r'{{([a-zA-Z_: ]+)}}', infobox.get('traded_as', ''))
    if not symbols:
        symbols = re.findall(
            r'{{([a-zA-Z_| ]+)}}', infobox.get('traded_as', '')
        )
    isins = []
    if 'isin' in infobox:
        isins.append(infobox['isin'])
    if 'isin2' in infobox:
        isins.append(infobox['isin2'])
    return name, founded, employees, loc, industry, symbols, isins
