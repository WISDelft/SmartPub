# import gensim
# from sklearn.cluster import KMeans
# import numpy as np
# from sklearn.externals import joblib
from __future__ import division
import matplotlib.pyplot as plt
from gensim.models.word2vec import Word2Vec
from sklearn.externals import joblib
# from sklearn.preprocessing import Imputer
# from sklearn import decomposition
# from sklearn.preprocessing import Normalizer
# from sklearn.pipeline import make_pipeline
from sklearn import decomposition
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans
from numbers import Number
import string
from sklearn.preprocessing import StandardScaler
from pandas import DataFrame
import sys, codecs, numpy
import operator
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from evaluation.Extract_NE import preprocess_NE

import sys, codecs, numpy
from itertools import repeat
from sklearn.metrics import silhouette_samples, silhouette_score
import csv
from nltk.corpus import stopwords
from nltk.corpus import wordnet
import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag, ne_chunk
from nltk.tokenize import SpaceTokenizer
import string
from preprocessing.Extract_NE import preprocess_NE
import gensim
from sklearn.cluster import KMeans
import numpy as np


class autovivify_list(dict):
    '''Pickleable class to replicate the functionality of collections.defaultdict'''

    def __missing__(self, key):
        value = self[key] = []
        return value

    def __add__(self, x):
        '''Override addition for numeric types when self is empty'''
        if not self and isinstance(x, Number):
            return x
        raise ValueError

    def __sub__(self, x):
        '''Also provide subtraction method'''
        if not self and isinstance(x, Number):
            return -1 * x
        raise ValueError

def build_word_vector_matrix(vector_file,propernouns):
    '''Read a GloVe array from sys.argv[1] and return its vectors and labels as arrays'''
    numpy_arrays = []
    labels_array = []
    with codecs.open(vector_file, 'r', 'utf-8') as f:
        for c, r in enumerate(f):
            sr = r.split()


            try:
                if sr[0] in propernouns and not wordnet.synsets(sr[0]):
                 labels_array.append(sr[0])
                # print(sr[0].strip())

                 numpy_arrays.append(numpy.array([float(i) for i in sr[1:]]))
            except:
                continue



    return numpy.array(numpy_arrays), labels_array


def find_word_clusters(labels_array, cluster_labels):
    '''Read the labels array and clusters label and return the set of words in each cluster'''
    cluster_to_words = autovivify_list()
    for c, i in enumerate(cluster_labels):
        cluster_to_words[i].append(labels_array[c])
    return cluster_to_words
