import logging

import config as cfg
from pyhelpers import tools

tools.setup_logging(file_name="xml_processor.log")

import sys
from lxml import etree
import gzip
import datetime
#modules to extract acm papers
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

# set to true if you want to persist to a local mongo DB (default connection)
storeToMongo = False

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

filters = {}



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
            # try to downlaod and store the thing if it is not in one of the skipped categories
            download_and_store(paper, db)


## stores stuff in mongo db, and downloads the PDF
def download_and_store(paper, db):
    global filters
    # the ee XML tag indicates that this paper has some kind of source attached (this will usually be an URL)
    if 'ee' in paper:
        # Do we want to skip this file? There are lots of reasons, see below... Skipping means we will not try to download it
        skip = False
        # filters have been set
        if len(filters)>0:
            for k, v in filters.items():
                if not (k in paper and paper[k]==v):
                    skip = True

        # do NOT skip if paper has a key, an ee entry
        if (not skip and type(paper['dblpkey']) is str and type(paper['ee']) is str):
            # check if it one of our supported types. IMPORTANT: ADD NEW TYPES HERE IF WE HAVE THEM!
            if (paper['ee'].endswith("pdf") or paper['ee'].startswith("doi.acm.org")):
                filename = paper['dblpkey']+".pdf"
                # downloadinfo is the dictionary which is later stored in the Mongo "downloads" collection to memorize
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
                                logging.info(
                                    'DBLP XML PROGRESS: XML Paper Entries {}      PDFs {}     PDFs in this Session {} '.format(
                                        paperCounter, numOfPDFobtained, numOfPDFobtainedInThisSession))
                else:
                    skip = False

            # Do the Download and store to MongoDB
            if not skip:
                try:
                    print(paper['dblpkey'])
                    # download based on type. IMPORTANT: Add supported types here, and also a few lines above!
                    if paper['ee'].endswith("pdf"):
                        # Normal PDF download
                        skipped=not tools.downloadFile(downloadinfo['url'], overwrite = False, folder = cfg.folder_pdf, localfilename=filename)
                    if paper['ee'].startswith("doi.acm.org"):
                        extract_paper(paper['ee'])
                        #raise BaseException('ACM DOI not supported yet: '+paper['dblpkey'])


                    if skipped:
                        logging.info(' Used local PDF copy for ' + paper['dblpkey'])
                    else:
                        logging.info(' Downloaded '+paper['dblpkey'])
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

#this function will access a given url  and will find the
#link of the pdf.
#Attention: WORKS ONLY IN THE TU DELFT NETWORK or VPN
def extract_paper(paper_url):
    #reguest to the url, add headers to avoid  HTTP Error: 403 Forbidden
    #the site will strike you out because you are a robot!
    req = Request(paper_url ,headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    #parse the html code
    soup = BeautifulSoup(webpage, 'html.parser')
    #select only the link tags
    for link in soup.find_all('a'):
        #the name of in the link tag is "FullTextPDF"
        if str(link.get('name')).endswith('PDF'):
            href_link = link.get('href')
            prefix = "http://dl.acm.org/"
            pdf_link = prefix + href_link
            #To avoid any conflicts I am taking the id of the link and the
            #ftid and I concatinate them together. I put +3 and +6 to
            #exclude  the "id=" and "ftid="
            pdf_id = href_link[href_link.find("id=")+3: href_link.find("&f")]
            file_id = href_link[href_link.find("ftid=")+6 : href_link.find("&d")]
            localfilename = pdf_id + '_' + file_id+'.pdf'
            #folder = "C:/Users/User/Documents/acm_pdfs/"
            tools.downloadFile(url=pdf_link, folder=cfg.folder_pdf, overwrite=False,
                                   localfilename= localfilename, printOutput=False)

def main(filter:("filter","option")=None):
    """

    :param filter: Only consider entries with which match certain filter conditions in the DBLP xml. Examples: -filter="{'book' : 'SIGIR'}" or -filter="{'journal' : 'PVLDB', 'year' : '2016'}"   (Note the usage of " and ')
    """
    import json
    global filters
    if filter:
        filters=json.loads(filter.replace("'",'"'))
        print("Using filters "+str(filters))

    tools.create_all_folders()
    # just a counter
    global numOfPDFobtained
    global numOfPDFobtainedInThisSession
    numOfPDFobtained = 0
    numOfPDFobtainedInThisSession = 0

    # get xml files
    tools.downloadFileWithProgress('http://dblp.uni-trier.de/xml/dblp.xml.gz', incrementKB=10 * 1024,
                                   folder=cfg.folder_dblp_xml, overwrite=False)
    tools.downloadFileWithProgress('http://dblp.uni-trier.de/xml/dblp.dtd', incrementKB=10 * 1024,
                                   folder=cfg.folder_dblp_xml, overwrite=False)


    # initialize connection to local mongoDB, database is named pub
    if storeToMongo:
        db = tools.connect_to_mongo()
    else:
        db = None


    # open xml and iterate over xml tree to extract relevant stuff
    with gzip.open(cfg.folder_dblp_xml+"dblp.xml.gz", 'rb') as file:
        context = etree.iterparse(file, dtd_validation=True, events=("start", "end"))
        fast_iter2(context, db)



if __name__ == '__main__':
    import plac
    plac.call(main)

