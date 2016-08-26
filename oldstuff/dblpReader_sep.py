
# coding: utf-8

# In[38]:

import dblp
authors = dblp.search('alessandro bozzon')
paper23=authors.iloc[23]


# In[2]:

url=paper23.Link


# In[3]:

import urllib
import os

webFile = urllib.urlopen(url)
pdfFile = open(url.split('/')[-1], 'w')
print pdfFile
pdfFile.write(webFile.read())
webFile.close()
pdfFile.close()







# In[60]:

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
rsrcmgr = PDFResourceManager()
retstr = StringIO()
codec = 'utf-8'
laparams = LAParams()
device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
fp = file('paper_91.pdf', 'rb')
interpreter = PDFPageInterpreter(rsrcmgr, device)
password = ""
maxpages = 0
caching = True
pagenos=set()
for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
fp.close()
device.close()
str1 = retstr.getvalue()
retstr.close()


