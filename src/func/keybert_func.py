from keybert import KeyBERT


def extract_keyword(text, kw_len_fr=1, kw_len_to=1, diversity=0.5, kw_num=10):
    # best model for multilingual documents according to KeyBERT, but much slower
    # for Japanese or Chinese, tokenizing the text before feeding to the model would be a better choice
    # kw_model = KeyBERT(model="paraphrase-multilingual-MiniLM-L12-v2")

    # KeyBERT also support embedding models, including Flair, Spacy, as well as LLM.
    # In this demo app, I use the default built-in model: "all-MiniLM-L6-v2"
    kw_model = KeyBERT()
    # use Maximal Marginal Relevance here, support other algorithms
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(kw_len_fr, kw_len_to),
                                         use_mmr=True, diversity=diversity, top_n=kw_num)
    return keywords
