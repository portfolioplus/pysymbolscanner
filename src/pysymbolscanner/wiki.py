import wikipedia as wp
import wptools
from pysymbolscanner.infobox import Infobox


def _get_infobox_of_page(name, lang):
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
        'sitz'
    ]
    ctx = sum(map(lambda x: 1 if x in infobox else 0, infobox_items))
    if ctx > 1:
        return True
    return False


def _is_in_infobox(infobox, value):
    ignore = [
        'SA',
        'S.A.',
        'Aktiengeselschaft',
        'AG',
        'Ag',
        'ag',
        'SE',
        'S.E.',
        'plc',
        'Plc',
        'PLC',
        'GmbH',
        '&',
        'Co.',
        'KGaA',
        'Corp.',
        'Co.',
        'Inc.'
        '(Class C)',
        '(Class B)',
        '(Class A)',
        '(A)',
        '(B)',
        '(C)',
        'OJSC',
        'PJSC',
    ]
    value = value.replace('Rosagro', 'Rusagro')
    values = [value] if len(value.split()) == 0 else value.split()
    values = list(filter(lambda x: x not in ignore, values))
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
        search = wp.search(page_search, results=3)
        if not search:
            continue
        for item in search:
            infobox = _get_infobox_of_page(item, lang)
            if _is_infobox(infobox) and _is_in_infobox(infobox, page_search):
                return infobox, lang
    return None


def get_infobox(page_search, lang_codes=['en', 'de', 'es', 'fr']):
    infobox = get_wiki_infobox(page_search, lang_codes)
    if infobox is None or infobox[1] is None:
        return None
    parsed_infobox = Infobox.from_wiki_infobox(*infobox)
    if not parsed_infobox.name:
        parsed_infobox.name = page_search
    return parsed_infobox


def get_merged_infobox(page_search, lang_codes=['en', 'de', 'es', 'fr']):
    result = None
    for infobox in map(
        lambda lang: get_infobox(page_search, [lang]), lang_codes
    ):
        if infobox is None:
            continue

        if result:
            result.update(infobox)
        else:
            result = infobox
    return result
