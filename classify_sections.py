from pyhelpers import tools
from playground import dictionary
import nltk
import time
import _pickle as cPickle
import textrazor
from nltk.corpus import wordnet

textrazor.api_key = "9f466f8622a88d099f740d54b435845746914cbc43c831652408a5eb"

booktitles = ['WWW','VLDB']
journals = ['TACO', 'JOCCH']

sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')


def vectorize(labeleddata, name_of_class):
    with open('classifiers/vectorizer_' + name_of_class + '.pkl', 'rb') as pickle_file:
        vectorizer = cPickle.load(pickle_file)
    X = vectorizer.transform(labeleddata)
    return X


def classify_sentence(sent, name_of_class):
    X = vectorize(sent, name_of_class)
    with open('classifiers/LogisticR_' + name_of_class + '_classifier.pkl', 'rb') as pickle_file:
        clf = cPickle.load(pickle_file)

    label = clf.predict(X)
    return label


def sentence_extraction(db):
    """
    this function classifies the sentences into different classess. we also extract a set of NER from the rhetorical texts using TextraZor we take all the chapters for each paper and we check each sentence separately.
    Also, we merge subsection to keep it consistent (Auxiliary functions: return_chapters(),
    merge_subsections().
    :param db:

    :return: list of tuples in the format (chapter number, paper_id, sentence)
    """

    list_of_pubs = []  # list of lists of different booktitles
    start = time.time()


    client = textrazor.TextRazor(extractors=["entities", "topics"])

    for booktitle in booktitles:
        mongo_string_search = {'$and': [{'booktitle': booktitle}, {'content.chapters': {'$exists': True}}]}
        list_of_pubs.append(return_chapters(mongo_string_search, db))
    end = time.time()
    print("Time of the return_chapters {}".format(end - start))

    count = 1
    collection_size = db.rhetorical.find({}).count()
    rhet_id = collection_size

    collection_size = db.ner.find({}).count()
    ner_id = collection_size

    start = time.time()
    for pubs in list_of_pubs:
        for paper in pubs:
            print(paper['dblpkey'])
            if check_if_paperprocessed_exist_in_db(db, paper['dblpkey']):
                print("This Paper has been checked already")
            else:

                dataset_rhet_sent = []
                print('####number of papers###########')
                print(count)
                count += 1
                if paper['abstract'] != "":

                    processed_sentences = []
                    text_razor = paper['abstract']
                    if text_razor:

                        response = client.analyze(text_razor)
                    else:
                        response = []
                    sentences = (sent_detector.tokenize(paper['abstract'].strip()))
                    for sentence in sentences:
                        sent = sentence.replace('"', '').strip()
                        sent = sent.replace(",", " ")
                        processed_sentences.append(sent)
                    if len(processed_sentences) > 1:
                        classes = ["objective", "software", "method", "dataset", "result"]
                        for cls in classes:
                            label = classify_sentence(processed_sentences, cls)
                            for i in range(len(label)):
                                if label[i] == 1:
                                    store_rhetorical_in_mongo(db, rhet_id, "abstract", paper['dblpkey'],
                                                              processed_sentences[i], cls, len(processed_sentences))

                                    textrazor_ent = []
                                    for entity in response.entities():
                                        # print("entity.id#############")
                                        # print(entity.id)
                                        tokens = processed_sentences[i].lower()
                                        # print(tokens)
                                        # print(entity.id.lower())
                                        if entity.id.lower() in tokens:
                                            if not wordnet.synsets(entity.id.lower()):

                                                store_ner_in_mongo(db, ner_id, cls, 'abstract', paper['dblpkey'], rhet_id,
                                                                   entity.id,
                                                                   entity.relevance_score,
                                                                   entity.confidence_score,
                                                                   entity.wikipedia_link, entity.freebase_types,
                                                                   entity.dbpedia_types,
                                                                   len(response.entities()), 0)


                                            else:
                                                store_ner_in_mongo(db, ner_id, cls, 'abstract', paper['dblpkey'], rhet_id,
                                                                   entity.id,
                                                                   entity.relevance_score,
                                                                   entity.confidence_score,
                                                                   entity.wikipedia_link, entity.freebase_types,
                                                                   entity.dbpedia_types,
                                                                   len(response.entities()), 1)



                                            ner_id += 1


                                    rhet_id += 1




                                    # if len(dataset_rhet_sent)>0:
                                    #   dataset_rhet_sent=''.join(dataset_rhet_sent)



                                    # store_rhetorical_in_mongo(db, rhet_id, "abstract", paper['dblpkey'],dataset_rhet_sent, cls)

                for i, chapter in enumerate(paper['chapters']):
                    text_razor = chapter
                    if text_razor:

                        response = client.analyze(text_razor)
                    else:
                        response = []
                    # response = client.analyze(text_razor)




                    processed_sentences = []
                    sentences = (sent_detector.tokenize(chapter.strip()))

                    for sentence in sentences:
                        sent = sentence.replace('"', '').strip()
                        sent = sent.replace(",", " ")
                        processed_sentences.append(sent)

                    if len(processed_sentences) > 2:
                        classes = ["objective", "software", "method", "dataset", "result"]
                        for cls in classes:

                            label = classify_sentence(processed_sentences, cls)
                            for j in range(len(label)):
                                if label[j] == 1:

                                    store_rhetorical_in_mongo(db, rhet_id, i, paper['dblpkey'],
                                                              processed_sentences[j], cls, len(processed_sentences))
                                    textrazor_ent = []
                                    for entity in response.entities():
                                        # print("entity.id")
                                        # print(entity.id)
                                        tokens = processed_sentences[j].lower()
                                        if entity.id.lower() in tokens:
                                            if not wordnet.synsets(entity.id.lower()):
                                                
                                                store_ner_in_mongo(db, ner_id, cls, i, paper['dblpkey'], rhet_id,
                                                                   entity.id,
                                                                   entity.relevance_score,
                                                                   entity.confidence_score,
                                                                   entity.wikipedia_link, entity.freebase_types,
                                                                   entity.dbpedia_types,
                                                                   len(response.entities()),0)

                                                
                                            else:
                                                store_ner_in_mongo(db, ner_id, cls, i, paper['dblpkey'], rhet_id,
                                                                   entity.id,
                                                                   entity.relevance_score,
                                                                   entity.confidence_score,
                                                                   entity.wikipedia_link, entity.freebase_types,
                                                                   entity.dbpedia_types,
                                                                   len(response.entities()), 1)
                                                

                                            # print(entity.id, entity.relevance_score, entity.confidence_score, entity.wikipedia_link)
                                            


                                            ner_id += 1


                                    rhet_id += 1


    # list_of_sentences.append(objective_sentences)
    return True


