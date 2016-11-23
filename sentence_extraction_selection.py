from pyhelpers import tools
from playground import dictionary
import nltk
import random
import time
import sys

booktitles = ['WWW', 'SIGIR', 'ESWC', 'ICWSM', 'VLDB']
journals = ['TACO']

filter_chapters = ['related work' , 'background', 'state of the art' ,'previous works']

sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')


def sentence_extraction(db):
    """
    this function retrieves all the sentences that contain phrases from the dictionary.py
    To do that, we take all the chapters for each paper and we check each sentence separately.
    Also, we merge subsection to keep it consistent (Auxiliary functions: return_chapters(),
    merge_subsections().
    :param db:
    :return: list of tuples in the format (chapter number, paper_id, sentence)
    """
    checker = set()
    list_of_pubs = [] # list of lists of different booktitles
    #change back to booktitles
    start = time.time()

    for booktitle in journals:
        ## i will test it locally so i use journals change later!!!!!!!!
        mongo_string_search = {'journal': booktitle}
        list_of_pubs.append(return_chapters(mongo_string_search, db))
    end = time.time()
    print("Tine of the return_chapters {}".format(end - start))

    list_of_sentences = []
    objective_sentences = list()
    flag_result = False
    flag_method = False
    flag_software = False
    flag_dataset = False
    count = 1

    start = time.time()
    for pubs in list_of_pubs:
        for paper in pubs:
            print(count)
            count += 1
            # print(chapters['dblpkey'], len(chapters['chapters']))

            if paper['abstract'] != "":
                objective_sentences.append(check_for_objective(paper['abstract'],paper['dblpkey']))
            for i, chapter in enumerate(paper['chapters']):

                sentences = (sent_detector.tokenize(chapter.lower().strip()))
                for sent in sentences:
                    if sent not in checker:
                        for word in dictionary.result:
                            tokens = nltk.word_tokenize(word.lower())
                            if len(tokens) > 1:
                                all_tokens_in_sent = check_tokens(sent, tokens)
                                if all_tokens_in_sent:
                                    list_of_sentences.append((i, paper['dblpkey'], sent, "result"))
                                    flag_result = True
                                    checker.add(sent)

                            elif word.lower() in sent:
                                list_of_sentences.append((i, paper['dblpkey'], sent, "result"))
                                flag_result = True
                                checker.add(sent)

                            if flag_result:
                                break
                        if not flag_result:
                            for word in dictionary.software:
                                tokens = nltk.word_tokenize(word.lower())
                                if len(tokens) > 1:
                                    all_tokens_in_sent = check_tokens(sent, tokens)
                                    if all_tokens_in_sent:
                                        list_of_sentences.append((i, paper['dblpkey'], sent, "software"))
                                        flag_software = True
                                        checker.add(sent)

                                elif word.lower() in sent:
                                    list_of_sentences.append((i, paper['dblpkey'], sent, "software"))
                                    flag_software = True
                                    checker.add(sent)

                                if flag_software:
                                    break
                        if not flag_software:
                            for word in dictionary.method:
                                tokens = nltk.word_tokenize(word.lower())
                                if len(tokens) > 1:
                                    all_tokens_in_sent = check_tokens(sent, tokens)
                                    if all_tokens_in_sent:
                                        list_of_sentences.append((i, paper['dblpkey'], sent, "method"))
                                        flag_method = True
                                        checker.add(sent)

                                elif word.lower() in sent:
                                    list_of_sentences.append((i, paper['dblpkey'], sent, "method"))
                                    flag_method = True
                                    checker.add(sent)
                                if flag_method:
                                    break
                        if not flag_method:
                            for word in dictionary.dataset:
                                tokens = nltk.word_tokenize(word.lower())
                                if len(tokens) > 1:
                                    all_tokens_in_sent = check_tokens(sent, tokens)
                                    if all_tokens_in_sent:
                                        list_of_sentences.append((i, paper['dblpkey'], sent, "dataset"))
                                        flag_dataset = True
                                        checker.add(sent)

                                elif word.lower() in sent:
                                    list_of_sentences.append((i, paper['dblpkey'], sent, "dataset"))
                                    flag_dataset = True
                                    checker.add(sent)

                                if flag_dataset:
                                    break
                        if not flag_dataset:
                            list_of_sentences.append((i, paper['dblpkey'], sent, "other"))
                        flag_result = False
                        flag_method = False
                        flag_software = False
                        flag_dataset = False

    end = time.time()
    print("Tine of the big loop {}".format(end - start))
    print("objective_sentences {}".format(len(objective_sentences)))
    list_of_sentences.append(objective_sentences)
    return list_of_sentences


