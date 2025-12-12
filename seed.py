from pymongo import MongoClient
import os
from dotenv import load_dotenv

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

# --------------------------------------
# Confirm before deleting existing users
# --------------------------------------
confirm = input("This will DELETE all users and re-insert 22 entries. Continue? (yes/no): ")
if confirm.lower() != "yes":
    print("Cancelled.")
    exit()

users_col.delete_many({})
print("\nOld users deleted.\n")

# --------------------------------------
# Admins (3 total)
# --------------------------------------
admins = [
    {
        "full_name": "Javeriya Mulla",
        "username": "juhi22",
        "password": "Juhim22@",
        "role": "admin"
    },
    {
        "full_name": "Shana Shaikh",
        "username": "Shana05",
        "password": "sha0608",
        "role": "admin"
    },
    {
        "full_name": "Security Head",
        "username": "sanubi_myself",
        "password": "bhindi",
        "role": "admin"
    }
]

# --------------------------------------
# Interns (19 total)
# --------------------------------------
interns = [
    {"full_name": "Tarun Asthana", "username": "tarun", "password": "tarun@2005", "role": "intern"},
    {"full_name": "Aryan Rajendraprasad Maurya", "username": "AryanMaurya19", "password": "aryan4563", "role": "intern"},
    {"full_name": "Tapeshkumar Thakur", "username": "tapeshthakur", "password": "Tapesh@1973", "role": "intern"},
    {"full_name": "Abhinav Singh", "username": "AbhinavSingh", "password": "Abhinav17#", "role": "intern"},
    {"full_name": "Ritesh Yadav", "username": "Ritesh99", "password": "Ritesh@9598", "role": "intern"},
    {"full_name": "Omwardhan Jha", "username": "Omwardhan", "password": "infinix@123", "role": "intern"},
    {"full_name": "Aryan Goud", "username": "AryanGoud", "password": "destiny9190", "role": "intern"},
    {"full_name": "Anurag Verma", "username": "Anurag654", "password": "@Anurag9324", "role": "intern"},
    {"full_name": "Shubham Sikakul", "username": "shubham10", "password": "shubh@1005", "role": "intern"},
    {"full_name": "Purva Parab", "username": "puv@5", "password": "pp546", "role": "intern"},
    {"full_name": "Sahil Ashar", "username": "sahil21", "password": "sahil@21", "role": "intern"},
    {"full_name": "Sakshi Sarge", "username": "sakshi24", "password": "sakshi@123", "role": "intern"},
    {"full_name": "Shivam Singh", "username": "shivamsingh", "password": "Shivam@102005", "role": "intern"},
    {"full_name": "Rahul Singh Rajpurohit", "username": "Rahul_Raj01", "password": "Rahul@Raj01", "role": "intern"},
    {"full_name": "Shreevathsa Bhat", "username": "Shreevathsa", "password": "shree17", "role": "intern"},
    {"full_name": "Tanmay Ramesh Walunj", "username": "tanmay5122", "password": "tanmay5122", "role": "intern"},
    {"full_name": "Akhila Prabhukeluskar", "username": "Akhila", "password": "@khila_05", "role": "intern"},
    {"full_name": "Mayank Upadhyay", "username": "Mayanku", "password": "123456789", "role": "intern"},
    {"full_name": "Rishikesh Saroj", "username": "rishikesh", "password": "0987654321", "role": "intern"}
]

# --------------------------------------
# Insert Admins + Interns
# --------------------------------------
users_col.insert_many(admins + interns)

print("Admins and Interns inserted successfully.\n")

# --------------------------------------
# Print Summary
# --------------------------------------
print("===== ADMINS (3) =====")
for a in admins:
    print(f"{a['full_name']} → {a['username']} | {a['password']}")

print("\n===== INTERNS (19) =====")
for i in interns:
    print(f"{i['full_name']} → {i['username']} | {i['password']}")

print("\n🎉 SEEDING COMPLETE! Total users inserted:", len(admins) + len(interns))
