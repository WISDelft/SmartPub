from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

from pyhelpers import tools

import config as cfg


def print_top_words(model, feature_names, n_top_words):
  with open(cfg.folder_culsters + "lda_full_text.csv", 'w', encoding='UTF-8') as f:
    for topic_idx, topic in enumerate(model.components_):
      print("Topic #%d:" % topic_idx)
      f.write("Topic #%d:" % topic_idx)
      print(",".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
      f.write(",".join([feature_names[i]
                      for i in topic.argsort()[:-n_top_words - 1:-1]]))
    print()
    f.write("\n")


def main():
  """
  new_pipe = [
    {
      "$match": {
        "$or": [{"booktitle": {
          '$in': ['JCDL', 'SIGIR', 'ECDL', 'TPDL', 'TREC', 'ICWSM', 'ESWC', 'WWW', 'ICSE', 'VLDB', 'ICSE (1)',
                  'ICSE (2)', 'ESWS', 'ESWC (1)', 'ESWC (2)']}},
                {'journal': {'$in': ['PVLDB', 'Machine Learning']}}]
      }
    },
    {
      "$lookup": {
        "from": "rhetorical_sentences",
        "localField": "_id",
        "foreignField": "paper_id",
        "as": "rhe_info"
      }
    },
    {
      "$unwind": "$rhe_info"
    },
    {
      "$group": {
        "_id": {
          "rhetorical": "$rhe_info.rhetorical"
        }
      }
    }
  ]
  
  unique_sentences = db.publications.aggregate(new_pipe, allowDiskUse=True)
  """
  db = tools.connect_to_mongo()
  sentences = db.rhetorical_sentences.find({'multiLabel_cls': {"$in": ['method']}})
  sent_list = set()
  for sent in sentences:
    sent_list.add(sent['rhetorical'])

  tf_vectorizer = CountVectorizer(stop_words='english', max_features= 1000)
  tf = tf_vectorizer.fit_transform(sent_list)
  #print()
  #print("Fit SVD+Normalization")
  #X = lsa.fit_transform(tf)

  lda = LatentDirichletAllocation(n_topics=45, max_iter=5,
                                  learning_method='online',
                                  learning_offset=50.,
                                  random_state=0)
  print("Start lda")
  lda.fit(tf)

  print("\nTopics in LDA model:")
  tf_feature_names = tf_vectorizer.get_feature_names()
  print_top_words(lda, tf_feature_names, 50)


if __name__ == '__main__':
  main()
