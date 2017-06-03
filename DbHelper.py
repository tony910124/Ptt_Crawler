from pymongo import MongoClient
import Config

DB = Config.DB
COLLECTION = Config.COLLECTION


def connectMongo():
	uri = "mongodb://localhost"
	client = MongoClient(uri)
	return client[DB]

def connectMongoCollection(collection = COLLECTION):
	uri = "mongodb://localhost"
	client = MongoClient(uri)
	db = client[DB]
	return db[collection]
