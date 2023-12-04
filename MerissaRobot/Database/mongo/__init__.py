from motor.motor_asyncio import AsyncIOMotorClient as MongoCli
from pymongo import MongoClient

from MerissaRobot import MONGO_DB_URI

MONGO_DB = "mongodb+srv://merissa:robot@cluster0.4yifs.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGO_DB_URI)
leveldb = MongoClient(MONGO_DB)

mongo = MongoCli(MONGO_DB)
mongodb = mongo.MerissaRobot
db = client["MerissaRobot"]
