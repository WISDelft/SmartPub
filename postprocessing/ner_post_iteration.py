
"""
This script uses the trained NER model in the (crf_trained_files or crf_trained_filesMet folder)
to extract entities from the text of papers and stores them in the post_processing_files folder.
"""
from nltk.tag.stanford import StanfordNERTagger
from nltk.corpus import stopwords
import re
import string
from default_config import ROOTHPATH,STANFORD_NER_PATH

filterbywordnet=[]


def iteration_nerER(numberOfSeeds,name,prevnumberOfIteration,numberOfIteration,iteration,es):
            print('started iteration.....', numberOfSeeds, name, numberOfIteration)

            print('numbers:', numberOfSeeds, iteration)

            # change crf_trained_files to  crf_trained_filesMet if you want to extract method entities
            path_to_model = ROOTHPATH + '/crf_trained_files/' + name + '_text_iteration' + prevnumberOfIteration + '_splitted' + str(
                    numberOfSeeds) + '_' + str(iteration) + '.ser.gz'

            nertagger = StanfordNERTagger(path_to_model, STANFORD_NER_PATH)

            newnames = []
            result = []
            filter_conference = ["WWW", "ICSE", "VLDB", "PVLDB", "JCDL", "TREC", "SIGIR", "ICWSM", "ECDL", "ESWC",
                                 "IEEE J. Robotics and Automation", "IEEE Trans. Robotics", "ICRA", "ICARCV", "HRI",
                                 "ICSR", "PVLDB", "TPDL", "ICDM", "Journal of Machine Learning Research",
                                 "Machine Learning"]
            for conference in filter_conference:

                query = {"query":
                    {"match": {
                        "journal": {
                            "query": conference,
                            "operator": "and"
                        }
                    }
                    }
                }

                res = es.search(index="ir", doc_type="publications",
                                body=query, size=10000)
                print(len(res['hits']['hits']))


                for doc in res['hits']['hits']:
                    # sentence = doc["_source"]["text"].replace(',', ' ')
                    sentence= doc["_source"]["content"]
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
                    sentence = re.sub(r"(\.)([A-Z])", r"\1 \2", sentence)
                    tagged = nertagger.tag(sentence .split())






                    for jj, (a, b) in enumerate(tagged):
                             #change DATA to MET if you want to extract method entities
                            if b == 'DATA':
                                a = a.translate(str.maketrans('', '', string.punctuation))
                                try:
                                    if res[jj + 1][1] == 'DATA':
                                        temp = res[jj + 1][0].translate(str.maketrans('', '', string.punctuation))

                                        bigram = a + ' ' + temp
                                        result.append(bigram)
                                except:
                                    continue

                                result.append(a)

            result=list(set(result))
            result = [w.replace('"', '') for w in result]
            filtered_words = [word for word in set(result) if word not in stopwords.words('english')]


            for word in set(filtered_words):
                try:
                        filterbywordnet.append(word)
                        newnames.append(word.lower())
                except:
                    newnames.append(word.lower())

            f1 = open(ROOTHPATH + '/post_processing_files/' + name + '_Iteration' + numberOfIteration + str(
                numberOfSeeds) + '_' + str(iteration) + '.txt', 'w')
            for item in filtered_words:
                f1.write(item + '\n')
            f1.close()
