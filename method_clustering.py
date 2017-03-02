from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn import decomposition
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.cluster import KMeans

from pyhelpers import tools

#import matplotlib.pyplot as plt
import numpy as np
import _pickle as pkl
import config as cfg


def is_int_or_float(s):
    ''' return 1 for int, 2 for float, -1 for not a number'''
    try:
        float(s)

        return 1 if s.count('.')==0 else 2
    except:
        return -1


def hasNumbers(inputString):
  return any(char.isdigit() for char in inputString)


def facet_embedding(db):
  papers = db.sentences_ner.distinct('paper_id')
  docs = []
  conf_flag = False
  journal_flag = False

  for p in papers:
    find_paper = db.publications.find({'_id':p})
    if 'booktitle' in find_paper and find_paper['booktitle'] in cfg.booktitles:
      conf_flag = True

    if 'journal' in find_paper and find_paper['journal'] in cfg.journals:
      journal_flag = True

    if conf_flag or journal_flag:
      ners = db.sentences_ner.distinct('ner', {'paper_id': p, 'inWordnet': 0})
      methodsString = ''
      for ne in ners:
        isint = is_int_or_float(ne)

        if not hasNumbers(ne):
          ne = ne.replace(' ', '')
          # ne= ne.replace('_','')
          methodsString = methodsString + str(ne) + ' '

      docs.append(methodsString)
    conf_flag = False
    journal_flag = False

  return docs

"""
The matplot give error on the server!!
  def plot_shilouete(X, min_k, max_k):
    s = []
    for n_clusters in range(min_k, max_k):
      kmeans = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=100, n_init=1)
      kmeans.fit(X)  # instead of the countvectorizer

      labels = kmeans.labels_
      centroids = kmeans.cluster_centers_

      s.append(silhouette_score(X, labels, sample_size=10000))
    x = range(15, 30)
    y = s
    # my_xticks = np.arange(2, 40, 5)
    # markers_on = [20,22] #, 'rD', markevery=markers_on
    # k = [2,4,11,15,26,34]
    plt.show()
    plt.xticks(np.arange(min(x), max(x) + 1, 2))
    plt.yticks(np.arange(min(y), max(y), 0.001))
    plt.xlabel("k-values")
    plt.ylabel("Silouette")
    plt.title("Silouette for K-means cell's behaviour")
    plt.plot(x, y)
    #plt.plot(x, y, 'rD', markevery=[3, 5, 9, 13])
    plt.grid(axis='y', linestyle='-')
    plt.savefig(cfg.folder_culsters +'silhouette_4_kmeans_methods_large.png', bbox_inches='tight')
    plt.show()
"""


def write_clusters(X,k_values,svd,vectorizer):
  print()
  print("Write results in Methods_Clusters_ROBOTS.csv ")
  with open(cfg.folder_culsters + "Methods_Clusters_ROBOTS.csv", 'w', encoding="UTF-8") as f:
    for k in k_values:
      km = KMeans(n_clusters=k, init='k-means++', max_iter=100, n_init=1, verbose=False)
      km.fit(X)
      # save the classifier
      with open(cfg.folder_pickle +  'k_means_methods_{}.pkl'.format(k), 'wb') as fid:
        pkl.dump(km, fid)
      original_space_centroids = svd.inverse_transform(km.cluster_centers_)
      order_centroids = original_space_centroids.argsort()[:, ::-1]

      terms = vectorizer.get_feature_names()
      f.write("Top terms with {} clusters".format(k))
      f.write("\n")
      for i in range(len(order_centroids)):
        f.write("Annotate Here,Cluster {}:".format(i))
        for ind in order_centroids[i, :40]:
          f.write(',{}'.format(terms[ind]))
        f.write("\n")
      f.write("\n")


def main():

  db = tools.connect_to_mongo()
  print("Collect list of NEE per publication")
  documents = facet_embedding(db)
  print()
  print("Create tfidfVectorixaer")
  vectorizer = TfidfVectorizer(ngram_range=(1, 1),lowercase= False)

  print()
  print("Fit documents tfidfVectorixaer")
  X = vectorizer.fit_transform(documents)
  Xc = (X.T * X)
  len(vectorizer.get_feature_names())

  print()
  print("Create SVD pipeline with {} components and normalization".format(900))
  svd = decomposition.TruncatedSVD(n_components=900, n_iter=5)
  normalizer = Normalizer(copy=False)
  lsa = make_pipeline(svd, normalizer)

  print()
  print("Fit SVD+Normalization")
  X = lsa.fit_transform(Xc)

  explained_variance = svd.explained_variance_ratio_.sum()
  print("Explained variance of the SVD step: {}%".format(int(explained_variance * 100)))

  #plot_shilouete(X=X, min_k = 5 , max_k = 10)
  write_clusters(X=X, k_values= [5], svd=svd, vectorizer=vectorizer)



if __name__ == '__main__':
  main()
