from nltk.tag.stanford import StanfordNERTagger
from elasticsearch import Elasticsearch
import itertools
import nltk
from pymongo import MongoClient
from nltk.corpus import wordnet
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from nltk.corpus import stopwords
import re
import csv
client = MongoClient('localhost:4321')
db = client.pub
import random
from nltk.tag.stanford import StanfordPOSTagger
# english_postagger = StanfordPOSTagger('/Users/sepidehmesbah/Downloads/stanford-postagger-full-2016-10-31/models/english-bidirectional-distsim.tagger', '/Users/sepidehmesbah/Downloads/stanford-postagger-full-2016-10-31/stanford-postagger.jar')
# print(english_postagger.tag('Figures 3 (a) and (b) show the precision-recall curves for the three datasets: MovieLens, NewsSmall and NewsBig.3'.split()))




def get_continuous_chunks(text):
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    #print pos_tag(word_tokenize(text))

    prev = None
    continuous_chunk = []
    current_chunk = []

    for i in chunked:
        if type(i) == Tree:
            current_chunk.append(" ".join([token for token, pos in i.leaves()]))
        elif current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
        else:
            continue
    return continuous_chunk
#my_sent="We use datasets from American Physical Society and select authors beginning their scientific careers at the year of 1993."





es = Elasticsearch(
    [{'host': 'localhost', 'port': 9200}]
)

es.cluster.health(wait_for_status='yellow')
client = MongoClient("localhost:4321")
pub = client.pub.dataset_names.find()
#path_to_model = "/Users/sepidehmesbah/Downloads/stanford-ner-2016-10-31/ner-modelparaLLPunc.ser.gz"

def check_if_id_exist_in_db(db, id,word):
    check_string = {'$and':[{'paper_id':id},{'word':word}]}
    if db.datasetNER.find_one(check_string) is not None:
        print("We already checked this paper")
        return True
    else:
        return False
def store_datasetname_in_mongo(db, id, title,journal, year, word,inwordNet,inds):
    my_ner = {
        "paper_id": id,
        "title": title,
        "journal": journal,
        "year":year,
        "word":word,
        "inwordNet":inwordNet,
        "inDS": inds

    }
    if check_if_id_exist_in_db(db, id,word):
        return False
    else:

        db.datasetNER.insert_one(my_ner)

        return True



filterbywordnet=[]