def check_if_rhetoricalsection_exist_in_db(db, chapter_num, paper_id):
    check_string = {'chapter_num': chapter_num, 'paper_id': paper_id}
    if db.rhetorical_sentences.find_one(check_string) is not None:
        print("We already checked this part")
        return True
    else:
        return False


def check_if_paperprocessed_exist_in_db(db, paper_id):
    check_string = {'paper_id': paper_id}
    if db.rhetorical_sentences.find_one(check_string) is not None:
        print("We already checked this paper")
        return True
    else:
        return False


def check_if_rhetorical_exist_in_db(db, chapter_num, paper_id, rhetorical, label):
    check_string = {'chapter_num': chapter_num, 'paper_id': paper_id, 'rhetorical': rhetorical, 'label': label}
    if db.rhetorical_sentences.find_one(check_string) is not None:
        print("Rhetorical already in db")
        return True
    else:
        return False


def check_if_ner_exist_in_db(db, chapter_num, paper_id, ner, label):
    check_string = {'chapter_num': chapter_num, 'paper_id': paper_id, 'ner': ner, 'label': label}
    if db.sentences_ner.find_one(check_string) is not None:
        print("Ner already in db")
        return True
    else:
        return False


def store_rhetorical_in_mongo(db, rhetorical_id, chapter_num, paper_id, rhetorical, label, totalsentences):
    rhet = {
        "rhetorical_id": rhetorical_id,
        "chapter_num": chapter_num,
        "paper_id": paper_id,
        "rhetorical": rhetorical,
        "label": label,
        "totalsentences": totalsentences

    }

    if check_if_rhetorical_exist_in_db(db, chapter_num, paper_id, rhetorical, label):
        return False
    else:

        db.rhetorical_sentences.insert_one(rhet)
        return True


def store_ner_in_mongo(db, ner_id, label, chapter_num, paper_id, rhetorical_id, ner, relevance_score, confidence_score,
                       wikipedia_link, freebase_types, dbpedia_types, totalner, inWordnet):
    my_ner = {
        "ner_id": ner_id,
        "label": label,
        "chapter_num": chapter_num,
        "paper_id": paper_id,
        "rhetorical_id": rhetorical_id,
        "ner": ner,
        "relevance_score": relevance_score,
        "confidence_score": confidence_score,
        "wikipedia_link": wikipedia_link,
        "freebase_types": freebase_types,
        "dbpedia_types": dbpedia_types,
        "totalner": totalner,
        'inWordnet':inWordnet

    }

    #if check_if_ner_exist_in_db(db, chapter_num, paper_id, ner, label):
    #    return False
    #else:
    print(chapter_num, paper_id, ner)
    db.sentences_ner.insert_one(my_ner)

    return True


def check_tokens(sent, tokens):
    count = 0
    sent = nltk.word_tokenize(sent)

    for t in tokens:
        for ts in sent:
            if t == ts:
                count += 1
                break
    if count == len(tokens):
        return True
    else:
        return False


