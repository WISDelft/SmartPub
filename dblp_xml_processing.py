# setup logging
import logging
logging.basicConfig(format='%(asctime)s %(message)s', filename='./logs/dblp_xml_processing.log', level=logging.DEBUG, filemode='w')
logging.debug("Start XML Parsing")
logging.getLogger().addHandler(logging.StreamHandler())

import sys
from lxml import etree
import gzip
import tools
import datetime
from pymongo import MongoClient

# set to true if you want to persist to a local mongo DB (default connection)
storeToMongo = True
# the path of the data folder (for XML and PDF)
data_folder = './data/'
# set to true if you want to skip downloading EE entries (pdf URLs) which have been accessed before (either sucessfully or unsucessfully)
# this only works if storeToMongo is set to True because the MongoDB must be accessed for that. (if you set storeToMongo to false, I will
# just assume that MongoDB is simply not active / there
skipPreviouslyAccessedURLs = True

# the categories you are interested in
CATEGORIES = set(
    ['article', 'inproceedings', 'proceedings', 'book', 'incollection', 'phdthesis', 'mastersthesis', 'www'])
# the categories you are NOT interested in
SKIP_CATEGORIES = set(['phdthesis', 'mastersthesis', 'www', 'proceedings'])
# the fields which should be in your each data item / mongo entry
DATA_ITEMS = ["title", "booktitle", "year", "journal", "crossref", "ee"]

# prints out a progress every X attempted downloads (including skips which had been downloaded before)
statusEveryXdownloads = 100







# helper just used for parsing the XML
def clear_element(element):
    element.clear()
    while element.getprevious() is not None:
        del element.getparent()[0]

# helper just used for parsing the XML
def extract_paper_elements(context):
    for event, element in context:
        if element.tag in CATEGORIES:
            yield element
            clear_element(element)

# main XML parser: iterates over the xml and extracts relevant info
def fast_iter2(context, db):
    global paperCounter
    for paperCounter, element in enumerate(extract_paper_elements(context)):
        # extract basic metadata from the dblp XML
        paper = {
            'type': element.tag,
           # 'mdate': element.get("mdate"),
            'dblpkey': element.get('key')
        }
        if paper['dblpkey'] is not None:
            paper['dblpkey'] = tools.normalizeDBLPkey(paper['dblpkey'])

        paper['authors'] = [author.text for author in element.findall("author")]
        for data_item in DATA_ITEMS:
            data = element.find(data_item)
            if data is not None:
                paper[data_item] = data.text

        if paper['type'] not in SKIP_CATEGORIES:
            downloadAndStore(paper, db)


## stores stuff in mongo db, and downloads the PDF
def downloadAndStore(paper, db):
    if 'ee' in paper:

        # only proceed if paper has a key, an ee entry, and that entry ends on pdf
        if (type(paper['dblpkey']) is str and type(paper['ee']) is str and paper['ee'].endswith("pdf")):
            filename = paper['dblpkey']+".pdf"
            # downloadinfo is the dictionary which is later stored in the Monfo "downloads" collection to memorize
            # which URLs have been accessed, and if that was successfull or not
            downloadinfo = {
                '_id': paper['ee'],
                'url': paper['ee'],
                'dblpkey': paper['dblpkey'],
                'lastaccessed': datetime.datetime.now(),
                'success': True
            }
            # decide if we want to skip this entry (e.g., it has been accessed before and we are in the mood for skipping)
            if skipPreviouslyAccessedURLs and storeToMongo:
                result = db.downloads.find_one({'_id': downloadinfo['_id']})
                if result is None:
                    skip = False
                else:
                    skip = True
                    if result['success']:
                        global numOfPDFobtained
                        global paperCounter
                        global numOfPDFobtainedInThisSession
                        numOfPDFobtained += 1
                        if numOfPDFobtained % statusEveryXdownloads is 0:
                            print(
                                'DBLP XML PROGRESS: XML Paper Entries {}      PDFs {}     PDFs in this Session {} '.format(
                                    paperCounter, numOfPDFobtained, numOfPDFobtainedInThisSession))

            else:
                skip = False

            # Do the Download
            if not skip:
                try:
                    # download
                    tools.downloadFileWithProgress(downloadinfo['url'], barlength = 0, overwrite = False, folder = './data/pdf/', localfilename=filename, incrementPercentage=0, incrementKB=0)
                    global numOfPDFobtainedInThisSession
                    numOfPDFobtainedInThisSession += 1
                    # store
                    if storeToMongo:
                        # set additional data
                        paper['_id'] = paper['dblpkey']
                        # store to mongo
                        db.publications.replace_one({'_id' : paper['_id']}, paper, upsert = True )
                        db.downloads.replace_one({'_id' : downloadinfo['_id']}, downloadinfo, upsert = True )
                except:
                    logging.exception('Cannot download or store '+paper['ee'], exc_info=False)
                    if storeToMongo:
                        downloadinfo['success'] = False
                        ex=sys.exc_info()
                        downloadinfo['error'] = repr(ex)
                        db.downloads.replace_one({'_id': downloadinfo['_id']}, downloadinfo, upsert=True)

def main():
        # just a counter
        global numOfPDFobtained
        global numOfPDFobtainedInThisSession
        numOfPDFobtained = 0
        numOfPDFobtainedInThisSession = 0

        # get xml files
        tools.downloadFileWithProgress('http://dblp.uni-trier.de/xml/dblp.xml.gz', incrementKB=10 * 1024,
                                       folder=data_folder, overwrite=False)
        tools.downloadFileWithProgress('http://dblp.uni-trier.de/xml/dblp.dtd', incrementKB=10 * 1024, folder=data_folder,
                                       overwrite=False)


        # initialize connection to local mongoDB, database is named pub
        if storeToMongo:
            client = MongoClient()
            db = client.pub


        with gzip.open(data_folder+"dblp.xml.gz", 'rb') as file:
            context = etree.iterparse(file, dtd_validation=True, events=("start", "end"))
            fast_iter2(context, db)

        #cursor.close()


if __name__ == '__main__':
    main()

