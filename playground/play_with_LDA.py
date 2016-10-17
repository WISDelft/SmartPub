from nltk.tokenize import word_tokenize, sent_tokenize
from string import punctuation
from nltk.corpus import stopwords, PlaintextCorpusReader, words
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
from nltk import  Text, FreqDist

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
def lda_per_chapter(db,mongo_search_string):
    # set no_cursor_timeout= true, to avoid "pymongo.errors.CursorNotFound"
    result = db.publications.find(mongo_search_string, no_cursor_timeout=True)
    en_stop = set(stopwords.words('english') + list(punctuation))

    for r in result:
        # fulltext = r['content']['chapters']
        chapter_text = ""
        for chapter in r['content']['chapters']:
            for paragraph in chapter['paragraphs']:
                chapter_text += paragraph
            sentences = sent_tokenize(chapter_text)
            for sent in sentences:
                tokens = word_tokenize(sent)
                stopped_tokens = [i for i in tokens if i not in en_stop]
                dictionary = corpora.Dictionary([stopped_tokens])
                corpus = [dictionary.doc2bow(text) for text in [stopped_tokens]]
                ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=2, id2word=dictionary, passes=50)
                print(ldamodel.print_topics(num_topics=2, num_words=3))

def common_statistics(db, mongo_search_string):
    # set no_cursor_timeout= true, to avoid "pymongo.errors.CursorNotFound"
    result = db.publications.find(mongo_search_string, no_cursor_timeout=True)
    en_stop = set(stopwords.words('english') + list(punctuation))

    for r in result:
        fulltext = r['content']['fulltext']
        words = word_tokenize(fulltext)
        fulltext_text = Text(words)
        # find bigrams that occur more often than we would expect based
        # on the frequency of individual words
        print(fulltext_text.collocations())
        # find the vocabulary of the paper
        words = [w.lower() for w in words if w.isalpha() and w not in en_stop]
        plot_frequency(words)
        findStats(fulltext)
        print(unusual_words(words))
        print(content_fraction(words))


def unusual_words(words):
    text_vocab = set(w.lower() for w in words if w.isalpha())
    english_vocab = set(w.lower() for w in words.words())
    unusual = text_vocab.difference(english_vocab)
    return sorted(unusual)


def plot_frequency(words):
    freq = FreqDist(words)
    freq.plot(50, cumulative=False)


#find out the stopwords ratio
def content_fraction(text):
    stop = stopwords.words('english')
    content = [w for w in text if w.lower() not in stop]
    return len(content)/len(text)


def findStats(fulltext):
    """
    find average sentence length, and the number of times
    each vocabulary item appears in the text on average (our lexical diversity score)
    :param fulltext: the entire raw text
    :return:
    """
    num_words = len(word_tokenize(fulltext))
    num_sents = len(sent_tokenize(fulltext))
    num_vocab = len(set([w.lower() for w in word_tokenize(fulltext)]))
    print(int(num_words / num_sents), int(num_words / num_vocab))


def main():
    # mongo search query
    mongo_string_search = {"dblpkey":"journals_ijclclp_WuC07"}
    db = tools.connect_to_mongo()
    # lda_per_chapter(db= db,mongo_search_string= mongo_string_search)
    common_statistics(db= db,mongo_search_string= mongo_string_search)

if __name__ == '__main__':
    main()