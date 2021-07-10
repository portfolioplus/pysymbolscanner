import re
import pycountry
import gettext
from unidecode import unidecode
from pysymbolscanner.stock import Stock
from pysymbolscanner.word_score import get_best_match
from pysymbolscanner.const import long_to_short
from pysymbolscanner.const import fallback_location


class Infobox:
    def __init__(
        self, name, founded, employees, loc, industry, symbols, isins
    ):
        self.name = name
        self.names = [name] if name else []
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

    def to_stock(self, index, symbol):
        symbols = [symbol] + self.symbols
        loc = fallback_location(index, self.location)
        return Stock(
            self.name,
            self.name,
            '',
            '',
            '' if not symbols else symbols[0],
            loc,
            index,
            self.industry,
            self.symbols,
            self.isins,
            self.founded,
            self.employees,
        )

    def update(self, infobox):
        if not self.name and infobox.name:
            self.name = long_to_short(infobox.name)
            self.names.append(self.name)
        elif infobox.name:
            self.names.append(long_to_short(infobox.name))
            # we take the name with the most occurrences
            if (
                len(set(map(self.names.count, self.names))) > 1
            ):  # checks if there is a max value
                self.name = long_to_short(
                    max(set(self.names), key=self.names.count)
                )
            else:
                self.name = self.names[0]
        if not self.founded:
            self.founded = infobox.founded
        if not self.employees:
            self.employees = infobox.employees
        if not self.location:
            self.location = infobox.location
        if not self.industry:
            self.industry = infobox.industry
        if not self.symbols:
            self.symbols = infobox.symbols
        elif infobox.symbols:
            self.symbols = list(set(self.symbols + infobox.symbols))
        elif infobox.isins:
            self.isins = list(set(self.isins + infobox.isins))


def clean_html(raw_html):
    cleaner = re.compile('<.*?>')
    cleantext = re.sub(cleaner, ' ', raw_html)
    cleantext = re.sub(' +', ' ', cleantext)
    return cleantext.strip()


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
    keys=[
        'native_name_lang',
        'location_country',
        'hq_location_country',
        'hq_location',
        'location',
        'land',
        'sitz',
        'siège (pays)',
        'sede',
    ],
):
    loc = get_value(infobox, keys)
    loc_translated = get_country(lang, loc if loc else str(infobox))
    if loc_translated:
        loc = loc_translated[0]
    return loc


def get_foundation_date(
    infobox,
    keys=[
        'foundation',
        'founded',
        'gründungsdatum',
        'date de création',
        'dates-clés',
        'fundación',
        'gründung_verein',
    ],
):
    founded = get_value(infobox, keys)
    if founded:
        founded = re.findall(r'\d{4}', founded)
        if founded:
            return int(min(founded))
    return ''


def get_employees(
    infobox, keys=['num_employees', 'mitarbeiterzahl', 'effectif', 'empleados']
):
    employees = get_value(infobox, keys)
    employees = employees.replace(',', '').replace('.', '')
    employees_items = re.findall(r'\d+', employees)
    if employees_items:
        employees = int(employees_items[0])
    return employees


def get_name(infobox, keys=['name', 'nam', 'nombre', 'unternehmen']):
    name = get_value(infobox, keys)
    regex_values = [
        r'{{color\|.+?\|(.+?)}}',
        r'{{[a-z]+\|(.+?)}}',
        r'\[\[#(.+?)\|.+?\]\]',
    ]
    for regex in regex_values:
        names = re.findall(regex, name)
        if names:
            return names[0]

    return clean_html(name)


def get_isins(infobox, keys=['isin', 'isin2', 'isin3', 'isin4']):
    result = []
    for key in keys:
        val = get_value(infobox, [key])
        if not val:
            continue
        isins = re.findall(r'([A-Z]{2}[A-Z0-9]{9}[0-9]{1})', val)
        if isins:
            result += isins
    return result


def get_symbols(infobox, keys=['traded_as', 'action', 'símbolo_bursátil']):
    val = get_value(infobox, keys)
    val = val.replace(r'\_', '')
    symbols = re.findall(r'{{([a-zA-Z0-9_: ]+)}}', val)
    if not symbols:
        symbols = re.findall(r'{{([a-zA-Z0-9_|\- ]+)}}', val)
    return symbols


def find_by_alpha_code(wiki_str, translate):
    result = None
    # find by alpha 2 or alpha 3 code
    for word_length in [3, 2]:
        if result:
            break

        extract = list(
            filter(
                lambda x, length=word_length: len(x) == length,
                wiki_str.lower().replace('.', '').split(' '),
            )
        )

        if not extract:
            continue

        word = extract[-1]
        result = next(
            filter(
                lambda key, length=word_length, alpha=word: translate[key][
                    length - 1
                ].lower()
                == alpha,
                translate,
            ),
            None,
        )
    return result


def get_country(loc, mystr):
    if not mystr:
        return None
    mystr = mystr.replace('.', '')
    mystr = clean_html(mystr)
    mystr = re.sub(r'[^0-9a-zA-Z _-]+', ' ', unidecode(mystr)).strip()
    mystr = mystr.replace('Russia', 'Russian Federation')
    mystr = mystr.replace('Russland', 'Russische Föderation')
    mystr = mystr.replace('England', 'United Kingdom')
    mystr = 'United States' if 'California' in mystr else mystr
    mystr = 'United States' if 'Florida' in mystr else mystr
    mystr = 'United Kingdom' if 'Jersey' in mystr else mystr
    mystr = 'Germany' if 'Berlin' in mystr and loc == 'en' else mystr
    mystr = 'Deutschland' if 'Berlin' in mystr and loc == 'de' else mystr
    mystr = 'Deutschland' if 'Düsseldorf' in mystr and loc == 'de' else mystr
    mystr = 'Germany' if 'Düsseldorf' in mystr and loc == 'en' else mystr
    mystr = 'United Kingdom' if 'Addlestone' in mystr else mystr
    mystr = 'France' if 'Vertou' in mystr and loc == 'en' else mystr
    mystr = 'Frankreich' if 'Vertou' in mystr and loc == 'de' else mystr
    mystr = 'United States' if 'New York City' in mystr else mystr

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

    # try to find the occurrence of country names in sentences
    country = next(
        filter(
            lambda key: unidecode(key.lower()) in unidecode(mystr.lower()),
            translate,
        ),
        None,
    )

    # try to find by alpha code
    if not country:
        country = find_by_alpha_code(mystr, translate)

    # try to find by similarity
    if not country:
        vals = list(translate.keys())
        words = mystr.split() if mystr.split() else mystr
        idx, score = max(
            map(lambda x: get_best_match(x, vals), words), key=lambda x: x[1]
        )
        if score > 0.8:
            country = vals[idx]
    # translate back to english
    if country:
        country = translate[country]
    return country


def parse_infobox(infobox, lang):
    if infobox is None:
        return None
    name = get_name(infobox)
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
    symbols = get_symbols(infobox)
    isins = get_isins(infobox)
    return name, founded, employees, loc, industry, symbols, isins
