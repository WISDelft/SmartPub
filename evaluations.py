from pyhelpers import tools

import itertools


def ner_with_wikipedia(db):
    response = db.sentences_ner.aggregate([{"$match": {"wikipedia_link": {"$ne": ""}}},
                                           {"$group":
                                                {'_id': {'ner': "$ner", 'wikipedia': "$wikipedia_link",
                                                         "wikiid": '$dbpedia_types'}, 'count': {'$sum': 1}}
                                            },
                                           {'$sort': {"count": -1}}
                                           ])

    f = open("ner1_with_wiki_descending.csv", "w", encoding="UTF-8")
    f.write(
        "ner, count, wikipedia,dbpedia_id")
    f.write("\n")

    for r in response:
        print(r['_id']['ner'])
        print(r['count'])
        str = ""
        for j in range(3):
            try:
                str = r['_id']['wikiid'][j] + "-"
            except:
                str = ""
                continue
        f.write("{},{},{},{}".format(r['_id']['ner'], r['count'], r['_id']['wikipedia'], str))
        f.write("\n")
    f.close()


def count_sentences(db):
    response = db.rhetorical_sentences.aggregate([{"$match": {'paper_id': {'$regex': 'conf_www'}}},
                                                  {"$group":
                                                       {'_id': {'paper_id': "$paper_id", 'chapter_num': "$chapter_num",
                                                                'totalsentences': '$totalsentences'},
                                                        'totalsentences': {'$sum': '$totalsentences'}}
                                                   }
                                                  ])
    totalcount = 0
    for r in response:
        # print(r['_id']['totalsentences'])
        temp = r['_id']['totalsentences']
        totalcount = totalcount + int(temp)
    print(totalcount)


def count_ner(db):
    response = db.sentences_ner.aggregate([{"$match": {'paper_id': {'$regex': 'conf_icwsm'}, 'label': 'dataset'}},
                                           {"$group":
                                                {'_id': {'ner': "$ner", 'label': "$label"}}
                                            }
                                           ])
    count = 0
    for r in response:
        count = count + 1
    print(count)


def ner_without_wikipedia(db):
    response = db.sentences_ner.aggregate([{"$match": {"wikipedia_link": ""}},
                                           {"$group":
                                                {'_id': {'ner': "$ner", 'wikipedia': "$wikipedia_link"},
                                                 'count': {'$sum': 1}}
                                            },
                                           {'$sort': {"count": 1}}
                                           ])

    f = open("ner_without_wikipedia_ascending.csv", "w", encoding="UTF-8")
    f.write(
        "ner, count, wikipedia")
    f.write("\n")

    for r in response:
        print(r['_id']['ner'])
        print(r['count'])
        f.write("{},{},{},{}".format(r['_id']['ner'], r['count'], r['_id']['wikipedia']))
        f.write("\n")
    f.close()


def ner_without_wikipedia_notinwordnet(db):
    response = db.sentences_ner.aggregate(
        [{"$match": {"wikipedia_link": "", "inWordnet": {"$exists": "true", "$ne": 1}}},
         {"$group":
              {"_id": {"ner": "$ner", "wikipedia": "$wikipedia_link"}, "count": {"$sum": 1}}
          }, {"$sort": {"count": 1}}
         ])

    f = open("ner_without_wikipedia_notinwordnet_ascending.csv", "w", encoding="UTF-8")
    f.write(
        "ner, count, wikipedia")
    f.write("\n")

    for r in response:
        print(r['_id']['ner'])
        print(r['count'])
        f.write("{},{},{}".format(r['_id']['ner'], r['count'], r['_id']['wikipedia']))
        f.write("\n")
    f.close()


def ner_without_wikipedia_inwordnet(db):
    response = db.sentences_ner.aggregate(
        [{"$match": {"wikipedia_link": "", "inWordnet": {"$exists": "true", "$ne": 0}}},
         {"$group":
              {"_id": {"ner": "$ner", "wikipedia": "$wikipedia_link"}, "count": {"$sum": 1}}
          }, {"$sort": {"count": -1}}
         ])

    f = open("ner_without_wikipedia_inwordnet_descending.csv", "w", encoding="UTF-8")
    f.write(
        "ner, count, wikipedia")
    f.write("\n")

    for r in response:
        print(r['_id']['ner'])
        print(r['count'])
        f.write("{},{},{}".format(r['_id']['ner'], r['count'], r['_id']['wikipedia']))
        f.write("\n")
    f.close()


