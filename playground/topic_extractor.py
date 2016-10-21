#!/usr/bin/env python
# -*- coding: utf-8 -*-


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation





def print_top_words(model, feature_names, n_top_words,section_name):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        with open(section_name + ".txt", "a") as myfile:
            myfile.write(",".join([feature_names[i]
                                   for i in topic.argsort()[:-n_top_words - 1:-1]]))
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
    print()


def get_topic(rhetorical_text,topics,section_name):

    n_features = 30
    n_topics =topics
    n_top_words = 30


    try:
        vectorizer = TfidfVectorizer(max_df=0.95, min_df=1, max_features=n_features, ngram_range=(2, 3),
                                     stop_words='english')
        X = vectorizer.fit_transform(rhetorical_text)



        nmf = NMF(n_components=n_topics, random_state=1).fit(X)
        tf_feature_names = vectorizer.get_feature_names()

        print("\nTopics in NMF model:")
        print_top_words(nmf, tf_feature_names, n_top_words,section_name)


        lda = LatentDirichletAllocation(n_topics=n_topics, max_iter=5,
                                            learning_method='online',
                                            learning_offset=50.,
                                            random_state=0)

        lda.fit(X)
        tf_feature_names = vectorizer.get_feature_names()

        print("\nTopics in LDA model:")
        print_top_words(lda, tf_feature_names, n_top_words,section_name)
    except:
        print "No topic found"
        pass