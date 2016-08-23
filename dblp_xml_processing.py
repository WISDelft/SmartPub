import sys
import os
from lxml import etree
import gzip
import tools

CATEGORIES = set(
    ['article', 'inproceedings', 'proceedings', 'book', 'incollection', 'phdthesis', "mastersthesis", "www"])
SKIP_CATEGORIES = set(['phdthesis', 'mastersthesis', 'www'])
DATA_ITEMS = ["title", "booktitle", "year", "journal", "ee"]

def connectToDatabase():
    return 'x'


def clear_element(element):
    element.clear()
    while element.getprevious() is not None:
        del element.getparent()[0]


def extract_paper_elements(context):
    for event, element in context:
        if element.tag in CATEGORIES:
            yield element
            clear_element(element)


def fast_iter2(context, cursor):
    for paperCounter, element in enumerate(extract_paper_elements(context)):
        authors = [author.text for author in element.findall("author")]
        paper = {
            'element': element.tag,
            'mdate': element.get("mdate"),
            'dblpkey': element.get('key')
        }
        for data_item in DATA_ITEMS:
            data = element.find(data_item)
            if data is not None:
                paper[data_item] = data

        if paper['element'] not in SKIP_CATEGORIES:
            populate_database(paper, authors, cursor)


def populate_database(paper, authors, cursor):
    if 'ee' in paper:
        ee_text=paper['ee'].text
        # only proceed if paper has a key, an ee entry, and that entry ends on pdf
        if (type(paper['dblpkey']) is str and type(ee_text) is str and ee_text.endswith("pdf")):
            # print('{p[ee].text}'.format(p=paper))
            filename = tools.normalizeDBLPkey(paper['dblpkey'])+".pdf"
            try:
                tools.downloadFileWithProgress(ee_text, barlength = 0, overwrite = False, folder = './data/pdf/', localfilename=filename, incrementPercentage=0, incrementKB=0)
            except:
                print("Failed to download "+ee_text)


def main():
        data_folder = './data/'
        # get xml files
        tools.downloadFileWithProgress('http://dblp.uni-trier.de/xml/dblp.xml.gz', incrementKB=10 * 1024,
                                       folder=data_folder, overwrite=False)
        tools.downloadFileWithProgress('http://dblp.uni-trier.de/xml/dblp.dtd', incrementKB=10 * 1024, folder=data_folder,
                                       overwrite=False)

        cursor = connectToDatabase()
        #cursor.execute("""SET NAMES utf8""")
        with gzip.open(data_folder+"dblp.xml.gz", 'rb') as file:
            context = etree.iterparse(file, dtd_validation=True, events=("start", "end"))
            fast_iter2(context, cursor)

        #cursor.close()


if __name__ == '__main__':
    main()
