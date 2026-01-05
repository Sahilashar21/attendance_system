# # # from flask import (
# # #     Flask, render_template, request,
# # #     redirect, url_for, session, send_file, flash
# # # )
# # # from datetime import datetime
# # # from openpyxl import Workbook, load_workbook
# # # import os

# # # from zipfile import BadZipFile  # add this at the top with other imports

# # # app = Flask(__name__)
# # # app.secret_key = "change-this-secret-key"

# # # ATTENDANCE_FILE = "attendance.xlsx"

# # # # ---- Test users ----
# # # USERS = {
# # #     "sahil": {"password": "sahil123", "role": "intern", "full_name": "Sahil"},
# # #     "test": {"password": "test123", "role": "intern", "full_name": "Test Intern"},
# # #     "admin": {"password": "admin123", "role": "admin", "full_name": "Admin"},
# # # }

# # # # Dropdown list for work types
# # # WORK_TYPES = ["Office", "Work from home", "Field work", "Other"]


# # # # ---------------- Excel Helpers ----------------

# # # def get_or_create_workbook():
# # #     if os.path.exists(ATTENDANCE_FILE):
# # #         try:
# # #             wb = load_workbook(ATTENDANCE_FILE)
# # #             return wb
# # #         except BadZipFile:
# # #             # If file is corrupt or not a real xlsx, recreate it
# # #             os.remove(ATTENDANCE_FILE)

# # #     # Create new workbook
# # #     wb = Workbook()
# # #     default_sheet = wb.active
# # #     wb.remove(default_sheet)
# # #     wb.save(ATTENDANCE_FILE)
# # #     return wb



# # # def get_today_sheet(wb):
# # #     sheet_name = datetime.now().strftime("%d-%m-%Y")
# # #     if sheet_name in wb.sheetnames:
# # #         return wb[sheet_name]
# # #     else:
# # #         ws = wb.create_sheet(title=sheet_name)
# # #         ws.append(["Student name", "present/absent", "Work type", "login time", "logout time"])
# # #         return ws


# # # def find_or_create_row(ws, student_name):
# # #     for row in range(2, ws.max_row + 1):
# # #         if ws[f"A{row}"].value == student_name:
# # #             return row

# # #     new_row = ws.max_row + 1
# # #     ws[f"A{new_row}"].value = student_name
# # #     return new_row


# # # def mark_login(username, work_type):
# # #     wb = get_or_create_workbook()
# # #     ws = get_today_sheet(wb)
# # #     row = find_or_create_row(ws, username)
# # #     now_str = datetime.now().strftime("%H:%M:%S")

# # #     ws[f"B{row}"] = "Present"
# # #     ws[f"C{row}"] = work_type
# # #     ws[f"D{row}"] = now_str

# # #     wb.save(ATTENDANCE_FILE)


# # # def mark_logout(username):
# # #     wb = get_or_create_workbook()
# # #     ws = get_today_sheet(wb)
# # #     row = find_or_create_row(ws, username)
# # #     now_str = datetime.now().strftime("%H:%M:%S")

# # #     ws[f"E{row}"] = now_str
# # #     wb.save(ATTENDANCE_FILE)


# # # def get_today_status(username):
# # #     wb = get_or_create_workbook()
# # #     ws = get_today_sheet(wb)

# # #     for row in range(2, ws.max_row + 1):
# # #         if ws[f"A{row}"].value == username:
# # #             return {
# # #                 "present": ws[f"B{row}"].value,
# # #                 "work_type": ws[f"C{row}"].value,
# # #                 "login_time": ws[f"D{row}"].value,
# # #                 "logout_time": ws[f"E{row}"].value
# # #             }

# # #     return {
# # #         "present": None,
# # #         "work_type": None,
# # #         "login_time": None,
# # #         "logout_time": None
# # #     }


# # # def read_sheet_for_date(date_str):
# # #     try:
# # #         dt = datetime.strptime(date_str, "%Y-%m-%d")
# # #     except ValueError:
# # #         return None, []

# # #     sheet_name = dt.strftime("%d-%m-%Y")
# # #     wb = get_or_create_workbook()

# # #     if sheet_name not in wb.sheetnames:
# # #         return sheet_name, []

# # #     ws = wb[sheet_name]
# # #     data = []

# # #     for row in range(2, ws.max_row + 1):
# # #         student = ws[f"A{row}"].value
# # #         if not student:
# # #             continue
# # #         data.append({
# # #             "student": student,
# # #             "status": ws[f"B{row}"].value,
# # #             "work_type": ws[f"C{row}"].value,
# # #             "login_time": ws[f"D{row}"].value,
# # #             "logout_time": ws[f"E{row}"].value,
# # #         })

# # #     return sheet_name, data


# # # # ---------------- Auth Helpers ----------------

# # # def login_required(role=None):
# # #     def wrapper(fn):
# # #         from functools import wraps

# # #         @wraps(fn)
# # #         def decorated(*args, **kwargs):
# # #             if "user" not in session:
# # #                 return redirect(url_for("login"))
# # #             if role and USERS[session["user"]]["role"] != role:
# # #                 return redirect(url_for("login"))
# # #             return fn(*args, **kwargs)

# # #         return decorated

# # #     return wrapper


# # # # ---------------- Routes ----------------

# # # @app.route("/")
# # # def index():
# # #     if "user" in session:
# # #         role = USERS[session["user"]]["role"]
# # #         return redirect(url_for("admin_dashboard" if role == "admin" else "intern_dashboard"))
# # #     return redirect(url_for("login"))


# # # @app.route("/login", methods=["GET", "POST"])
# # # def login():
# # #     if request.method == "POST":
# # #         username = request.form["username"].strip()
# # #         password = request.form["password"].strip()

# # #         user = USERS.get(username)
# # #         if user and user["password"] == password:
# # #             session["user"] = username
# # #             flash("Login successful!", "success")

# # #             if user["role"] == "admin":
# # #                 return redirect(url_for("admin_dashboard"))
# # #             else:
# # #                 return redirect(url_for("intern_dashboard"))

# # #         flash("Invalid credentials", "danger")

# # #     return render_template("login.html")


# # # @app.route("/logout")
# # # def logout():
# # #     session.clear()
# # #     flash("Logged out.", "info")
# # #     return redirect(url_for("login"))


# # # @app.route("/intern")
# # # @login_required(role="intern")
# # # def intern_dashboard():
# # #     username = session["user"]
# # #     user = USERS[username]
# # #     status = get_today_status(username)

# # #     return render_template(
# # #         "intern_dashboard.html",
# # #         name=user["full_name"],
# # #         username=username,
# # #         work_types=WORK_TYPES,
# # #         status=status,
# # #     )


