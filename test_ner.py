from pyhelpers import tools
import math



def is_int_or_float(s):
    ''' return 1 for int, 2 for float, -1 for not a number'''
    try:
        float(s)

        return 1 if s.count('.')==0 else 2
    except ValueError:
        return -1

def test_ner(db):
    response = db.sentences_ner.distinct('ner', {"inWordnet": {'$exists': 'true', '$ne': 1}})
    totalner = db.get_collection('sentences_ner').find({}).count()
    f = open("ner_tfidf.csv", "w", encoding="UTF-8")
    f.write("ner, idf, objective_tf, dataset_tf, method_tf, software_tf, result_tf,objective_tfidf, dataset_tfidf, method_tfidf, software_tfidf, result_tfidf")
    f.write("\n")
    print(len(response))
    count = 0
    for r in response:
        print(count)
        count = count + 1
        isint = is_int_or_float(r)

        if isint == -1:
            ner_count = []
            total = db.get_collection('sentences_ner').find({'ner': r}).count()

            objectivecount = db.get_collection('sentences_ner').find({'ner': r, 'label': 'objective'}).count()
            datasetcount = db.get_collection('sentences_ner').find({'ner': r, 'label': 'dataset'}).count()
            methodcount = db.get_collection('sentences_ner').find({'ner': r, 'label': 'method'}).count()
            softwarecount = db.get_collection('sentences_ner').find({'ner': r, 'label': 'software'}).count()
            resultcount = db.get_collection('sentences_ner').find({'ner': r, 'label': 'result'}).count()
            if objectivecount!=0:
                objectivecount = 1 + math.log(objectivecount)
            if datasetcount!=0:
                datasetcount = 1 + math.log(datasetcount)
            if methodcount!=0:
                methodcount = 1 + math.log(methodcount)
            if softwarecount!=0:
                softwarecount = 1 + math.log(softwarecount)
            if resultcount!=0:
                resultcount = 1 + math.log(resultcount)


            idf = math.log(totalner / total)
            objectivecountidf = objectivecount * idf
            datasetcountidf = datasetcount * idf
            methodcountidf = methodcount * idf
            softwarecountidf = softwarecount * idf
            resultcountidf = resultcount * idf


            f.write("{},{},{},{},{},{},{},{},{},{},{},{}".format(r, idf,  objectivecount, datasetcount, methodcount, softwarecount,resultcount, objectivecountidf, datasetcountidf, methodcountidf, softwarecountidf, resultcountidf))
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
            "label": ""
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
                "label": ""
            }
        mymulti = 0
        mysingle = 0
        for i in list_of_docs:

            for j in list_of_docs:
                if i['paper_id'] == j['paper_id'] and i['rhetorical_id'] == j['rhetorical_id'] and i['label'] != j[
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

    test_ner(db)
    #rhetorical(db)
    #dataset_method_relation(db)
    #count_dataset_method(db)


if __name__ == '__main__':
    main()
