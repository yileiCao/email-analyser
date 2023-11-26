from keybert import KeyBERT


def extract_keyword(text):
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 3), use_mmr=True, diversity=0.5)
    return keywords


if __name__ == '__main__':
    pass