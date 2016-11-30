from pyhelpers import tools
from playground import dictionary
import nltk
import random
import time
import config
import sys

booktitles = ['WWW', 'SIGIR', 'ESWC', 'ICWSM', 'VLDB']
journals = ['TACO', 'JOCCH']

filter_chapters = ['related work' , 'background', 'state of the art' ,'previous works']

sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')


def sentence_extraction(db, publication_limit):
    """
    this function retrieves all the sentences that contain phrases from the dictionary.py
    To do that, we take all the chapters for each paper and we check each sentence separately.
    Also, we merge subsection to keep it consistent (Auxiliary functions: return_chapters(),
    merge_subsections().
    :param db:
    :param publication_limit
    :return: list of tuples in the format (chapter number, paper_id, sentence)
    """
    checker = set()
    list_of_pubs = [] # list of lists of different booktitles
    start = time.time()

    objective_sentences = list()
    dataset_sentences = list()
    method_sentences = list()
    software_sentences = list()
    result_sentences = list()
    other_sentences = list()

    for booktitle in booktitles:
        mongo_string_search = {'$and': [{'booktitle': booktitle}, {'content.chapters': {'$exists': True}}]}
        list_of_pubs.append(return_chapters(mongo_string_search, db, publication_limit))
    end = time.time()
    print("Time of the return_chapters {}".format(end - start))

    objective_keys = list(db.keywords.find({"label":"objective"}))
    dataset_keys = list(db.keywords.find({"label":"dataset"}))
    method_keys = list(db.keywords.find({"label": "method"}))
    software_keys = list(db.keywords.find({"label": "software"}))
    result_keys = list(db.keywords.find({"label": "result"}))

    flag_result = False
    flag_method = False
    flag_software = False
    flag_dataset = False
    flag_objective = False
    count = 1
    collection_size = db.sentence.find({}).count()
    sent_id = collection_size

    start = time.time()
    for pubs in list_of_pubs:
        for paper in pubs:
            print(count)
            count += 1
            if paper['abstract'] != "":
                #check_abstract(abstract_id, paper['dblpkey'],objective_keys,dataset_keys,method_keys,software_keys,result_keys)
                #objsents = check_for_objective(paper['abstract'],paper['dblpkey']).copy()
                #for obj_sent in objsents:
                #    objective_sentences.append(obj_sent)


                sentences = (sent_detector.tokenize(paper['abstract'].lower().strip()))
                for sent in sentences:
                    set_of_keywords = set()
                    #if sent not in checker:
                    #print(sent)
                    for word in result_keys:
                        #print(sent,word['term'])
                        tokens = nltk.word_tokenize(word['term'].lower())
                        if len(tokens) > 1:
                            all_tokens_in_sent = check_tokens(sent, tokens)
                            if all_tokens_in_sent:
                                flag_result = True
                                set_of_keywords.add(word['key_id'])

                                    # list_of_sentences.append((i, paper['dblpkey'], sent, "result"))
                                    # result_sentences.append((i, paper['dblpkey'], sent, "result"))
                                    # checker.add(sent)

                        elif word['term'].lower() in sent:
                            set_of_keywords.add(word['key_id'])
                            flag_result = True

                                # list_of_sentences.append((i, paper['dblpkey'], sent, "result"))
                                # result_sentences.append((i, paper['dblpkey'], sent, "result"))
                                # checker.add(sent)

                                # if flag_result:
                                #    break
                        # if not flag_result:
                    for word in software_keys:
                        tokens = nltk.word_tokenize(word['term'].lower())
                        if len(tokens) > 1:
                            all_tokens_in_sent = check_tokens(sent, tokens)
                            if all_tokens_in_sent:
                                set_of_keywords.add(word['key_id'])
                                flag_software = True

                                    # list_of_sentences.append((i, paper['dblpkey'], sent, "software"))
                                    # software_sentences.append((i, paper['dblpkey'], sent, "software"))
                                    # checker.add(sent)

                        elif word['term'].lower() in sent:
                            set_of_keywords.add(word['key_id'])
                            flag_software = True

                                # list_of_sentences.append((i, paper['dblpkey'], sent, "software"))
                                # software_sentences.append((i, paper['dblpkey'], sent, "software"))
                                # checker.add(sent)

                                # if flag_software:
                                #    break
                        # if not flag_software:
                    for word in method_keys:
                        tokens = nltk.word_tokenize(word['term'].lower())
                        if len(tokens) > 1:
                            all_tokens_in_sent = check_tokens(sent, tokens)
                            if all_tokens_in_sent:
                                flag_method = True
                                set_of_keywords.add(word['key_id'])

                                    # list_of_sentences.append((i, paper['dblpkey'], sent, "method"))
                                    # method_sentences.append((i, paper['dblpkey'], sent, "method"))
                                    # checker.add(sent)
                        elif word['term'].lower() in sent:
                            flag_method = True
                            set_of_keywords.add(word['key_id'])

                                # list_of_sentences.append((i, paper['dblpkey'], sent, "method"))
                                # method_sentences.append((i, paper['dblpkey'], sent, "method"))
                                # checker.add(sent)
                                # if flag_method:
                                #    break

                        # if not flag_method:
                    for word in dataset_keys:
                        tokens = nltk.word_tokenize(word['term'].lower())
                        if len(tokens) > 1:
                            all_tokens_in_sent = check_tokens(sent, tokens)
                            if all_tokens_in_sent:
                                flag_dataset = True
                                set_of_keywords.add(word['key_id'])

                                    # list_of_sentences.append((i, paper['dblpkey'], sent, "dataset"))
                                    # dataset_sentences.append((i, paper['dblpkey'], sent, "dataset"))
                                    # checker.add(sent)

                        elif word['term'].lower() in sent:
                            flag_dataset = True
                            set_of_keywords.add(word['key_id'])

                                # list_of_sentences.append((i, paper['dblpkey'], sent, "dataset"))

                                # dataset_sentences.append((i, paper['dblpkey'], sent, "dataset"))
                                # checker.add(sent)
                                # if flag_dataset:
                                #    break

                    for word in objective_keys:
                        tokens = nltk.word_tokenize(word['term'].lower())
                        #print(sent,word['term'])
                        if len(tokens) > 1:
                            all_tokens_in_sent = check_tokens(sent, tokens)
                            if all_tokens_in_sent:
                                flag_objective = True
                                set_of_keywords.add(word['key_id'])

                                    # objective_sentences.append(("abstract", dblpkey, sent, "objective"))
                                    # break
                        elif word['term'].lower() in sent:
                            flag_objective = True
                            set_of_keywords.add(word['key_id'])

                                # objective_sentences.append(("abstract", dblpkey, sent, "objective"))
                                # break
                        #print(sent)
                    store_sentence_in_mongo(db, sent_id, "abstract", paper['dblpkey'], set_of_keywords,
                                                sent.replace(",", " "), flag_dataset, flag_objective, flag_software,
                                                flag_result, flag_method)

                    sent_id += 1


                            # if not flag_dataset:
                            # list_of_sentences.append((i, paper['dblpkey'], sent, "other"))
                            #    other_sentences.append((i, paper['dblpkey'], sent, "other"))
                    flag_result = False
                    flag_method = False
                    flag_software = False
                    flag_dataset = False
                    flag_objective = False



            for i, chapter in enumerate(paper['chapters']):

                sentences = (sent_detector.tokenize(chapter.lower().strip()))
                for  sent in sentences:
                    set_of_keywords = set()
                    for word in result_keys:
                        tokens = nltk.word_tokenize(word['term'].lower())
                        if len(tokens) > 1:
                            all_tokens_in_sent = check_tokens(sent, tokens)
                            if all_tokens_in_sent:
                                flag_result = True
                                set_of_keywords.add(word['key_id'])

                                    #list_of_sentences.append((i, paper['dblpkey'], sent, "result"))
                                    #result_sentences.append((i, paper['dblpkey'], sent, "result"))
                                    #checker.add(sent)

                        elif word['term'].lower() in sent:
                            set_of_keywords.add(word['key_id'])
                            flag_result = True

                                #list_of_sentences.append((i, paper['dblpkey'], sent, "result"))
                                #result_sentences.append((i, paper['dblpkey'], sent, "result"))
                                #checker.add(sent)

                            #if flag_result:
                            #    break
                        #if not flag_result:
                    for word in software_keys:
                        tokens = nltk.word_tokenize(word['term'].lower())
                        if len(tokens) > 1:
                            all_tokens_in_sent = check_tokens(sent, tokens)
                            if all_tokens_in_sent:
                                set_of_keywords.add(word['key_id'])
                                flag_software = True

                                    #list_of_sentences.append((i, paper['dblpkey'], sent, "software"))
                                    #software_sentences.append((i, paper['dblpkey'], sent, "software"))
                                    #checker.add(sent)

                        elif word['term'].lower() in sent:
                            set_of_keywords.add(word['key_id'])
                            flag_software = True

                                #list_of_sentences.append((i, paper['dblpkey'], sent, "software"))
                                #software_sentences.append((i, paper['dblpkey'], sent, "software"))
                                #checker.add(sent)

                            #if flag_software:
                            #    break
                        #if not flag_software:
                    for word in method_keys:
                        tokens = nltk.word_tokenize(word['term'].lower())
                        if len(tokens) > 1:
                            all_tokens_in_sent = check_tokens(sent, tokens)
                            if all_tokens_in_sent:
                                flag_method = True
                                set_of_keywords.add(word['key_id'])

                                    #list_of_sentences.append((i, paper['dblpkey'], sent, "method"))
                                    #method_sentences.append((i, paper['dblpkey'], sent, "method"))
                                    #checker.add(sent)
                        elif word['term'].lower() in sent:
                            flag_method = True
                            set_of_keywords.add(word['key_id'])

                                #list_of_sentences.append((i, paper['dblpkey'], sent, "method"))
                                #method_sentences.append((i, paper['dblpkey'], sent, "method"))
                                #checker.add(sent)
                            #if flag_method:
                            #    break


                        #if not flag_method:
                    for word in dataset_keys:
                        tokens = nltk.word_tokenize(word['term'].lower())
                        if len(tokens) > 1:
                            all_tokens_in_sent = check_tokens(sent, tokens)
                            if all_tokens_in_sent:
                                flag_dataset = True
                                set_of_keywords.add(word['key_id'])

                                    #list_of_sentences.append((i, paper['dblpkey'], sent, "dataset"))
                                    #dataset_sentences.append((i, paper['dblpkey'], sent, "dataset"))
                                    #checker.add(sent)

                        elif word['term'].lower() in sent:
                            flag_dataset = True
                            set_of_keywords.add(word['key_id'])

                                #list_of_sentences.append((i, paper['dblpkey'], sent, "dataset"))

                                #dataset_sentences.append((i, paper['dblpkey'], sent, "dataset"))
                                #checker.add(sent)
                            #if flag_dataset:
                            #    break

                    for word in objective_keys:
                        tokens = nltk.word_tokenize(word['term'].lower())
                        if len(tokens) > 1:
                            all_tokens_in_sent = check_tokens(sent, tokens)
                            if all_tokens_in_sent:
                                flag_objective = True
                                set_of_keywords.add(word['key_id'])

                                    #objective_sentences.append(("abstract", dblpkey, sent, "objective"))
                                    #break
                        elif word['term'].lower() in sent:
                            flag_objective = True
                            set_of_keywords.add(word['key_id'])

                                #objective_sentences.append(("abstract", dblpkey, sent, "objective"))
                                #break
                    #print(flag_dataset,flag_method,flag_objective,flag_result,flag_software)
                    store_sentence_in_mongo(db,sent_id, i, paper['dblpkey'], set_of_keywords,sent.replace(",", " "), flag_dataset,flag_objective,flag_software,flag_result,flag_method)
                    sent_id += 1

                        #if not flag_dataset:
                            #list_of_sentences.append((i, paper['dblpkey'], sent, "other"))
                        #    other_sentences.append((i, paper['dblpkey'], sent, "other"))
                    flag_result = False
                    flag_method = False
                    flag_software = False
                    flag_dataset = False
                    flag_objective = False

    end = time.time()
    print("Time of the big loop {} seconds".format(end - start))
    #print("objective_sentences {}".format(len(objective_sentences)))
    #list_of_sentences.append(objective_sentences)
    return  True


