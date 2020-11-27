import wikipedia as wp
import wptools
from pysymbolscanner.word_score import get_best_match
import re
import pycountry
import gettext

def get_page(page_search):
    lang_codes = ['en', 'de', 'es', 'fr']
    for lang in lang_codes:
        try:
            return (
                lang,
                wptools.page(
                    page_search, lang=lang, silent=True, verbose=False
                ).get_parse(),
            )
        except:
            try:
                wp.set_lang(lang)
                search = wp.search(page_search)
                if search:
                    idx, score = get_best_match(page_search, search)
                    if score > 0.75:
                        return (
                            lang,
                            wptools.page(
                                search[idx],
                                lang=lang,
                                silent=True,
                                verbose=False,
                            ).get_parse(),
                        )
            except:
                pass
    return None


def get_infobox(page_search):
    page = get_page(page_search)
    if page:
        lang, page = page
        return lang, page.data.get('infobox', None)
    return None


def get_infobox_items(page_search):
    infobox = get_infobox(page_search)
    if not infobox:
        return None
    lang, infobox = infobox
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
    locs = get_countries(lang, loc if loc else str(infobox))
    if locs:
        loc = locs[0]
    if employees_items:
        employees = int(employees_items[0])
    if founded:
        founded = int(min(founded))
    industry = re.findall(
        r'\[[a-zA-Z_ ]+\|([a-zA-Z_ ]+)\]', infobox.get('industry', '')
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
    return founded, employees, loc, industry, symbols


def get_countries(loc, mystr):
    if loc != 'en':
        german = gettext.translation('iso3166', pycountry.LOCALES_DIR, languages=[loc])
        german.install()
    items = list(
        filter(
            lambda x: x[0].lower() in mystr.lower()
            or x[1].lower() == mystr.replace('.', '').lower(),
            map(
                lambda cou: (cou.name, cou.alpha_2),
                pycountry.countries,
            ),
        )
    )
    item = None if len(items) > 0 else items[0]
    if loc != 'en':
        eng = gettext.translation('iso3166', pycountry.LOCALES_DIR, languages=[loc])
        eng.install()
    return item