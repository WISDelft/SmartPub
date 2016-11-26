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

    flag_result = False
    flag_method = False
    flag_software = False
    flag_dataset = False
    count = 1
    objective_count = 0
    start = time.time()
    for pubs in list_of_pubs:
        for paper in pubs:
            print(count)
            count += 1
            if paper['abstract'] != "":
                objsents = check_for_objective(paper['abstract'],paper['dblpkey']).copy()
                for obj_sent in objsents:
                    objective_sentences.append(obj_sent)
            for i, chapter in enumerate(paper['chapters']):
                sentences = (sent_detector.tokenize(chapter.lower().strip()))
                for sent in sentences:
                    if sent not in checker:
                        for word in dictionary.result:
                            tokens = nltk.word_tokenize(word.lower())
                            if len(tokens) > 1:
                                all_tokens_in_sent = check_tokens(sent, tokens)
                                if all_tokens_in_sent:
                                    #list_of_sentences.append((i, paper['dblpkey'], sent, "result"))
                                    flag_result = True
                                    result_sentences.append((i, paper['dblpkey'], sent, "result"))
                                    checker.add(sent)

                            elif word.lower() in sent:
                                #list_of_sentences.append((i, paper['dblpkey'], sent, "result"))
                                flag_result = True
                                result_sentences.append((i, paper['dblpkey'], sent, "result"))
                                checker.add(sent)

                            if flag_result:
                                break
                        if not flag_result:
                            for word in dictionary.software:
                                tokens = nltk.word_tokenize(word.lower())
                                if len(tokens) > 1:
                                    all_tokens_in_sent = check_tokens(sent, tokens)
                                    if all_tokens_in_sent:
                                        #list_of_sentences.append((i, paper['dblpkey'], sent, "software"))
                                        flag_software = True
                                        software_sentences.append((i, paper['dblpkey'], sent, "software"))
                                        checker.add(sent)

                                elif word.lower() in sent:
                                    #list_of_sentences.append((i, paper['dblpkey'], sent, "software"))
                                    flag_software = True
                                    software_sentences.append((i, paper['dblpkey'], sent, "software"))
                                    checker.add(sent)

                                if flag_software:
                                    break
                        if not flag_software:
                            for word in dictionary.method:
                                tokens = nltk.word_tokenize(word.lower())
                                if len(tokens) > 1:
                                    all_tokens_in_sent = check_tokens(sent, tokens)
                                    if all_tokens_in_sent:
                                        #list_of_sentences.append((i, paper['dblpkey'], sent, "method"))
                                        flag_method = True
                                        method_sentences.append((i, paper['dblpkey'], sent, "method"))
                                        checker.add(sent)
                                elif word.lower() in sent:
                                    #list_of_sentences.append((i, paper['dblpkey'], sent, "method"))
                                    flag_method = True
                                    method_sentences.append((i, paper['dblpkey'], sent, "method"))
                                    checker.add(sent)
                                if flag_method:
                                    break
                        if not flag_method:
                            for word in dictionary.dataset:
                                tokens = nltk.word_tokenize(word.lower())
                                if len(tokens) > 1:
                                    all_tokens_in_sent = check_tokens(sent, tokens)
                                    if all_tokens_in_sent:
                                        #list_of_sentences.append((i, paper['dblpkey'], sent, "dataset"))
                                        flag_dataset = True
                                        dataset_sentences.append((i, paper['dblpkey'], sent, "dataset"))
                                        checker.add(sent)

                                elif word.lower() in sent:
                                    #list_of_sentences.append((i, paper['dblpkey'], sent, "dataset"))
                                    flag_dataset = True
                                    dataset_sentences.append((i, paper['dblpkey'], sent, "dataset"))
                                    checker.add(sent)
                                if flag_dataset:
                                    break
                        if not flag_dataset:
                            #list_of_sentences.append((i, paper['dblpkey'], sent, "other"))
                            other_sentences.append((i, paper['dblpkey'], sent, "other"))
                        flag_result = False
                        flag_method = False
                        flag_software = False
                        flag_dataset = False

    end = time.time()
    print("Time of the big loop {} seconds".format(end - start))
    #print("objective_sentences {}".format(len(objective_sentences)))
    #list_of_sentences.append(objective_sentences)
    return objective_sentences,method_sentences,result_sentences,software_sentences,dataset_sentences,other_sentences


