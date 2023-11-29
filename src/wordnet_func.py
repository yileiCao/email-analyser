import nltk
from nltk.corpus import wordnet as wn


def get_lemmas_en(word):
    e_set = set()
    for ss in wn.synsets(word):
        if ss.name().endswith('01') or ss.name().endswith('02'):
            e_set.update(ss.lemma_names())
    e_result = '|'.join(e_set)
    return e_result


def get_lemmas_jpn(word):
    j_set = set()
    for ss in wn.synsets(word):
        if ss.name().endswith('01') or ss.name().endswith('02'):
            j_set.update(ss.lemma_names('jpn'))
    j_set = list(j_set)
    for idx, word in enumerate(j_set):
        j_set[idx] = word.split('+')[0]
    j_result = '|'.join(j_set)
    return j_result

