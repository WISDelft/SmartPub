import numpy as np
from sklearn.model_selection import train_test_split
import random
from elasticsearch import Elasticsearch
import itertools
import nltk
from pymongo import MongoClient
from nltk.corpus import wordnet
import re
import csv
regex = re.compile(".*?\((.*?)\)")
import _pickle as cPickle
from sklearn.model_selection import train_test_split
from nltk import tokenize
from random import shuffle

def extract(numberOfSeeds):
    papernames=[]
    dsnames=[]
    X_testB=[]
    # with open('/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation/X_testB_50_manually_splitted.tsv', 'r') as tsvin:
    #     tsvin = csv.reader(tsvin, delimiter='\t')
    #
    #     for row in tsvin:
    #         # print(row)
    #         try:
    #           if row[1]=='DATA':
    #            # print(row[0])
    #            X_testB.append(row[0])
    #         except:
    #             continue
    # X_testB =list(set(X_testB))
    # #print(dsnames)
    # # print(len(dsnames))
    with open('/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation/dataset-names-testb.txt', 'r') as file:
        for row in file.readlines():
            X_testB.append(row.strip())
    X_testB=[ds.lower() for ds in X_testB]
    print(X_testB)



    corpuspath = "/Users/sepidehmesbah/SmartPub/DataProfiling/test_papers.txt"

    with open(corpuspath, "r") as file:
                for row in file.readlines():
                    papernames.append(row.strip())
    es = Elasticsearch(
        [{'host': 'localhost', 'port': 9200}]
    )
    dsnames=[]
    corpuspath = "/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation/dataset-names-trainfinal.txt"
    with open(corpuspath,"r") as file:
        for row in file.readlines():
            dsnames.append(row.strip())

    for i in range(0,10):
        dsnames = [x.lower() for x in dsnames]
        #random.shuffle(dsnames)

        dsnames=list(set(dsnames))
        print(len(dsnames))
        print(dsnames)
        X_train=random.sample(dsnames, numberOfSeeds)
        #X_train=dsnames[0:numberOfSeeds]

        paragraph=[]
        for dataset in X_train:
            datasetname = re.sub(r'\([^)]*\)', '', dataset)

            print(datasetname)

            # Exact Matching
            # query = {"query": {
            #     "bool": {
            #         "must": {
            #             "term":{
            #                 "text": datasetname
            #             }
            #         }
            #     }
            # }}
            # query = {"query":
            #     {"match": {
            #         "text": {
            #             "query": datasetname,
            #             "operator": "and"
            #         }
            #     }
            #     }
            # }

            query = {"query":
                {"match": {
                    "content.chapter.sentpositive": {
                        "query": datasetname,
                        "operator": "and"
                    }
                }
                }
            }

            # res = es.search(index="ind", doc_type="allsentnum",
            #                 body=query, size=15)
            # print(len(res['hits']['hits']))
            res = es.search(index="twosent", doc_type="twosentnorules",
                            body=query, size=10000)
            print(len(res['hits']['hits']))


            for doc in res['hits']['hits']:

                    #sentence = doc["_source"]["text"].replace(',', ' ')
                    sentence = doc["_source"]["content.chapter.sentpositive"]
                    #print(sentence)
                    #sentence = sentence.replace('\'', "")
                    # mynames =''
                    words = nltk.word_tokenize(doc["_source"]["content.chapter.sentpositive"])
                    lengths = [len(x) for x in words]
                    average = sum(lengths) / len(lengths)
                    if average < 3:
                     continue
                    # if any(ext in sentence for ext in corpus):
                    #         score=1
                    # else:
                    #         score=0


                    sentence = sentence.replace("@ BULLET", "")
                    sentence = sentence.replace("@BULLET", "")
                    sentence = sentence.replace(", ", " , ")
                    sentence = sentence.replace('(', '')
                    sentence = sentence.replace(')', '')
                    sentence = sentence.replace('[', '')
                    sentence = sentence.replace(']', '')
                    sentence = sentence.replace(',', ' ,')
                    sentence = sentence.replace('?', ' ?')
                    sentence = sentence.replace('..', '.')
                    #sentence = "".join(c for c in sentence if c not in ('!', "'", '"', ';', '?', '\(', '\)', '\[', '\]'))
                    if any(ext in sentence.lower() for ext in X_testB):
                    # for bb in X_testB:
                    #     if bb not in sentence:
                    #         paragraph.append(sentence)
                      continue
                    #
                    #
                    else:
                        sentences=tokenize.sent_tokenize(sentence)
                        for sent in sentences:
                            if sent not in paragraph:
                                paragraph.append(sent)
        paragraph=list(set(paragraph))
        X_traintext, X_testA= train_test_split(
        paragraph,  test_size=0.3, random_state=100)
        f1 = open('/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_train_'+str(numberOfSeeds)+'_'+str(i)+'.txt', 'w')
        for item in X_traintext:
            f1.write(item)
        f1.close()
        f1 = open('/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_testA_'+str(numberOfSeeds)+'_'+str(i)+'.txt', 'w')
        for item in X_testA:
            f1.write(item)
        f1.close()
        f1 = open('/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_Seeds_' + str(numberOfSeeds) + '_' + str(i) + '.txt', 'w')
        for item in X_train:
            f1.write(item + '\n')
        f1.close()

extract(2)
extract(5)
extract(10)
extract(25)
extract(50)
extract(100)