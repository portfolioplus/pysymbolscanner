from difflib import SequenceMatcher
from pysymbolscanner.const import long_to_short


def _remove(word, word_filter):
    for old in word_filter:
        word = word.replace(old, '').strip()
        word = ' '.join(word.split())
        word = word.strip()
    return word


def _search(sentence_a, sentence_b, ignore):
    words_a = [sentence_a] if not sentence_a.split() else sentence_a.split()
    words_b = [sentence_b] if not sentence_b.split() else sentence_b.split()
    words_a = list(filter(lambda x: x not in ignore, words_a))
    words_b = list(filter(lambda x: x not in ignore, words_b))
    for word_a in words_a:
        for word_b in words_b:
            if word_a == word_b:
                return True
    return False


def get_best_match(word, items, word_filter=[]):
    if word_filter:
        new_word = _remove(word, word_filter)
        word = new_word if new_word else word
        items = list(
            map(
                lambda x: x[1] if x[1] else x[0],
                map(lambda x: (x, _remove(x, word_filter)), items),
            )
        )

    socres = list(get_scores(word, items))
    max_score = max(socres)
    idx_max_score = socres.index(max_score)
    return idx_max_score, max_score


def deep_search(word, items, ignore=[]):
    ignore = list(map(lambda x: x.lower(), ignore))
    word = long_to_short(word)
    result = []
    for idx, item in enumerate(items):
        if _search(item.lower(), word.lower(), ignore):
            result.append(idx)
    if not result:
        return -1, -1
    idx_max_score, max_score = get_best_match(
        word, map(lambda idx: items[idx], result)
    )
    return result[idx_max_score], max_score


def get_scores(word, items):
    return map(
        lambda item: get_score(word, item),
        items,
    )


def get_score(word_a, word_b):
    return SequenceMatcher(None, word_a.lower(), word_b.lower()).ratio()
