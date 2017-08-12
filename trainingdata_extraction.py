"""
Here we will extract a number of sentences for the training data using different number of dataset name seeds (e.g  2,5,10,...) 
"""

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
    
    #First we get the dataset names which have been used in the testing set (TestB) to exclude them from the training sentences
    with open('/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation/dataset-names-testb.txt', 'r') as file:
        for row in file.readlines():
            X_testB.append(row.strip())
    #lowercase the names
    X_testB=[ds.lower() for ds in X_testB]



    #Getting the list of papers which can be used for as the developement data
    corpuspath = "/Users/sepidehmesbah/SmartPub/DataProfiling/test_papers.txt"
    with open(corpuspath, "r") as file:
                for row in file.readlines():
                    papernames.append(row.strip())
                    
    #Initialize the elastic search                
    es = Elasticsearch(
        [{'host': 'localhost', 'port': 9200}]
    )
    dsnames=[]
    
    #List of seed names
    corpuspath = "/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation/dataset-names-trainfinal.txt"
    with open(corpuspath,"r") as file:
        for row in file.readlines():
            dsnames.append(row.strip())

    
    #10 times randomly pick i number of seeds
    for i in range(0,10):
        dsnames = [x.lower() for x in dsnames]

        dsnames=list(set(dsnames))

        #shuffle the list
        X_train=random.sample(dsnames, numberOfSeeds)


        paragraph=[]
        
        #using the seeds,extract the sentences from the publications using the query in elastic search
        for dataset in X_train:
            datasetname = re.sub(r'\([^)]*\)', '', dataset)

            print(datasetname)

            #Matching
            query = {"query":
                {"match": {
                    "content.chapter.sentpositive": {
                        "query": datasetname,
                        "operator": "and"
                    }
                }
                }
            }

            res = es.search(index="twosent", doc_type="twosentnorules",
                            body=query, size=10000)
            print(len(res['hits']['hits']))


            #clean up the sentences and if they dont contain the names of the testB then add them as the training data
            for doc in res['hits']['hits']:

                    sentence = doc["_source"]["content.chapter.sentpositive"]
                  
                    words = nltk.word_tokenize(doc["_source"]["content.chapter.sentpositive"])
                    lengths = [len(x) for x in words]
                    average = sum(lengths) / len(lengths)
                    if average < 3:
                     continue
                  
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
                    
                    
                    if any(ext in sentence.lower() for ext in X_testB):
           
                      continue
                  
                    else:
                        sentences=tokenize.sent_tokenize(sentence)
                        for sent in sentences:
                            if sent not in paragraph:
                                paragraph.append(sent)
        
        paragraph=list(set(paragraph))
        
        #Split the data into training and testing and keep the sentences and also the seed names for annotation that will be used later
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
