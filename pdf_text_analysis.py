"""
Here we will play around with some cool text analysis
in order to find out which procedure is more suitable
for our task
"""
import nltk, re, pprint, sys
from pyhelpers import tools
from TextSummarize import TextSummarize

# define the source of raw text, we could either add fulltext, or chapters
features_with_raw_data = ["chapters"]
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


def iteratePuplications(mongo_string_search):
    # initialize the db connection
    db = tools.connect_to_mongo()
    # set no_cursor_timeout= true, to avoid "pymongo.errors.CursorNotFound"
    result = db.publications.find(mongo_string_search, no_cursor_timeout=True)

    # we need to think ways of text analysis
    # first we are going to use the entire text
    # (i.e content.fulltext) and then per chapter
    name_entities = []
    info_extr = []
    ts = TextSummarize()
    for r in result:
        # print(r['content']['fulltext'])
        if "fulltext" in features_with_raw_data:
            info_extr = ie_preprocess(r['content']['fulltext'])
            name_entities = name_entity_rec(info_extr)
        elif "chapters" in features_with_raw_data:
            for chapter in r['content']['chapters']:
                chapter_text = ""
                for paragraph in chapter['paragraphs']:
                    chapter_text += paragraph
                # print(chapter_text)
                print("Summary: Chapter")
                for s in ts.summarize(chapter_text, 4):
                    print("*",s)
                print("Summary: end")
                info_extr = ie_preprocess(chapter_text)
                name_entities.append(name_entity_rec(info_extr))

    return name_entities


def main():
    # mongo search query
    mongo_string_search = {"dblpkey":"journals_mala_Wadler00"}
    iteratePuplications(mongo_string_search)

if __name__ == '__main__':
    main()
