#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rdflib
from rdflib import Namespace, Literal, Graph, BNode, URIRef
from rdflib.namespace import RDF, DC
from pyhelpers import tools
import datetime
''''
This script is used to populate the DMS ontology
'''


g = Graph()

'''
Name Spaces used
'''
dms = Namespace("https://github.com/mesbahs/DMS/blob/master/dms.owl#")
org = Namespace("http://purl.org/orb/1.0/")
deo = Namespace("http://purl.org/spar/deo#")
doco = Namespace("http://purl.org/spar/doco#")
skos = Namespace("http://www.w3.org/2004/02/skos/core#")
disco = Namespace("http://rdf-vocabulary.ddialliance.org/discovery#")
dcterms = Namespace("http://purl.org/dc/terms/")
prov = Namespace("http://www.w3.org/ns/prov#")
ontosoft = Namespace("http://ontosoft.org/software#")
cito = Namespace("http://purl.org/spar/cito#")
mydc = Namespace("http://purl.org/dc/elements/1.1/")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")


"""
Object and data  properties
"""
wasAttributedTo = rdflib.term.URIRef(prov + 'wasAttributedTo')
publisher = rdflib.term.URIRef(mydc + 'publisher')
contains = rdflib.term.URIRef('http://www.essepuntato.it/2008/12/pattern#contains')
describesExperiment = rdflib.term.URIRef(dms + 'describesExperiment')
usesDataset = rdflib.term.URIRef(dms + 'usedDataset')
usesMethod = rdflib.term.URIRef(dms + 'usedMethod')
relatedTo = rdflib.term.URIRef(dms + 'relatedTo')
produces = rdflib.term.URIRef(dms + 'produced')
usesSoftware = rdflib.term.URIRef(dms + 'usedSoftware')
hasObjective = rdflib.term.URIRef(dms + 'hasObjective')
provvalue = rdflib.term.URIRef(prov + 'value')
isImplementationOf = rdflib.term.URIRef(dms + 'isImplementationOf')
isConfigurationOf = rdflib.term.URIRef(dms + 'isConfigurationOf')
hasConfidence = rdflib.term.URIRef(dms + 'hasConfidence')
isA = rdflib.term.URIRef(rdfs + 'isA')
wasGeneratedBy = rdflib.term.URIRef(prov + 'wasGeneratedBy')
generatedAtTime = rdflib.term.URIRef(prov + 'generatedAtTime')
datafileprop = rdflib.term.URIRef(disco + 'dataFile')
isDefinedBy = rdflib.term.URIRef(rdfs + 'isDefinedBy')

rhetoricalIdentiticationMethod = URIRef(dms + 'RIMethod' + 'Logisticregression')
g.add((rhetoricalIdentiticationMethod, RDF.type, URIRef(dms + 'RhetoricalIdentificationMethod')))


def rdf_paper_metadata_creator(g, id, title, author, publicationYear, journal):
    """
    Adding the meta data of the paper (id, title, author, publicationYear and publisher) to the graph.
    """
    paper = rdflib.term.BNode(id)
    g.add((paper, RDF.type, URIRef(dms + 'Publication')))
    experiment = rdflib.term.BNode("Experiment_"+id)
    g.add((experiment, RDF.type, URIRef(dms + 'Experiment')))

    g.add((paper, DC.title, Literal(title)))
    g.add((paper, DC.date, Literal(publicationYear)))
    g.add((paper, publisher, Literal(journal)))
    for r in author:
        g.add((paper, wasAttributedTo, Literal(r)))
    return paper, experiment, g


