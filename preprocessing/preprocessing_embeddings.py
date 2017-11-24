"""
This script will be used to find similar dataset/method
names based on the existing seeds using embedding clustering.
"""
from numbers import Number
from sklearn.preprocessing import StandardScaler
import codecs, numpy
from sklearn.metrics import silhouette_score
from nltk.corpus import stopwords
from nltk.corpus import wordnet
import string
from preprocessing.Extract_NE import preprocess_NE
from sklearn.cluster import KMeans
from default_config import ROOTHPATH
import nltk


class autovivify_list(dict):

    '''Pickleable class to replicate the functionality of collections.defaultdict'''

    def __missing__(self, key):
        value = self[key] = []
        return value

    def __add__(self, x):
        '''Override addition for numeric types when self is empty'''
        if not self and isinstance(x, Number):
            return x
        raise ValueError

    def __sub__(self, x):
        '''Also provide subtraction method'''
        if not self and isinstance(x, Number):
            return -1 * x
        raise ValueError

def build_word_vector_matrix(vector_file,propernouns):
    '''Read a GloVe array from sys.argv[1] and return its vectors and labels as arrays'''
    numpy_arrays = []
    labels_array = []
    with codecs.open(vector_file, 'r', 'utf-8') as f:
        for c, r in enumerate(f):
            sr = r.split()


            try:
                if sr[0] in propernouns  and not wordnet.synsets(sr[0]) and  sr[0].lower() not in stopwords.words('english') and 'dataset' not in sr[0].lower():
                 labels_array.append(sr[0])
                # print(sr[0].strip())

                 numpy_arrays.append(numpy.array([float(i) for i in sr[1:]]))
            except:
                continue



    return numpy.array(numpy_arrays), labels_array


def find_word_clusters(labels_array, cluster_labels):
    '''Read the labels array and clusters label and return the set of words in each cluster'''
    cluster_to_words = autovivify_list()
    for c, i in enumerate(cluster_labels):
        cluster_to_words[i].append(labels_array[c])
    return cluster_to_words

def clusteringec_all_dataset(numberOfSeeds,name ,numberOfIteration,iteration):

   #in the first iteration use the initial text extracted using the seeds
    if int(numberOfIteration) == 0:
        fileUnlabelled = ROOTHPATH + '/evaluation_files/X_train_' + str(numberOfSeeds) + '_' + str(iteration) + '.txt'

    # in the next iterations use the text extracted using the new set of seeds
    else:
        fileUnlabelled = ROOTHPATH + '/evaluation_files/' + name + 'text_Iteration' + numberOfIteration + str(
            numberOfSeeds) + '_' + str(iteration) + '.txt'

    #extract all the entities from the text
    propernouns = preprocess_NE(fileUnlabelled)

    dsnames = []

    #extract all the seed names
    corpuspath = ROOTHPATH+'/evaluation_files/X_Seeds_' + str(
        numberOfSeeds) + '_' + str(iteration) + '.txt'
    with open(corpuspath, "r") as file:
        for row in file.readlines():
            dsnames.append(row.strip())
            propernouns.append(row.strip())


    #this step is used for the iterations >1
    # for i in range(1, int(numberOfIteration)+1):
    #     with open(ROOTHPATH+'/evaluation_files/' + name + '_Iteration' + str(
    #             i) + '_POS_' + str(
    #         numberOfSeeds) + '_' + str(iteration) + '.txt', 'r') as file:
    #         for row in file.readlines():
    #             dsnames.append(row.strip())
    #             propernouns.append(row.strip())


    #replace the space between the bigram words with _ (for the word2vec embedding)
    newpropernouns = []
    bigrams = []
    for pp in propernouns:
        temp = pp.split(' ')
        if len(temp) > 1:
            bigram = list(nltk.bigrams(pp.split()))

            for bi in bigram:
                bi = bi[0].lower() + '_' + bi[1].lower()
                # print(bi)
                newpropernouns.append(bi)
        else:
            newpropernouns.append(pp)

    dsnames = [x.lower() for x in dsnames]


    dsnames = [s.translate(str.maketrans('', '', string.punctuation)) for s in dsnames]

    sentences_split = [s.lower() for s in newpropernouns]

    #use the word2vec model
    df, labels_array = build_word_vector_matrix(
        ROOTHPATH+"/models/modelword2vecbigram.txt", sentences_split)



    #CLuster the extracted entities 
    if len(df) >= 9:
        for n_clusters in range(2, 10):

            df = StandardScaler().fit_transform(df)
            kmeans_model = KMeans(n_clusters=n_clusters, max_iter=300, n_init=100)
            kmeans_model.fit(df)
            cluster_labels = kmeans_model.labels_

            cluster_to_words = find_word_clusters(labels_array, cluster_labels)
            cluster_labelss = kmeans_model.fit_predict(df)


            # for c in cluster_to_words:
            #     print(cluster_to_words[c])
            # # print("\n")
            finallist = []
            for c in cluster_to_words:
                counter = dict()

                for word in cluster_to_words[c]:
                    counter[word] = 0
                for word in cluster_to_words[c]:
                    if word in dsnames:


                        for ww in cluster_to_words[c]:
                            finallist.append(ww.replace('_',' '))




            try:

                silhouette_avg = silhouette_score(df, cluster_labelss)

                if silhouette_avg > maxcluster:
                    maxcluster = silhouette_avg
                    thefile = open(
                        ROOTHPATH+"/evaluation_files/" + name + "Pre_Iteration" + numberOfIteration + "_POS_" + str(
                            numberOfSeeds) + "_" + str(iteration) + ".txt", 'w')

                    for item in finallist:
                        #if item.lower() not in dsnames:
                            thefile.write("%s\n" % item)
            except:

                continue





