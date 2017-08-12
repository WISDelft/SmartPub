from nltk.tokenize import word_tokenize
from nltk import tokenize
def preprocess(numberOfSeeds):
    for iteration in range(0, 10):


        fileUnlabelled = open(
            '/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_train_' + str(numberOfSeeds) + '_' + str(iteration) + '.txt', 'r')
        text = fileUnlabelled.read()
        lines = (tokenize.sent_tokenize(text.strip()))

        print(len(lines))

        lines = list(set(lines))
        sentences=''
        for line in lines:

            words = word_tokenize(line)
            flag=False
            for word in words:
                if '.' in word:
                    splitted_word=list(word)

                    for i,ww in enumerate(splitted_word):
                        if ww=='.':
                         try:

                            if splitted_word[i+1].isupper():
                                flag=True
                         except:
                             continue
                if flag:
                    flag=False
                    word=word.replace('.','. ')
                sentences=sentences+' '+word
        text_file = open('/Users/sepidehmesbah/Downloads/ner-crf-master/evaluation_files/X_testAp_' + str(numberOfSeeds) + '_' + str(iteration) + '.txt', 'w')
        text_file.write(sentences)
        text_file.close()







preprocess(2)
preprocess(5)
preprocess(10)
preprocess(25)
preprocess(50)
preprocess(100)


