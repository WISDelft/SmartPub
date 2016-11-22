import logging
from pyhelpers import tools, grobid_mapping
tools.setup_logging()
import pprint


def main():
    db = tools.connect_to_mongo()
    result = db.downloads.count({"success" : True})
    print('{:>25} {:>8d}'.format("PDFs downloaded", result))
    #
    result = db.downloads.count({"success": False})
    print('{:>25} {:>8d}'.format("broken DBLP links", result))
    #
    result = db.publications.count({"content": {"$exists": True}})
    print('{:>25} {:>8d}'.format("fulltexts extracted", result))

    #print the papers from WWW
    result = db.publications.count({"booktitle": "WWW"})
    print('{:>25} {:>8d}'.format("WWW papers", result))

    #db.inventory.find({ $ and: [{price: { $ne: 1.99}}, {price: { $exists: true}}]    })
    result = db.publications.count({'$and' : [{'booktitle' :'WWW'} , {'content.chapters':{'$exists':True}}]})
    print('{:>25} {:>8d}'.format("Successful extractions WWW papers", result))

    #print the papers from WWW
    result = db.publications.count({"booktitle": "SIGIR"})
    print('{:>25} {:>8d}'.format("SIGIR papers", result))

    #print the papers from WWW
    result = db.publications.count({"booktitle": "ESWC"})
    print('{:>25} {:>8d}'.format("ESWC papers", result))

    #print the papers from WWW
    result = db.publications.count({"booktitle": "ICWSM"})
    print('{:>25} {:>8d}'.format("ICWSM papers", result))

    #print the papers from WWW
    result = db.publications.count({"booktitle": "VLDB"})
    print('{:>25} {:>8d}'.format("VLDB papers", result))
if __name__ == '__main__':
    main()