def clusteringec_all_method(numberOfSeeds,name , numberOfIteration,iteration):


    if int(numberOfIteration) == 0:
        fileUnlabelled = ROOTHPATH + '/evaluation_filesMet/X_train_' + str(numberOfSeeds) + '_' + str(iteration) + '.txt'
    else:
        fileUnlabelled = ROOTHPATH + '/evaluation_filesMet/' + name + 'text_Iteration' + numberOfIteration + str(
            numberOfSeeds) + '_' + str(iteration) + '.txt'
    propernouns = preprocess_NE(fileUnlabelled)

    dsnames = []

    corpuspath = ROOTHPATH+'/evaluation_filesMet/X_Seeds2_' + str(
        numberOfSeeds) + '_' + str(iteration) + '.txt'
    with open(corpuspath, "r") as file:
        for row in file.readlines():
            dsnames.append(row.strip())
            propernouns.append(row.strip())


    #this step is used for the iterations >1
    # for i in range(1, int(numberOfIteration)+1):
    #             with open(ROOTHPATH+'/evaluation_filesMet/' + name + '_Iteration' + str(
    #                     i) + '_POS_' + str(
    #                 numberOfSeeds) + '_' + str(iteration) + '.txt', 'r') as file:
    #                 for row in file.readlines():
    #                     dsnames.append(row.strip())
    #                     propernouns.append(row.strip())


    newpropernouns = []
    bigrams = []
    for pp in propernouns:
        temp = pp.split(' ')
        if len(temp) > 1:
            bigram = list(nltk.bigrams(pp.split()))

            for bi in bigram:
                bi = bi[0].lower() + '_' + bi[1].lower()
                # print(bi)
                newpropernouns.append(bi)
        else:
            newpropernouns.append(pp)
    dsnames = [x.lower() for x in dsnames]


    dsnamestemp = [s.translate(str.maketrans('', '', string.punctuation)) for s in dsnames]
    finalds = []
    for ds in dsnamestemp:
        dss = ds.split(' ')
        if len(dss) > 1:
            ds = ds.replace(' ', '_')
        finalds.append(ds)

    sentences_split = [s.lower() for s in newpropernouns]

    df, labels_array = build_word_vector_matrix(
        ROOTHPATH+"/models/modelword2vecbigram.txt", sentences_split)


    sse = {}
    maxcluster = 0
    if len(df) >= 9:
        for n_clusters in range(2, 10):

            df = StandardScaler().fit_transform(df)
            kmeans_model = KMeans(n_clusters=n_clusters, max_iter=300, n_init=100)
            kmeans_model.fit(df)
            cluster_labels = kmeans_model.labels_

            cluster_to_words = find_word_clusters(labels_array, cluster_labels)
            cluster_labelss = kmeans_model.fit_predict(df)
            sse[n_clusters] = kmeans_model.inertia_

            finallist = []
            for c in cluster_to_words:
                counter = dict()
                for word in cluster_to_words[c]:
                    counter[word] = 0
                for word in cluster_to_words[c]:
                    if word in finalds:


                        for ww in cluster_to_words[c]:
                            finallist.append(ww.replace('_',' '))




            try:

                silhouette_avg = silhouette_score(df, cluster_labelss)

                if silhouette_avg > maxcluster:
                    maxcluster = silhouette_avg
                    thefile = open(
                        ROOTHPATH+"/evaluation_filesMet/" + name + "Pre_Iteration" + numberOfIteration + "_POS_" + str(
                            numberOfSeeds) + "_" + str(iteration) + ".txt", 'w')

                    for item in finallist:
                        #if item.lower() not in dsnames:
                            thefile.write("%s\n" % item)

            except:

                continue


    else:
        for n_clusters in range(2, len(df)):

            df = StandardScaler().fit_transform(df)
            kmeans_model = KMeans(n_clusters=n_clusters, max_iter=300, n_init=100)
            kmeans_model.fit(df)
            cluster_labels = kmeans_model.labels_

            cluster_to_words = find_word_clusters(labels_array, cluster_labels)
            cluster_labelss = kmeans_model.fit_predict(df)
            sse[n_clusters] = kmeans_model.inertia_

            finallist = []
            for c in cluster_to_words:
                counter = dict()
                dscounter = 0
                for word in cluster_to_words[c]:
                    counter[word] = 0
                for word in cluster_to_words[c]:
                    if word in finalds:

                        for ww in cluster_to_words[c]:
                            finallist.append(ww.replace('_', ' '))

            try:

                silhouette_avg = silhouette_score(df, cluster_labelss)

                if silhouette_avg > maxcluster:
                    maxcluster = silhouette_avg
                    thefile = open(
                        ROOTHPATH + "/evaluation_filesMet/" + name + "Pre_Iteration" + numberOfIteration + "_POS_" + str(
                            numberOfSeeds) + "_" + str(iteration) + ".txt", 'w')

                    for item in finallist:
                        # if item.lower() not in dsnames:
                        thefile.write("%s\n" % item)
                    for item in bigrams:
                        # if item.lower() not in dsnames:
                        thefile.write("%s\n" % item)

            except:

                continue
