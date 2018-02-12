from nltk.tag.stanford import StanfordNERTagger
from nltk.corpus import wordnet
from nltk.corpus import stopwords

"""
For extracting method entities replace all the "DATA" with "MET"
"""
path_to_jar = "PATH_TO/stanford-ner.jar"
path_to_model='PATH_TO/trained_ner_DATA.ser.gz'



def get_NEs(res):
    result = []

    for i, (a, b) in enumerate(res):
        if b == 'DATA':
            temp = a
            if i > 1:
                j = i - 1
                if res[j][1] == 'DATA':
                    continue
            j = i + 1
            try:
                if res[j][1] == 'DATA':
                    temp = b
                    temp = res[j][0] + ' ' + b
                    z = j + 1
                    if res[j][1] == 'DATA':
                        temp = a + ' ' + res[j][0] + ' ' + res[z][0]

            except:
                continue

            # result.append(a)
            result.append(temp)


    filter_bywordnet = []
    filtered_bystopword = [word for word in set(result) if word not in stopwords.words('english')]

    for word in set(filtered_bystopword):
        if not wordnet.synsets(word):
            filter_bywordnet.append(word)
    return filter_bywordnet

file = open('PATH_TO_TEXT', 'r')
text= file.read()
nertagger = StanfordNERTagger(path_to_model, path_to_jar)

res = nertagger.tag(text.split())
get_NEs(res)