# # # @app.route("/intern/mark-login", methods=["POST"])
# # # @login_required(role="intern")
# # # def intern_mark_login():
# # #     work_type = request.form.get("work_type")
# # #     if not work_type:
# # #         flash("Select work type.", "warning")
# # #     else:
# # #         mark_login(session["user"], work_type)
# # #         flash("Login attendance marked!", "success")

# # #     return redirect(url_for("intern_dashboard"))


# # # @app.route("/intern/mark-logout", methods=["POST"])
# # # @login_required(role="intern")
# # # def intern_mark_logout():
# # #     mark_logout(session["user"])
# # #     flash("Logout time marked!", "success")
# # #     return redirect(url_for("intern_dashboard"))


# # # @app.route("/admin", methods=["GET", "POST"])
# # # @login_required(role="admin")
# # # def admin_dashboard():
# # #     date_str = request.form.get("date") if request.method == "POST" else datetime.now().strftime("%Y-%m-%d")
# # #     sheet_name, rows = read_sheet_for_date(date_str)

# # #     return render_template(
# # #         "admin_dashboard.html",
# # #         date_str=date_str,
# # #         sheet_name=sheet_name,
# # #         rows=rows,
# # #     )


# # # @app.route("/admin/download")
# # # @login_required(role="admin")
# # # def download_excel():
# # #     return send_file(ATTENDANCE_FILE, as_attachment=True)


# # # # ---------------------------------------
# # # if __name__ == "__main__":
# # #     app.run(debug=True)



# # from flask import (
# #     Flask, render_template, request,
# #     redirect, url_for, session, flash
# # )
# # from datetime import datetime
# # from bson.objectid import ObjectId
# # from pymongo import MongoClient
# # import os
# # from dotenv import load_dotenv

# # load_dotenv()

# # app = Flask(__name__)
# # app.secret_key = "super-secret-key"


# # # -----------------------------------------
# # # MONGO CONNECTION (LOCAL + ATLAS READY)
# # # -----------------------------------------

# # USE_ATLAS = os.getenv("USE_ATLAS", "false").lower() == "true"

# # if USE_ATLAS:
# #     atlas_user = os.getenv("MONGO_ATLAS_USER")
# #     atlas_pass = os.getenv("MONGO_ATLAS_PASS")
# #     atlas_cluster = os.getenv("MONGO_ATLAS_CLUSTER")

# #     MONGO_URI = f"mongodb+srv://{atlas_user}:{atlas_pass}@{atlas_cluster}/?retryWrites=true&w=majority"
# # else:
# #     MONGO_URI = "mongodb://localhost:27017/"  # Local DB


# # client = MongoClient(MONGO_URI)
# # db = client["attendance_system"]

# # users_col = db["users"]
# # attendance_col = db["attendance"]


# # # -----------------------------------------
# # # AUTH DECORATOR
# # # -----------------------------------------
# # def login_required(role=None):
# #     def decorator(fn):
# #         from functools import wraps

# #         @wraps(fn)
# #         def wrapper(*args, **kwargs):
# #             if "user_id" not in session:
# #                 return redirect(url_for("login"))

# #             user = users_col.find_one({"_id": ObjectId(session["user_id"])})

# #             if role and user["role"] != role:
# #                 return redirect(url_for("login"))

# #             return fn(*args, **kwargs)

# #         return wrapper
# #     return decorator


# # def get_today_record(user_id):
# #     today = datetime.now().strftime("%Y-%m-%d")
# #     return attendance_col.find_one({"user_id": user_id, "date": today})


# # # -----------------------------------------
# # # ROUTES
# # # -----------------------------------------

# # @app.route("/")
# # def home():
# #     if "user_id" not in session:
# #         return redirect(url_for("login"))

# #     user = users_col.find_one({"_id": ObjectId(session["user_id"])})

# #     if user["role"] == "admin":
# #         return redirect(url_for("admin_dashboard"))
# #     else:
# #         return redirect(url_for("intern_dashboard"))


# # # -----------------------------------------
# # # LOGIN
# # # -----------------------------------------

# # @app.route("/login", methods=["GET", "POST"])
# # def login():
# #     if request.method == "POST":
# #         username = request.form["username"].strip()
# #         password = request.form["password"].strip()

# #         user = users_col.find_one({"username": username, "password": password})

# #         if user:
# #             session["user_id"] = str(user["_id"])
# #             flash("Login successful!", "success")

# #             if user["role"] == "admin":
# #                 return redirect(url_for("admin_dashboard"))
# #             else:
# #                 return redirect(url_for("intern_dashboard"))

# #         flash("Invalid username or password", "danger")

# #     return render_template("login.html")


# # @app.route("/logout")
# # def logout():
# #     session.clear()
# #     return redirect(url_for("login"))


# # # -----------------------------------------
# # # INTERN DASHBOARD
# # # -----------------------------------------

# # WORK_TYPES = ["Office", "Work From Home", "Field Work", "Other"]


# # @app.route("/intern")
# # @login_required(role="intern")
# # def intern_dashboard():
# #     user = users_col.find_one({"_id": ObjectId(session["user_id"])})

# #     record = get_today_record(user["_id"])

# #     return render_template(
# #         "intern_dashboard.html",
# #         user=user,
# #         record=record,
# #         work_types=WORK_TYPES
# #     )


# # # MARK LOGIN
# # @app.route("/intern/mark-login", methods=["POST"])
# # @login_required(role="intern")
# # def mark_login():
# #     user_id = ObjectId(session["user_id"])
# #     work_type = request.form["work_type"]
# #     today = datetime.now().strftime("%Y-%m-%d")

# #     if get_today_record(user_id):
# #         flash("Login already marked today!", "warning")
# #         return redirect(url_for("intern_dashboard"))

# #     attendance_col.insert_one({
# #         "user_id": user_id,
# #         "date": today,
# #         "work_type": work_type,
# #         "login_time": datetime.now().strftime("%H:%M:%S"),
# #         "logout_time": None,
# #         "status": "Present",
# #         "hours_worked": None
# #     })

# #     flash("Login marked!", "success")
# #     return redirect(url_for("intern_dashboard"))


# # # MARK LOGOUT (Calculate hours worked)
# # @app.route("/intern/mark-logout", methods=["POST"])
# # @login_required(role="intern")
# # def mark_logout():
# #     user_id = ObjectId(session["user_id"])
# #     today = datetime.now().strftime("%Y-%m-%d")

# #     record = attendance_col.find_one({"user_id": user_id, "date": today})

# #     if not record:
# #         flash("Please mark login first!", "danger")
# #         return redirect(url_for("intern_dashboard"))

# #     login_time_str = record.get("login_time")
# #     logout_time_str = datetime.now().strftime("%H:%M:%S")

# #     # Convert times
# #     login_dt = datetime.strptime(login_time_str, "%H:%M:%S")
# #     logout_dt = datetime.strptime(logout_time_str, "%H:%M:%S")

# #     diff = logout_dt - login_dt
# #     total_seconds = diff.total_seconds()