#propernouns=['organizational','hashing','underwater','initialized','keeps','respondents','Road', 'OpenStreetMap', 'Beijing', 'Aalborg', 'Beijing', 'Analyze', 'User', 'U', 'BELIEF', 'BDMS', 'Bob', 'Lake Forest', 'facebook', 'twitter', 'imdb', 'instagram']
def clustering(numberOfSeeds):
    tokenizer = SpaceTokenizer()
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    stop_words = set(stopwords.words('english'))
    for iteration in range(0, 10):
        path='/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_trainp_' + str(numberOfSeeds) + '_' + str(iteration) + '.txt'
        propernouns=preprocess_NE(path)
        dsnames = []
        dsnamestemp = []
        # corpuspath='/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_SeedsEC2_' + str(numberOfSeeds) + '_' + str(iteration) + '.txt'
        #
        #
        # with open(corpuspath, "r") as file:
        #     for row in file.readlines():
        #         dsnames.append(row.strip())
        corpuspath = '/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_Seeds_' + str(
            numberOfSeeds) + '_' + str(iteration) + '.txt'

        with open(corpuspath, "r") as file:
            for row in file.readlines():
                dsnames.append(row.strip())
                propernouns.append(row.strip())

        dsnames = [x.lower() for x in dsnames]
        # with open('used_names.csv','r') as tsv:
        #
        #     for line in csv.reader(tsv, delimiter=','):
        #         dsnames.append(line[0])
        model = gensim.models.KeyedVectors.load_word2vec_format('/Users/sepidehmesbah/Downloads/ner-crf-master/preprocessing/modelFasttext.vec')
        sentences_split = [s.lower() for s in propernouns]
       # print(sentences_split)
        df, labels_array  = build_word_vector_matrix("/Users/sepidehmesbah/Downloads/ner-crf-master/model/modelFasttext.txt",sentences_split)
        #print('labels_arraaaaayyy')
       # print(labels_array)
        #print(df)
        sse = {}
        maxcluster=0
        if len(df) >= 9:
            for n_clusters in range(2,10):

                df = StandardScaler().fit_transform(df)
                kmeans_model = KMeans(n_clusters=n_clusters,  max_iter=300, n_init=100)
                kmeans_model.fit(df)
                cluster_labels = kmeans_model.labels_
                cluster_inertia = kmeans_model.inertia_
                #print(' cluster_inertia  cluster_inertia  cluster_inertia  cluster_inertia')
                #print(cluster_inertia)
                cluster_to_words = find_word_clusters(labels_array, cluster_labels)
                cluster_labelss = kmeans_model.fit_predict(df)
                sse[n_clusters]=kmeans_model.inertia_


                for c in cluster_to_words:
                    print(cluster_to_words[c])
                #     print("\n")
                finallist = []
                for c in cluster_to_words:
                    counter = dict()
                    dscounter = 0
                    for word in cluster_to_words[c]:
                        counter[word] = 0
                    for word in cluster_to_words[c]:
                        if word in dsnames:

                            dscounter = dscounter + 1

                            # for ww in cluster_to_words[c]:
                            #     similarityy = model.similarity(word, ww)
                            #     #print(int(similarityy))
                            #     if similarityy < 0.59:
                            #         if ww not in dsnames:
                            #
                            #             counter[ww] = counter[ww] + 1
                    clusterlist = []
                    #print('dscounter')
                    #print(dscounter)
                    if dscounter >0:
                        # if dscounter == 1:
                        #     for word, value in counter.items():
                        #         if value == 0:
                        #             finallist.append(word)
                        #
                        # elif 1 < dscounter <= 3:
                        #     for word, value in counter.items():
                        #         if value < 2:
                        #             finallist.append(word)
                        # else:
                        #     for word, value in counter.items():
                        #         if value < 4:
                        for word in cluster_to_words[c]:
                            clusterlist.append(word)
                            finallist.append(word)
                        print(clusterlist)

                    else:
                        print('no ds names')

                #print(finallist)
                try:

                    silhouette_avg = silhouette_score(df, cluster_labelss)
                    print("For n_clusters =", n_clusters,
                          "The average silhouette_score is :", silhouette_avg)
                    if silhouette_avg > maxcluster:
                        print('MAXXXXXXX')
                        maxcluster = silhouette_avg
                        thefile = open(
                            "/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_SeedsEC2_" + str(
                                numberOfSeeds) + "_" + str(iteration) + ".txt", 'w')

                        for item in finallist:
                            if item.lower() not in dsnamestemp and item.lower() not in dsnames:
                                thefile.write("%s\n" % item)
                        print('printing the final list.....of...', n_clusters)
                        print(finallist)
                except:
                    print("ERROR:::Silhoute score invalid")
                    continue
        else:
            for n_clusters in range(2, len(df)):

                df = StandardScaler().fit_transform(df)
                kmeans_model = KMeans(n_clusters=n_clusters, max_iter=300, n_init=100)
                kmeans_model.fit(df)
                cluster_labels = kmeans_model.labels_
                cluster_inertia = kmeans_model.inertia_
                # print(' cluster_inertia  cluster_inertia  cluster_inertia  cluster_inertia')
                # print(cluster_inertia)
                cluster_to_words = find_word_clusters(labels_array, cluster_labels)
                cluster_labelss = kmeans_model.fit_predict(df)
                sse[n_clusters] = kmeans_model.inertia_

                for c in cluster_to_words:
                    print(cluster_to_words[c])
                # print("\n")
                finallist=[]
                for c in cluster_to_words:
                    counter = dict()
                    dscounter = 0
                    for word in cluster_to_words[c]:
                        counter[word] = 0
                    for word in cluster_to_words[c]:
                        if word in dsnames:

                            dscounter = dscounter + 1

                            # for ww in cluster_to_words[c]:
                            #     similarityy = model.similarity(word, ww)
                            #     # print(int(similarityy))
                            #     if similarityy < 0.58:
                            #         if ww not in dsnames:
                            #             counter[ww] = counter[ww] + 1
                    clusterlist = []
                    # print('dscounter')
                    # print(dscounter)
                    if dscounter > 0:
                        for word in cluster_to_words[c]:
                            clusterlist.append(word)
                            finallist.append(word)
                        print(clusterlist)

                    else:
                        print('no ds names')

                #print(finallist)
                try:

                    silhouette_avg = silhouette_score(df, cluster_labelss)
                    print("For n_clusters =", n_clusters,
                          "The average silhouette_score is :", silhouette_avg)
                    if silhouette_avg > maxcluster:
                        maxcluster = silhouette_avg
                        thefile = open(
                            "/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_SeedsEC2_" + str(
                                numberOfSeeds) + "_" + str(iteration) + ".txt", 'w')

                        for item in finallist:
                            if item.lower() not in dsnamestemp and item.lower() not in dsnames:
                                thefile.write("%s\n" % item)
                        print('printing the final list.....of...', n_clusters)
                        print(finallist)
                except:
                    print("ERROR:::Silhoute score invalid")
                    continue




        # print('printing the final list.....')
        # print(finallist)
        # thefile = open("/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_SeedsEC2_"+str(numberOfSeeds)+"_"+str(iteration)+".txt", 'w')
        #
        # for item in finallist:
        #     if item.lower() not in dsnamestemp and item.lower() not in dsnames:
        #         thefile.write("%s\n" % item)
    return finallist


