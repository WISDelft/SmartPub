import pickle
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from pyhelpers import tools
import config



# we take the first index because the result is in a list
def update_classes(sentence, cls):
  real_classes = ['objective', 'software', 'dataset', 'method', 'result']
  sentences = []
  sentences.append(sentence)
  update_classes = []
  classification = cls.predict(sentences)
  for i, label in enumerate(classification[0]):
    if label == 1:
      update_classes.append(real_classes[i])

  return update_classes



def main():
  db = tools.connect_to_mongo()
  with open(config.folder_classifiers + 'random_forest_cls_16.pickle', 'rb') as handle:
    cls = pickle.load(handle)
  my_cursor = list(db.rhetorical_sentences.find({'multiLabel_cls': {'$exists': False}}))
  for res in my_cursor:
    db.rhetorical_sentences.find_one_and_update(res,
                                                {'$set': {"multiLabel_cls": update_classes(res['rhetorical'], cls)}})

if __name__ == '__main__':
    main()