def store_sentence_in_mongo(db,sentence_id, chapter_num, paper_id, keywords, sentence, f_data, f_obj, f_soft, f_res,f_meth):
    my_sent = {
        "sent_id": sentence_id,
        "chapter_num": chapter_num,
        "paper_id": paper_id,
        "keywords": list(keywords),
        "sentence":sentence,
        "dataset": 1 if f_data else 0,
        "objective": 1 if f_obj else 0,
        "software": 1 if f_soft else 0,
        "result": 1 if f_res else 0,
        "method": 1 if f_meth else 0,
        "other": 0 if f_data or f_obj or f_soft or f_res or f_meth else 1
    }
    check_string = {'$and': [{'chapter_num': chapter_num}, {'paper_id': paper_id}, {'sentence':sentence}]}
    if db.sentences.find(check_string).count() > 1:
        #print("Already in db")
        return False
    else:
        db.sentences.insert_one(my_sent)
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

def return_chapters(mongo_string_search, db, publication_limit):
    # mongo_string_search = {"dblpkey": "{}".format(dblkey)}
    results = db.publications.find(mongo_string_search).limit(publication_limit)
    chapters = list()
    chapter_nums = list()
    list_of_docs = list()
    #list_of_abstracts = list()
    merged_chapters = list()
    my_dict = {
        "dblpkey": "",
        "chapters": list(),
        "abstract": ""
    }
    for i, r in enumerate(results):
        #try:
            # list_of_sections = list()
            my_dict['dblpkey'] = r['dblpkey']
            #print(r['content']['abstract'])
            try:
                my_dict['abstract'] = r['content']['abstract']
            except:
                my_dict['abstract'] = ""
                #print(my_dict)
                #sys.exit(1)
            try:
                for chapter in r['content']['chapters']:
                    #print(r['dblpkey'])
                    if (chapter == {}):
                        continue
                    # remove the filter that removes related works
                    #elif str(chapter['title']).lower() in filter_chapters:
                        #print(chapter['title'])
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
    #print(len(chapters[0]))
    for j,num in enumerate(chapters[0]):
        tmp = num.split(".")[0]
        numbers.add(tmp)
    numbers = sorted(numbers)
    new_list = list()
    for k,num in enumerate(numbers):
        merged = ""
        count = 0
        for i,ch_num in enumerate(chapters[0]):
            if ch_num.startswith(num):
                count += 1
                merged += chapters[1][i]
                # print (num,ch_num)
        new_list.append(merged)
    return new_list




