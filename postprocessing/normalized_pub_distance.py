"""
This scripts uses PMI to filter out irrelevant entities
"""
from elasticsearch import Elasticsearch

import re

regex = re.compile(".*?\((.*?)\)")
import math
def NPD(dsnames):
        result=[]
        #print('Started  PMI filtering...')

        #context words for dataset
        contextwords=['dataset', 'corpus', 'collection','repository','benchmark','website']

        # context words for method
        #contextwords = ['method', 'model', 'algorithm', 'approach','technique']


        es = Elasticsearch(
            [{'host': 'localhost', 'port': 9200}]
        )




        dsnames = [x.lower() for x in dsnames]

        dsnames=list(set(dsnames))

        X_train=dsnames

        for cn in contextwords:
            for datasetname in X_train:
                    if any(x in datasetname.lower() for x in contextwords):
                        result.append(datasetname)
                    NN = 2897901

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
                                    body=query, size=100)

                    totala=res['hits']['total']


                    query = {"query":
                        {"match": {
                            "content.chapter.sentpositive": {
                                "query": cn,
                                "operator": "and"
                            }
                        }
                        }
                    }

                    res = es.search(index="twosent", doc_type="twosentnorules",
                                    body=query, size=100)

                    totalb=res['hits']['total']

                    querytext=datasetname+' '+cn
                    #print(querytext)

                    query = {"query":
                        {"match": {
                            "content.chapter.sentpositive": {
                                "query": querytext,
                                "operator": "and"
                            }
                        }
                        }
                    }

                    res = es.search(index="twosent", doc_type="twosentnorules",
                                    body=query, size=100)

                    totalab=res['hits']['total']




                    try:
                        totalab = totalab / NN
                        totala = totala / NN
                        totalb = totalb / NN
                        PMI = totalab / (totala * totalb)
                        PMI=math.log(PMI, 2)
                        #print(PMI)
                        #
                       #print(querytext,totalab/totala)
                        if  PMI >= 2:
                               result.append(datasetname)


                    except:

                        continue

        return result