# #     hours = int(total_seconds // 3600)
# #     minutes = int((total_seconds % 3600) // 60)

# #     hours_worked = f"{hours}h {minutes}m"

# #     attendance_col.update_one(
# #         {"user_id": user_id, "date": today},
# #         {"$set": {
# #             "logout_time": logout_time_str,
# #             "hours_worked": hours_worked
# #         }}
# #     )

# #     flash("Logout marked! Hours worked calculated.", "success")
# #     return redirect(url_for("intern_dashboard"))


# # # -----------------------------------------
# # # ADMIN DASHBOARD
# # # -----------------------------------------

# # @app.route("/admin", methods=["GET", "POST"])
# # @login_required(role="admin")
# # def admin_dashboard():
# #     date = request.form.get("date") or datetime.now().strftime("%Y-%m-%d")

# #     records = list(attendance_col.find({"date": date}))

# #     # Attach user info
# #     for r in records:
# #         u = users_col.find_one({"_id": r["user_id"]})
# #         r["name"] = u["full_name"]
# #         r["username"] = u["username"]

# #     return render_template(
# #         "admin_dashboard.html",
# #         records=records,
# #         date=date
# #     )


# # # -----------------------------------------
# # # ADD INTERN
# # # -----------------------------------------

# # @app.route("/admin/add-intern", methods=["GET", "POST"])
# # @login_required(role="admin")
# # def add_intern():
# #     if request.method == "POST":
# #         full_name = request.form["full_name"].strip()
# #         username = request.form["username"].strip()
# #         password = request.form["password"].strip()

# #         existing = users_col.find_one({"username": username})
# #         if existing:
# #             flash("Username already exists!", "danger")
# #             return redirect(url_for("add_intern"))

# #         users_col.insert_one({
# #             "full_name": full_name,
# #             "username": username,
# #             "password": password,
# #             "role": "intern"
# #         })

# #         flash("Intern added successfully!", "success")
# #         return redirect(url_for("admin_dashboard"))

# #     return render_template("add_intern.html")


# # # -----------------------------------------
# # # START APP
# # # -----------------------------------------

# # if __name__ == "__main__":
# #     app.run(debug=True)



# # from flask import (
# #     Flask, render_template, request,
# #     redirect, url_for, session, flash
# # )
# # from datetime import datetime
# # from bson.objectid import ObjectId
# # from pymongo import MongoClient
# # import os
# # from dotenv import load_dotenv

# # load_dotenv()

# # app = Flask(__name__)
# # app.secret_key = "super-secret-key"

# # # -----------------------------------------
# # # MONGO CONNECTION (LOCAL + ATLAS READY)
# # # -----------------------------------------

# # USE_ATLAS = os.getenv("USE_ATLAS", "false").lower() == "true"

# # if USE_ATLAS:
# #     atlas_user = os.getenv("MONGO_ATLAS_USER")
# #     atlas_pass = os.getenv("MONGO_ATLAS_PASS")
# #     atlas_cluster = os.getenv("MONGO_ATLAS_CLUSTER")
# #     MONGO_URI = f"mongodb+srv://{atlas_user}:{atlas_pass}@{atlas_cluster}/?retryWrites=true&w=majority"
# # else:
# #     MONGO_URI = "mongodb://localhost:27017/"

# # client = MongoClient(MONGO_URI)
# # db = client["attendance_system"]

# # users_col = db["users"]
# # attendance_col = db["attendance"]

# # # -----------------------------------------
# # # AUTO-CREATE ADMIN USER IF MISSING
# # # -----------------------------------------
# # if users_col.count_documents({}) == 0:
# #     users_col.insert_one({
# #         "username": "admin",
# #         "password": "admin123",
# #         "full_name": "Admin",
# #         "role": "admin"
# #     })

# # # -----------------------------------------
# # # AUTH DECORATOR
# # # -----------------------------------------
# # def login_required(role=None):
# #     def decorator(fn):
# #         from functools import wraps

# #         @wraps(fn)
# #         def wrapper(*args, **kwargs):
# #             if "user_id" not in session:
# #                 return redirect(url_for("login"))

# #             user = users_col.find_one({"_id": ObjectId(session["user_id"])})

# #             # Prevent NoneType errors
# #             if not user:
# #                 session.clear()
# #                 return redirect(url_for("login"))

# #             if role and user["role"] != role:
# #                 return redirect(url_for("login"))

# #             return fn(*args, **kwargs)
# #         return wrapper
# #     return decorator

# # # -----------------------------------------
# # # UTILS
# # # -----------------------------------------
# # def get_today_record(user_id):
# #     today = datetime.now().strftime("%Y-%m-%d")
# #     return attendance_col.find_one({"user_id": user_id, "date": today})

# # # -----------------------------------------
# # # ROUTES
# # # -----------------------------------------

# # @app.route("/")
# # def home():
# #     if "user_id" not in session:
# #         return redirect(url_for("login"))

# #     user = users_col.find_one({"_id": ObjectId(session["user_id"])})

# #     return redirect(url_for("admin_dashboard" if user["role"] == "admin" else "intern_dashboard"))

# # # -----------------------------------------
# # # LOGIN
# # # -----------------------------------------

# # @app.route("/login", methods=["GET", "POST"])
# # def login():
# #     if request.method == "POST":
# #         username = request.form["username"].strip()
# #         password = request.form["password"].strip()

# #         user = users_col.find_one({"username": username, "password": password})

# #         if user:
# #             session["user_id"] = str(user["_id"])
# #             flash("Login successful!", "success")
# #             return redirect("/")

# #         flash("Invalid username or password", "danger")

# #     return render_template("login.html")

# # @app.route("/logout")
# # def logout():
# #     session.clear()
# #     return redirect(url_for("login"))

# # # -----------------------------------------
# # # INTERN DASHBOARD
# # # -----------------------------------------

# # WORK_TYPES = ["Office", "Work From Home"]

# # @app.route("/intern")
# # @login_required(role="intern")
# # def intern_dashboard():
# #     user = users_col.find_one({"_id": ObjectId(session["user_id"])})
# #     record = get_today_record(user["_id"])

# #     return render_template("intern_dashboard.html",
# #                            user=user,
# #                            record=record,
# #                            work_types=WORK_TYPES)

# # # Intern Login
# # @app.route("/intern/mark-login", methods=["POST"])
# # @login_required(role="intern")
# # def mark_login():
# #     user_id = ObjectId(session["user_id"])
# #     work_type = request.form["work_type"]
# #     today = datetime.now().strftime("%Y-%m-%d")

# #     if get_today_record(user_id):
# #         flash("Login already marked today!", "warning")
# #         return redirect(url_for("intern_dashboard"))

# #     attendance_col.insert_one({
# #         "user_id": user_id,
# #         "date": today,
# #         "work_type": work_type,
# #         "login_time": datetime.now().strftime("%H:%M:%S"),
# #         "logout_time": None,
# #         "status": "Present",
# #         "hours_worked": None
# #     })

