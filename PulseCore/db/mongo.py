from pymongo import MongoClient
from config import MONGO_URL, DB_NAME

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

users = db.users
states = db.states
messages = db.messages
stats = db.stats
tasks = db.tasks
