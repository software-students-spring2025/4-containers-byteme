from pymongo import MongoClient
import os

print(os.getenv("MONGO_HOST"))
print(os.getenv("MONGO_PORT"))
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = int(os.getenv("MONGO_PORT"))
MONGO_DB = os.getenv("MONGO_DB")

client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
db = client[MONGO_DB]