# #     flash("Login marked!", "success")
# #     return redirect(url_for("intern_dashboard"))

# # # Intern Logout
# # @app.route("/intern/mark-logout", methods=["POST"])
# # @login_required(role="intern")
# # def mark_logout():
# #     user_id = ObjectId(session["user_id"])
# #     today = datetime.now().strftime("%Y-%m-%d")

# #     record = attendance_col.find_one({"user_id": user_id, "date": today})

# #     if not record:
# #         flash("Please mark login first!", "danger")
# #         return redirect(url_for("intern_dashboard"))

# #     login_str = record["login_time"]
# #     logout_str = datetime.now().strftime("%H:%M:%S")

# #     login_dt = datetime.strptime(login_str, "%H:%M:%S")
# #     logout_dt = datetime.strptime(logout_str, "%H:%M:%S")

# #     diff = logout_dt - login_dt
# #     hours = diff.seconds // 3600
# #     minutes = (diff.seconds % 3600) // 60

# #     attendance_col.update_one(
# #         {"_id": record["_id"]},
# #         {"$set": {"logout_time": logout_str, "hours_worked": f"{hours}h {minutes}m"}}
# #     )

# #     flash("Logout marked!", "success")
# #     return redirect(url_for("intern_dashboard"))

# # # -----------------------------------------
# # # ADMIN DASHBOARD
# # # -----------------------------------------

# # @app.route("/admin", methods=["GET", "POST"])
# # @login_required(role="admin")
# # def admin_dashboard():
# #     date = request.form.get("date") or datetime.now().strftime("%Y-%m-%d")
# #     records = list(attendance_col.find({"date": date}))

# #     for r in records:
# #         u = users_col.find_one({"_id": r["user_id"]})
# #         r["name"] = u["full_name"]
# #         r["username"] = u["username"]

# #     return render_template("admin_dashboard.html", records=records, date=date)

# # # -----------------------------------------
# # # ADD INTERN
# # # -----------------------------------------

# # @app.route("/admin/add-intern", methods=["GET", "POST"])
# # @login_required(role="admin")
# # def add_intern():
# #     if request.method == "POST":
# #         full_name = request.form["full_name"].strip()
# #         username = request.form["username"].strip()
# #         password = request.form["password"].strip()

# #         if users_col.find_one({"username": username}):
# #             flash("Username already exists!", "danger")
# #             return redirect(url_for("add_intern"))

# #         users_col.insert_one({
# #             "full_name": full_name,
# #             "username": username,
# #             "password": password,
# #             "role": "intern"
# #         })

# #         flash("Intern added successfully!", "success")
# #         return redirect(url_for("admin_dashboard"))

# #     return render_template("add_intern.html")

# # # -----------------------------------------
# # # START APP
# # # -----------------------------------------

# # if __name__ == "__main__":
# #     app.run(host="0.0.0.0", port=5000)







# from flask import (
#     Flask, render_template, request,
#     redirect, url_for, session, flash
# )
# from datetime import datetime
# from bson.objectid import ObjectId
# from pymongo import MongoClient
# import os
# from dotenv import load_dotenv
# import pytz   # <-- IST timezone support

# load_dotenv()

# app = Flask(__name__)
# app.secret_key = "super-secret-key"

# # -----------------------------------------
# # TIMEZONE (IST)
# # -----------------------------------------
# IST = pytz.timezone("Asia/Kolkata")

# def now_ist():
#     """Return datetime in IST timezone"""
#     return datetime.now(IST)


# # -----------------------------------------
# # MONGO CONNECTION (LOCAL + ATLAS READY)
# # -----------------------------------------
# USE_ATLAS = os.getenv("USE_ATLAS", "false").lower() == "true"

# if USE_ATLAS:
#     atlas_user = os.getenv("MONGO_ATLAS_USER")
#     atlas_pass = os.getenv("MONGO_ATLAS_PASS")
#     atlas_cluster = os.getenv("MONGO_ATLAS_CLUSTER")
#     MONGO_URI = f"mongodb+srv://{atlas_user}:{atlas_pass}@{atlas_cluster}/?retryWrites=true&w=majority"
# else:
#     MONGO_URI = "mongodb://localhost:27017/"

# client = MongoClient(MONGO_URI)
# db = client["attendance_system"]

# users_col = db["users"]
# attendance_col = db["attendance"]


# # -----------------------------------------
# # AUTO-CREATE ADMIN USER
# # -----------------------------------------
# if users_col.count_documents({}) == 0:
#     users_col.insert_one({
#         "username": "admin",
#         "password": "admin123",
#         "full_name": "Admin",
#         "role": "admin"
#     })


# # -----------------------------------------
# # AUTH DECORATOR
# # -----------------------------------------
# def login_required(role=None):
#     def decorator(fn):
#         from functools import wraps

#         @wraps(fn)
#         def wrapper(*args, **kwargs):
#             if "user_id" not in session:
#                 return redirect(url_for("login"))

#             user = users_col.find_one({"_id": ObjectId(session["user_id"])})

#             if not user:
#                 session.clear()
#                 return redirect(url_for("login"))

#             if role and user["role"] != role:
#                 return redirect(url_for("login"))

#             return fn(*args, **kwargs)

#         return wrapper
#     return decorator


# # -----------------------------------------
# # UTILS
# # -----------------------------------------
# def get_today_record(user_id):
#     today = now_ist().strftime("%Y-%m-%d")
#     return attendance_col.find_one({"user_id": user_id, "date": today})


# # -----------------------------------------
# # ROUTES
# # -----------------------------------------
# @app.route("/")
# def home():
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     user = users_col.find_one({"_id": ObjectId(session["user_id"])})
#     return redirect(url_for("admin_dashboard" if user["role"] == "admin" else "intern_dashboard"))


# # -----------------------------------------
# # LOGIN
# # -----------------------------------------
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"].strip()
#         password = request.form["password"].strip()

#         user = users_col.find_one({"username": username, "password": password})

#         if user:
#             session["user_id"] = str(user["_id"])
#             flash("Login successful!", "success")
#             return redirect("/")

#         flash("Invalid username or password", "danger")

#     return render_template("login.html")


# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect(url_for("login"))


# # -----------------------------------------
# # INTERN DASHBOARD
# # -----------------------------------------
# WORK_TYPES = ["Office", "Work From Home"]

# @app.route("/intern")
# @login_required(role="intern")
# def intern_dashboard():
#     user = users_col.find_one({"_id": ObjectId(session["user_id"])})
#     record = get_today_record(user["_id"])

#     return render_template("intern_dashboard.html",
#                            user=user,
#                            record=record,
#                            work_types=WORK_TYPES)


