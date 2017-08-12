import subprocess
import re


def run_command(numberOfSeeds):
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
    outputfile=open('/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation/aaaembedingclustering__testAoutputs.txt','a')
    for iteration in range(0, 10):

        command = 'java -cp /Users/sepidehmesbah/Downloads/stanford-ner-2016-10-31/stanford-ner.jar edu.stanford.nlp.ie.crf.CRFClassifier -prop /Users/sepidehmesbah/Downloads/ner-crf-master/prop_files/austen' + str(numberOfSeeds) + '_' + str(iteration) + '.prop'

        p = subprocess.call(command,
                         stdout=outputfile,
                         stderr=subprocess.STDOUT, shell=True)




def create_austenprop(numberOfSeeds):


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
run_command(2)
run_command(5)
run_command(10)
run_command(25)
run_command(50)
run_command(100)

# outputfile = open('/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation/simplerule+embedding2_4.txt', 'a')
#
# command='java -cp /Users/sepidehmesbah/Downloads/stanford-ner-2016-10-31/stanford-ner.jar edu.stanford.nlp.ie.crf.CRFClassifier -loadClassifier /Users/sepidehmesbah/Downloads/stanford-ner-2016-10-31/simplerule+embedding2_4.ser.gz -testFile /Users/sepidehmesbah/Downloads/ner-crf-master/evaluation/X_testB_50_manually_splitted.tsv'
# p = subprocess.call(command,
#                          stdout=outputfile,
#                          stderr=subprocess.STDOUT, shell=True)
# outputfile.close()