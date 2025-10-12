from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

def push_data(data,db_name="webscrapping", collection_name = "articles"):
    if not data:
        return "no data"
    
    load_dotenv()
    mongo_password = os.getenv('mongo_password')
    username = os.getenv("evalynnjagi02_db_user")

    uri = f"mongodb+srv://{username}:{mongo_password}p@cluster1.87p81ry.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client[db_name]
    collection = db[collection_name]

    collection.insert_many(data)
# Send a ping to confirm a successful connection

    try:
        client.admin.command('ping')
        print(f"inserted successful {len(data)} document into {db} and {collection_name}")
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    
