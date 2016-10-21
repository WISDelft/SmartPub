#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nltk
import urllib2
import requests
from BeautifulSoup import BeautifulSoup as Soup
import re
import sys

reload(sys)
sys.setdefaultencoding('utf8')


#get the full text of the pdf
def grobid_text(url):

    f = urllib2.urlopen(url)
    params = {'input': f.read()}
    r = requests.post("http://localhost:8080/processFulltextDocument", files=params)

    return r


#get the section by name
def get_section(url,section_name):

    r=grobid_text(url)
    soup = Soup(r.content)
    paragraphs=[]
    paragraph=[]
    divs = soup.findAll('div')
    for tag in divs:
        tdTags = tag.find('head')
        if tdTags:
            for tags in tdTags:

                if section_name in tags:
                    paragraphs = tag.find('p')
    paragraphs=re.sub('<[^>]+>', '', str(paragraphs))
    print "laaaaaaaa"
    return  paragraphs



#2 gram analysis
def get_2grams(txt,section_name):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = (sent_detector.tokenize(txt.strip()))

    for i in range(0, len(sentences)):
        tokens = nltk.word_tokenize(sentences[i])
        tagged_sent = nltk.pos_tag(tokens)

        for (w1, t1), (w2, t2) in nltk.bigrams(tagged_sent):
            if t1.startswith("PRP") and t2.startswith("VB") or t2.startswith("MD"):

                gram=w1+" "+w2
                print gram
                with open(section_name+".txt", "a") as myfile:
                    myfile.write(gram+",")


def get_3grams(txt,section_name):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = (sent_detector.tokenize(txt.strip()))

    for i in range(0, len(sentences)):
        tokens = nltk.word_tokenize(sentences[i])
        tagged_sent = nltk.pos_tag(tokens)

        for (w1, t1), (w2, t2),(w3,t3) in nltk.trigrams(tagged_sent):
            if t1.startswith("PRP") and t3.startswith("VB"):
                gram = w1 + " " + w2 + " " + w3
                print gram
                with open(section_name + ".txt", "a") as myfile:
                    myfile.write(gram + ",")


def get_unigrams(txt):
    for i in range(0, len(txt)):
        tokens = nltk.word_tokenize(txt[i])
        tagged_sent = nltk.pos_tag(tokens)
        propernoun = [word for word, pos in tagged_sent if pos == 'NNP']
        print propernoun


def get_fig_table(url):
    text=grobid_text(url)
    text=text.content



    soup = Soup(text)
    paragraphs = soup.findAll('p')
    paragraphs = paragraphs[1:]
    paragraphs = re.sub('<[^>]+>', '', str(paragraphs))
    paragraph = paragraphs.decode("utf8")

    fig_tab= []

    indexes =['figure', 'Figure', 'table', 'Table', 'fig.', 'Fig.']
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = (sent_detector.tokenize(paragraph.strip()))
    print len(sentences)

    for i, j in enumerate(sentences):
        if any(word in j for word in indexes):
            try:

                fig_tab.append(sentences[i - 1])
            except:
                print "list indext out of range"
                pass
            fig_tab.append(j)
            try:

             fig_tab.append(sentences[i + 1])
            except:
                print "list indext out of range"
                pass

    fig_tab = ".".join(fig_tab)
    return fig_tab


def get_link_index(paperUrls):
    indexes=[]
    for pp in paperUrls:

        for p in pp:
            print p[0]
            st=p[1]
            st=st[:-1]
            if st == 'n="1">':
                indexes.append(' 1 ')
            elif st == 'n="2">':
                indexes.append(' 2 ')
            elif st == 'n="3">':
                indexes.append(' 3 ')
            elif st == 'n="4">':
                indexes.append(' 4 ')
            elif st == 'n="5">':
                indexes.append(' 5 ')
            elif st == 'n="6">':
                indexes.append(' 6 ')
            elif st == 'n="7">':
                indexes.append(' 7 ')
            elif st == 'n="8">':
                indexes.append(' 8 ')
            elif st == 'n="9">':
                indexes.append(' 9 ')

            elif st.isdigit():

                indexes.append(' '+st+' ')
            else:
                indexes.append(p[0])

    return indexes



def get_Links(url):
    text=grobid_text(url)
    text=text.content

    #text=text.decode("utf8")

    paperUrls = []

    urls = re.findall(
        r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:".,<>?«»“”‘’]))',
        text)
    for uri in urls:
        if uri[0]!="http://www.tei-c.org/ns/1.0" and uri[0]!="http://www.w3.org/2001/XMLSchema-instance" and uri[0]!="http://www.w3.org/1999/xlink" and uri[0]!="https://github.com/kermitt2/grobid":
            try:
                 index=re.findall(r"((\S+\s+|)"+uri[0]+")", text)
                 paperUrls.append(index)
            except:
                 pass
    print paperUrls
    soup = Soup(text)
    paragraphs = soup.findAll('p')
    paragraphs = paragraphs[1:]
    paragraphs=re.sub('<[^>]+>', '', str(paragraphs))

    footnotes = []
    paragraph = paragraphs.decode("utf8")
    indexes = get_link_index(paperUrls)

    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = (sent_detector.tokenize(paragraph.strip()))

    for i, j in enumerate(sentences):
        if any(word in j for word in indexes):
            try:

                footnotes.append(sentences[i - 1])
            except:
                print "list indext out of range"
                pass
            footnotes.append(j)
            try:

                footnotes.append(sentences[i + 1])
            except:
                print "list indext out of range"
                pass


    footnotes=".".join(footnotes)
    return footnotes




#get_section("https://arxiv.org/pdf/1607.03274v1.pdf","INTRODUCTION")