# # -----------------------------------------
# # MARK LOGIN
# # -----------------------------------------
# @app.route("/intern/mark-login", methods=["POST"])
# @login_required(role="intern")
# def mark_login():
#     user_id = ObjectId(session["user_id"])
#     work_type = request.form["work_type"]
#     today = now_ist().strftime("%Y-%m-%d")

#     if get_today_record(user_id):
#         flash("Login already marked today!", "warning")
#         return redirect(url_for("intern_dashboard"))

#     attendance_col.insert_one({
#         "user_id": user_id,
#         "date": today,
#         "work_type": work_type,
#         "login_time": now_ist().strftime("%H:%M:%S"),
#         "logout_time": None,
#         "status": "Present",
#         "hours_worked": None
#     })

#     flash("Login marked!", "success")
#     return redirect(url_for("intern_dashboard"))


# # -----------------------------------------
# # MARK LOGOUT
# # -----------------------------------------
# @app.route("/intern/mark-logout", methods=["POST"])
# @login_required(role="intern")
# def mark_logout():
#     user_id = ObjectId(session["user_id"])
#     today = now_ist().strftime("%Y-%m-%d")

#     record = attendance_col.find_one({"user_id": user_id, "date": today})

#     if not record:
#         flash("Please mark login first!", "danger")
#         return redirect(url_for("intern_dashboard"))

#     login_str = record["login_time"]
#     logout_str = now_ist().strftime("%H:%M:%S")

#     login_dt = datetime.strptime(login_str, "%H:%M:%S")
#     logout_dt = datetime.strptime(logout_str, "%H:%M:%S")

#     diff = logout_dt - login_dt
#     hours = diff.seconds // 3600
#     minutes = (diff.seconds % 3600) // 60

#     attendance_col.update_one(
#         {"_id": record["_id"]},
#         {"$set": {"logout_time": logout_str, "hours_worked": f"{hours}h {minutes}m"}}
#     )

#     flash("Logout marked!", "success")
#     return redirect(url_for("intern_dashboard"))


# # -----------------------------------------
# # ADMIN DASHBOARD
# # -----------------------------------------
# @app.route("/admin", methods=["GET", "POST"])
# @login_required(role="admin")
# def admin_dashboard():
#     date = request.form.get("date") or now_ist().strftime("%Y-%m-%d")
#     records = list(attendance_col.find({"date": date}))

#     for r in records:
#         u = users_col.find_one({"_id": r["user_id"]})
#         r["name"] = u["full_name"]
#         r["username"] = u["username"]

#     return render_template("admin_dashboard.html", records=records, date=date)


# # -----------------------------------------
# # ADD INTERN
# # -----------------------------------------
# @app.route("/admin/add-intern", methods=["GET", "POST"])
# @login_required(role="admin")
# def add_intern():
#     if request.method == "POST":
#         full_name = request.form["full_name"].strip()
#         username = request.form["username"].strip()
#         password = request.form["password"].strip()

#         if users_col.find_one({"username": username}):
#             flash("Username already exists!", "danger")
#             return redirect(url_for("add_intern"))

#         users_col.insert_one({
#             "full_name": full_name,
#             "username": username,
#             "password": password,
#             "role": "intern"
#         })

#         flash("Intern added successfully!", "success")
#         return redirect(url_for("admin_dashboard"))

#     return render_template("add_intern.html")


# # -----------------------------------------
# # START APP
# # -----------------------------------------
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)




from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash, send_file
)
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import pytz
import pandas as pd
from io import BytesIO
import calendar

load_dotenv()

app = Flask(__name__)
app.secret_key = "super-secret-key"

# -----------------------------------------
# TIMEZONE (IST)
# -----------------------------------------
IST = pytz.timezone("Asia/Kolkata")

def now_ist():
    return datetime.now(IST)


# -----------------------------------------
# MONGO CONNECTION
# -----------------------------------------
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
attendance_col = db["attendance"]
holidays_col = db["holidays"]
leaves_col = db["leaves"]


# -----------------------------------------
# AUTO-CREATE ADMIN USER
# -----------------------------------------
if users_col.count_documents({}) == 0:
    users_col.insert_one({
        "username": "admin",
        "password": "admin123",
        "full_name": "Admin",
        "role": "admin"
    })


# -----------------------------------------
# AUTH DECORATOR
# -----------------------------------------
def login_required(role=None):
    def decorator(fn):
        from functools import wraps

        @wraps(fn)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))

            user = users_col.find_one({"_id": ObjectId(session["user_id"])})

            if not user:
                session.clear()
                return redirect(url_for("login"))

            if role and user["role"] != role:
                return redirect(url_for("login"))

            return fn(*args, **kwargs)

        return wrapper
    return decorator


# -----------------------------------------
# UTILITY
# -----------------------------------------
def get_today_record(user_id):
    today = now_ist().strftime("%Y-%m-%d")
    return attendance_col.find_one({"user_id": user_id, "date": today})


# -----------------------------------------
# HOME
# -----------------------------------------
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = users_col.find_one({"_id": ObjectId(session["user_id"])})
    return redirect(url_for("admin_dashboard" if user["role"] == "admin" else "intern_dashboard"))