def clustering_2ndround(numberOfSeeds):
    tokenizer = SpaceTokenizer()
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    stop_words = set(stopwords.words('english'))
    for iteration in range(0, 10):
        path='/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_trainp_' + str(numberOfSeeds) + '_' + str(iteration) + '.txt'
        propernouns=preprocess_NE(path)
        dsnames = []
        dsnamestemp = []
        corpuspath='/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_SeedsEC2_' + str(numberOfSeeds) + '_' + str(iteration) + '.txt'


        with open(corpuspath, "r") as file:
            for row in file.readlines():
                dsnames.append(row.strip())
        corpuspath = '/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_Seeds_' + str(
            numberOfSeeds) + '_' + str(iteration) + '.txt'

        with open(corpuspath, "r") as file:
            for row in file.readlines():
                dsnamestemp.append(row.strip())

        dsnames = [x.lower() for x in dsnames]
        # with open('used_names.csv','r') as tsv:
        #
        #     for line in csv.reader(tsv, delimiter=','):
        #         dsnames.append(line[0])
        model = gensim.models.KeyedVectors.load_word2vec_format('/Users/sepidehmesbah/Downloads/ner-crf-master/preprocessing/modelFasttext.vec')
        sentences_split = [s.lower() for s in propernouns]
       # print(sentences_split)
        df, labels_array  = build_word_vector_matrix("/Users/sepidehmesbah/Downloads/ner-crf-master/model/modelFasttext.txt",sentences_split)
        #print('labels_arraaaaayyy')
       # print(labels_array)
        #print(df)
        sse = {}
        maxcluster=0
        if len(df) >= 9:
            for n_clusters in range(2,10):

                df = StandardScaler().fit_transform(df)
                kmeans_model = KMeans(n_clusters=n_clusters,  max_iter=300, n_init=100)
                kmeans_model.fit(df)
                cluster_labels = kmeans_model.labels_
                cluster_inertia = kmeans_model.inertia_
                #print(' cluster_inertia  cluster_inertia  cluster_inertia  cluster_inertia')
                #print(cluster_inertia)
                cluster_to_words = find_word_clusters(labels_array, cluster_labels)
                cluster_labelss = kmeans_model.fit_predict(df)
                sse[n_clusters]=kmeans_model.inertia_


                for c in cluster_to_words:
                    print(cluster_to_words[c])
                #     print("\n")

                for c in cluster_to_words:
                    counter = dict()
                    dscounter = 0
                    for word in cluster_to_words[c]:
                        counter[word] = 0
                    for word in cluster_to_words[c]:
                        if word in dsnames:

                            dscounter = dscounter + 1

                            for ww in cluster_to_words[c]:
                                similarityy = model.similarity(word, ww)
                                #print(int(similarityy))
                                if similarityy < 0.58:
                                    if ww not in dsnames:

                                        counter[ww] = counter[ww] + 1
                    finallist = []
                    #print('dscounter')
                    #print(dscounter)
                    if dscounter >0:
                        if dscounter == 1:
                            for word, value in counter.items():
                                if value == 0:
                                    finallist.append(word)

                        elif 1 < dscounter <= 3:
                            for word, value in counter.items():
                                if value < 2:
                                    finallist.append(word)
                        else:
                            for word, value in counter.items():
                                if value < 4:
                                    finallist.append(word)
                        #print(finallist)

                    else:
                        print('no ds names')

                print(finallist)
                try:

                    silhouette_avg = silhouette_score(df, cluster_labelss)
                    print("For n_clusters =", n_clusters,
                          "The average silhouette_score is :", silhouette_avg)
                    if silhouette_avg > maxcluster:
                        maxcluster = silhouette_avg
                        joblib.dump(kmeans_model, 'word2vec_cluster.pkl')
                except:
                    print("ERROR:::Silhoute score invalid")
                    continue
        else:
            for n_clusters in range(2, len(df)):

                df = StandardScaler().fit_transform(df)
                kmeans_model = KMeans(n_clusters=n_clusters, max_iter=300, n_init=100)
                kmeans_model.fit(df)
                cluster_labels = kmeans_model.labels_
                cluster_inertia = kmeans_model.inertia_
                # print(' cluster_inertia  cluster_inertia  cluster_inertia  cluster_inertia')
                # print(cluster_inertia)
                cluster_to_words = find_word_clusters(labels_array, cluster_labels)
                cluster_labelss = kmeans_model.fit_predict(df)
                sse[n_clusters] = kmeans_model.inertia_

                for c in cluster_to_words:
                    print(cluster_to_words[c])
                # print("\n")

                for c in cluster_to_words:
                    counter = dict()
                    dscounter = 0
                    for word in cluster_to_words[c]:
                        counter[word] = 0
                    for word in cluster_to_words[c]:
                        if word in dsnames:

                            dscounter = dscounter + 1

                            for ww in cluster_to_words[c]:
                                similarityy = model.similarity(word, ww)
                                # print(int(similarityy))
                                if similarityy < 0.58:
                                    if ww not in dsnames:
                                        counter[ww] = counter[ww] + 1
                    finallist = []
                    # print('dscounter')
                    # print(dscounter)
                    if dscounter > 0:
                        if dscounter == 1:
                            for word, value in counter.items():
                                if value == 0:
                                    finallist.append(word)

                        elif 1 < dscounter <= 3:
                            for word, value in counter.items():
                                if value < 2:
                                    finallist.append(word)
                        else:
                            for word, value in counter.items():
                                if value < 4:
                                    finallist.append(word)
                                    # print(finallist)

                    else:
                        print('no ds names')

                print(finallist)
                try:

                    silhouette_avg = silhouette_score(df, cluster_labelss)
                    print("For n_clusters =", n_clusters,
                          "The average silhouette_score is :", silhouette_avg)
                    if silhouette_avg > maxcluster:
                        maxcluster = silhouette_avg
                        joblib.dump(kmeans_model, 'word2vec_cluster.pkl')
                except:
                    print("ERROR:::Silhoute score invalid")
                    continue

        finallist = []
        try:
            loaded_model = joblib.load('word2vec_cluster.pkl')
            cluster_labels = loaded_model.labels_
            clusterstoword = find_word_clusters(labels_array, cluster_labels)

            print('optimal number of clusters')
            print(len(clusterstoword))
            for c in clusterstoword:
                counter = dict()
                dscounter = 0
                for word in clusterstoword[c]:
                    counter[word] = 0
                for word in clusterstoword[c]:
                    if word in dsnames:
                        dscounter = dscounter + 1

                        for ww in clusterstoword[c]:
                            similarityy = model.similarity(word, ww)
                            # print(int(similarityy))
                            if similarityy < 0.58:
                                if ww not in dsnames:
                                    counter[ww] = counter[ww] + 1

                if dscounter > 0:
                    if dscounter == 1:
                        for word, value in counter.items():

                            if value == 0:
                                if word.lower() != 'dataset' and word.lower() != 'datasets':
                                    finallist.append(word)

                    elif 1 < dscounter <= 3:
                        for word, value in counter.items():
                            if value < 2:
                                if word.lower() != 'dataset' and word.lower() != 'datasets':
                                    finallist.append(word)
                    else:
                        for word, value in counter.items():
                            if value < 4:
                                if word.lower() != 'dataset' and word.lower() != 'datasets':
                                    finallist.append(word)

                else:
                    print('no ds names')
        except:
            print('list index out of range')

        print('printing the final list.....')
        print(finallist)
        thefile = open("/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_SeedsEC2_"+str(numberOfSeeds)+"_"+str(iteration)+".txt", 'w')

        for item in finallist:
            if item.lower() not in dsnamestemp and item.lower() not in dsnames:
                thefile.write("%s\n" % item)
    return finallist
