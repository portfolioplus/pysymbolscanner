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
    ]
    ctx = sum(map(lambda x: 1 if x in infobox else 0, infobox_items))
    if ctx > 1:
        return True
    return False


def get_infobox(page_search):
    lang_codes = ['en', 'de', 'es', 'fr']
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


def get_infobox_items(page_search):
    infobox = get_infobox(page_search)
    if infobox is None or infobox[1] is None:
        return None
    lang, infobox = infobox
    name = infobox.get('name', '')
    founded = infobox.get('foundation', '')
    founded = re.findall(r'\d{4}', founded)
    if not founded:
        founded = infobox.get('founded', '')
        founded = re.findall(r'\d{4}', founded)
    employees_str = (
        infobox.get('num_employees', '').replace(',', '').replace('.', '')
    )
    employees_items = re.findall(r'\d+', employees_str)
    loc = infobox.get('location_country', '')
    if not loc:
        loc = infobox.get('hq_location_country', '')
    if not loc:
        loc = infobox.get('location', '')
    loc_translated = get_country(lang, loc if loc else str(infobox))
    if loc_translated:
        loc = loc_translated[0]
    if employees_items:
        employees = int(employees_items[0])
    if founded:
        founded = int(min(founded))
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
                lambda x: (_(x.name), (x.name, x.alpha_2)), pycountry.countries
            )
        )
    else:
        translate = dict(
            map(lambda x: (x.name, (x.name, x.alpha_2)), pycountry.countries)
        )

    country = next(
        filter(
            lambda key: key.lower() in mystr.lower()
            or translate[key][1].lower() == mystr.replace('.', '').lower(),
            translate,
        ),
        None,
    )
    if country:
        country = translate[country]
    return country