import pymongo
from flask import g


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        client = pymongo.MongoClient()
        db = g.db = client.get_database('metro')

    return db
