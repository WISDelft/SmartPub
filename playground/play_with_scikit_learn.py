from pyhelpers import tools
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import numpy as np
import pandas as pd
import nltk
import re
import os
import codecs
from sklearn import feature_extraction
import mpld3
import os  # for os.path.basename

import matplotlib.pyplot as plt
import matplotlib as mpl
import string
from nltk.tag import pos_tag

from sklearn.manifold import MDS


import sys
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib

from sklearn.cluster import KMeans

from gensim import corpora, models, similarities
# load nltk's SnowballStemmer as variabled 'stemmer'
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")

# here I define a tokenizer and stemmer which returns the set of stems in the text that it is passed

def tokenize_and_stem(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems


def tokenize_only(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    return filtered_tokens




def create_dataset(db,mongo_search_string):
    mylist = {"data": {}}

    documents = db.publications.find(mongo_search_string, no_cursor_timeout=True)
    paragraphs = []
    for i, doc in enumerate(documents):
        for chapter in doc['content']['chapters']:
            par = ""
            # paragraphs.append(chapter['paragraphs'])
            for paragraph in chapter['paragraphs']:
                par += str(paragraph)
                # words = word_tokenize(paragraph)
                # stop = stopwords.words('english')
                # normalize_words = [w.lower() for w in words if w not in stop if w.isalpha()]
                paragraphs.append(par)

    return paragraphs


def strip_proppers(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent) if word.islower()]
    return "".join(
        [" " + i if not i.startswith("'") and i not in string.punctuation else i for i in tokens]).strip()


def strip_proppers_POS(text):
    tagged = pos_tag(text.split())  # use NLTK's part of speech tagger
    non_propernouns = [word for word, pos in tagged if pos != 'NNP' and pos != 'NNPS']
    return non_propernouns

def main():
    # mongo search query
    mongo_string_search = {"dblpkey":"journals_ijclclp_WuC07"}
    # mongo_string_search = {"dblpkey" : {"$in": ["journals_ijclclp_WuC07", "journals_mala_Wadler00"]}}
    db = tools.connect_to_mongo()
    # lda_per_chapter(db= db,mongo_search_string= mongo_string_search)
    paragraphs = create_dataset(db= db,mongo_search_string= mongo_string_search)
    # print(mylists)
    print(paragraphs[3][:10])

    # not super pythonic, no, not at all.
    # use extend so it's a big flat list of vocab
    totalvocab_stemmed = []
    totalvocab_tokenized = []
    for i in paragraphs:
        allwords_stemmed = tokenize_and_stem(i)  # for each item in 'synopses', tokenize/stem use str not list obj
        totalvocab_stemmed.extend(allwords_stemmed)  # extend the 'totalvocab_stemmed' list

        allwords_tokenized = tokenize_only(i)
        totalvocab_tokenized.extend(allwords_tokenized)

    vocab_frame = pd.DataFrame({'words': totalvocab_tokenized}, index=totalvocab_stemmed)
    print('there are ' + str(vocab_frame.shape[0]) + ' items in vocab_frame')

    print(vocab_frame.head())
    # define vectorizer parameters
    tfidf_vectorizer = TfidfVectorizer(max_df=0.8, max_features=200000,
                                       min_df=0.2, stop_words='english',
                                       use_idf=True, tokenizer=tokenize_and_stem, ngram_range=(1, 3))


    tfidf_matrix = tfidf_vectorizer.fit_transform(paragraphs)  # fit the vectorizer to synopses
    print(tfidf_matrix.shape)
    terms = tfidf_vectorizer.get_feature_names()
    print(terms)
    dist = 1 - cosine_similarity(tfidf_matrix)

    num_clusters = 10

    km = KMeans(n_clusters=num_clusters)

    km.fit(tfidf_matrix)

    clusters = km.labels_.tolist()

    # save your model
    joblib.dump(km,  'doc_cluster.pkl')

    # uncomment the below to load your model
    #km = joblib.load('doc_cluster.pkl')

    clusters = km.labels_.tolist()

    pars = {'paragraphs': paragraphs, 'cluster': clusters}

    frame = pd.DataFrame(pars, index=[clusters], columns=['cluster'])
    print(frame['cluster'].value_counts()) # number of films per cluster (clusters from 0 to 4)



    print("Top terms per cluster:")
    print()
    # sort cluster centers by proximity to centroid
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]

    for i in range(num_clusters):
        print("Cluster %d words:" % i, end='')

        for ind in order_centroids[i, :6]:  # replace 6 with n words per cluster
            print(' %s' % vocab_frame.ix[terms[ind].split(' ')].values.tolist()[0][0].encode('utf-8', 'ignore'),
                  end=',')
        print()  # add whitespace
        print()  # add whitespace

        #print("Cluster %d titles:" % i, end='')
        #for title in frame.ix[i]['title'].values.tolist():
        #    print(' %s,' % title, end='')
        print()  # add whitespace
        print()  # add whitespace

    print()
    print()


    # convert two components as we're plotting points in a two-dimensional plane
    # "precomputed" because we provide a distance matrix
    # we will also specify `random_state` so the plot is reproducible.
    mds = MDS(n_components=2, dissimilarity="precomputed", random_state=1)

    pos = mds.fit_transform(dist)  # shape (n_components, n_samples)

    xs, ys = pos[:, 0], pos[:, 1]
    print()
    print()

    # set up colors per clusters using a dict
    cluster_colors = {0: '#1b9e77', 1: '#d95f02', 2: '#7570b3', 3: '#e7298a', 4: '#66a61e', 5: "#667754",
                      6: '#ff5544', 7: "#d45433", 8: '#888888', 9: "#998898"}

    # set up cluster names using a dict
    cluster_names = {0: 'e, n, e, x, c, e',
                     1: 'x, margins, hyperplane, svm, d, support',
                     2: 'bullet, feature, mean, respectively, f, measurement',
                     3: 'feature, emotion, recognition, used, compensation, extraction',
                     4: 'x, y, kernel, kernel, bullet, x',
                     5: 'bullet, feature, mean, respectively, f, measurement',
                     6: 'emotion, states, emotion, y, estimated, exp',
                     7: 'e, feature, n, states, emotion, feature',
                     8: 'margins, vector, margins, figure, figure, so-called',
                     9: 'feature, emotion, recognition, extraction, models, compensation'}
    # create data frame that has the result of the MDS plus the cluster numbers and titles
    df = pd.DataFrame(dict(x=xs, y=ys, label=clusters, title=[c for c,i in enumerate(clusters)]))

    # group by cluster
    groups = df.groupby('label')

    # set up plot
    fig, ax = plt.subplots(figsize=(17, 9))  # set size
    ax.margins(0.05)  # Optional, just adds 5% padding to the autoscaling

    # iterate through groups to layer the plot
    # note that I use the cluster_name and cluster_color dicts with the 'name' lookup to return the appropriate color/label
    for name, group in groups:
        ax.plot(group.x, group.y, marker='o', linestyle='', ms=12,
                label=cluster_names[name], color=cluster_colors[name],
                mec='none')
        ax.set_aspect('auto')
        ax.tick_params( \
            axis='x',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom='off',  # ticks along the bottom edge are off
            top='off',  # ticks along the top edge are off
            labelbottom='off')
        ax.tick_params( \
            axis='y',  # changes apply to the y-axis
            which='both',  # both major and minor ticks are affected
            left='off',  # ticks along the bottom edge are off
            top='off',  # ticks along the top edge are off
            labelleft='off')


    ax.legend(numpoints=1)  # show legend with only 1 point

    # add label in x,y position with the label as the film title
    for i in range(len(df)):
        ax.text(df.ix[i]['x'], df.ix[i]['y'], df.ix[i]['title'], size=8)

    plt.show()  # show the plot

    # uncomment the below to save the plot if need be
    # plt.savefig('clusters_small_noaxes.png', dpi=200)


if __name__ == '__main__':
    main()