from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn import preprocessing
from pyhelpers import tools

from sklearn.pipeline import make_pipeline
from sklearn import decomposition

def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
    print()


def main():
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
  db = tools.connect_to_mongo()
  unique_sentences = db.publications.aggregate(new_pipe, allowDiskUse=True)

  uniqu_sent = list()
  for sent in unique_sentences:
    uniqu_sent.append(sent['_id']['rhetorical'])

  tf_vectorizer = CountVectorizer(stop_words='english')
  tf = tf_vectorizer.fit_transform(uniqu_sent)

  svd = decomposition.TruncatedSVD(n_components=100, n_iter=5)
  # normalizer = Normalizer(copy=False)
  min_max_scaler = preprocessing.MinMaxScaler()
  lsa = make_pipeline(svd, min_max_scaler)

  print()
  print("Fit SVD+Normalization")
  X = lsa.fit_transform(tf)

  lda = LatentDirichletAllocation(n_topics=45, max_iter=5,
                                  learning_method='online',
                                  learning_offset=50.,
                                  random_state=0)
  lda.fit(X)

  print("\nTopics in LDA model:")
  tf_feature_names = tf_vectorizer.get_feature_names()
  print_top_words(lda, tf_feature_names, 50)


if __name__ == '__main__':
  main()
