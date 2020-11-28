import wikipedia as wp
import wptools
from pysymbolscanner.word_score import get_best_match, get_scores
import re
import pycountry
import gettext


def get_infobox(page_search):
    lang_codes = ['en', 'de', 'es', 'fr']
    for lang in lang_codes:
        wp.set_lang(lang)
        search = wp.search(page_search)
        scores = get_scores(page_search, search)
        scored_search = zip(scores, search)
        sorted_scored_search = sorted(scored_search, key=lambda tup: tup[0])
        for item in sorted_scored_search:

        try:
            infobox = (
                wptools.page(page_search, lang=lang)
                .get_parse()
                .data['infobox']
            )
            if infobox is None:
                raise EnvironmentError
            return (lang, infobox)
        except:
            try:

                if search:
                    idx, score = get_best_match(page_search, search)
                    if score > 0.75:
                        return (
                            lang,
                            wptools.page(search[idx], lang=lang).get_parse(),
                        )
            except:
                pass
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
    return name, founded, employees, loc, industry, symbols


def get_country(loc, mystr):
    if not mystr:
        return None

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