def rdf_paper_section(g, id, experiment, paper, section_id, sentence_id, sentences, label, NER, NER_ID, NER_Wikipedia):
    """
        Adding sections and sentences along with their  corePipelineConcept to the graph
        """
    section = rdflib.term.BNode(str(id) + '-' + str(section_id))

    g.add((section, RDF.type, URIRef(doco + 'Section')))
    g.add((paper, contains, section))
    g.add((paper, describesExperiment, experiment))

    sentence = rdflib.term.BNode(str(id) + '-' + str(section_id) + '-' + str(sentence_id))
    g.add((sentence, RDF.type, URIRef(doco + 'Sentence')))
    g.add((section, contains, sentence))
    g.add((sentence, provvalue, Literal(sentences)))

    if label == 'dataset':

        for ii, nn in enumerate(NER):

            corePipelineConcept = rdflib.term.BNode(
                str(id) + '-' + 'CPC-dataset' + '-' + str(section_id) + '-' + str(NER_ID[ii]))
            datafile = rdflib.term.BNode(str(id) + '-' + 'datafile' + '-' + str(section_id) + '-' + str(NER_ID[ii]))
            nn=nn.replace(" ","")
            nn=nn.lower()
            dataset = rdflib.term.BNode("dataset_" + nn)
            if (dataset, None, None) not in g:

                g.add((dataset, RDF.type, URIRef(disco + 'LogicalDataset')))

            g.add((datafile, RDF.type, URIRef(disco + 'DataFile')))
            g.add((datafile, provvalue, Literal(nn)))
            g.add((dataset, datafileprop, URIRef(disco + datafile)))
            g.add((corePipelineConcept, RDF.type, URIRef(dms + 'CorePipelineConcept')))
            g.add((dataset, isA, corePipelineConcept))
            g.add((corePipelineConcept, provvalue, Literal(nn)))
            g.add((corePipelineConcept, wasGeneratedBy, rhetoricalIdentiticationMethod))
            g.add((corePipelineConcept, generatedAtTime, Literal(datetime.datetime.now())))

            g.add((sentence, contains, corePipelineConcept))

            g.add((experiment, usesDataset, datafile))

            if NER_Wikipedia[ii] != "":
                wiki = URIRef(NER_Wikipedia[ii])
                g.add((corePipelineConcept, isDefinedBy, wiki))


    elif label == 'method':

        for ii, nn in enumerate(NER):
            corePipelineConcept = rdflib.term.BNode(
                str(id) + '-' + 'CPC-method' + '-' + str(section_id) + '-' +  str(NER_ID[ii]))
            methodImplementation = rdflib.term.BNode(
                str(id) + '-' + 'method' + '-' + str(section_id) + '-' +  str(NER_ID[ii]))
            method = rdflib.term.BNode( "method_" + nn)
            if (method, None, None) not in g:

                g.add((method, RDF.type, URIRef(deo + 'Methods')))

            g.add((methodImplementation, RDF.type, URIRef(dms + 'MethodImplementation')))
            g.add((methodImplementation, provvalue, Literal(nn)))
            g.add((corePipelineConcept, RDF.type, URIRef(dms + 'CorePipelineConcept')))
            g.add((experiment, usesMethod, methodImplementation))
            g.add((methodImplementation, isImplementationOf, method))
            g.add((method, isA, corePipelineConcept))
            g.add((corePipelineConcept, provvalue, Literal(nn)))
            g.add((corePipelineConcept, wasGeneratedBy, rhetoricalIdentiticationMethod))
            g.add((corePipelineConcept, generatedAtTime, Literal(datetime.datetime.now())))

            g.add((sentence, contains, corePipelineConcept))
            if NER_Wikipedia[ii] != "":
                wiki = URIRef(NER_Wikipedia[ii])
                g.add((corePipelineConcept, isDefinedBy, wiki))
    elif label == 'software':
        for ii, nn in enumerate(NER):
            corePipelineConcept = rdflib.term.BNode(

                str(id) + '-' + 'CPC-software' + '-' + str(section_id) + '-' + str(NER_ID[ii]))
            softwareImplementation = rdflib.term.BNode(
                str(id) + '-' + 'software' + '-' + str(section_id) + '-' + str(NER_ID[ii]))
            software = rdflib.term.BNode( "software_" + Literal(nn))
            g.add((corePipelineConcept, provvalue, Literal(nn)))
            if (software, None, None) not in g:

                g.add((software, RDF.type, URIRef(ontosoft + 'Software')))

            g.add((softwareImplementation, RDF.type, URIRef(dms + 'SoftwareConfiguration')))
            g.add((softwareImplementation, provvalue, Literal(nn)))
            g.add((corePipelineConcept, RDF.type, URIRef(dms + 'CorePipelineConcept')))
            g.add((software, isA, corePipelineConcept))
            g.add((softwareImplementation, isConfigurationOf, software))
            g.add((experiment, usesSoftware, softwareImplementation))
            g.add((sentence, contains, corePipelineConcept))
            g.add((corePipelineConcept, wasGeneratedBy, rhetoricalIdentiticationMethod))
            g.add((corePipelineConcept, generatedAtTime, Literal(datetime.datetime.now())))
            g.add((corePipelineConcept, provvalue, Literal(nn)))
            if NER_Wikipedia[ii] != "":
                wiki = URIRef(NER_Wikipedia[ii])
                g.add((corePipelineConcept, isDefinedBy, wiki))
    elif label == 'objective':
        for ii, nn in enumerate(NER):
            corePipelineConcept = rdflib.term.BNode(
                str(id) + '-' + 'CPC-objective' + '-' + str(section_id) + '-' +  str(NER_ID[ii]))
            objective = rdflib.term.BNode(str(id) + '-' + 'objective' + '-' + str(section_id) + '-' +  str(NER_ID[ii]))

            g.add((objective, RDF.type, URIRef(dms + 'Objective')))
            g.add((corePipelineConcept, RDF.type, URIRef(dms + 'CorePipelineConcept')))
            g.add((experiment, hasObjective, objective))

            g.add((objective, isA, corePipelineConcept))
            g.add((corePipelineConcept, wasGeneratedBy, rhetoricalIdentiticationMethod))
            g.add((corePipelineConcept, provvalue, Literal(nn)))
            g.add((corePipelineConcept, generatedAtTime, Literal(datetime.datetime.now())))

            g.add((sentence, contains, corePipelineConcept))
            if NER_Wikipedia[ii] != "":
                wiki = URIRef(NER_Wikipedia[ii])
                g.add((corePipelineConcept, isDefinedBy, wiki))
            g.add((objective, provvalue, Literal(nn)))

    elif label == 'result':
        for ii, nn in enumerate(NER):
            corePipelineConcept = rdflib.term.BNode(
                str(id) + '-' + 'CPC-result' + '-' + str(section_id) + '-' +  str(NER_ID[ii]))
            result = rdflib.term.BNode(str(id) + '-' + 'result' + '-' + str(section_id) + '-' + str(NER_ID[ii]))

            g.add((result, RDF.type, URIRef(deo + 'Results')))
            g.add((corePipelineConcept, RDF.type, URIRef(dms + 'CorePipelineConcept')))

            g.add((result, isA, corePipelineConcept))
            g.add((corePipelineConcept, wasGeneratedBy, rhetoricalIdentiticationMethod))
            g.add((corePipelineConcept, generatedAtTime, Literal(datetime.datetime.now())))
            g.add((corePipelineConcept, provvalue, Literal(nn)))

            g.add((sentence, contains, corePipelineConcept))
            if NER_Wikipedia[ii] != "":
                wiki = URIRef(NER_Wikipedia[ii])
                g.add((corePipelineConcept, isDefinedBy, wiki))
            g.add((result, provvalue, Literal(nn)))

