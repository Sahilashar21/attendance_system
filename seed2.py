from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()

# -----------------------------
# Mongo Connection (Local/Atlas)
# -----------------------------
USE_ATLAS = os.getenv("USE_ATLAS", "false").lower() == "true"

if USE_ATLAS:
    atlas_user = os.getenv("MONGO_ATLAS_USER")
    atlas_pass = os.getenv("MONGO_ATLAS_PASS")
    atlas_cluster = os.getenv("MONGO_ATLAS_CLUSTER")
    MONGO_URI = f"mongodb+srv://{atlas_user}:{atlas_pass}@{atlas_cluster}/?retryWrites=true&w=majority"
else:
    MONGO_URI = "mongodb://localhost:27017/"

client = MongoClient(MONGO_URI)
db = client["attendance_system"]
users_col = db["users"]
db.users.insert_one({
    "username": "Ravik14",
    "password": "ravindravm14",
    "full_name": "Ravindra Kamtam",
    "role": "admin"
})
print("Admin created")
