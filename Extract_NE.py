"""
This script is used to extract all the NEs from the text
"""
import nltk

def preprocess_NE(filepath):

    fileUnlabelled=open(filepath,'r')
    text = fileUnlabelled.read()
    
    print('started to extract general NE from paragraphs....')
    
    sentences = nltk.sent_tokenize(text)
    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
    chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)
    entity_names = []
    for tree in chunked_sentences:

        entity_names.extend(extract_entity_names(tree))
    return entity_names

def extract_entity_names(t):
    entity_names = []

    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))

    return set(entity_names)

