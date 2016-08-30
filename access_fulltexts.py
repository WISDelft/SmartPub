import logging
from pyhelpers import tools, grobid_mapping
tools.setup_logging()
import pprint

def main():
    tools.create_all_folders()
    # mongo_search_string = {'_id': 'journals_pvldb_SelkeLB12'}
    mongo_search_string = {'_id': 'journals_webology_Fedushko14'}
    #mongo_search_string = {'journal': 'PVLDB'}
    ##
    db = tools.connect_to_mongo()
    result = db.publications.find(mongo_search_string)

    for r in result:
        print(r['title'])
        if 'authors' in r:
            for a in r['authors']:
                print("  {}".format(a))
        if 'content' in r:
            if 'abstract' in r['content']:
                pprint.pprint(r['content']['abstract'])
            if 'fulltext' in r['content']:
                pprint.pprint(r['content']['fulltext'])


if __name__ == '__main__':
    main()