def is_int_or_float(s):
    ''' return 1 for int, 2 for float, -1 for not a number'''
    try:
        float(s)

        return 1 if s.count('.')==0 else 2
    except ValueError:
        return -1

def create_linked_data(db,g):

    paper_names = db.rhetorical_sentences.distinct('paper_id')
    count=0
    for pub in paper_names:

            count=count+1


            print(pub)

            paperauthors = list()

            results = db.get_collection('rhetorical_sentences').find({'paper_id': pub})
            paper = db.get_collection('publications').find({'_id': pub})
            for j, p in enumerate(paper):
                for author in p['authors']:
                    paperauthors.append(author)
                paperinstance, experiment, g = rdf_paper_metadata_creator(g, pub, p['title'], paperauthors, p['year'],
                                                                          p['booktitle'])

            for i, r in enumerate(results):

                NER = []
                NER_ID = []
                NER_Wikipedia = []
                ner = db.get_collection('sentences_ner').find(
                    {'paper_id': r['paper_id'], 'rhetorical_id': r['rhetorical_id'], 'label': r['label'], "inWordnet": {'$exists': 'true', '$ne': 1}})
                for namednr in ner:
                    isint = is_int_or_float(namednr['ner'])

                    if isint == -1:
                        NER.append(namednr['ner'])
                        NER_ID.append(namednr['_id'])
                        NER_Wikipedia.append(namednr['wikipedia_link'])

                rdf_paper_section(g, r['paper_id'], experiment, paperinstance, r['chapter_num'], r['_id'],
                                  r['rhetorical'], r['label'], NER, NER_ID, NER_Wikipedia)
            #g.serialize(destination='/data/SmartPub/logs/eswc.owl', format='xml')
    g.serialize(destination='/data/SmartPub/logs/eswc.owl', format='xml')


def main():
    db = tools.connect_to_mongo()
    create_linked_data(db,g)


if __name__ == '__main__':
    main()

