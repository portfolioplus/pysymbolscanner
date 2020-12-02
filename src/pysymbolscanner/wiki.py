import wikipedia as wp
import wptools
from pysymbolscanner.word_score import get_scores
from pysymbolscanner.infobox import Infobox


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


def get_wiki_infobox(page_search, lang_codes=['en', 'de', 'es', 'fr']):
    for lang in lang_codes:
        infobox = _get_infobox_of_page(page_search, lang)
        if _is_infobox(infobox):
            return infobox, lang
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
                return infobox, lang
    return None


def get_infobox(page_search, lang_codes=['en', 'de', 'es', 'fr']):
    infobox = get_wiki_infobox(page_search, lang_codes)
    if infobox is None or infobox[1] is None:
        return None
    return Infobox.from_wiki_infobox(*infobox)


def get_merged_infobox(page_search, lang_codes=['en', 'de', 'es', 'fr']):
    infoboxes = []
    for infobox in map(
        lambda lang: get_infobox(page_search, [lang]), lang_codes
    ):
        if infobox is None:
            continue
        infoboxes.append(infobox)
    return infoboxes
