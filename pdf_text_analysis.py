from pyhelpers import tools

def iteratePuplications(mongo_string_search):
    # initilize the db connection
    db = tools.connect_to_mongo()
    # set no_cursor_timeout= true, to avoid "pymongo.errors.CursorNotFound"
    result = db.publications.find(mongo_string_search, no_cursor_timeout=True)

    # we need to think ways of text analysis
    for r in result:
        pass

def main():
    # mongo search query
    mongo_string_search = {"dblpkey":"journals_mala_Wadler00"}
    iteratePuplications(mongo_string_search)

if __name__ == '__main__':
    main()
