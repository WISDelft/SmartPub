from nltk.tokenize import word_tokenize, sent_tokenize
from string import punctuation
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models

import gensim
from pyhelpers import tools

"""
Silly example of LDA
"""
"""

doc_a = "Brocolli is good to eat. My brother likes to eat good brocolli, but not my mother."
doc_b = "My mother spends a lot of time driving my brother around to baseball practice."
doc_c = "Some health experts suggest that driving may cause increased tension and blood pressure."
doc_d = "I often feel pressure to perform well at school, but my mother never seems to drive my brother to do better."
doc_e = "Health professionals say that brocolli is good for your health."

# compile sample documents into a list
doc_set = [doc_a, doc_b, doc_c, doc_d, doc_e]

raw = doc_a.lower()
tokens = word_tokenize(raw)

# create English stop words list with punctuations
en_stop = set(stopwords.words('english') + list(punctuation))

# remove stop words from tokens
stopped_tokens = [i for i in tokens if i not in en_stop]


# Create p_stemmer of class PorterStemmer
p_stemmer = PorterStemmer()

# stem token
texts = [p_stemmer.stem(i) for i in stopped_tokens]
print(texts)
# Constructing a document-term matrix
# parse an array of tokens
dictionary = corpora.Dictionary([texts])
print(dictionary)

corpus = [dictionary.doc2bow(text) for text in [texts]]
print(corpus)

# corpus is a document-term matrix and now we’re ready to generate an LDA model
ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=3, id2word = dictionary, passes=20)

print(ldamodel.print_topics(num_topics=3, num_words=3))

ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=2, id2word = dictionary, passes=20)
print(ldamodel.print_topics(num_topics=2, num_words=4))

##### end of the silly example
"""

def main():
    # mongo search query
    mongo_string_search = {"dblpkey":"journals_mala_Wadler00"}
    db = tools.connect_to_mongo()
    # set no_cursor_timeout= true, to avoid "pymongo.errors.CursorNotFound"
    result = db.publications.find(mongo_string_search, no_cursor_timeout=True)
    en_stop = set(stopwords.words('english') + list(punctuation))

    for r in result:
        fulltext = r['content']['fulltext']
        tokens = word_tokenize(fulltext)

        stopped_tokens = [i for i in tokens if i not in en_stop]
        print(stopped_tokens)
        dictionary = corpora.Dictionary([stopped_tokens])
        corpus = [dictionary.doc2bow(text) for text in [stopped_tokens]]
        ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=2, id2word=dictionary, passes=20)

    print(ldamodel.print_topics(num_topics=2, num_words=5))


if __name__ == '__main__':
    main()