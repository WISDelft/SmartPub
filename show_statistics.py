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


if __name__ == '__main__':
    main()