def return_chapters(mongo_string_search, db):
    # mongo_string_search = {"dblpkey": "{}".format(dblkey)}
    results = db.publications.find(mongo_string_search)
    chapters = list()
    chapter_nums = list()
    list_of_docs = list()
    # list_of_abstracts = list()
    merged_chapters = list()
    my_dict = {
        "dblpkey": "",
        "chapters": list(),
        "abstract": ""
    }
    for i, r in enumerate(results):
        # try:
        # list_of_sections = list()
        my_dict['dblpkey'] = r['dblpkey']
        my_dict['title'] = r['title']
        # print(r['content']['abstract'])
        try:
            my_dict['abstract'] = r['content']['abstract']
        except:
            my_dict['abstract'] = ""
            # print(my_dict)
            # sys.exit(1)
        try:
            for chapter in r['content']['chapters']:
                # print(r['dblpkey'])
                if (chapter == {}):
                    continue
                    # remove the filter that removes related works
                    # elif str(chapter['title']).lower() in filter_chapters:
                    # print(chapter['title'])
                #    continue
                section = ""
                chapter_nums.append(chapter['chapter_num'])
                # print(chapter['title'])
                for paragraph in chapter['paragraphs']:
                    if paragraph == {}:
                        continue
                    section += paragraph
                chapters.append(section)
                section = ""
            chapters = chapter_nums, chapters
            my_dict['chapters'] = merge_subsections(chapters)

            list_of_docs.append(my_dict)
            my_dict = {
                "dblpkey": "",
                "chapters": list(),
                "abstract": ""
            }
            chapters = list()
            chapter_nums = list()
        except:
            # print("eeror")
            print("Document {} has a Key Error - continue to the next document".format(r['dblpkey']))
            continue
    return list_of_docs


def merge_subsections(chapters):
    numbers = set()
    # print(len(chapters[0]))
    for j, num in enumerate(chapters[0]):
        tmp = num.split(".")[0]
        numbers.add(tmp)
    numbers = sorted(numbers)
    new_list = list()
    for k, num in enumerate(numbers):
        merged = ""
        count = 0
        for i, ch_num in enumerate(chapters[0]):
            if ch_num.startswith(num):
                count += 1
                merged += chapters[1][i]
                # print (num,ch_num)
        new_list.append(merged)
    return new_list


def drop_create_rhetorical_collection(db):
    db.create_collection("rhetorical_sentences")
    print("Collection 'rhetorical' created")


def drop_create_ner_collection(db):
    db.create_collection("sentences_ner")
    print("Collection 'ner' dropped and created")


def drop_create_keyword_collection(db):
    collections = db.collection_names()
    if "keywords" in collections:
        db.keywords.drop()
        db.create_collection("keywords")
        print("Collection 'keywords' dropped and created")
        """
        my_dict = {
            "objective": dictionary.objective,
            "dataset": dictionary.dataset,
            "method": dictionary.method,
            "software": dictionary.software,
            "result": dictionary.result
        }
        """
        key_id = 0
        key_set = set()
        for key in dictionary.objective:
            if key.lower() not in key_set:
                key_word = {
                    'key_id': key_id,
                    'label': "objective",
                    'term': key.lower()
                }
                db.keywords.insert_one(key_word)
                key_id += 1
                key_set.add(key.lower())

        key_set = set()
        for key in dictionary.software:
            if key.lower() not in key_set:
                key_word = {
                    'key_id': key_id,
                    'label': "software",
                    'term': key.lower()
                }
                db.keywords.insert_one(key_word)
                key_id += 1
                key_set.add(key.lower())

        key_set = set()
        for key in dictionary.method:
            if key.lower() not in key_set:
                key_word = {
                    'key_id': key_id,
                    'label': "method",
                    'term': key.lower()
                }
                db.keywords.insert_one(key_word)
                key_id += 1
                key_set.add(key.lower())

        key_set = set()
        for key in dictionary.dataset:
            if key.lower() not in key_set:
                key_word = {
                    'key_id': key_id,
                    'label': "dataset",
                    'term': key.lower()
                }
                db.keywords.insert_one(key_word)
                key_id += 1
                key_set.add(key.lower())

        key_set = set()
        for key in dictionary.result:
            if key.lower() not in key_set:
                key_word = {
                    'key_id': key_id,
                    'label': "result",
                    'term': key.lower()
                }
                db.keywords.insert_one(key_word)
                key_id += 1
                key_set.add(key.lower())

        return False


def main():
    db = tools.connect_to_mongo()
    """


    if check_collection_sentences_exist(db):
        print("Collection 'sentences'  exist")
    else:
        print("Collection 'sentences' was created")

    if check_collection_keywords_exist(db):
        print("Collection 'keywords'  exist")
    else:
        print("Collection 'keywords' was created")

    """
    # aggregatedb(db)
    # drop_create_sentence_collection(db)
    # drop_create_keyword_collection(db)
    # start = time.time()
    sentence_extraction(db)  # 626

    # drop_create_ner_collection(db)
    # drop_create_rhetorical_collection(db)
    """
    re = db.sentences.aggregate([
        {"$group": {
            "_id": {"sentence": "$sentence", "chapter_num": "$chapter_num", "paper_id": "$paper_id"},
            "uniqueIds": {"$addToSet": "$_id"},
            "count": {"$sum": 1}
        }},
        {"$match": {
            "count": {"$gt": 1}
        }}
    ])
    """
    # end = time.time()
    # print("Total time {} seconds".format(end - start))
    # create_datasets(128,db)


if __name__ == '__main__':
    main()
