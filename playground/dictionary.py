#import en
from collections import defaultdict


"""""
    A list of all possible verb tenses
            ['past', '3rd singular present', 'past participle', 'infinitive',
            'present participle', '1st singular present', '1st singular past',
            #'past plural', '2nd singular present', '2nd singular past',
            '3rd singular past', 'present plural']
"""""

objective=['introduce','introduced','we use', 'We use','we also', 'We also','arguing','argued','argues','argue', 'concluding','concluded','concludes','conclude','demonstrating','demonstrated','demonstrates','demonstrate','indicating','indicated','presenting','presented','presents', 'present','recommending','recommended','recommends','recommend','showing','showed','shows','show','shown', 'suggested','suggests','suggest','indicated','indicates','indicate','find','findings','finding', 'found', 'result','we used','We used','we list', 'We list','this research','This research','we find', 'We find','We conducted','we conducted','our research','Our research','we show', 'We show','we construct','We construct','we employ', 'We employ','we discuss','We discuss','this study', 'This study','we explore', 'We explore','We present','we present','We compare', 'we compare','we develop', 'We develop', 'we define', 'We define','in this study','In this study','The goal', 'the goal','we describe', 'We describe','this work', 'This work','aims','we perform','We perform','In this paper', 'we propose','We propose', 'the present paper','The present paper', 'the present study','we study', 'We study','the aim of this paper','The aim of this paper','we aim','We aim','the purpose of this paper','The purpose of this paper', 'we investigate','We investigate', 'we introduce','We introduce', 'in this work','In this work', 'we examine','We examine','This paper', 'this paper', 'this article', 'This article', 'analyze','analyzed','analyzes', 'analyse','analysed','analyses']


dataset=['dataset','Dataset','datasource','Datasource','data source','Data source', 'data from','Data from', 'collected from','open data', 'OpenData','database','databases','Open data', 'Foursquare','Facebook', 'Twitter','Instagram','Weibo', 'Flickr', 'OpenStreetMap','Google places', 'LBSN','Brightkite', 'Gowalla','geo-tagged','Census data','census data','mobility data', 'Mobility data']

method=['Algorithm','algorithm','analyze','analyzed','analyzes', 'analyse','analysed','analyses','approach', 'Aproach','methodology','Methodology','method', 'Method','framework', 'Framework', 'Figure', 'figure', 'table', 'Table','technique', 'Technique' ]


result=['see','seen','precision','recall', 'F1', 'concluding','concluded','concludes','conclude','demonstrating','demonstrated','demonstrates','demonstrate','indicating','indicated','showing','showed','shows','show','shown' ,'suggested','suggests','suggest', 'find','findings','finding', 'found', 'result', 'Figure', 'figure', 'table', 'Table']

def leaders(xs, top=50):
    counts = defaultdict(int)
    for x in xs:
        counts[x] += 1
    return sorted(counts.items(), reverse=True, key=lambda tup: tup[1])[:top]


def myreadlines(f, newline):
  buf = ""
  while True:
    while newline in buf:
      pos = buf.index(newline)
      yield buf[:pos]
      buf = buf[pos + len(newline):]
    chunk = f.read(4096)
    if not chunk:
      yield buf
      break
    buf += chunk
introduction=[]
abstract=[]
method=[]
dataset=[]
with open('introduction.txt') as f:
  for line in myreadlines(f, ","):
      introduction.append(line)

print leaders(introduction)

with open('abstract.txt') as f:
  for line in myreadlines(f, ","):
      abstract.append(line)

print leaders(abstract)

with open('method.txt') as f:
  for line in myreadlines(f, ","):
      method.append(line)

print leaders(method)

with open('dataset.txt') as f:
  for line in myreadlines(f, ","):
      dataset.append(line)

print leaders(dataset)

#for r in result:
#    print en.verb.past(r)