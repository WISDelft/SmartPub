"""
Here we will play around with some cool text analysis
in order to find out which procedure is more suitable
for our task
"""
import nltk, re, pprint, sys
from pyhelpers import tools
from TextSummarize import TextSummarize
from nltk.tokenize import word_tokenize
from string import punctuation
from nltk.corpus import stopwords
from gensim import corpora, models
#from K_means_clustering import  My_kmeans
import config
# define the source of raw text, we could either add fulltext, or chapters
to_sum = ["fulltext","chapters","paragraphs","abstract"]
lda_topics = 3
lda_passes = 100

# basic pipeline of information extraction from raw data
def ie_preprocess(document):
    sentences = nltk.sent_tokenize(document) # sentence segmentation, list of strings
    sentences = [ nltk.word_tokenize(sent) for sent in sentences] # tokenizing, list of lists of strings
    sentences = [nltk.pos_tag(sent) for sent in sentences] # Part of Speech recognition, lists of lists of tuples
    return sentences


def name_entity_rec(results):
    """
    Find the entities in the text using the
    name entity recognition from nltk
    """
    mylist = []
    for sent in results:
        mylist.append(nltk.ne_chunk(sent, binary=False))
    return mylist


def print_summary(list_of_sentences):
    """
    This function just prints the summary of the given text
    :param list_of_sentences:
    :return: print summary
    """
    for sent in list_of_sentences:
        print(sent)


def summarize_process(mongo_string_search):
    """
    In this function we are creating the summary for each paper. Not only from the entire
    paper but also from each chapter and paragraph.
    :param mongo_string_search:
    :return:
    """
    result = getPublications(mongo_string_search)
    name_entities = []
    info_extr = []
    ts = TextSummarize()
    paragraphs_summarize = []
    chapter_summarize = []
    full_text_summarize = []
    dblkey = ""
    papers_summary = []
    mydict = {
        "dblpkey" : "",
        "abstract_sum":[],
        "fulltext_sum":[],
        "chapter_sum":[],
        "paragraph_sum":[]
    }
    for r in result:
        mydict['dblpkey'] = r['dblpkey']
        if "content" in r and "abstract" in r['content'] and "abstract" in to_sum:
            mydict['abstract_sum']= ts.summarize(r['content']['abstract'],10)
        if "content" in r and "fulltext" in r['content'] and "fulltext"  in to_sum:
            full_text_summarize= ts.summarize(r['content']['fulltext'],50)
            mydict['fulltext_sum'] = full_text_summarize
        if "content" in r and "chapters" in r['content'] and "chapters" in to_sum:
            for chapter in r['content']['chapters']:
                str_chapter=""
                for paragraph in chapter['paragraphs']:
                    str_chapter += paragraph
                    if "paragraphs" in to_sum:
                        if len(word_tokenize(paragraph)) > 1:
                            paragraphs_summarize.append(ts.summarize(str(paragraph),5))
                chapter_summarize.append(ts.summarize(str_chapter,10))
        mydict["chapter_sum"] = chapter_summarize
        mydict["paragraph_sum"] = paragraphs_summarize
        # here i use the copy() because otherwise we just copy the reference
        papers_summary.append(mydict.copy())
        paragraphs_summarize=[]
        chapter_summarize=[]
        full_text_summarize=[]

    return papers_summary

def getPublications(mongo_string_search):
    # initialize the db connection
    db = tools.connect_to_mongo()
    # set no_cursor_timeout= true, to avoid "pymongo.errors.CursorNotFound"
    result = db.publications.find(mongo_string_search, no_cursor_timeout=True)
    return result


