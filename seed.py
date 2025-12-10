from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import random

# -----------------------------
# CONFIG: CHANGE IF NEEDED
# -----------------------------
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "attendance_system"

WORK_TYPES = ["Office", "Work From Home", "Field Work", "Other"]

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

users_col = db["users"]
attendance_col = db["attendance"]

print("🌱 Starting seed script...")

# -----------------------------
# Fetch interns only
# -----------------------------
interns = list(users_col.find({"role": "intern"}))

if not interns:
    print("❌ No interns found. Please run app.py once so default users get inserted.")
    exit()


# -----------------------------
# Generate 10 days of data
# -----------------------------
today = datetime.now()
days_to_insert = 10

for i in range(days_to_insert):
    date = (today - timedelta(days=i)).strftime("%Y-%m-%d")

    for intern in interns:
        user_id = intern["_id"]
        work_type = random.choice(WORK_TYPES)

        # Random login & logout times
        login_hour = random.randint(9, 11)    # between 9 AM and 11 AM
        logout_hour = random.randint(17, 19)  # between 5 PM and 7 PM

        login_time = f"{login_hour}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"
        logout_time = f"{logout_hour}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"

        # Insert the attendance document
        attendance_col.insert_one({
            "user_id": user_id,
            "date": date,
            "work_type": work_type,
            "login_time": login_time,
            "logout_time": logout_time,
            "status": "Present"
        })

    print(f"✔ Inserted attendance for {date}")

print("\n🎉 Done! Seed data for 10 days created successfully.")