# -----------------------------------------
# LOGIN
# -----------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        user = users_col.find_one({"username": username, "password": password})

        if user:
            session["user_id"] = str(user["_id"])
            flash("Login successful!", "success")
            return redirect("/")

        flash("Invalid username or password", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# -----------------------------------------
# INTERN DASHBOARD
# -----------------------------------------
WORK_TYPES = ["Office", "Work From Home"]

@app.route("/intern")
@login_required(role="intern")
def intern_dashboard():
    user = users_col.find_one({"_id": ObjectId(session["user_id"])})
    record = get_today_record(user["_id"])

    # --- New Logic: Monthly Stats & History ---
    selected_month = request.args.get("month")
    if not selected_month:
        selected_month = now_ist().strftime("%Y-%m")
    
    # Fetch records for selected month (using regex for date string)
    monthly_records = list(attendance_col.find({
        "user_id": user["_id"],
        "date": {"$regex": f"^{selected_month}"}
    }).sort("date", -1))

    # Calculate Total Hours
    total_minutes = 0
    work_type_counts = {}
    total_days_worked = len(monthly_records)
    
    # Chart Data
    chart_labels = []
    chart_data = []
    daily_hours_target = int(user.get("daily_hours", 8))

    for r in monthly_records:
        hw = r.get("hours_worked")
        if hw:
            try:
                # Format is "Xh Ym"
                parts = hw.split(" ")
                h = int(parts[0].replace("h", ""))
                m = int(parts[1].replace("m", ""))
                total_minutes += (h * 60) + m
                
                # For Chart (Float hours)
                float_hours = h + (m / 60)
                chart_labels.append(r["date"][8:]) # Just the day part
                chart_data.append(round(float_hours, 2))
                
                # Early Leaver Indicator
                if float_hours < daily_hours_target and r.get("work_type") != "Holiday":
                    r["early_leaver"] = True
            except:
                pass
        
        # Count Work Types for Stats
        wt = r.get("work_type", "Other")
        work_type_counts[wt] = work_type_counts.get(wt, 0) + 1
    
    # Reverse lists for chart so they are chronological (since records are sorted desc)
    chart_labels.reverse()
    chart_data.reverse()
    
    hours = total_minutes // 60
    minutes = total_minutes % 60
    total_hours_month = f"{hours}h {minutes}m"

    # --- Calculate Standard/Target Hours (Based on Admin Assignment) ---
    daily_hours = int(user.get("daily_hours", 8)) # Default to 8 if not set
    standard_hours_val = total_days_worked * daily_hours
    standard_hours_str = f"{standard_hours_val}h"

    # Fetch Leaves
    leaves = list(leaves_col.find({"user_id": user["_id"]}).sort("start_date", -1))

    # Fetch Holidays from DB
    holidays = list(holidays_col.find({}).sort("date", 1))
    joining_date = user.get("joining_date")
    ending_date = user.get("ending_date")

    # --- Calendar Logic ---
    try:
        year, month = map(int, selected_month.split('-'))
    except ValueError:
        now = now_ist()
        year, month = now.year, now.month

    # Get matrix of month (0 = Monday, ..., 6 = Sunday)
    month_cal = calendar.monthcalendar(year, month)
    
    # Check if today is a holiday (for the Mark Attendance form)
    today_dt = now_ist()
    today_str = today_dt.strftime("%Y-%m-%d")
    today_holiday = holidays_col.find_one({"date": today_str})

    # If not an admin holiday, check if it is Sunday
    if not today_holiday and today_dt.weekday() == 6:
        today_holiday = {"name": "Sunday"}

    # Maps for fast lookup
    attendance_map = {r["date"]: r["work_type"] for r in monthly_records}
    holiday_map = {h["date"]: h["name"] for h in holidays}
    today_str = now_ist().strftime("%Y-%m-%d")

    calendar_data = []
    for week in month_cal:
        week_data = []
        for idx, day in enumerate(week):
            if day == 0:
                week_data.append(None)
                continue
            
            date_str = f"{year}-{month:02d}-{day:02d}"
            is_sunday = (idx == 6)
            is_holiday = date_str in holiday_map
            holiday_name = holiday_map.get(date_str, "")
            
            circle_color = None
            tooltip = ""

            if date_str in attendance_map:
                wt = attendance_map[date_str].lower()
                if "home" in wt:
                    circle_color = "yellow"
                    tooltip = "Work From Home"
                else:
                    circle_color = "green"
                    tooltip = "Office"
            elif not is_holiday and not is_sunday and date_str < today_str:
                # Absent: Check if within employment period
                is_active = True
                if joining_date and date_str < joining_date: is_active = False
                if ending_date and date_str > ending_date: is_active = False
                
                if is_active:
                    circle_color = "red"
                    tooltip = "Absent"
            
            week_data.append({
                "day": day, 
                "is_sunday": is_sunday, 
                "is_holiday": is_holiday,
                "holiday_name": holiday_name,
                "circle_color": circle_color, 
                "tooltip": tooltip
            })
        calendar_data.append(week_data)

    return render_template("intern_dashboard.html",
                           user=user,
                           record=record,
                           work_types=WORK_TYPES,
                           monthly_records=monthly_records,
                           total_hours_month=total_hours_month,
                           holidays=holidays,
                           selected_month=selected_month,
                           work_type_counts=work_type_counts,
                           total_days_worked=total_days_worked,
                           calendar_data=calendar_data,
                           standard_hours_str=standard_hours_str,
                           today_holiday=today_holiday,
                           leaves=leaves,
                           chart_labels=chart_labels,
                           chart_data=chart_data)


# MARK LOGIN
@app.route("/intern/mark-login", methods=["POST"])
@login_required(role="intern")
def mark_login():
    user_id = ObjectId(session["user_id"])
    work_type = request.form["work_type"]
    today_dt = now_ist()
    today = today_dt.strftime("%Y-%m-%d")

    if holidays_col.find_one({"date": today}) or today_dt.weekday() == 6:
        flash("Cannot mark attendance on a holiday or Sunday!", "danger")
        return redirect(url_for("intern_dashboard"))

    if get_today_record(user_id):
        flash("Login already marked today!", "warning")
        return redirect(url_for("intern_dashboard"))

    attendance_col.insert_one({
        "user_id": user_id,
        "date": today,
        "work_type": work_type,
        "login_time": now_ist().strftime("%H:%M:%S"),
        "logout_time": None,
        "status": "Present",
        "hours_worked": None
    })

    flash("Login marked!", "success")
    return redirect(url_for("intern_dashboard"))


# MARK LOGOUT
@app.route("/intern/mark-logout", methods=["POST"])
@login_required(role="intern")
def mark_logout():
    user_id = ObjectId(session["user_id"])
    today = now_ist().strftime("%Y-%m-%d")

    record = attendance_col.find_one({"user_id": user_id, "date": today})
    if not record:
        flash("Please mark login first!", "danger")
        return redirect(url_for("intern_dashboard"))

    login_str = record["login_time"]
    logout_str = now_ist().strftime("%H:%M:%S")

    login_dt = datetime.strptime(login_str, "%H:%M:%S")
    logout_dt = datetime.strptime(logout_str, "%H:%M:%S")

    diff = logout_dt - login_dt
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60

    attendance_col.update_one(
        {"_id": record["_id"]},
        {"$set": {"logout_time": logout_str,
                  "hours_worked": f"{hours}h {minutes}m"}}
    )

    flash("Logout marked!", "success")
    return redirect(url_for("intern_dashboard"))


# APPLY LEAVE
@app.route("/intern/apply-leave", methods=["POST"])
@login_required(role="intern")
def apply_leave():
    user_id = ObjectId(session["user_id"])
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    reason = request.form.get("reason")
    
    leaves_col.insert_one({
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
        "reason": reason,
        "status": "Pending",
        "applied_on": now_ist()
    })
    flash("Leave application submitted.", "success")
    return redirect(url_for("intern_dashboard"))


# -----------------------------------------
# ADMIN DASHBOARD
# -----------------------------------------
# @app.route("/admin", methods=["GET", "POST"])
# @login_required(role="admin")
# def admin_dashboard():
#     date = request.form.get("date") or now_ist().strftime("%Y-%m-%d")

#     # Attendance records
#     records = list(attendance_col.find({"date": date}))

#     for r in records:
#         u = users_col.find_one({"_id": r["user_id"]})
#         r["name"] = u["full_name"]
#         r["username"] = u["username"]

#     # All interns for delete section
#     interns = list(users_col.find({"role": "intern"}))

#     return render_template("admin_dashboard.html",
#                            records=records,
#                            interns=interns,
#                            date=date)




# @app.route("/admin", methods=["GET", "POST"])
# @login_required(role="admin")
# def admin_dashboard():
#     date = request.form.get("date") or now_ist().strftime("%Y-%m-%d")

#     # Get all interns
#     interns = list(users_col.find({"role": "intern"}))

#     # Get attendance records for selected date
#     records = list(attendance_col.find({"date": date}))

#     # Convert attendance list → dictionary for fast lookup
#     attendance_map = {str(r["user_id"]): r for r in records}

#     # Final table rows
#     final_rows = []

#     for intern in interns:
#         intern_id = str(intern["_id"])

#         if intern_id in attendance_map:
#             r = attendance_map[intern_id]
#             final_rows.append({
#                 "name": intern["full_name"],
#                 "username": intern["username"],
#                 "work_type": r.get("work_type", "-"),
#                 "login_time": r.get("login_time", "-"),
#                 "logout_time": r.get("logout_time", "-"),
#                 "hours_worked": r.get("hours_worked", "-"),
#                 "status": r.get("status", "Present")
#             })
#         else:
#             # Intern has no attendance → Absent
#             final_rows.append({
#                 "name": intern["full_name"],
#                 "username": intern["username"],
#                 "work_type": "-",
#                 "login_time": "-",
#                 "logout_time": "-",
#                 "hours_worked": "-",
#                 "status": "Absent"
#             })

#     return render_template("admin_dashboard.html",
#                            records=final_rows,
#                            interns=interns,
#                            date=date)

@app.route("/admin", methods=["GET", "POST"])
@login_required(role="admin")
def admin_dashboard():
    # 1. Determine Selected Date (GET param preferred for links)
    date = request.args.get("date")
    if not date:
        date = request.form.get("date") or now_ist().strftime("%Y-%m-%d")

    # Get all interns
    interns = list(users_col.find({"role": "intern"}))
    
    # Get Pending Leaves
    pending_leaves = list(leaves_col.find({"status": "Pending"}))
    for l in pending_leaves:
        u = users_col.find_one({"_id": l["user_id"]})
        if u:
            l["intern_name"] = u["full_name"]

    # Get attendance records for selected date
    attendance_records = list(attendance_col.find({"date": date}))

    # Map user_id to record
    attendance_map = {str(r["user_id"]): r for r in attendance_records}

    # Check if selected date is a holiday
    holiday_record = holidays_col.find_one({"date": date})
    is_sunday = (datetime.strptime(date, "%Y-%m-%d").weekday() == 6)
    today_str = now_ist().strftime("%Y-%m-%d")

    final_rows = []

    for intern in interns:
        intern_id = str(intern["_id"])
        joining_date = intern.get("joining_date")
        
        # Filter out interns who haven't joined yet based on the selected date
        if joining_date and date < joining_date:
            continue

        ending_date = intern.get("ending_date")
        daily_hours = int(intern.get("daily_hours", 8))
        is_early_leaver = False

        if intern_id in attendance_map:
            r = attendance_map[intern_id]
            
            # Calculate Early Leaver Status
            hw = r.get("hours_worked")
            if hw and "h" in hw:
                try:
                    parts = hw.split(" ")
                    h = int(parts[0].replace("h", ""))
                    m = int(parts[1].replace("m", ""))
                    if (h + m/60) < daily_hours:
                        is_early_leaver = True
                except:
                    pass

            final_rows.append({
                "user_id": intern_id,
                "name": intern["full_name"],
                "username": intern["username"],
                "work_type": r.get("work_type", "-"),
                "login_time": r.get("login_time", "-"),
                "logout_time": r.get("logout_time", "-"),
                "hours_worked": r.get("hours_worked", "-"),
                "status": "Present",
                "is_early_leaver": is_early_leaver
            })
        else:
            status = "Absent"
            if ending_date and date > ending_date:
                status = "-"
            elif date > today_str:
                status = "-"
            elif holiday_record:
                status = f"Holiday: {holiday_record['name']}"
            elif is_sunday:
                status = "Holiday: Sunday"

            final_rows.append({
                "user_id": intern_id,
                "name": intern["full_name"],
                "username": intern["username"],
                "work_type": "-",
                "login_time": "-",
                "logout_time": "-",
                "hours_worked": "-",
                "status": status,
                "is_early_leaver": False
            })

    # Sort: Present first → Absent later
    final_rows.sort(key=lambda x: 0 if x["status"] == "Present" else 1)

    # Calculate Stats for Dashboard
    total_interns_count = len(final_rows)
    present_count = sum(1 for r in final_rows if r["status"] == "Present")
    absent_count = sum(1 for r in final_rows if r["status"] == "Absent")

    # Fetch Holidays for Admin View
    holidays = list(holidays_col.find({}).sort("date", 1))
    holiday_map = {h["date"]: h["name"] for h in holidays}

    # --- Calendar Logic for Admin ---
    # Determine which month to show in the calendar widget
    calendar_month = request.args.get("month")
    if not calendar_month:
        calendar_month = date[:7]  # Default to the selected date's month

    try:
        year, month = map(int, calendar_month.split('-'))
    except:
        now = now_ist()
        year, month = now.year, now.month

    month_cal = calendar.monthcalendar(year, month)
    calendar_data = []

    for week in month_cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)
                continue
            
            day_date_str = f"{year}-{month:02d}-{day:02d}"
            is_selected = (day_date_str == date)
            is_sunday = (calendar.weekday(year, month, day) == 6)
            is_holiday = day_date_str in holiday_map
            
            week_data.append({
                "day": day,
                "full_date": day_date_str,
                "is_selected": is_selected,
                "is_sunday": is_sunday,
                "is_holiday": is_holiday,
                "holiday_name": holiday_map.get(day_date_str, "")
            })
        calendar_data.append(week_data)

    return render_template("admin_dashboard.html",
                           records=final_rows,
                           interns=interns,
                           holidays=holidays,
                           date=date,
                           calendar_data=calendar_data,
                           calendar_month=calendar_month,
                           total_interns=total_interns_count,
                           present_count=present_count,
                           absent_count=absent_count,
                           pending_leaves=pending_leaves)


