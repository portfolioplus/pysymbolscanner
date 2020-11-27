import wikipedia as wp
import wptools
from pysymbolscanner.word_score import get_best_match
import re
import pycountry


def get_page(page_search):
    lang_codes = ['en', 'de', 'es', 'fr']
    for lang in lang_codes:
        try:
            return wptools.page(
                page_search, lang=lang, silent=True, verbose=False
            ).get_parse()
        except:
            try:
                wp.set_lang(lang)
                search = wp.search(page_search)
                if search:
                    idx, score = get_best_match(page_search, search)
                    if score > 0.75:
                        return wptools.page(
                            search[idx], lang=lang, silent=True, verbose=False
                        ).get_parse()
            except:
                pass
    return None


def get_infobox(page_search):
    page = get_page(page_search)
    if page:
        return page.data.get('infobox', None)
    return None


def get_infobox_items(page_search):
    infobox = get_infobox(page_search)
    if not infobox:
        return None
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
    locs = get_countries(loc if loc else str(infobox))
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


def get_countries(mystr):
    items = filter(
        lambda x: x in mystr, map(lambda cou: cou.name, pycountry.countries)
    )
    return list(items)