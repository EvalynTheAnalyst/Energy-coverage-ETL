import os
import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from urllib.parse import quote_plus #small helper to make text safer to input inside a url.
from scrape import fetch_data

def push_data(df, db_name="africa_energy1", collection_name="energy_data1"):
    """Push dataframe data to MongoDB Atlas collection"""
    try:
        # Load .env credentials
        load_dotenv()
        username = os.getenv("username")
        mongo_password = quote_plus(os.getenv("mongo_password"))

        # Build connection URI
        uri = uri = f"mongodb+srv://evalynnjagi02_db_user:osYYtCVAuG6AW9eH@cluster1.87p81ry.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client[db_name]
        collection = db[collection_name]

        print(f"\n[CONNECTING] Connected to MongoDB Atlas → Database:{db_name}, Collection: {collection_name}")


        # Convert to list of dictionaries for MongoDB
        df.columns = df.columns.map(str)
        df["year_values"] = df.apply(
        lambda row: {str(year): row[str(year)] for year in range(2000, 2023)},
        axis=1
        )
        df = df[["country","metric","unit","sector","sub_sector","source","source_link","year_values"]]
        
        data = df.to_dict(orient='records')

        # Insert into MongoDB
        if data:
            result = collection.insert_many(data)
            print(f"[SUCCESS] Inserted {len(result.inserted_ids)} records")
        else:
            print("[WARNING] No data found")

        client.admin.command('ping')
        print("[OK] MongoDB connection verified.")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to push data: {e}")
        return False
    
if __name__ == "__main__":
    push_data(fetch_data())

    

    
