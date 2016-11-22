from pyhelpers import tools
from playground import dictionary
import nltk
import random

booktitles = ['WWW', 'SIGIR', 'ESWC', 'ICWSM', 'VLDB']
journals = ['TACO','JOCCH']


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
    for booktitle in booktitles:
        mongo_string_search = {'booktitle': booktitle}
        list_of_pubs.append(return_chapters(mongo_string_search, db))

    list_of_sentences = []
    for pubs in list_of_pubs:
        for paper in pubs:
            # print(chapters['dblpkey'], len(chapters['chapters']))
            for i, chapter in enumerate(paper['chapters']):
                sentences = nltk.sent_tokenize(chapter)
                for sent in sentences:
                    if sent not in checker:
                        for word in dictionary.objective:
                            if word in sent:
                                list_of_sentences.append((i, paper['dblpkey'], sent))
                                checker.add(sent)
                        for word in dictionary.result:
                            if word in sent:
                                list_of_sentences.append((i, paper['dblpkey'], sent))
                                checker.add(sent)
                        for word in dictionary.method:
                            if word in sent:
                                list_of_sentences.append((i, paper['dblpkey'], sent))
                                checker.add(sent)
                        for word in dictionary.software:
                            if word in sent:
                                list_of_sentences.append((i, paper['dblpkey'], sent))
                                checker.add(sent)
                        for word in dictionary.dataset:
                            if word in sent:
                                list_of_sentences.append((i, paper['dblpkey'], sent))
                                checker.add(sent)

    #print(len(list_of_sentences))
    return list_of_sentences


def return_chapters(mongo_string_search, db):
    # mongo_string_search = {"dblpkey": "{}".format(dblkey)}
    results = db.publications.find(mongo_string_search)
    chapters = list()
    chapter_nums = list()
    list_of_docs = list()
    merged_chapters = list()
    my_dict = {
        "dblpkey": "",
        "chapters": list()
    }
    for i, r in enumerate(results):
        try:
            # list_of_sections = list()
            my_dict['dblpkey'] = r['dblpkey']
            for chapter in r['content']['chapters']:
                if chapter == {}:
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
                "chapters": list()
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
    sentences = sentence_extraction(db)
    print(len(sentences))
    randomly_selection(number_of_files= 5, sentences= sentences)



if __name__ == '__main__':
    main()
