import os

MONGO_URL = os.getenv(
    "MONGO_URL",
    "mongodb://mgg:070809@127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&authSource=admin&appName=mongosh+2.6.0",
)
DB_NAME = "agent_chat"
