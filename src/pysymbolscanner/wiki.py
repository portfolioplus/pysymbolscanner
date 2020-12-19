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


def _is_in_infobox(infobox, search):
    search = search.replace('Rosagro', 'Rusagro')
    search_items = [search] if len(search.split()) == 0 else search.split()
    values = list(filter(lambda x: x not in most_common_endings, search_items))
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


def get_wiki_page_title_and_links(link, lang_codes):
    get_url = requests.get(link)
    get_text = get_url.text
    soup = BeautifulSoup(get_text, "html.parser")
    company = soup.find('h1').text
    links = soup.findAll(
        'a', href=True, attrs={'class': 'interlanguage-link-target'}
    )
    links = list(
        filter(
            lambda x: x[1] in lang_codes,
            map(lambda x: (x['href'], x['lang']), links),
        )
    )
    return company, links


def get_merged_infobox(page_search, link, link_lang, lang_codes=None):
    if lang_codes is None:
        lang_codes = ['en', 'de', 'es', 'fr']
    result = None
    page_search_dict = dict(map(lambda x: (x, None), lang_codes))

    # find all wikipages for company name
    if link and link_lang:
        wiki_url = get_wiki_url(link_lang, link.replace('/wiki/', ''))
        company, links = get_wiki_page_title_and_links(
            wiki_url, lang_codes
        )
        page_search_dict[link_lang] = company
        for wiki_link, wiki_link_lang in links:
            company, _ = get_wiki_page_title_and_links(
                wiki_link, lang_codes
            )
            page_search_dict[wiki_link_lang] = company

    # get all infobox data for each wikipage
    for lang in lang_codes:
        if not page_search_dict[lang]:
            continue
        infobox = get_infobox(page_search_dict[lang], [lang])
        if infobox is None:
            continue

        if result:
            result.update(infobox)
        else:
            result = infobox

    return result


def get_wiki_url(lang, title):
    return f'https://{lang}.wikipedia.org/wiki/{title}'
