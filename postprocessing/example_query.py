"""
JUST EXAMPLE:This script will be used to query some senetences using a keword.
"""
from elasticsearch import Elasticsearch

###############################

es = Elasticsearch(
    [{'host': 'localhost', 'port': 9200}]
)
es.cluster.health(wait_for_status='yellow')
keyword='clueweb trec'

query = {"query":
    {"match": {
        "content.chapter.sentpositive": {
            "query": keyword ,
            "operator": "and"
        }
    }
    }
}

res = es.search(index="twosent", doc_type="twosentnorules",
                body=query, size=10)
print(len(res['hits']['hits']))

docs = []
for doc in res['hits']['hits']:
    print(doc["_source"]["content.chapter.sentpositive"])


