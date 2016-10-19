import  string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

"""



f = open('useful_phrases.txt', 'r')
lines = f.readlines()
categories = 0
en_stop = set(stopwords.words('english') + list(string.punctuation))

x = open("dataset.csv", "w")
all_words = set()
for line in lines:
    mystr = line.split()
    if len(mystr) != 0:
        if not mystr[0].isnumeric():
            words = word_tokenize(line)
            words = [w.lower() for w in words if w not in en_stop]
            x.write(str(words)+ "# {}".format(categories))
            x.write("\n")
        else:
            categories += 1

x.close()
f.close()
"""

y = open("dataset.csv", "r")
lines = y.readlines()
previous = 1
set_of_words = set()
z = open("final_dataset.csv", "w")
count = 1
for line in lines:
    mystr2 = line.strip().split(sep=',')
    next_num = int(mystr2[len(mystr2)-1].strip())
    print ("next number: {} , previous number: {}".format(next_num,previous))
    if previous == next_num:
        for word in mystr2:
            if not word.strip().isnumeric():
                set_of_words.add(word)

        #for w in mywords:
        #    words.add(w)
    else:
        #list_of_words.append()
        count += 1
        z.write(str(set_of_words) + ",{}".format(previous))
        set_of_words= set()
        z.write("\n")
        previous = next_num

z.write(str(set_of_words) + ",{}".format(previous))
print(count)
y.close()
z.close()