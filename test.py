from bson.son import SON
from pymongo import MongoClient

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