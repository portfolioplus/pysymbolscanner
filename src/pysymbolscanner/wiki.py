import wikipedia as wp
import wptools
from pysymbolscanner.infobox import Infobox
from pysymbolscanner.const import (
    blocklist_search,
    most_common_endings,
    remove_most_common_endings,
)
import requests
from bs4 import BeautifulSoup


def _get_infobox_of_page(name, check_item, lang):
    try:
        if lang == 'es':
            opt = {
                'boxterm': 'Ficha',
                'skip': ['imageinfo'],
                'silent': True,
                'lang': lang,
            }
        else:
            opt = {'skip': ['imageinfo'], 'silent': True, 'lang': lang}
        page = wptools.page(name, **opt).get_parse()
        # search item must be in data
        search_str = str(page.data.get('wikitext', '')).lower()
        check_item_search = remove_most_common_endings(check_item).lower()
        name_search = remove_most_common_endings(name).lower()
        ctx_name = max(
            (
                search_str.count(check_item_search),
                search_str.count(name_search),
            )
        )
        if name_search != check_item_search and ctx_name < 5:
            return None
        infobox = page.data['infobox']
        if infobox:
            infobox = {k.lower(): v for k, v in infobox.items()}
        return infobox
    except LookupError:
        return None


def _is_infobox(infobox):
    if infobox is None:
        return False
    infobox_items = [
        'nam',
        'effectif',
        'date de création',
        'siège (pays)',
        'name',
        'foundation',
        'hq_location_country',
        'unternehmen',
        'gründung_verein',
        'location',
        'industry',
        'num_employees',
        'traded_as',
        'isin',
        'gründungsdatum',
        'mitarbeiterzahl',
        'nombre',
        'empleados',
        'sede',
        'sitz',
    ]
    ctx = sum(map(lambda x: 1 if x in infobox else 0, infobox_items))
    if ctx > 1:
        return True
    return False


def _is_in_infobox(infobox, value):
    value = value.replace('Rosagro', 'Rusagro')
    values = [value] if len(value.split()) == 0 else value.split()
    values = list(filter(lambda x: x not in most_common_endings, values))
    ctx = 0
    for value in values:
        if any(
            map(
                lambda x, val=value: val.lower() in x.lower(), infobox.values()
            )
        ):
            ctx += 1
    result = ctx / len(values) > 0.5
    return result


def get_wiki_infobox(page_search, lang_codes=['en', 'de', 'es', 'fr']):
    for lang in lang_codes:
        wp.set_lang(lang)
        search = filter(
            lambda x: x not in blocklist_search,
            wp.search(page_search, results=3),
        )
        if not search:
            continue
        for item in search:
            infobox = _get_infobox_of_page(item, page_search, lang)
            if _is_infobox(infobox):
                return infobox, lang
    return None


def get_infobox(page_search, lang_codes=['en', 'de', 'es', 'fr']):
    infobox = get_wiki_infobox(page_search, lang_codes)
    if infobox is None or infobox[1] is None:
        return None
    parsed_infobox = Infobox.from_wiki_infobox(*infobox)
    if not parsed_infobox.name:
        parsed_infobox.name = page_search
        parsed_infobox.names.append(page_search)
    return parsed_infobox


def get_merged_infobox(page_search, link, link_lang, lang_codes=None):
    if lang_codes is None:
        lang_codes = ['en', 'de', 'es', 'fr']
    result = None
    # find wiki name
    if link and link_lang:
        wiki_url = get_wiki_url(link_lang, link.replace('/wiki/', ''))
        get_url = requests.get(wiki_url)
        get_text = get_url.text
        soup = BeautifulSoup(get_text, "html.parser")
        company = soup.find('h1').text
        if company:
            page_search = company

    for infobox in map(
        lambda lang, search=page_search: get_infobox(search, [lang]),
        lang_codes,
    ):
        if infobox is None:
            continue

        if result:
            result.update(infobox)
        else:
            result = infobox

        if result.name:
            page_search = result.name
    return result


def get_wiki_url(lang, title):
    return f'https://{lang}.wikipedia.org/wiki/{title}'
