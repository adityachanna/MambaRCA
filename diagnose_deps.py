import os
from pathlib import Path
from dotenv import load_dotenv
import asyncio
from pymongo import MongoClient
import certifi

# Load .env
env_path = Path(__file__).parent / "backend" / ".env"
load_dotenv(env_path)

async def check_mongo():
    uri = os.getenv("uri") or os.getenv("MONGODB_URI")
    print(f"Connecting to MongoDB with URI: {uri[:20]}...")
    client = MongoClient(
        uri,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000
    )
    try:
        client.admin.command('ping')
        print("MongoDB: Connected successfully!")
    except Exception as e:
        print(f"MongoDB: Failed to connect - {e}")

if __name__ == "__main__":
    asyncio.run(check_mongo())
