
"""
This scripts generated training data and trains NER using different number of seeds and approach.
We already extracted the training data using the seed terms (done with different number of seeds 10 times) and they are stored in the evaluation_files folder.

For example in the evaluation_files folder X_Seeds_5_0.txt are the seed terms in case of having just 5 seeds and the X_train_5_0.txt are the extracted sentences using those seeds
"""
import multiprocessing

from preprocessing import ner_training,preprocessing_embeddings
from postprocessing import trainingdata_generation

from default_config import ROOTHPATH
from gensim.models import Doc2Vec
print(multiprocessing.cpu_count())
modeldoc2vec = Doc2Vec.load(ROOTHPATH + '/models/doc2vec.model')




"""
Term expansion approach for the first iteration
"""

#perform term expnasion on the text of the training data using different number of seeds (i.e. 5,10,25,50,100)
for number in range(0,10):

        preprocessing_embeddings.clusteringec_all_dataset(5, 'term_expansion', str(0), str(number))
        preprocessing_embeddings.clusteringec_all_dataset(10, 'term_expansion', str(0), str(number))
        preprocessing_embeddings.clusteringec_all_dataset(25, 'term_expansion', str(0), str(number))
        preprocessing_embeddings.clusteringec_all_dataset(50,'term_expansion' , str(0),str(number))
        preprocessing_embeddings.clusteringec_all_dataset(100, 'term_expansion', str(0), str(number))

#training data generation
for number in range(0,10):
    trainingdata_generation.post_generate_training(5,'term_expansion' , str(0),str(number))
    trainingdata_generation.post_generate_training(10,'term_expansion' , str(0),str(number))
    trainingdata_generation.post_generate_training(25,'term_expansion' , str(0),str(number))
    trainingdata_generation.post_generate_training(50,'term_expansion' , str(0),str(number))
    trainingdata_generation.post_generate_training(100,'term_expansion' , str(0),str(number))

#training the NER model which will be saved in the crf_trained_files folder
ner_training.create_austenprop(5, 'term_expansion', str(0))
ner_training.create_austenprop(10, 'term_expansion', str(0))
ner_training.create_austenprop(25, 'term_expansion', str(0))
ner_training.create_austenprop(50, 'term_expansion', str(0))
ner_training.create_austenprop(100, 'term_expansion', str(0))
#
ner_training.training_austenprop(5, 'term_expansion', str(0))
ner_training.training_austenprop(10, 'term_expansion', str(0))
ner_training.training_austenprop(25, 'term_expansion', str(0))
ner_training.training_austenprop(50, 'term_expansion', str(0))
ner_training.training_austenprop(100, 'term_expansion', str(0))







"""
Sentence approach for the first iteration
"""

for number in range(0,10):

        preprocessing_embeddings.clusteringec_all_dataset(5, 'sentence_expansion', str(0), str(number))
        preprocessing_embeddings.clusteringec_all_dataset(10, 'sentence_expansion', str(0), str(number))
        preprocessing_embeddings.clusteringec_all_dataset(25, 'sentence_expansion', str(0), str(number))
        preprocessing_embeddings.clusteringec_all_dataset(50,'sentence_expansion' , str(0),str(number))
        preprocessing_embeddings.clusteringec_all_dataset(100, 'sentence_expansion', str(0), str(number))
#
# # #
for number in range(0,10):
    trainingdata_generation.post_generate_trainingSE(5,'sentence_expansion' , str(0),str(number),modeldoc2vec)
    trainingdata_generation.post_generate_trainingSE(10,'sentence_expansion' , str(0),str(number),modeldoc2vec)
    trainingdata_generation.post_generate_trainingSE(25,'sentence_expansion' , str(0),str(number),modeldoc2vec)
    trainingdata_generation.post_generate_trainingSE(50,'sentence_expansion' , str(0),str(number),modeldoc2vec)
    trainingdata_generation.post_generate_trainingSE(100,'sentence_expansion' , str(0),str(number),modeldoc2vec)

ner_training.create_austenprop(5, 'sentence_expansion', str(0))
ner_training.create_austenprop(10, 'sentence_expansion', str(0))
ner_training.create_austenprop(25, 'sentence_expansion', str(0))
ner_training.create_austenprop(50, 'sentence_expansion', str(0))
ner_training.create_austenprop(100, 'sentence_expansion', str(0))
#
ner_training.training_austenprop(5, 'sentence_expansion', str(0))
ner_training.training_austenprop(10, 'sentence_expansion', str(0))
ner_training.training_austenprop(25, 'sentence_expansion', str(0))
ner_training.training_austenprop(50, 'sentence_expansion', str(0))
ner_training.training_austenprop(100, 'sentence_expansion', str(0))