def ner_dataset_without_wiki_not_inwordnet(db):
    response = db.sentences_ner.aggregate(
        [{"$match": {"wikipedia_link": "", "inWordnet": {'$exists': 'true', '$ne': 1}, 'label': 'dataset'}},
         {"$group":
              {'_id': {'ner': "$ner", 'wikipedia': "$wikipedia_link"}, 'count': {'$sum': 1}}
          },
         {'$sort': {"count": -1}}
         ])

    f = open("ner_dataset2_without_wiki_not_inwordnet.csv", "w", encoding="UTF-8")
    f.write(
        "ner, count, wikipedia")
    f.write("\n")

    for r in response:
        print(r['_id']['ner'])
        print(r['count'])
        f.write("{},{},{}".format(r['_id']['ner'], r['count'], r['_id']['wikipedia']))
        f.write("\n")
    f.close()


def dataset_method_relation(db):
    f = open("Facebookicwsm_method.csv", "w", encoding="UTF-8")
    f.write(
        "method, count")
    f.write("\n")

    papers = db.sentences_ner.distinct('paper_id', {'ner': 'Facebook', 'paper_id': {'$regex': 'conf_icwsm'}})
    for p in papers:
        print(p)
        methods = db.sentences_ner.aggregate(
            [{"$match": {'paper_id': p, "inWordnet": {'$exists': 'true', '$ne': 1}, 'label': 'method'}},
             {"$group":
                  {'_id': {'ner': "$ner"}, 'count': {'$sum': 1}}
              }, {'$sort': {'count': -1}}
             ])
        for m in methods:
            f.write("{},{}".format(m['_id']['ner'], m['count'], ))
            f.write("\n")
    f.close()


def check_www(db):
    res = db.rhetorical_sentences.aggregate(
        [{"$match": {'paper_id': {'$regex': 'conf_www'}, 'chapter_num': {'$gt': 9}}},
         {"$group":
              {'_id': {'paper_id': "$paper_id", 'chapter_num': "$chapter_num",
                       'totalsentences': '$totalsentences'},
               'totalsentences': {'$sum': '$totalsentences'}}
          }
         ])
    count = 0

    for r in res:
        count = count + 1
        print(r['_id']['paper_id'])
    print(count)


def getKey(item):
    return item[0]


def count_dataset_method(db):
    result = []
    f = open("Pinterestdataset_method_sorted.csv", "w", encoding="UTF-8")
    f.write(
        "method, count")
    f.write("\n")
    with open('Pinterestdataset_method.csv', "r") as fp:
        for i in fp.readlines():
            tmp = i.split(",")
            try:
                result.append((tmp[0], float(tmp[1])))
                # result.append((eval(tmp[0]), eval(tmp[1])))
            except:
                pass

    result = [(sum(i[1] for i in group), key) for key, group in
              itertools.groupby(sorted(result, key=lambda i: i[0]), lambda i: i[0])]
    result = sorted(result, key=getKey)

    for r in result:
        f.write("{},{}".format(r[0], r[1]))
        f.write("\n")

    f.close()


def analysis(db):
    response = db.sentences_ner.aggregate(
        [{"$match": {"wikipedia_link": {'$ne': ""}, 'label': 'dataset'}},
         {"$group":
              {'_id': {'ner': "$ner", 'wikipedia': "$wikipedia_link"}, 'count': {'$sum': 1}}
          },
         {'$sort': {"count": -1}}
         ])

    f = open("ner_dataset2_without_wiki_not_inwordnet.csv", "w", encoding="UTF-8")
    f.write(
        "ner, count, wikipedia")
    f.write("\n")

    for r in response:
        print(r['_id']['ner'])
        print(r['count'])
        f.write("{},{},{}".format(r['_id']['ner'], r['count'], r['_id']['wikipedia']))
        f.write("\n")
    f.close()
