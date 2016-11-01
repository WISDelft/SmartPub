from nltk import tokenize
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest
import logging

class TextSummarize:
    def __init__(self, min_th = 0.1, max_th = 0.9):
        """
        Initialization of the summarizer
        :param min_th: words with frequency less than min_th will be ignored
        :param max_th: words with frequency higher than max_th will be ignored
        """
        self._min_th = min_th
        self._max_th = max_th
        self._stopwords = set(stopwords.words('english') + list(punctuation))

    def _compute_frequencies(self,sentences):
        """
        Compute the frequency of each word in the given sentence
        :param sentences: list of tokenized sentences
        :return: a list that shows the frequency of each word
        """

        # we could use the nltk frequency method (maybe later), however
        # it is easy to create our own using default dictionary
        freq = defaultdict(int)

        for sentence in sentences:
            for token in sentence:
                if token not in self._stopwords:
                    freq[token] += 1
        # now we need to normalize the frequency dict
        # by dividing all the values with the highest value

        max_freq = float(max(freq.values()))
        for token in freq.keys():
            freq[token] = freq[token] / max_freq
            # now we need to filter out instances based on the thresholds
            if freq[token] > self._max_th or freq[token] < self._min_th:
                freq[token] = -1
        to_be_deleted = []
        for key, value in freq.items():
            if value == 0:
                to_be_deleted.append(key)
        for k in to_be_deleted:
            del freq[k]

        return freq

    def summarize(self, text, n):
        """
        Summarize the text using the frequencies of the words
        :param text:
        :param n: number of sentences of the summary
        :return:
        """
        sentences = tokenize.sent_tokenize(text) # nltk toolbox list of sentences
        # check if the summary is longer that the input
        if n > len(sentences):
            n = int(len(sentences)/2)
            logging.warning('Watch out! argument n is larger than the sentences thus the n now is equal with'
                            'half of the sentences!')  # will print a message to the console

        token_sent = [ tokenize.word_tokenize( s.lower()) for s in sentences] # nltk list of list of words/tokens
        self._freq = self._compute_frequencies(token_sent)
        ranking = defaultdict(int)
        for i,sent in enumerate(token_sent):
            for word in sent:
                if word in self._freq:
                    ranking[i] += self._freq[word]
        sents_idx = self._ranking(ranking,n)
        return [sentences[j] for j in sents_idx]

    def _ranking(self,ranking,n):
        """
        Returns the n  highest sentences
        :param ranking:
        :param n:
        :return:
        """
        return nlargest(n,ranking, key=ranking.get)