@app.route("/admin/intern-profile/<user_id>")
@login_required(role="admin")
def admin_intern_profile(user_id):
    user = users_col.find_one({"_id": ObjectId(user_id)})
    if not user:
        flash("User not found", "danger")
        return redirect(url_for("admin_dashboard"))

    # Selected Month for stats (default current)
    selected_month = request.args.get("month")
    if not selected_month:
        selected_month = now_ist().strftime("%Y-%m")

    # --- 1. Current Month Stats ---
    monthly_records = list(attendance_col.find({
        "user_id": ObjectId(user_id),
        "date": {"$regex": f"^{selected_month}"}
    }).sort("date", -1))

    work_type_counts = {}
    total_minutes = 0

    for r in monthly_records:
        # Count Work Types
        wt = r.get("work_type", "Other")
        work_type_counts[wt] = work_type_counts.get(wt, 0) + 1

        # Sum Hours
        hw = r.get("hours_worked")
        if hw:
            try:
                parts = hw.split(" ")
                h = int(parts[0].replace("h", ""))
                m = int(parts[1].replace("m", ""))
                total_minutes += (h * 60) + m
            except: pass

    total_hours_month = f"{total_minutes // 60}h {total_minutes % 60}m"

    # --- 2. Previous Month Stats ---
    curr_date_obj = datetime.strptime(selected_month + "-01", "%Y-%m-%d")
    prev_month_date = curr_date_obj - timedelta(days=1)
    prev_month_str = prev_month_date.strftime("%Y-%m")

    prev_records = list(attendance_col.find({
        "user_id": ObjectId(user_id),
        "date": {"$regex": f"^{prev_month_str}"}
    }))

    prev_minutes = sum([
        (int(r["hours_worked"].split(" ")[0][:-1]) * 60 + int(r["hours_worked"].split(" ")[1][:-1]))
        for r in prev_records if r.get("hours_worked")
    ])
    prev_month_hours = f"{prev_minutes // 60}h {prev_minutes % 60}m"

    # --- Standard Hours Calculation ---
    daily_hours = int(user.get("daily_hours", 8))
    standard_hours_val = len(monthly_records) * daily_hours
    standard_hours_str = f"{standard_hours_val}h"

    return render_template("admin_intern_profile.html",
                           user=user,
                           selected_month=selected_month,
                           monthly_records=monthly_records,
                           work_type_counts=work_type_counts,
                           total_hours_month=total_hours_month,
                           prev_month_str=prev_month_str,
                           prev_month_hours=prev_month_hours,
                           standard_hours_str=standard_hours_str)


