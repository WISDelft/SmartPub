from sklearn.feature_extraction.text import  CountVectorizer

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer

from sklearn import decomposition
from nltk.corpus import stopwords
from pyhelpers import tools
from sklearn.metrics import  silhouette_score
import config as cfg

import _pickle as pkl


from sklearn.cluster import KMeans





def is_number(s):
  try:
    float(s)
    return True
  except ValueError:
    return False


def calculate_s_scores(X, min_k, max_k, facet):
  s = []
  max_val = 0
  maximum_k = 0
  with open(cfg.folder_pickle+"silhouette_scores_between_multilabel_{}_{}_{}.csv".format(facet, min_k, max_k), 'w',
            encoding="UTF-8") as f:
    for n_clusters in range(min_k, max_k):
      kmeans = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=100, n_init=1)
      kmeans.fit(X)  # instead of the countvectorizer

      labels = kmeans.labels_
      centroids = kmeans.cluster_centers_
      s_score = silhouette_score(X, labels, sample_size=1000)

      if s_score >= max_val:
        max_val = s_score
        maximum_k = n_clusters

      f.write("{},{}".format(n_clusters, s_score))
      f.write("\n")
      print("{},{}".format(n_clusters, s_score))
      # s.append(silhouette_score(X, labels, sample_size=10000))
  print("Max k: {}, s_score: {}".format(maximum_k, max_val))
  return (maximum_k)

def facet_embedding(db, facet):
  stopset = list(set(stopwords.words('english')))
  papers = db.publications.distinct('_id', {"content": {"$exists": True}})
  docs = []
  conf_flag = False
  journal_flag = False
  count = 0
  for i, p in enumerate(papers):
    if i % 1000 == 0:
      print(i, end=",")
    find_paper = db.publications.find_one({'_id': p})
    # if 'booktitle' in find_paper and find_paper['booktitle'] in ['JCDL','SIGIR','ECDL','TPDL','TREC', 'ICWSM', 'ESWC', 'WWW', 'ICSE', 'VLDB', 'ICSE (1)', 'ICSE (2)', 'ESWS', 'ESWC (1)', 'ESWC (2)' , 'ICDM', 'KDD']:
    if 'booktitle' in find_paper and find_paper['booktitle'] in ['HRI', 'ICARCV', 'ICRA']:
      conf_flag = True

    # if 'journal' in find_paper and find_paper['journal'] in ['PVLDB', 'Machine Learning']:
    if 'journal' in find_paper and find_paper['journal'] in ['IEEE Trans. Robotics']:
      journal_flag = True

    if conf_flag or journal_flag:
      count += 1
      ners = db.sentences_ner.distinct('ner', {'paper_id': p, 'multiLabel_cls': {'$in': [facet]}, 'inWordnet': 0})

      methodsString = ''

      for ne in ners:
        ner_no_stop_words = ""
        # isint = is_int_or_float(ne)

        # if isint == -1:
        #  ne = ne.replace(' ', '')
        #  methodsString = methodsString + str(ne) + ' '
        if not is_number(ne):
          # in_ne = word_tokenize(ne)
          # for i,t in enumerate(in_ne):
          #     if t.lower() not in stopset:
          #            ner_no_stop_words += t + ""
          ne = ne.replace(' ', '')
          methodsString = methodsString + str(ne) + ' '
          # ne= ne.replace('_','')
          # methodsString = methodsString + str(ner_no_stop_words) + ' '

      docs.append(methodsString)

      conf_flag = False
      journal_flag = False
  print('Total {}'.format(count))
  return docs


def cluster_facet_topics(X,num_clusters, facet,count_model,svd):
    km = KMeans(n_clusters=num_clusters, init='k-means++', max_iter=100, n_init=1, verbose=False)
    km.fit(X)
    # save the classifier
    with open(cfg.folder_pickle+'co_occur_K_means_{}_{}_robots_lowercase.pkl'.format(num_clusters,facet), 'wb') as fid:
        pkl.dump(km, fid)

    with open(cfg.folder_pickle+'co_occur_K_means_{}_vectorizer_{}_robots_lowercase.pkl'.format(num_clusters,facet), 'wb') as fid:
        pkl.dump(count_model, fid)

    with open(cfg.folder_pickle+'co_occur_K_means_{}_svd_{}_robots_lowercase.pkl'.format(num_clusters,facet), 'wb') as fid:
        pkl.dump(svd, fid)

    original_space_centroids = svd.inverse_transform(km.cluster_centers_)
    order_centroids = original_space_centroids.argsort()[:, ::-1]
    #order_centroids = km.cluster_centers_.argsort()[:, ::-1]


    with open(cfg.folder_pickle+'co_occur_K_means_{}_{}_robots_lowercase.csv'.format(num_clusters,facet), 'w', encoding= 'UTF-8') as f:

        term_list = count_model.get_feature_names()
        f.write("Top terms with {} clusters".format(num_clusters))
        f.write('\n')
        for i in range(len(order_centroids)):
            f.write("Annotate Here,Cluster {}:".format(i))
            for ind in order_centroids[i, :40]:
                f.write(',{}'.format(term_list[ind]))
            f.write("\n")
        f.write("\n")
    return km

def main():
  db = tools.connect_to_mongo()
  method_documents = facet_embedding(db, 'method')

  count_model = CountVectorizer(ngram_range=(1, 1), lowercase=True,
                                token_pattern=r'(?u)\b\w\w+\b-\b\w\w+\b|\b\w\w+\b')  # Convert a collection of text documents to a matrix of token counts- default unigram model

  # vectorizer = TfidfVectorizer(ngram_range=(1,1), lowercase= False)

  print()
  print("Fit documents count vectorizer")
  X = count_model.fit_transform(method_documents)
  Xc = (X.T * X)
  # len(vectorizer.get_feature_names())



  print()
  print("Create SVD pipeline with {} components and normalization".format(200))
  svd = decomposition.TruncatedSVD(n_components=200, n_iter=5)
  normalizer = Normalizer(copy=False)
  lsa = make_pipeline(svd, normalizer)

  print()
  print("Fit SVD+Normalization")
  X = lsa.fit_transform(Xc)

  #with open('X_k_means_method_multilabel_DataPipelines_{}.pkl'.format(2), 'wb') as vec:
  #  pkl.dump(X, vec)

  #explained_variance = svd.explained_variance_ratio_.sum()
  #print("Explained variance of the SVD step: {}%".format(int(explained_variance * 100)))

  maximum_k = calculate_s_scores(X, 15, 50, 'method')
  km = cluster_facet_topics(X, maximum_k, 'method',count_model,svd)

if __name__ == '__main__':
    main()
