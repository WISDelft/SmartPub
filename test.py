import sys
from lxml import etree
import gzip
import tools
import datetime
from pymongo import MongoClient
from bson.son import SON

client = MongoClient()
db = client.pub


## count conferences
pipeline=[
    {"$group": {"_id": "$booktitle", "count": {"$sum": 1}}},
    {"$sort": SON([("count", -1), ("_id", -1)])}
]
result=db.publications.aggregate(pipeline)
for r in result:
    print(r)


## count journals
pipeline=[
    {"$group": {"_id": "$journal", "count": {"$sum": 1}}},
    {"$sort": SON([("count", -1), ("_id", -1)])}
]
result=db.publications.aggregate(pipeline)
for r in result:
    print(r)