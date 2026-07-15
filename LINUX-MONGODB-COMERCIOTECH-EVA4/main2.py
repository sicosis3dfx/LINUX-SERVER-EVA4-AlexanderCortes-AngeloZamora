from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

load_dotenv()

user = quote_plus(os.getenv("MONGO_USER"))
password = quote_plus(os.getenv("MONGO_PASSWORD"))
host = os.getenv("MONGO_HOST", "ec2-54-82-115-133.compute-1.amazonaws.com")
port = os.getenv("MONGO_PORT", "27017")
db_name = os.getenv("MONGO_DB", "comerciotech")
auth_source = os.getenv("MONGO_AUTH_SOURCE", "comerciotech")

uri = f"mongodb://{user}:{password}@{host}:{port}/{db_name}?authSource={auth_source}"

client = MongoClient(uri)
db = client[db_name]

client.admin.command("ping")

print("Conexión exitosa a MongoDB")