"""
In this code we will annotated the sentences which where extracted by trainingdata_extraction.py using the seed files.
"""
from itertools import repeat
import csv
from nltk.corpus import stopwords
from nltk.corpus import wordnet
import nltk
from nltk.tokenize import word_tokenize
from nltk import tokenize
from nltk import pos_tag, ne_chunk
from nltk.tokenize import SpaceTokenizer
from nltk.corpus import stopwords
from nltk.corpus import wordnet
import string
import gensim
from sklearn.cluster import KMeans
import numpy as np
from nltk.stem.porter import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer




def generate_training(numberOfSeeds):
    tokenizer = SpaceTokenizer()
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    for iteration in range(0,10):
        dsnames=[]
       
    #get the seed names and lowercase them
        corpuspath='/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_Seeds_' + str(numberOfSeeds) + '_' + str(iteration) + '.txt'
        with open(corpuspath, "r") as file:
            for row in file.readlines():
                dsnames.append(row.strip())
   
        dsnames=[x.lower() for x in dsnames]
        dsnames = list(set(dsnames))

         
        fileUnlabelled=open('/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_testAp_' + str(numberOfSeeds) + '_' + str(iteration) + '.txt','r')

        text=fileUnlabelled.read()
        text=text.replace('\\','')
        text=text.replace('/','')
        text = text.replace('"', '')
        text = text.replace('(', '')
        text = text.replace(')', '')
        text = text.replace('[', '')
        text = text.replace(']', '')
        text = text.replace(',', ' ,')
        text = text.replace('?', ' ?')
        text = text.replace('..', '.')

        #Split the text into sentences
        lines = (tokenize.sent_tokenize(text.strip()))
        labelledtext=list()

        print(len(lines))

        lines=list(set(lines))
        #in each line check if there exists a match word to the seed names, if yes add the /DATA label to the word
        for line in lines:

           index = [i for i, x in enumerate(dsnames) if dsnames[i] in line.lower()]
           worddict = dict()
           words=word_tokenize(line)

           for word in words:
               #word = word.translate(str.maketrans('', '', string.punctuation))
               worddict[word] = ''

           if index:

               for i in index:

                #print(dsnames[i])

                flag = False
                for idx, word in enumerate(words):
                    #word=word.translate(str.maketrans('', '', string.punctuation))
                    
                    if flag==True:

                        flag=False
                        if word[0].isupper():
                           worddict[word] = word + '/DATA'
                        # else:
                        #
                        #     try:
                        #         if word==',' or word=='and':
                        #             if words[idx + 1][0].isupper():
                        #                 worddict[words[idx + 1]] = words[idx + 1] + '/DATA'
                        #                 dsnames.append(words[idx + 1])
                        #                 if words[idx + 2]== ',' or words[idx + 2] == 'and':
                        #                     if words[idx + 3][0].isupper():
                        #                       worddict[words[idx + 3]] = words[idx + 3] + '/DATA'
                        #                       dsnames.append(words[idx + 3])
                        #
                        #
                        #
                        #             elif words[idx - 1][0].isupper():
                        #                 worddict[words[idx - 1]] = words[idx - 1] + '/DATA'
                        #                 dsnames.append(words[idx -1])
                        #                 if words[idx - 2] == ',' or words[idx - 2] == 'and':
                        #                     if words[idx - 3][0].isupper():
                        #                         worddict[words[idx - 3]] = words[idx - 3] + '/DATA'
                        #                         dsnames.append(words[idx - 3])
                        #
                        #     except:
                        #         continue


                    if word.lower() in dsnames[i] and len(word)>2:
                        splitted=dsnames[i].split(' ')

                        checkngram=False
                        if len(splitted)>1:

                            for sp in range(len(splitted)):
                              try:
                                if words[idx + sp].lower() in dsnames[i]:


                                    checkngram=True
                                    #worddict[word] = word + '/DATA'
                                else:
                                    #print(words[idx + sp].lower())
                                    checkngram = False
                              except:
                                 checkngram = False


                            if checkngram==True:
                                 checkngram=False
                                 for sp in range(0,len(splitted)):
                                    # print(words[idx + sp])

                                     worddict[words[idx + sp]] = words[idx + sp] + '/DATA'



                        else:
                            worddict[word]=word + '/DATA'
                           # word=word + '/DATA'
                           # flag = True
                        # # if words[idx - 1] == ',' or words[idx - 1] == 'and':
                        # #     if words[idx - 2][0].isupper():
                        # #             worddict[words[idx - 2]] = words[idx - 2] + '/DATA'
                        # #             if words[idx - 3][0].isupper():
                        #                  worddict[words[idx - 3]] = words[idx - 3] + '/DATA'
                    elif dsnames[i] in word.lower() and len(word)>2:
                        if len(word)<4:
                            if word.lower().startswith(dsnames[i]) :
                                # if  word.lower() not in stopwords.words('english') and not wordnet.synsets(word.lower()):
                                    worddict[word] = word + '/DATA'
                        else:
                            worddict[word] = word + '/DATA'

                                # word = word + '/DATA'
                                # flag =True
                                # if words[idx - 1] == ',' or words[idx - 1] == 'and':
                                #     if words[idx - 2][0].isupper():
                                #         worddict[words[idx - 2]] = words[idx - 2] + '/DATA'
                                #         if words[idx - 3][0].isupper():
                                #             worddict[words[idx - 3]] = words[idx - 3] + '/DATA'



                       # print(word)
               sentence=''
               for i,word in enumerate(words):
                       if worddict[word]=='':
                           sentence=sentence+' ' +word
                       else:
                        #try:
                           if '/DATA' in worddict[words[i+1]] or '/DATA' in worddict[words[i-1]]:

                              sentence=sentence+ ' ' + worddict[word]
                           elif 'data' in word.lower():
                               sentence = sentence + ' ' + word
                           else:
                               sentence = sentence + ' ' + worddict[word]
               labelledtext.append(sentence)
                
           else:
               labelledtext.append(line)
                
        inputs = []
        #generate the tab seperated file  for each word an it's label like the example below:
        '''
        Two	O
        well	O
        known	O
        public	O
        image	O
        datasets	O
        ,	O
        NUS-WIDE	DATA
        25	O
        and	O
        ImageNet	DATA
        '''
        for ll in labelledtext:
               words = word_tokenize(ll)

               for word in words:
                   if '/DATA' in word:
                       label = 'DATA'
                       word = word.split('/')
                       word = word[0]

                   else:
                       label = 'O'
                   inputs.append([word, label])
        with open('/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/seednames_test_' + str(numberOfSeeds) + '_' + str(iteration) + '.txt', 'w') as file:
               for item in inputs:
                   row = str(item[0]) + '\t' + str(item[1]) + "\n"
                   file.write(row)
        file = open('/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/seednames_test_splitted' + str(numberOfSeeds) + '_' + str(iteration) + '.txt', 'w')
        with open('/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/seednames_test_' + str(numberOfSeeds) + '_' + str(iteration) + '.txt', 'r') as tsvin:
               tsvin = csv.reader(tsvin, delimiter='\t')

               for row in tsvin:
                   # print(row)
                   if '###' in row[0]:
                       continue
                   elif row[0] == '.':
        
                       rows = str(row[0]) + '\t' + str(row[1]) + "\n"
                       file.write(rows)
                       file.write("\n")
                   else:
                       rows = str(row[0]) + '\t' + str(row[1]) + "\n"
                       file.write(rows)

        file.close()



generate_training(2)
generate_training(5)
generate_training(10)
generate_training(25)
generate_training(50)
generate_training(100)