# -----------------------------------------
# HOLIDAY MANAGEMENT
# -----------------------------------------
@app.route("/admin/add-holiday", methods=["POST"])
@login_required(role="admin")
def add_holiday():
    name = request.form.get("name")
    date = request.form.get("date")
    
    if name and date:
        if not holidays_col.find_one({"date": date}):
            holidays_col.insert_one({"name": name, "date": date})
            flash("Holiday added successfully!", "success")
        else:
            flash("A holiday already exists on this date.", "warning")
            
    return redirect(url_for("admin_dashboard", date=date))

@app.route("/admin/delete-holiday", methods=["POST"])
@login_required(role="admin")
def delete_holiday():
    holiday_id = request.form.get("holiday_id")
    holidays_col.delete_one({"_id": ObjectId(holiday_id)})
    flash("Holiday deleted.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/manage-leave", methods=["POST"])
@login_required(role="admin")
def manage_leave():
    leave_id = request.form.get("leave_id")
    action = request.form.get("action") # 'Approved' or 'Rejected'
    
    if action in ["Approved", "Rejected"]:
        leaves_col.update_one({"_id": ObjectId(leave_id)}, {"$set": {"status": action}})
        flash(f"Leave request {action}.", "success")
    
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete-intern", methods=["POST"])
@login_required(role="admin")
def delete_intern():
    username = request.form.get("username")

    user = users_col.find_one({"username": username})

    if not user:
        flash("Intern not found!", "danger")
        return redirect(url_for("admin_dashboard"))

    user_id = user["_id"]

    users_col.delete_one({"_id": user_id})
    attendance_col.delete_many({"user_id": user_id})

    flash(f"Intern '{username}' deleted successfully!", "success")
    return redirect(url_for("admin_dashboard"))


#update intern
@app.route("/admin/update-intern", methods=["POST"])
@login_required(role="admin")
def update_intern():
    original_username = request.form.get("original_username")
    full_name = request.form.get("full_name").strip()
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()
    daily_hours = request.form.get("daily_hours", 8)
    joining_date = request.form.get("joining_date")
    ending_date = request.form.get("ending_date")

    user = users_col.find_one({"username": original_username})
    if not user:
        flash("Intern not found!", "danger")
        return redirect(url_for("admin_dashboard"))

    update_data = {
        "full_name": full_name,
        "username": username,
        "password": password,
        "daily_hours": int(daily_hours),
        "joining_date": joining_date,
        "ending_date": ending_date
    }

    users_col.update_one({"_id": user["_id"]}, {"$set": update_data})

    flash(f"Intern '{username}' updated successfully!", "success")
    return redirect(url_for("admin_dashboard"))


# -----------------------------------------
# DOWNLOAD EXCEL
# -----------------------------------------
@app.route("/admin/download", methods=["POST"])
@login_required(role="admin")
def download_excel():
    date = request.form.get("date") or now_ist().strftime("%Y-%m-%d")
    records = list(attendance_col.find({"date": date}))

    rows = []
    for r in records:
        u = users_col.find_one({"_id": r["user_id"]})
        rows.append({
            "Full Name": u["full_name"],
            "Username": u["username"],
            "Work Type": r.get("work_type", "-"),
            "Login Time": r.get("login_time", "-"),
            "Logout Time": r.get("logout_time", "-"),
            "Hours Worked": r.get("hours_worked", "-"),
            "Status": r.get("status", "-")
        })

    df = pd.DataFrame(rows)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    filename = f"attendance_{date}.xlsx"
    return send_file(output,
                     download_name=filename,
                     as_attachment=True,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.route("/admin/download-intern-report/<user_id>")
@login_required(role="admin")
def download_intern_report(user_id):
    user = users_col.find_one({"_id": ObjectId(user_id)})
    if not user:
        flash("Intern not found", "danger")
        return redirect(url_for("admin_dashboard"))

    records = list(attendance_col.find({"user_id": ObjectId(user_id)}).sort("date", -1))

    rows = []
    for r in records:
        rows.append({
            "Date": r.get("date"),
            "Work Type": r.get("work_type", "-"),
            "Login Time": r.get("login_time", "-"),
            "Logout Time": r.get("logout_time", "-"),
            "Hours Worked": r.get("hours_worked", "-"),
            "Status": r.get("status", "-")
        })

    df = pd.DataFrame(rows)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    filename = f"Report_{user['username']}.xlsx"
    return send_file(output, download_name=filename, as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")



# -----------------------------------------
# ADD INTERN
# -----------------------------------------
@app.route("/admin/add-intern", methods=["GET", "POST"])
@login_required(role="admin")
def add_intern():
    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        daily_hours = request.form.get("daily_hours", 8)
        joining_date = request.form.get("joining_date")

        if users_col.find_one({"username": username}):
            flash("Username already exists!", "danger")
            return redirect(url_for("add_intern"))

        users_col.insert_one({
            "full_name": full_name,
            "username": username,
            "password": password,
            "role": "intern",
            "daily_hours": int(daily_hours),
            "joining_date": joining_date
        })

        flash("Intern added successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("add_intern.html")


# -----------------------------------------
# START SERVER
# -----------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
