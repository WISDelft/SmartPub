
# mdocker pull lfoppiano/grobid:0.4.1-SNAPSHOT
# https://grobid.readthedocs.io/en/latest/Grobid-docker/
# https://github.com/kennknowles/python-jsonpath-rw

import requests
import logging
import tools
tools.setup_logging()
import config as cfg
from lxml import etree
import grobid_mapping
import pprint
from six import text_type
import os



def get_grobid_xml(paper_id):
    """
    Loads the GROBID XML of the paper with the provided DBLP id. If possible uses the XML cache. If not, uses the
    GROBID web service. New results are caches.
    :param paper_id:
    :return an LXML root node of the grobid XML
    """

    filename=cfg.folder_pdf+paper_id+".pdf"
    filename_xml=cfg.folder_content_xml+paper_id+".xml"

    ## check if XML file is already available
    if os.path.isfile(filename_xml):
        ## yes, load from cache
        root=etree.parse(filename_xml)
        return root
    else:
        if not os.path.isfile(filename):
            raise Exception("PDF for "+paper_id+" does not exist.")
        ## no, get from GROBID
        url = cfg.grobid_url + '/processFulltextDocument'
        params = {
            'input': open(filename, 'rb')
        }
        response = requests.post(url, files=params)
        if response.status_code == 200:
            ## it worked. now parse the result to XML
            parser = etree.XMLParser(encoding='UTF-8', recover=True)
            tei = response.content
            tei = tei if not isinstance(tei, text_type) else tei.encode('utf-8')
            root = etree.fromstring(tei, parser)
            ## and store it to xml cache
            with open(filename_xml, 'wb') as f:
                f.write(etree.tostring(root, pretty_print=True))
            return root
        else:
            raise Exception("Error calling GROBID for "+paper_id+": "+str(response.status_code)+" "+response.reason)


def process_paper(dblpkey, db):
    """
    Loads a paper with the given dblpkey, and extracts its content
    :param dblpkey: the DBLP id of the paper which is to be processed
    :param db: mongo db
    :return:
    """
    NS = {'tei': 'http://www.tei-c.org/ns/1.0'}
    try:
        xml=get_grobid_xml(dblpkey)
        result=grobid_mapping.tei_to_dict(xml)
        #
        #try:
        if 'abstract' in result:
            db.publications.update_one(
                {'_id': dblpkey},
                {'$set': {'content_abstract': result["abstract"]}}
            )
        if 'fulltext' in result:
            db.publications.update_one(
                {'_id': dblpkey},
                {'$set': {'content_fulltext': result["fulltext"]}}
            )
            with open(cfg.folder_content_xml + dblpkey + ".txt", 'w') as f:
                # f.write(result["fulltext"])
                print(result["fulltext"])
        #except:
        #    pprint.pprint(result)
        #
        logging.info("Processed "+dblpkey)
    except:
        logging.exception('Cannot process paper ' +dblpkey, exc_info=True)
    # pprint.pprint(result)
    # for ref in result['references']:
    #     print(ref)
    # print(etree.tostring(result['fulltext'], pretty_print=True))


def process_papers(mongo_search_string):
    db = tools.connect_to_mongo()
    result = db.publications.find(mongo_search_string)
    for r in result:
        process_paper(r['dblpkey'], db)



def main():
    mongo_search_string = {'_id': 'journals_pvldb_ChaytorW10'}
    mongo_search_string = {'journal': 'PVLDB'}
    process_papers(mongo_search_string)

    ### we neeed unicode handling!!!!!!!


if __name__ == '__main__':
    main()