from difflib import SequenceMatcher


def get_best_match(word, items):
    socres = list(
        map(
            lambda tu: SequenceMatcher(None, tu[0], tu[1]).ratio(),
            map(lambda item: (word.lower(), item.lower()), items),
        )
    )
    max_score = max(socres)
    idx = socres.index(max_score)
    return idx, max_score


def get_scores(word, items):
    return map(
        lambda item: get_score(word, item),
        items,
    )


def get_score(word_a, word_b):
    return SequenceMatcher(None, word_a.lower(), word_b.lower()).ratio()


def get_word_list_diff(words_a, words_b):
    words_a = sorted(words_a)
    words_b = sorted(words_b)

    result = []
    stocks_b_short = list(
        map(lambda x: x.split()[0] if len(x.split()) > 0 else x, words_b)
    )
    for ida, stock_a in enumerate(words_a):
        _, max_score = get_best_match(stock_a, words_b)
        if max_score > 0.75:
            result.append(ida)
        else:
            word_splited = stock_a.split()
            if not word_splited:
                continue
            _, max_score_short = get_best_match(
                word_splited[0], stocks_b_short
            )
            if max_score_short == 1.0:
                result.append(ida)
    missing = [value for idx, value in enumerate(words_a) if idx not in result]
    return missing