def embedding_similarity(numberOfSeeds):
    model = gensim.models.KeyedVectors.load_word2vec_format(
        '/Users/sepidehmesbah/Downloads/ner-crf-master/preprocessing/modelFasttext.vec')

    for iteration in range(0, 2):
        path = '/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_trainp_' + str(
            numberOfSeeds) + '_' + str(iteration) + '.txt'
        propernouns = preprocess_NE(path)
        propernouns = [x.lower() for x in propernouns]
        dsnames = []
        dsnamestemp = []
        finallist=[]
        corpuspath = '/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_Seeds_' + str(
            numberOfSeeds) + '_' + str(iteration) + '.txt'

        with open(corpuspath, "r") as file:
            for row in file.readlines():
                dsnames.append(row.strip())

        dsnames = [x.lower() for x in dsnames]

        for word in propernouns:
            for ww in dsnames:
               try:

                   similarityy = model.similarity(word, ww)
                   print(word,ww,similarityy)
                   if similarityy < 0.58 and not wordnet.synsets(word):
                       finallist.append(word)
               except:
                   continue
        #
        # print('printing the final list.....')
        # print(finallist)
        # finallist=list(set(finallist))
        # thefile = open("/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_SeedsES1_" + str(
        #     numberOfSeeds) + "_" + str(iteration) + ".txt", 'w')
        #
        # for item in finallist:
        #     if item.lower() not in dsnamestemp and item.lower() not in dsnames:
        #         thefile.write("%s\n" % item)


