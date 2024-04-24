from pymongo import MongoClient

class MongoDBClient:
    def __init__(self, uri="mongodb://localhost:27017/"):
        self.client = MongoClient(uri)

    def get_collection(self, db_name, collection_name):
        db = self.client[db_name]
        return db[collection_name]