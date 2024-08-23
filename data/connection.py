from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the username and password from environment variables
db_username = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')

# Construct the URI using the loaded environment variables
uri = f"mongodb+srv://{db_username}:{db_password}@cluster0.igoixbd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client (but do not connect immediately)
client = MongoClient(uri, server_api=ServerApi('1'))

# Test the connection (but only if this script is run directly)
if __name__ == "__main__":
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
