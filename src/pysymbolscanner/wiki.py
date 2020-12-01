import wikipedia as wp
import wptools
from pysymbolscanner.word_score import get_best_match, get_scores
import re
import pycountry
import gettext


def _get_infobox_of_page(page, lang):
    infobox = wptools.page(page, lang=lang).get_parse().data['infobox']
    if infobox:
        infobox = {k.lower(): v for k, v in infobox.items()}
    return infobox


def _is_infobox(infobox):
    if infobox is None:
        return False
    infobox_items = [
        'name',
        'foundation',
        'hq_location_country',
        'location',
        'industry',
        'num_employees',
        'traded_as',
        'isin',
        'gründungsdatum',
        'mitarbeiterzahl',
    ]
    ctx = sum(map(lambda x: 1 if x in infobox else 0, infobox_items))
    if ctx > 1:
        return True
    return False


def get_infobox(page_search, lang_codes=['en', 'de', 'es', 'fr']):
    for lang in lang_codes:
        infobox = _get_infobox_of_page(page_search, lang)
        if _is_infobox(infobox):
            return lang, infobox
        wp.set_lang(lang)
        search = wp.search(page_search)
        scores = get_scores(page_search, search)
        scored_search = zip(scores, search)
        sorted_scored_search = list(
            sorted(scored_search, key=lambda tup: tup[0])
        )
        sorted_scored_search.reverse()
        for item in sorted_scored_search:
            infobox = _get_infobox_of_page(item[1], lang)
            if _is_infobox(infobox):
                return lang, infobox
    return None


def _get_value(infobox, keys):
    return next(
        filter(
            lambda x: x is not None,
            map(lambda key: infobox.get(key, None), keys),
        ),
        '',
    )

def _get_location(
    infobox,
    lang,
    keys=['location_country', 'hq_location_country', 'location', 'sitz'],
):
    loc = _get_value(infobox, keys)
    loc_translated = get_country(lang, loc if loc else str(infobox))
    if loc_translated:
        loc = loc_translated[0]
    return loc

def _get_foundation_date(
    infobox,
    keys=['foundation', 'founded', 'gründungsdatum'],
):
    founded = _get_value(infobox, keys)
    if founded:
        founded = re.findall(r'\d{4}', founded)
        if founded:
            return int(min(founded))
    return ''

def _get_employees(infobox, keys=['num_employees', 'mitarbeiterzahl']):
    employees = _get_value(infobox, keys)
    employees = employees.replace(',', '').replace('.', '')
    employees_items = re.findall(r'\d+', employees)
    if employees_items:
        employees = int(employees_items[0])
    return employees


def get_infobox_items(page_search, lang_codes=['en', 'de', 'es', 'fr']):
    infobox = get_infobox(page_search, lang_codes)
    if infobox is None or infobox[1] is None:
        return None
    lang, infobox = infobox
    name = infobox.get('name', '')
    loc = _get_location(infobox, lang)
    founded = _get_foundation_date(infobox)
    employees = _get_employees(infobox)

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


def get_merged_infoboxes(page_search, lang_codes=['en', 'de', 'es', 'fr']):
    keys = [
        'name',
        'founded',
        'employees',
        'loc',
        'industry',
        'symbols',
        'isins',
    ]
    infobox = dict.fromkeys(keys, [])
    for infobox_items in map(
        lambda lang: get_infobox_items(page_search, [lang]), lang_codes
    ):
        if infobox_items is None:
            continue
        infobox.update(dict(zip(keys, infobox_items)))
    return infobox


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
                lambda x: (_(x.name), (x.name, x.alpha_2, x.alpha_3)), pycountry.countries
            )
        )
    else:
        translate = dict(
            map(lambda x: (x.name, (x.name, x.alpha_2, x.alpha_3)), pycountry.countries)
        )

    country = next(
        filter(
            lambda key: key.lower() in mystr.lower()
            or translate[key][1].lower() == mystr.replace('.', '').lower()
            or translate[key][2].lower() == mystr.replace('.', '').lower(),
            translate,
        ),
        None,
    )
    if not country:
        extract = list(filter(lambda x: len(x) == 2, mystr.lower().replace('.', '').split(' ')))
        if extract:
            extract = extract[-1]
            country = next(
                filter(
                    lambda key: translate[key][1].lower() == extract,
                    translate,
                ),
                None,
            )
    if not country:
        extract = list(filter(lambda x: len(x) == 3, mystr.lower().replace('.', '').split(' ')))
        if extract:
            extract = extract[-1]
            country = next(
                filter(
                    lambda key: translate[key][2].lower() == extract,
                    translate,
                ),
                None,
            )
    if country:
        country = translate[country]
    return country