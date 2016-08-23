from sickle import Sickle
import xmltodict
import json
import html


sickle = Sickle('http://export.arxiv.org/oai2')
records = sickle.ListRecords(metadataPrefix='oai_dc', set='cs', ignore_deleted=True)


namespaces = { 'http://www.openarchives.org/OAI/2.0/': 'oai',
    'http://www.openarchives.org/OAI/2.0/oai_dc/': 'oiadc',
    'http://www.w3.org/2001/XMLSchema-instance': None,
    'http://purl.org/dc/elements/1.1/' : 'purl'
}

records = sickle.ListRecords(metadataPrefix='oai_dc', set='cs', ignore_deleted=True)


for r in records:
    # convert OAI XML response to dictionary
    d = xmltodict.parse(r.raw, xml_attribs=True, process_namespaces=True, namespaces=namespaces)
    # strip newlines from asbtracts
    try:
        d['oai:record']['oai:metadata']['oiadc:dc']['purl:description'][0]=d['oai:record']['oai:metadata']['oiadc:dc']['purl:description'][0].replace('\n',' ')
    except Exception:
        pass
    # convert dictionary to json
    print(json.dumps(d, indent=4))