
from sklearn.preprocessing import Normalizer
from nltk.tokenize import word_tokenize
import numpy as np
import config as cfg
import _pickle as pkl
from gensim.models import Word2Vec
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


def main():
  print("Proces word2vec + DBSCAN")
  with open(cfg.folder_pickle +"Method_terms.pkl", 'rb') as pickle_file:
    Method_terms = list(pkl.load(pickle_file))

  w2v_models = list()
  w2v_models.append(Word2Vec.load(cfg.folder_pickle + 'Word2VecModel_size_200_win_5_rh_coll_v2'))
  w2v_models.append(Word2Vec.load(cfg.folder_pickle + 'Word2VecModel_size_200_win_25_rh_coll_v2'))
  w2v_models.append(Word2Vec.load(cfg.folder_pickle + 'Word2VecModel_size_200_win_50_rh_coll_v2'))
  w2v_models.append(Word2Vec.load(cfg.folder_pickle + 'Word2VecModel_size_200_win_200_rh_coll_v2'))

  for num, model in enumerate(w2v_models):
    my_list = get_w2vArray(model,Method_terms)
    w2v_array = np.asarray(my_list)
    print(w2v_array.shape)

    # Normalize
    w2v_array = StandardScaler().fit_transform(w2v_array)

    # DBSCAN
    db = DBSCAN(eps=0.1, min_samples=5, metric='euclidean', algorithm= 'ball_tree').fit(w2v_array)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

    print('Estimated number of clusters: %d' % n_clusters_)
    with open(cfg.folder_culsters + "DBSCAN_W2V_model_{}.csv".format(num), 'w', encoding='UTF-8') as f:
      for i in range(n_clusters_):
        f.write("cluster {}:, Anotate Here,".format(i))
        for j, label in enumerate(labels):
          if label == i:
            f.write("{},".format(Method_terms[j]))
        f.write("\n")
    """
    for i in range(n_clusters_):
      print("cluster {}:".format(i), end="")
    for j, label in enumerate(labels):
      if label == i:
        print("{},".format(list(Method_terms)[j]), end=" ")
    print()
    """

    print("Store DBSCAN")
    with open(cfg.folder_pickle + "dbscan_cluster_{}.pkl".format(num), 'wb') as pickle_file:
      pkl.dump(obj=db, file=pickle_file)
    print("Next Model")
    # print("Outilers:".format(i), end= "")
    # for j,label in enumerate(labels):
    #    if label == -1:
    #        print ("{},".format(Method_terms[j]), end=" ")


def get_w2vArray(w2v_model, Method_terms):
    my_list = list()
    count = 0
    length = 0
    term_list = list()
    for term in Method_terms:
        tmp = np.zeros(200) # do not forget to change it if you use different window size
        in_terms = word_tokenize(term)
        for i,t in enumerate(in_terms):
            try:
                #print(t)
                length+=1
                tmp += w2v_model.wv.word_vec(str(t))

                #my_list.append(w2v_model.wv.word_vec(term))

            except:
                #tmp += np.zeros(100)
                count +=1

        my_list.append(tmp / length)
        #term_list.append(term)
        length = 0
            #print(term)
            #my_list.append(np.zeros(200))
    print("terms: {}, meth_terms: {}, terms not in voc: {}".format(len(my_list), len(Method_terms),count))
    return my_list

if __name__ == '__main__':
  main()
