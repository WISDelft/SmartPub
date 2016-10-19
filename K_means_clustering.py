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

class My_kmeans:


    def __init__(self, num_cluster, mongo_string, terms_printed):
        """
        Initialization of the summarizer
        :param min_th: words with frequency less than min_th will be ignored
        :param max_th: words with frequency higher than max_th will be ignored
        """
        self._num_cluster = num_cluster
        self._mongo_string = mongo_string
        self._terms_printed = terms_printed


    def _tokenize_only(self,text):
        # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
        tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
        filtered_tokens = []
        # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
        for token in tokens:
            if re.search('[a-zA-Z]', token):
                filtered_tokens.append(token)
        return filtered_tokens

    def _create_dataset(self,db,mongo_search_string):
        """
        Get the paragraphs and create a list with all the paragraphs of a pdf
        :param db:
        :param mongo_search_string:
        :return:
        """
        mylist = {"data": {}}

        documents = db.publications.find(mongo_search_string, no_cursor_timeout=True)
        paragraphs = []
        for i, doc in enumerate(documents):
            for chapter in doc['content']['chapters']:
                par = ""
                # paragraphs.append(chapter['paragraphs'])
                for paragraph in chapter['paragraphs']:
                    par += str(paragraph)
                    paragraphs.append(par)

        return paragraphs

    def _strip_proppers_POS(self,text):
        """
        Using the nltk pos (part of speech) tagger remove all the proper nouns
        :param text:
        :return:
        """
        tagged = pos_tag(text.split())  # use NLTK's part of speech tagger
        non_propernouns = [word for word, pos in tagged if pos != 'NNP' and pos != 'NNPS']
        return non_propernouns


    def _print_top_n_terms(self,km, vocab_frame,terms):
        # sort cluster centers by proximity to centroid
        order_centroids = km.cluster_centers_.argsort()[:, ::-1]

        for i in range(self._num_cluster):
            print("Cluster %d words:" % i, end='')

            for ind in order_centroids[i, :self._terms_printed]:
                print(' %s' % vocab_frame.ix[terms[ind].split(' ')].values.tolist()[0][0].encode('utf-8', 'ignore'),
                      end=',')
            print()  # add whitespace
            print()  # add whitespace


    def k_means_process(self):
        """
        This function deploys the k-means algorithm by creating
        tf-idf matrix and cosine similarity to measure the distance
        :param num_clusters:
        :return:
        """

        db = tools.connect_to_mongo()
        paragraphs = self._create_dataset(db=db, mongo_search_string=self._mongo_string)


        totalvocab_stemmed = []
        totalvocab_tokenized = []
        for i in paragraphs:
            allwords_stemmed = self._tokenize_only(i)  # for each item in 'paragraphs', tokenize
            totalvocab_stemmed.extend(allwords_stemmed)  # extend the 'totalvocab_stemmed' list

            allwords_tokenized =  self._tokenize_only(i)
            totalvocab_tokenized.extend(allwords_tokenized)

        vocab_frame = pd.DataFrame({'words': totalvocab_tokenized}, index=totalvocab_stemmed)
        print('there are ' + str(vocab_frame.shape[0]) + ' items in vocab_frame')

        # define vectorizer parameters
        tfidf_vectorizer = TfidfVectorizer(max_df=0.8, max_features=200000,
                                           min_df=0.2, stop_words='english',
                                           use_idf=True, tokenizer= self._tokenize_only, ngram_range=(1, 3))

        tfidf_matrix = tfidf_vectorizer.fit_transform(paragraphs)  # fit the vectorizer to synopses
        print("dimensions of the tfidf matrix {}".format(tfidf_matrix.shape ))
        terms = tfidf_vectorizer.get_feature_names()
        print("terms: {}".format(terms))
        dist = 1 - cosine_similarity(tfidf_matrix)

        km = KMeans(n_clusters=self._num_cluster)

        km.fit(tfidf_matrix)

        clusters = km.labels_.tolist()

        # save your model
        joblib.dump(km, 'doc_cluster.pkl')

        # uncomment the below to load your model
        # km = joblib.load('doc_cluster.pkl')

        self._print_top_n_terms(km, vocab_frame,terms)


#def main():
#    mongo_string_search = {"dblpkey": "journals_ijclclp_WuC07"}
    # k_means_process(num_clusters=5,mongo_search_string=mongo_string_search)

