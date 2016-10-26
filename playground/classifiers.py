
import nltk
from scipy import sparse
import dictionary
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

"""
Examples of clasifiers

"""



def get_extra_features(train):
    """
     Extract some meta data from the sentences (verbs, lexicons)
    """

    metadata=[]
    adverbs=[]
    lexicon=[]
    dataset=dictionary.dataset

    X=[x[0] for x in train]
    for i in range(0,len(X)):
        tokens = nltk.word_tokenize(X[i])
        tagged_sent=nltk.pos_tag(tokens)
        verbs = [word for word, pos in tagged_sent if pos == 'VBP' or pos == 'MD']
        if verbs:
                metadata.append(verbs[0])
        else:
            metadata.append("")
        adverb = [word for word, pos in tagged_sent if pos == 'RB']
        if adverb:
                adverbs.append(adverb[0])
        else:
            adverbs.append("")

        if any(word in X[i] for word in dataset):
               lexicon.append("dataset")
        else:
            lexicon.append("")
    return metadata,lexicon


def vectorize(train, metadata,lexicon):

    """
    add meta data to the feature vector
    """
    Y=[x[1] for x in train]


    X=[x[0] for x in train]

    vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=500,
                                         stop_words='english')
    X = vectorizer.fit_transform(X)
    vect2 = TfidfVectorizer(max_df=0.95, min_df=2, max_features=500)
    vect3 = TfidfVectorizer(max_df=0.95, min_df=2, max_features=500)

    metadata=vect2.fit_transform(metadata)
    lexicon=vect3.fit_transform(lexicon)
    merged_X = sparse.hstack((X, metadata))
    merged_x=sparse.hstack((merged_X, lexicon))

    X_train, X_test, y_train, y_test =train_test_split(merged_X , Y, test_size=.4, random_state=42)
    return X_train, X_test, y_train, y_test

def random_forest_classifier(X_train, X_test, y_train, y_test):
    clf=RandomForestClassifier(max_depth=6, n_estimators=43, max_features=100)
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    print "random_forest_classifier:"
    print score
    return clf
    #print clf.predict(X_test[400])
    #print y_test[400]

def SVC_classifier(X_train, X_test, y_train, y_test):
    clf1=SVC(gamma=1, C=1)
    clf1.fit(X_train, y_train)
    score = clf1.score(X_test, y_test)
    print "SVC_classifier:"
    print score
    return clf1


def fasttext_classifier():
     classifier = fasttext.supervised('fasttexttrain.txt', 'model', label_prefix='__label__')
     texts = ['Our dataset consists of geo-tagged activity logs from Four- square.', 'The presented data was extracted using the open source Twitter API v1.1 [6].','In this section we introduce the notation and the problem setting we will be working with in the rest of the paper.']
     labels = classifier.predict(texts)
     print labels
     result = classifier.test('test.txt')
     print 'P@1:', result.precision
     print 'R@1:', result.recall
     print 'Number of examples:', result.nexamples

def main():

  train=dictionary.train+dictionary.train2
  metadata,lexicon=get_extra_features(train)
  X_train, X_test, y_train, y_test = vectorize(train, metadata,lexicon)
  randomf_clf=random_forest_classifier(X_train, X_test, y_train, y_test)
  svc_clf=SVC_classifier(X_train, X_test, y_train, y_test)
  fasttext_classifier()


if __name__ == '__main__':
    main()


