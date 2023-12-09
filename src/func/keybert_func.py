from keybert import KeyBERT


def extract_keyword(text, kw_len_fr=1, kw_len_to=3, diversity=0.5, kw_num=5):
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(kw_len_fr, kw_len_to),
                                         use_mmr=True, diversity=diversity, top_n=kw_num)
    return keywords