def is_int_or_float(s):
    ''' return 1 for int, 2 for float, -1 for not a number'''
    try:
        float(s)

        return 1 if s.count('.')==0 else 2
    except ValueError:
        return -1

def test_ner(db):
    response = db.sentences_ner.distinct('ner', {"inWordnet": {'$exists': 'true', '$ne': 1}})
    f = open("ner_performance1.csv", "w", encoding="UTF-8")
    f.write(
        "ner, objective, dataset, method, software, result")
    f.write("\n")
    print(len(response))
    count = 0
    for r in response:
        print(count)
        count = count + 1
        isint=is_int_or_float(r)

        if isint == -1:
            ner_count = []
            total = db.get_collection('sentences_ner').find({'ner': r}).count()

            objectivecount = db.get_collection('sentences_ner').find({'ner': r, 'label': 'objective'}).count()
            datasetcount = db.get_collection('sentences_ner').find({'ner': r, 'label': 'dataset'}).count()
            methodcount = db.get_collection('sentences_ner').find({'ner': r, 'label': 'method'}).count()
            softwarecount = db.get_collection('sentences_ner').find({'ner': r, 'label': 'software'}).count()
            resultcount = db.get_collection('sentences_ner').find({'ner': r, 'label': 'result'}).count()
            ner_count.append(objectivecount / total)
            ner_count.append(datasetcount / total)
            ner_count.append(methodcount / total)
            ner_count.append(softwarecount / total)
            ner_count.append(resultcount / total)
            norm = [(float(i) - min(ner_count)) / (max(ner_count) - min(ner_count)) for i in ner_count]

            f.write("{},{},{},{},{},{}".format(r, norm[0], norm[1], norm[2], norm[3], norm[4]))
            f.write("\n")
    f.close()


def rhetorical(db):
    response = db.get_collection('rhetorical_sentences').find({})
    cc = db.get_collection('rhetorical_sentences').find({}).count()
    print(cc)
    f = open("measure_of_dispersion.csv", "w", encoding="UTF-8")
    f.write(
        ".paper_id,'rhetorical_id', single_sent, multi_sent")
    f.write("\n")
    list_multi = []
    list_single = []
    count = 0
    for rr in response:
        print(count)
        count = count + 1

        res = db.get_collection('rhetorical_sentences').find({'rhetorical': rr['rhetorical']})
        total = db.get_collection('rhetorical_sentences').find({'rhetorical': rr['rhetorical']}).count()

        multi = 0

        list_of_docs = list()

        my_dict = {
            "paper_id": "",
            "rhetorical_id": "",
            "label": "",
            "rhetorical":""
        }
        for i, r in enumerate(res):
            # try:
            # list_of_sections = list()
            my_dict['paper_id'] = r['paper_id']
            # print(r['content']['abstract'])

            my_dict['rhetorical_id'] = r['rhetorical_id']
            my_dict['label'] = r['label']

            list_of_docs.append(my_dict)
            my_dict = {
                "paper_id": "",
                "rhetorical_id": "",
                "label": "",
                "rhetorical": ""
            }
        mymulti = 0
        mysingle = 0
        for i in list_of_docs:

            for j in list_of_docs:
                if i['paper_id'] == j['paper_id'] and i['rhetorical'] == j['rhetorical'] and i['label'] != j[
                    'label']:
                    multi = multi + 1
            if multi > 0:
                mymulti = mymulti + 1
            else:
                mysingle = mysingle + 1
            multi = 0


        list_multi.append(mymulti)
        list_single.append(mysingle)
        f.write("{},{},{},{}".format(r['paper_id'], r['rhetorical_id'], mysingle / total, mymulti / total))
        f.write("\n")
    summulti = sum(list_multi)
    sumsingle = sum(list_single)
    print(summulti)
    print(sumsingle)
    f.close()


def main():
    db = tools.connect_to_mongo()

    #test_ner(db)
    rhetorical(db)
    #dataset_method_relation(db)
    #count_dataset_method(db)


if __name__ == '__main__':
    main()