def clustering_2(numberOfSeeds):
                       tokenizer = SpaceTokenizer()
                       sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
                       stop_words = set(stopwords.words('english'))
                       for iteration in range(0, 10):
                           path = '/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_trainp_' + str(
                               numberOfSeeds) + '_' + str(iteration) + '.txt'
                           propernouns = preprocess_NE(path)
                           dsnames = []
                           dsnamestemp = []
                           # corpuspath = '/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_SeedsEC3_' + str(
                           #     numberOfSeeds) + '_' + str(iteration) + '.txt'
                           #
                           # with open(corpuspath, "r") as file:
                           #     for row in file.readlines():
                           #         dsnames.append(row.strip())
                           corpuspath = '/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_Seeds_' + str(
                               numberOfSeeds) + '_' + str(iteration) + '.txt'

                           with open(corpuspath, "r") as file:
                               for row in file.readlines():
                                   dsnames.append(row.strip())

                           dsnames = [x.lower() for x in dsnames]
                           # with open('used_names.csv','r') as tsv:
                           #
                           #     for line in csv.reader(tsv, delimiter=','):
                           #         dsnames.append(line[0])
                           model = gensim.models.KeyedVectors.load_word2vec_format(
                               '/Users/sepidehmesbah/Downloads/ner-crf-master/preprocessing/modelFasttext.vec')
                           sentences_split = [s.lower() for s in propernouns]
                           # print(sentences_split)
                           df, labels_array = build_word_vector_matrix(
                               "/Users/sepidehmesbah/Downloads/ner-crf-master/model/modelFasttext.txt", sentences_split)
                           # print('labels_arraaaaayyy')
                           # print(labels_array)
                           # print(df)
                           sse = {}
                           maxcluster = 0
                           if len(df) >= 9:
                               for n_clusters in range(2, 10):
                                   finallist=[]

                                   df = StandardScaler().fit_transform(df)
                                   kmeans_model = KMeans(n_clusters=n_clusters, max_iter=300, n_init=100)
                                   kmeans_model.fit(df)
                                   cluster_labels = kmeans_model.labels_
                                   cluster_inertia = kmeans_model.inertia_
                                   # print(' cluster_inertia  cluster_inertia  cluster_inertia  cluster_inertia')
                                   # print(cluster_inertia)
                                   cluster_to_words = find_word_clusters(labels_array, cluster_labels)
                                   cluster_labelss = kmeans_model.fit_predict(df)
                                   sse[n_clusters] = kmeans_model.inertia_

                                   for c in cluster_to_words:
                                       print(cluster_to_words[c])
                                   # print("\n")

                                   for c in cluster_to_words:
                                       counter = dict()
                                       dscounter = 0
                                       for word in cluster_to_words[c]:
                                           counter[word] = 0
                                       for word in cluster_to_words[c]:
                                           if word in dsnames:



                                               for ww in cluster_to_words[c]:
                                                   if ww not in dsnames:
                                                       similarityy = model.similarity(word, ww)
                                                       # print(int(similarityy))
                                                       if similarityy > 0.59:
                                                           finallist .append(ww)




                                   #print(finallist)
                                   try:

                                       silhouette_avg = silhouette_score(df, cluster_labelss)
                                       print("For n_clusters =", n_clusters,
                                             "The average silhouette_score is :", silhouette_avg)
                                       if silhouette_avg > maxcluster:
                                           maxcluster = silhouette_avg
                                           thefile = open(
                                               "/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_SeedsEC3_" + str(
                                                   numberOfSeeds) + "_" + str(iteration) + ".txt", 'w')
                                           finallist=list(set(finallist))

                                           for item in finallist:
                                               if item.lower() not in dsnamestemp and item.lower() not in dsnames:
                                                   thefile.write("%s\n" % item)
                                           print('printing the final list.....of...', n_clusters)
                                           print(finallist)
                                   except:
                                       print("ERROR:::Silhoute score invalid")
                                       continue
                           else:
                               for n_clusters in range(2, len(df)):
                                   finallist=[]
                                   df = StandardScaler().fit_transform(df)
                                   kmeans_model = KMeans(n_clusters=n_clusters, max_iter=300, n_init=100)
                                   kmeans_model.fit(df)
                                   cluster_labels = kmeans_model.labels_
                                   cluster_inertia = kmeans_model.inertia_
                                   # print(' cluster_inertia  cluster_inertia  cluster_inertia  cluster_inertia')
                                   # print(cluster_inertia)
                                   cluster_to_words = find_word_clusters(labels_array, cluster_labels)
                                   cluster_labelss = kmeans_model.fit_predict(df)
                                   sse[n_clusters] = kmeans_model.inertia_

                                   for c in cluster_to_words:
                                       print(cluster_to_words[c])
                                   # print("\n")

                                   for c in cluster_to_words:
                                       counter = dict()
                                       dscounter = 0
                                       for word in cluster_to_words[c]:
                                           counter[word] = 0
                                       for word in cluster_to_words[c]:
                                           if word in dsnames:

                                               dscounter = dscounter + 1

                                               for ww in cluster_to_words[c]:
                                                   for ww in cluster_to_words[c]:
                                                       if ww not in dsnames:
                                                           similarityy = model.similarity(word, ww)
                                                           # print(int(similarityy))
                                                           if similarityy > 0.59:
                                                               finallist.append(ww)

                                   try:

                                       silhouette_avg = silhouette_score(df, cluster_labelss)
                                       print("For n_clusters =", n_clusters,
                                             "The average silhouette_score is :", silhouette_avg)
                                       if silhouette_avg > maxcluster:
                                           maxcluster = silhouette_avg
                                           thefile = open(
                                               "/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_SeedsEC3_" + str(numberOfSeeds) + "_" + str(iteration) + ".txt", 'w')

                                           finallist = list(set(finallist))
                                           for item in finallist:
                                               if item.lower() not in dsnamestemp and item.lower() not in dsnames:
                                                   thefile.write("%s\n" % item)
                                           print('printing the final list.....of...', n_clusters)
                                           print(finallist)
                                   except:
                                       print("ERROR:::Silhoute score invalid")
                                       continue

                           finallist = []

clustering_2(2)
clustering_2(5)
clustering_2(10)
clustering_2(25)
clustering_2(50)
clustering_2(100)
#embedding_similarity(2)
# embedding_similarity(5)
# embedding_similarity(10)
# embedding_similarity(25)
# embedding_similarity(50)
# embedding_similarity(100)





