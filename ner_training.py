"""
This Script, creates the property file for different training data files, then trains a CRF and tests it on 2 different test sets testA, testB.
"""
import subprocess
import re


def test_on_testB(numberOfSeeds):
    ''' Testing the trained crf on testB '''
    outputfile = open('/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation/aaaembedingclustering_testBoutputs.txt', 'a')
    for iteration in range(0, 10):
        command='java -cp /Users/sepidehmesbah/Downloads/stanford-ner-2016-10-31/stanford-ner.jar edu.stanford.nlp.ie.crf.CRFClassifier -loadClassifier /Users/sepidehmesbah/Downloads/ner-crf-master/evaluation/embedingclustering_splitted'+ str(numberOfSeeds) + '_' + str(iteration) +'.ser.gz -testFile /Users/sepidehmesbah/Downloads/ner-crf-master/evaluation/X_testB_50_manually_splitted3.tsv'
        p = subprocess.call(command,
                         stdout=outputfile,
                         stderr=subprocess.STDOUT, shell=True)
    outputfile.close()

#run_command('java -cp /Users/sepidehmesbah/Downloads/stanford-ner-2016-10-31/stanford-ner.jar edu.stanford.nlp.ie.crf.CRFClassifier -loadClassifier /Users/sepidehmesbah/Downloads/stanford-ner-2016-10-31/seednames_splitted2_1.tsv.ser.gz -testFile /Users/sepidehmesbah/Downloads/ner-crf-master/evaluation/X_testB_50_manually_splitted.tsv')


###############

def training_austenprop(numberOfSeeds):
    ''' Training the CRF and testing on TestA '''
    outputfile=open('/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation/aaaembedingclustering__testAoutputs.txt','a')
    for iteration in range(0, 10):

        command = 'java -cp /Users/sepidehmesbah/Downloads/stanford-ner-2016-10-31/stanford-ner.jar edu.stanford.nlp.ie.crf.CRFClassifier -prop /Users/sepidehmesbah/Downloads/ner-crf-master/prop_files/austen' + str(numberOfSeeds) + '_' + str(iteration) + '.prop'

        p = subprocess.call(command,
                         stdout=outputfile,
                         stderr=subprocess.STDOUT, shell=True)




def create_austenprop(numberOfSeeds):
    ''' Generating the property files'''
    outputfile = open('/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation/austen.prop', 'r')
    text=outputfile.read()
    print(text)
    for iteration in range(0, 10):
        modifiedpath='trainFile=/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/embedingclustering_splitted' + str(numberOfSeeds) + '_' + str(iteration) + '.txt'
        modifiedpathtest = 'testFile=/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/embedingclustering_test_splitted' + str(numberOfSeeds) + '_' + str(iteration) + '.txt'
        serializeTo='serializeTo=seednames__splitted' + str(numberOfSeeds) + '_' + str(iteration) +'.ser.gz'
        edited = re.sub(r'trainFile.*?txt', modifiedpath, text, flags=re.DOTALL)
        edited = re.sub(r'testFile.*?txt', modifiedpathtest, edited, flags=re.DOTALL)
        edited = re.sub(r'serializeTo.*?gz', serializeTo, edited, flags=re.DOTALL)
        print(edited)
        text_file = open('/Users/sepidehmesbah/Downloads/ner-crf-master/prop_files/austen'+ str(numberOfSeeds) + '_' + str(iteration) + '.prop', 'w')
        text_file.write(edited)
        text_file.close()

# create_austenprop(2)
# create_austenprop(5)
# create_austenprop(10)
# create_austenprop(25)
# create_austenprop(50)
# create_austenprop(100)
# training_austenprop(2)
# training_austenprop(5)
# training_austenprop(10)
# training_austenprop(25)
# training_austenprop(50)
# training_austenprop(100)
test_on_testB(2)
test_on_testB(5)
test_on_testB(10)
test_on_testB(25)
test_on_testB(50)
test_on_testB(100)

