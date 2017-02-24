import pickle
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from pymongo import ReturnDocument
from pyhelpers import tools
import config




def main():
  db = tools.connect_to_mongo()
  my_rheto = list(db.rhetorical_sentences.find({}))
  for res in my_rheto:
    updateRes = db.sentences_ner.update_many({
      'paper_id': res['paper_id'],
      'rhetorical_id': res['rhetorical_id']
    },
      {
        '$set': {
          'multiLabel_cls': res['multiLabel_cls']
        }
      },
    upsert = False)
    print("paper_id: {}, rhetorical_id: {},Paper Matched: {}, Paper Updated: {}".format(res['paper_id'],res['rhetorical_id'],updateRes.matched_count, updateRes.modified_count))




if __name__ == '__main__':
    main()
