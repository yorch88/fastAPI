from pymongo import MongoClient

client = MongoClient("mongodb://mongo_db:27017")
try:
    client.admin.command("ping")
    print("Connected successfully!")
except Exception as e:
    print(f"Connection failed: {e}")