def check_for_objective(abstract, dblpkey):
    objective_sentences = list()
    other_sentences = list()
    sentences = (sent_detector.tokenize(abstract.lower().strip()))
    #sentences = nltk.sent_tokenize(abstract.lower().strip())
    flag_objective = False
    for sent in sentences:
        for word in dictionary.objective:
            tokens = nltk.word_tokenize(word.lower())
            if len(tokens) > 1:
                all_tokens_in_sent = check_tokens(sent, tokens)
                if all_tokens_in_sent:
                    objective_sentences.append(("abstract", dblpkey, sent, "objective"))
                    flag_objective = True
                    break
            elif word.lower() in sent:
                objective_sentences.append(("abstract", dblpkey, sent, "objective"))
                flag_objective = True
                break
        if not flag_objective:
            other_sentences.append(("abstract", dblpkey, sent, "other"))

    return objective_sentences


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
                    elif str(chapter['title']).lower() in filter_chapters:
                        #print(chapter['title'])
                        continue
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


def randomly_selection(all_sentcences):
    """

    :param all_sentcences:
    :return:
    """

    objective_sentences = list(all_sentcences[0])
    method_sentences =  list(all_sentcences[1])
    result_sentences =  list(all_sentcences[2])
    software_sentences =  list(all_sentcences[3])
    dataset_sentences =   list(all_sentcences[4])
    other_sentences =   list(all_sentcences[5])

    filenames = ['objective.csv', 'method.csv', 'result.csv', 'software.csv', 'dataset.csv', 'other.csv']

    objective_sentences = random.sample(k=len(objective_sentences), population= objective_sentences)
    #print("objective sentences in random selection: {}".format(len(objective_sentences)))
    f = open(config.folder_datasets+filenames[0],'w', encoding='UTF-8')
    for tu in objective_sentences:
        my_string = ','.join([str(item).replace(",", "") for item in tu])
        f.write(my_string)
        f.write("\n")
    f.close()

    method_sentences = random.sample(k=len(method_sentences),population= method_sentences)
    f = open(config.folder_datasets+filenames[1],'w', encoding='UTF-8')
    for tu in method_sentences:
        my_string = ','.join([str(item).replace(",", "") for item in tu])
        f.write(my_string)
        f.write("\n")
    f.close()

    result_sentences = random.sample(k=len(result_sentences),population= result_sentences)
    f = open(config.folder_datasets+filenames[2],'w', encoding='UTF-8')
    for tu in result_sentences:
        my_string = ','.join([str(item).replace(",", "") for item in tu])
        f.write(my_string)
        f.write("\n")
    f.close()

    software_sentences = random.sample(k=len(software_sentences),population= software_sentences)
    f = open(config.folder_datasets+filenames[3],'w', encoding='UTF-8')
    for tu in software_sentences:
        my_string = ','.join([str(item).replace(",", "") for item in tu])
        f.write(my_string)
        f.write("\n")
    f.close()

    dataset_sentences = random.sample(k=len(dataset_sentences),population= dataset_sentences)
    f = open(config.folder_datasets+filenames[4],'w', encoding='UTF-8')
    for tu in dataset_sentences:
        my_string = ','.join([str(item).replace(",", "") for item in tu])
        f.write(my_string)
        f.write("\n")
    f.close()

    other_sentences = random.sample(k=len(other_sentences),population= other_sentences)
    f = open(config.folder_datasets+filenames[5],'w', encoding='UTF-8')
    for tu in other_sentences:
        my_string = ','.join([str(item).replace(",", "") for item in tu])
        f.write(my_string)
        f.write("\n")
    f.close()


def check_collection_sentences_exist(db):
    collections = db.collection_names()
    if "sentences" in collections:
        db.sentences.drop()
        print("Collection dropped")
        return True
    else:
        db.create_collection("sentences")
        return False


def store_sentences_in_mongo(db, all_senteces):
    for category in all_senteces:
        for sent in category:
            sentence_info = {
                "chapter": sent[0],
                "pubId": sent[1],
                "sentence": sent[2].replace(",", ""),
                "class": sent[3]
            }
            #print (sentence_info)
            res = db.sentences.find({'sentence': sentence_info['sentence']}).count()

            #print (res)

            if res == 0:
                #print("sentence not in the collection")
                db.sentences.insert_one(sentence_info)
            else:
                #print("sentence already in the collection")
                #print(sent[2])
                continue


def create_datasets(num_of_sentences,db):
    labels = ["objective", "software", "method", "dataset", "result", "other"]
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


def main():
    db = tools.connect_to_mongo()
    if check_collection_sentences_exist(db):
        print("Collection 'sentences'  exist")
    else:
        print("Collection 'sentences' was created")

    start = time.time()
    #extract sentences from 100 publication from each booktitle
    all_sentences = sentence_extraction(db=db,publication_limit=5)
    store_sentences_in_mongo(db,all_sentences)
    end = time.time()
    print("Total time {} seconds".format(end - start))
    #randomly_selection(all_sentences)
    create_datasets(1000,db)


if __name__ == '__main__':
    main()