def check_for_objective(abstract, dblpkey):
    list_of_sentences = list()
    sentences = (sent_detector.tokenize(abstract.lower().strip()))
    flag_objective = False
    for sent in sentences:
        for word in dictionary.objective:
            tokens = nltk.word_tokenize(word.lower())
            if len(tokens) > 1:
                all_tokens_in_sent = check_tokens(sent, tokens)
                if all_tokens_in_sent:
                    list_of_sentences.append(("abstract", dblpkey, sent, "objective"))
                    flag_objective = True
                    break
            elif word.lower() in sent:
                list_of_sentences.append(("abstract", dblpkey, sent, "objective"))
                flag_objective = True
                break
        if not flag_objective:
            list_of_sentences.append(("abstract", dblpkey, sent, "other"))


    return list_of_sentences


def check_tokens(sent, tokens):
    count = 0
    sent = nltk.word_tokenize(sent)

    for t in tokens:
        for ts in sent:
            if t == ts:
                count += 1
                break
    if count == len(tokens):
        #print(tokens, sent)
        return True
    else:
        return False

def return_chapters(mongo_string_search, db):
    # mongo_string_search = {"dblpkey": "{}".format(dblkey)}
    results = db.publications.find(mongo_string_search).limit(5)
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


def only_sentences(mongo_string_search,db):
    results = db.publications.find(mongo_string_search).limit(2)
    list_of_sentences = list()
    list_of_chapters = list()
    for i, r in enumerate(results):
            try:
                list_of_sentences.append(sent_detector.tokenize(r['content']['abstract'].lower().strip()))
            except:
                print("No abstract")
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
                    #chapter_nums.append(chapter['chapter_num'])
                    # print(chapter['title'])
                    for paragraph in chapter['paragraphs']:
                        if paragraph == {}:
                            continue
                        section += paragraph
                    list_of_sentences.append(sent_detector.tokenize(section.lower().strip()))
                    #chapters.append(section)
                    section = ""
                #chapters = chapter_nums, chapters
                #merged_sec = merge_subsections(chapters)

                #list_of_chapters.append(merged_sec)

                chapters = list()
                #chapter_nums = list()
            except:
            # print("eeror")
                print("Document {} has a Key Error - continue to the next document".format(r['dblpkey']))
                continue
    return list_of_sentences


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


def randomly_selection(number_of_files, sentences):
    """
    create csv files by taking random samples
    :param number_of_files:
    :param sentences:
    """
    number_of_sentences = int(len(sentences)/ number_of_files)
    copy_sentence = sentences.copy()
    for i in range(0,number_of_files):
        random_senetences = random.sample(copy_sentence,number_of_sentences)
        f = open("dataset_{}.csv".format(i), "w", encoding="UTF-8")
        for rnd_sent in random_senetences:
            # remove commas from the sentence to avoid any misunderstanding
            my_string = ','.join([str(item).replace(",","") for item in rnd_sent]) + ','
            f.write(my_string)
            f.write("\n")
            copy_sentence.remove(rnd_sent)
        f.close()
        print("Finish file {}".format(i))


def main():
    db = tools.connect_to_mongo()


    start = time.time()
    sentences = sentence_extraction(db)
    end = time.time()
    print(end - start)
    print(len(sentences))
    randomly_selection(number_of_files= 1, sentences= sentences)



if __name__ == '__main__':
    main()
