from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")
db = client["attendance_system"]
db.users.insert_one({
    "username": "admin",
    "password": "admin123",
    "full_name": "Admin",
    "role": "admin"
})
print("Admin created")