def check_collection_sentences_exist(db):
    collections = db.collection_names()
    if "sentences" in collections:
        #db.sentences.drop()
        #db.create_collection("sentences")
        #print("Collection dropped and created")
        return True
    else:
        db.create_collection("sentences")
        return False

def check_collection_keywords_exist(db):
    collections = db.collection_names()
    if "keywords" in collections:
        # db.sentences.drop()
        # print("Collection dropped")
        return True
    else:
        db.create_collection("keywords")
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



def create_datasets(num_of_sentences,db):
    labels = ["objective", "software", "method", "dataset", "result", "other"]
    size_of_collection = 0


    for label in labels:
        sent_id = []
        res = db.sentences.find({label: 1})
        for r in res:
            sent_id.append(r['_id'])

        #print(sent_id)
        shuffle_list = random.sample(sent_id, len(sent_id))
        f = open(config.folder_datasets + label + ".csv", "w", encoding="UTF-8")
        f.write("sentence_id, chapter_id, paper_id, keywords, sentence, objective, software, dataset, method, result, other")
        f.write("\n")
        for i, sid in enumerate(shuffle_list):
            if i < num_of_sentences:
                res = db.sentences.find_one({'_id': sid})
                chapter_num = res['chapter_num']
                pubid = res['paper_id']
                sent_id = res['_id']
                keywords = str(res['keywords']).replace(",","")
                sentence = res['sentence']
                objective = res['objective']
                software = res['software']
                dataset = res['dataset']
                method = res['method']
                result = res['result']
                other = res['other']
                #print(pubid)
                f.write("{},{},{},{},{},{},{},{},{},{},{}".format(sent_id,chapter_num,pubid,keywords,sentence,
                                                                  objective,software,dataset,method,result,other))
                f.write("\n")
        f.close()
    """
    my_list = list()
    for label in labels:
        print(label)
        results = db.sentences.find({"class":label})
        f = open(config.folder_datasets+label+".csv", "w", encoding="UTF-8")
        for i,res in enumerate(results):
            print(i)
            mystring = ("{},{},{},{}".format(res['chapter'], res['pubId'], res['sentence'], res['class']))
            my_list.append(mystring)

        my_list = random.sample(k=len(my_list), population=my_list)

        for i, string in enumerate(my_list):
            if i < num_of_sentences:
                f.write(string)
                f.write("\n")
            else:
                break
        my_list = list()
        f.close()
        """


def main():
    db = tools.connect_to_mongo()
    if check_collection_sentences_exist(db):
        print("Collection 'sentences'  exist")
    else:
        print("Collection 'sentences' was created")

    if check_collection_keywords_exist(db):
        print("Collection 'keywords'  exist")
    else:
        print("Collection 'keywords' was created")
    start = time.time()
    sentence_extraction(db, 170)
    end = time.time()
    print("Total time {} seconds".format(end - start))
    create_datasets(1000,db)


if __name__ == '__main__':
    main()
