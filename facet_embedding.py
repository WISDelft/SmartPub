from sklearn.feature_extraction.text import CountVectorizer
from pyhelpers import tools
import scipy.sparse as sp
from matplotlib.mlab import PCA
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn import decomposition
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans, MiniBatchKMeans



def is_int_or_float(s):
    ''' return 1 for int, 2 for float, -1 for not a number'''
    try:
        float(s)

        return 1 if s.count('.')==0 else 2
    except ValueError:
        return -1

####
def facet_embedding(db):
    papers=db.sentences_ner.distinct('paper_id')
    docs=[]

    for p in papers:

        print(p)
        ners=db.sentences_ner.distinct('ner',{'paper_id':p, 'label':'method', 'inWordnet':0})
        methodsString = ''
        for ne in ners:
            isint =is_int_or_float(ne)

            if isint==-1:
                ne=ne.replace(' ','')
                methodsString=methodsString+str(ne)+' '

        docs.append(methodsString)




    count_model = CountVectorizer(
        ngram_range=(1, 1))  # Convert a collection of text documents to a matrix of token counts- default unigram model
    X = count_model.fit_transform(docs)
    Xc = (X.T * X)  # this is co-occurrence matrix in sparse csr format
    #g = sp.diags(1. / Xc.diagonal())
    #Xc_norm = g * Xc  # normalized co-occurence matrix
    # Xc.setdiag(0) # sometimes you want to fill same word cooccurence to 0

    print("Performing dimensionality reduction using LSA")
    svd = decomposition.TruncatedSVD(algorithm='randomized', n_components=100, n_iter=5
                                     )
    # Vectorizer results are normalized, which makes KMeans behave as
    # spherical k-means for better results. Since LSA/SVD results are
    # not normalized, we have to redo the normalization.
    normalizer = Normalizer(copy=False)
    lsa = make_pipeline(svd, normalizer)

    X = lsa.fit_transform(Xc)

    print()
    km = KMeans(n_clusters=7)
    #km = MiniBatchKMeans(n_clusters=5, init='k-means++', init_size=1000, batch_size=1000, n_init=10,
    #                     )
    km.fit(X)

    original_space_centroids = svd.inverse_transform(km.cluster_centers_)
    order_centroids = original_space_centroids.argsort()[:, ::-1]

    terms = count_model.get_feature_names()
    for i in range(len(order_centroids)):
        print("Cluster %d:" % i, end='')
        for ind in order_centroids[i, :10]:
            print(' %s' % terms[ind], end='')
        print()




def main():
    db = tools.connect_to_mongo()
    facet_embedding(db)




if __name__ == '__main__':
    main()