#filter_conference = ["WWW", "ICSE", "VLDB", "JCDL", "TREC", "SIGIR", "ICWSM", "ECDL", "ESWC"]
#filter_conference = ["Journal of Machine Learning Research","ICDM","ICWSM","WWW", "ICSE", "VLDB", "PVLDB", "JCDL", "TREC",  "SIGIR",  "ECDL", "ESWC",  "IEEE J. Robotics and Automation", "IEEE Trans. Robotics","ICRA","ICARCV", "HRI", "ICSR", "PVLDB", "TPDL", "ICDM","Journal of Machine Learning Research","Machine Learning"]
def iteration_ner(numberOfSeeds):
    for iteration in range(0, 10):
        print('numbers:',numberOfSeeds,iteration)
        path_to_model = "/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation/embedingclustering_splitted"+ str(numberOfSeeds) + '_' + str(iteration) +".ser.gz"
        path_to_jar = "/Users/sepidehmesbah/Downloads/stanford-ner-2016-10-31/stanford-ner.jar"
        nertagger=StanfordNERTagger(path_to_model, path_to_jar)
        papernames=[]
        newnames=[]
        corpuspath = "/Users/sepidehmesbah/SmartPub/DataProfiling/test_papers.txt"

        with open(corpuspath, "r") as file:
                        for row in file.readlines():
                            papernames.append(row.strip())

        for paper in papernames:
            #print(paper)

            query = {"query":
                {"match": {
                    "_id": {
                        "query": paper,
                        "operator": "and"
                    }
                }
                }
            }

            res = es.search(index="irdms", doc_type="dmspublications",
                            body=query,  size=10000)
           # print(len(res['hits']['hits']))
            # random_int=random.sample(range(0, 616), 150)
            # for i in random_int:
            #      print(res['hits']['hits'][i]['_id'])

            for doc in res['hits']['hits']:
                # sentence = doc["_source"]["text"].replace(',', ' ')
                sentence = doc["_source"]["content"]
                # sentence = sentence.replace('\'', "")
                # mynames =''
                #query = "Figures 3 (a) and (b) show the precision-recall curves for the three datasets: MovieLens, NewsSmall and NewsBig. For the NewsBig dataset we were unable to run the memory based algorithm as it would not scale to these numbers; keeping the data in memory for such a large dataset was not feasible, while keeping it on disk and making random disk seeks would have taken a long time"
                #query="The approach selecting the lead sentences, which is taken as the baseline popularly on the DUC01 dataset, is denoted as LEAD. A similar method is to select the lead sentence in each paragraph. Since the information about the paragraphs is not available in DUC01, we do not include this method as a baseline. Two other unsupervised methods we compare include Gong’s algorithm based on LSA and Mihalcea’s algorithm based on graph analysis. Among the several options of Mihalcea’s algorithm, the method based on the authority score of HITS on the directed backward graph is the best. It is taken by us for comparison. These two unsupervised methods are denoted by LSA and HITS respectively."
                #query="The data set is an open benchmark data set which contains 147 documentsummary pairs from Document Understanding Conference (DUC) 2001 http://duc.nist.gov/. We use it because it is for (generic single-document, extraction task) that we are interested in and it is well preprocessed. We denoted it by DUC01."
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
                res = nertagger.tag(sentence.split())
                #print(res)

                result = []
                result2=[]

                #print(doc["_source"]["title"])
                #result.append(doc["_source"]["title"])
                temp=''

                for i, (a, b) in enumerate(res):

                    if b == 'DATA':
                        result.append(a)





                        #result.append(a)


                #print(set(result))
                datasets=[]
                # if result:
                #     for r in set(result):
                #         datasets.append(r)
                #
                #         for i, (a, b) in enumerate(res):
                #
                #             if a==r:
                #
                #                 if i>0:
                #                     j=i-1
                #                     if res[j][0] == 'and' or ',' in res[j][0]:
                #                         j = j - 1
                #                     try:
                #                         datasets.append(r)
                #                         j = j - 1
                #
                #                         if res[j][0] == 'and' or ',' in res[j][0]:
                #
                #
                #                             #datasets.append(res[j][0])
                #                             j = j - 1
                #                             datasets.append(res[j][0])
                #                     except:
                #                         continue
                #
                #                     z=i+1
                #                     try:
                #
                #                         if ',' in res[i][0] or res[z][0] == 'and' or ',' in res[z][0] or res[z][0] == ' and' or res[z][0] == 'and ':
                #                             #datasets.append(res[z][0])
                #                             z=z+1
                #                             datasets.append(res[z][0])
                #                     except:
                #                         continue

               #print(set(datasets))
                #filterbywordnet=[]
                filtered_words = [word for word in set(result) if word not in stopwords.words('english')]


                #filterbywordnet = [word for word in filtered_words if not wordnet.synsets(word)]
                #print(filtered_words)
                for word in set(filtered_words):
                    inwordNet=1
                    inds=0
                    if not wordnet.synsets(word):
                        filterbywordnet.append(word)
                        newnames.append(word)
                        inwordNet = 0


                    #store_datasetname_in_mongo(db,doc["_id"],doc["_source"]["title"], doc["_source"]["journal"],doc["_source"]["year"],  word, inwordNet,inds)
               # print(set(filtered_words))
        newnames=list(set(newnames))
        f1 = open('/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation/ec_NewNEs1'+ str(numberOfSeeds) + '_' + str(iteration) +'.txt', 'w')
        for item in newnames:
            f1.write(item + '"\n')
        f1.close()

iteration_ner(2)
iteration_ner(5)
iteration_ner(10)
iteration_ner(25)
iteration_ner(50)
iteration_ner(100)
#print(set(result2))
    #print(get_continuous_chunks(query))



            # for word in res:
            #     if word[0] == r:
            #         if temp=='and' or ',' in temp:
            #          result.append(word[0])
            #     temp=word[0]

#query="Social media provides a continuously-updated stream of data which has proven useful for predicting group behaviors and modeling populations. Associating data with the particular geolocation from which it originated creates a powerful tool for modeling geographic phenomena, such as tracking the flu, predicting elections, or observing linguistic differences between groups. However, only a small amount of social media data comes with location; for example, less than one percent of twitter posts are associated with a geolocation . Therefore, recent work has focused on geoinference for predicting the locations of posts. One direction of geoinference using social networks has produced approaches that claim to accurately locate the majority of posts within tens of kilometers of their true locations (McGee, Caverlee, and Cheng 2013; Rout et al. 2013; Jurgens 2013; Compton, Jurgens, and Allen 2014)."