def LDA_process(mongo_string_search):
    """
    Find the topics for each paper/chapter/paragraph using LDA
    :param mongo_string_search:
    :return:
    """
    result = getPublications(mongo_string_search)
    mydict = {
        "dblpkey": "",
        "abstract_LDA": [],
        "fulltext_LDA": [],
        "chapter_LDA": [],
        "paragraph_LDA": []
    }
    paragraphs_lda = []
    chapter_lda = []
    papers_lda = []
    en_stop = set(stopwords.words('english') + list(punctuation))
    for r in result:
        mydict['dblpkey'] = r['dblpkey']
        if "content" in r and "abstract" in r['content']:
            tokens = word_tokenize(r['content']['abstract'])
            stopped_tokens = [i.lower() for i in tokens if i not in en_stop]
            dictionary = corpora.Dictionary([stopped_tokens])
            corpus = [dictionary.doc2bow(text) for text in [stopped_tokens]]
            lda_model = models.ldamodel.LdaModel(corpus, num_topics=lda_topics, id2word=dictionary, passes=lda_passes)
            k = lda_model.num_topics
            mydict["abstract_LDA"] = lda_model.print_topics(k)
            #print(mydict["abstract_LDA"])

        if "content" in r and "fulltext" in r['content']:
            tokens = word_tokenize(r['content']['fulltext'])
            stopped_tokens = [i.lower() for i in tokens if i not in en_stop]
            dictionary = corpora.Dictionary([stopped_tokens])
            corpus = [dictionary.doc2bow(text) for text in [stopped_tokens]]
            lda_model = models.ldamodel.LdaModel(corpus, num_topics=lda_topics, id2word=dictionary, passes=lda_passes)
            k = lda_model.num_topics
            mydict["fulltext_LDA"] = lda_model.print_topics(k)
        if "content" in r and "chapters" in r['content'] :
            for chapter in r['content']['chapters']:
                str_chapter = ""
                for paragraph in chapter['paragraphs']:
                    str_chapter += paragraph
                    if len(word_tokenize(paragraph)) > 1:
                        tokens = word_tokenize(paragraph)
                        stopped_tokens = [i.lower() for i in tokens if i not in en_stop]
                        dictionary = corpora.Dictionary([stopped_tokens])
                        corpus = [dictionary.doc2bow(text) for text in [stopped_tokens]]
                        lda_model = models.ldamodel.LdaModel(corpus, num_topics=lda_topics, id2word=dictionary, passes=lda_passes)
                        paragraphs_lda.append(lda_model.print_topics(lda_model.num_topics))
                tokens = word_tokenize(str_chapter)
                stopped_tokens = [i.lower() for i in tokens if i not in en_stop]
                dictionary = corpora.Dictionary([stopped_tokens])
                corpus = [dictionary.doc2bow(text) for text in [stopped_tokens]]
                lda_model = models.ldamodel.LdaModel(corpus, num_topics=lda_topics, id2word=dictionary, passes=lda_passes)
                chapter_lda.append(lda_model.print_topics(lda_model.num_topics))
        mydict["paragraph_LDA"] = paragraphs_lda
        mydict["chapter_LDA"] = chapter_lda
        # here i use the copy() because otherwise we just copy the reference
        papers_lda.append(mydict.copy())
        chapter_lda = []
        paragraphs_lda = []

    return papers_lda

def frequency_of_keywords_in_collection(db):
    db_keywords = list(db.keywords.find({}))
    sentences = list(db.sentences.find({"other": 0}))
    f = open(config.folder_log+"keywords_frequency.csv", "w", encoding="UTF-8")
    f.write("key_id,label,term,frequency")
    f.write("\n")
    for k in db_keywords:
        count = 0
        for sent in sentences:
            if k["key_id"] in sent['keywords']:
                count += 1
        #print("{},{},{},{}".format(k['key_id'], k['label'], k['term'],count))
        f.write("{},{},{},{}".format(k['key_id'], k['label'], k['term'],count))
        f.write("\n")
    f.close()

def frequency_of_keywords_in_datasets(db):
    db_keywords = list(db.keywords.find({}))
    filenames = ['Objective_new_SM.csv', 'Software_new_SM.csv','Dataset_new_SM.csv', 'Method_new_SM.csv', 'Result_new_SM.csv']

    count_obj=0
    count_soft=0
    count_data=0
    count_meth=0
    count_res=0

    print("key_id,label,term,file,occurrences,correct_objective,correct_software,correct_dataset,correct_method,correct_results")
    for k in db_keywords:
        appear_in_file = 0
        count_obj = 0
        count_soft = 0
        count_data = 0
        count_meth = 0
        count_res = 0
        for file in filenames:
            with open(config.folder_datasets+file, "r",encoding="UTF-8") as f:
                next(f) # skip header
                for line in f:
                    my_line = line.split(",")
                    string_keys = my_line[3].replace('[',"").replace("]","").replace(" ",",").split(",")
                    line_keys = map(int, string_keys)
                    #print(k['key_id'], line_keys)
                    if k['key_id'] in line_keys:
                        appear_in_file += 1
                        if my_line[5] == '1':
                            count_obj += 1
                        if my_line[6] == '1':
                            count_soft += 1
                        if my_line[7] == '1':
                            count_data += 1
                        if my_line[8] == '1':
                            count_meth += 1
                        if my_line[9] == '1':
                            count_res += 1
            print("{},{},{},{},{},{},{},{},{},{} ".format(k['key_id'], k['label'], k['term'], file, appear_in_file, count_obj, count_soft, count_data, count_meth, count_res))
            appear_in_file=0
            count_obj = 0
            count_soft = 0
            count_data = 0
            count_meth = 0
            count_res = 0





def main():
    # mongo search query
    #mongo_string_search = {"dblpkey":{"$in":["journals_ijclclp_WuC07","journals_mala_Wadler00"]}}
    """


    mongo_string_search = {"dblpkey": "journals_ijclclp_WuC07"}
    print("Summaries")
    summaries = summarize_process(mongo_string_search)
    # comment out if you want prettify print
    #pprint.pprint(summaries)
    print(summaries)
    print("End of Summaries")
    print()

    print("LDA")
    ldas = LDA_process(mongo_string_search=mongo_string_search)
    # comment out if you want prettify print
    # pprint.pprint(ldas)
    print(ldas)
    print("End of LDA")
    print()

    print("K-means")
    kmeans = My_kmeans(mongo_string=mongo_string_search,num_cluster=5,terms_printed=3)
    kmeans.k_means_process()
    print("End of K-means")
    print()
    """
    db = tools.connect_to_mongo()
    #frequency_of_keywords_in_collection(db)
    frequency_of_keywords_in_datasets(db)


if __name__ == '__main__':
    main()
