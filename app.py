# # from flask import (
# #     Flask, render_template, request,
# #     redirect, url_for, session, send_file, flash
# # )
# # from datetime import datetime
# # from openpyxl import Workbook, load_workbook
# # import os

# # from zipfile import BadZipFile  # add this at the top with other imports

# # app = Flask(__name__)
# # app.secret_key = "change-this-secret-key"

# # ATTENDANCE_FILE = "attendance.xlsx"

# # # ---- Test users ----
# # USERS = {
# #     "sahil": {"password": "sahil123", "role": "intern", "full_name": "Sahil"},
# #     "test": {"password": "test123", "role": "intern", "full_name": "Test Intern"},
# #     "admin": {"password": "admin123", "role": "admin", "full_name": "Admin"},
# # }

# # # Dropdown list for work types
# # WORK_TYPES = ["Office", "Work from home", "Field work", "Other"]


# # # ---------------- Excel Helpers ----------------

# # def get_or_create_workbook():
# #     if os.path.exists(ATTENDANCE_FILE):
# #         try:
# #             wb = load_workbook(ATTENDANCE_FILE)
# #             return wb
# #         except BadZipFile:
# #             # If file is corrupt or not a real xlsx, recreate it
# #             os.remove(ATTENDANCE_FILE)

# #     # Create new workbook
# #     wb = Workbook()
# #     default_sheet = wb.active
# #     wb.remove(default_sheet)
# #     wb.save(ATTENDANCE_FILE)
# #     return wb



# # def get_today_sheet(wb):
# #     sheet_name = datetime.now().strftime("%d-%m-%Y")
# #     if sheet_name in wb.sheetnames:
# #         return wb[sheet_name]
# #     else:
# #         ws = wb.create_sheet(title=sheet_name)
# #         ws.append(["Student name", "present/absent", "Work type", "login time", "logout time"])
# #         return ws


# # def find_or_create_row(ws, student_name):
# #     for row in range(2, ws.max_row + 1):
# #         if ws[f"A{row}"].value == student_name:
# #             return row

# #     new_row = ws.max_row + 1
# #     ws[f"A{new_row}"].value = student_name
# #     return new_row


# # def mark_login(username, work_type):
# #     wb = get_or_create_workbook()
# #     ws = get_today_sheet(wb)
# #     row = find_or_create_row(ws, username)
# #     now_str = datetime.now().strftime("%H:%M:%S")

# #     ws[f"B{row}"] = "Present"
# #     ws[f"C{row}"] = work_type
# #     ws[f"D{row}"] = now_str

# #     wb.save(ATTENDANCE_FILE)


# # def mark_logout(username):
# #     wb = get_or_create_workbook()
# #     ws = get_today_sheet(wb)
# #     row = find_or_create_row(ws, username)
# #     now_str = datetime.now().strftime("%H:%M:%S")

# #     ws[f"E{row}"] = now_str
# #     wb.save(ATTENDANCE_FILE)


# # def get_today_status(username):
# #     wb = get_or_create_workbook()
# #     ws = get_today_sheet(wb)

# #     for row in range(2, ws.max_row + 1):
# #         if ws[f"A{row}"].value == username:
# #             return {
# #                 "present": ws[f"B{row}"].value,
# #                 "work_type": ws[f"C{row}"].value,
# #                 "login_time": ws[f"D{row}"].value,
# #                 "logout_time": ws[f"E{row}"].value
# #             }

# #     return {
# #         "present": None,
# #         "work_type": None,
# #         "login_time": None,
# #         "logout_time": None
# #     }


# # def read_sheet_for_date(date_str):
# #     try:
# #         dt = datetime.strptime(date_str, "%Y-%m-%d")
# #     except ValueError:
# #         return None, []

# #     sheet_name = dt.strftime("%d-%m-%Y")
# #     wb = get_or_create_workbook()

# #     if sheet_name not in wb.sheetnames:
# #         return sheet_name, []

# #     ws = wb[sheet_name]
# #     data = []

# #     for row in range(2, ws.max_row + 1):
# #         student = ws[f"A{row}"].value
# #         if not student:
# #             continue
# #         data.append({
# #             "student": student,
# #             "status": ws[f"B{row}"].value,
# #             "work_type": ws[f"C{row}"].value,
# #             "login_time": ws[f"D{row}"].value,
# #             "logout_time": ws[f"E{row}"].value,
# #         })

# #     return sheet_name, data


# # # ---------------- Auth Helpers ----------------

# # def login_required(role=None):
# #     def wrapper(fn):
# #         from functools import wraps

# #         @wraps(fn)
# #         def decorated(*args, **kwargs):
# #             if "user" not in session:
# #                 return redirect(url_for("login"))
# #             if role and USERS[session["user"]]["role"] != role:
# #                 return redirect(url_for("login"))
# #             return fn(*args, **kwargs)

# #         return decorated

# #     return wrapper


# # # ---------------- Routes ----------------

# # @app.route("/")
# # def index():
# #     if "user" in session:
# #         role = USERS[session["user"]]["role"]
# #         return redirect(url_for("admin_dashboard" if role == "admin" else "intern_dashboard"))
# #     return redirect(url_for("login"))


# # @app.route("/login", methods=["GET", "POST"])
# # def login():
# #     if request.method == "POST":
# #         username = request.form["username"].strip()
# #         password = request.form["password"].strip()

# #         user = USERS.get(username)
# #         if user and user["password"] == password:
# #             session["user"] = username
# #             flash("Login successful!", "success")

# #             if user["role"] == "admin":
# #                 return redirect(url_for("admin_dashboard"))
# #             else:
# #                 return redirect(url_for("intern_dashboard"))

# #         flash("Invalid credentials", "danger")

# #     return render_template("login.html")


# # @app.route("/logout")
# # def logout():
# #     session.clear()
# #     flash("Logged out.", "info")
# #     return redirect(url_for("login"))


# # @app.route("/intern")
# # @login_required(role="intern")
# # def intern_dashboard():
# #     username = session["user"]
# #     user = USERS[username]
# #     status = get_today_status(username)

# #     return render_template(
# #         "intern_dashboard.html",
# #         name=user["full_name"],
# #         username=username,
# #         work_types=WORK_TYPES,
# #         status=status,
# #     )


# # @app.route("/intern/mark-login", methods=["POST"])
# # @login_required(role="intern")
# # def intern_mark_login():
# #     work_type = request.form.get("work_type")
# #     if not work_type:
# #         flash("Select work type.", "warning")
# #     else:
# #         mark_login(session["user"], work_type)
# #         flash("Login attendance marked!", "success")

# #     return redirect(url_for("intern_dashboard"))


# # @app.route("/intern/mark-logout", methods=["POST"])
# # @login_required(role="intern")
# # def intern_mark_logout():
# #     mark_logout(session["user"])
# #     flash("Logout time marked!", "success")
# #     return redirect(url_for("intern_dashboard"))


# # @app.route("/admin", methods=["GET", "POST"])
# # @login_required(role="admin")
# # def admin_dashboard():
# #     date_str = request.form.get("date") if request.method == "POST" else datetime.now().strftime("%Y-%m-%d")
# #     sheet_name, rows = read_sheet_for_date(date_str)

# #     return render_template(
# #         "admin_dashboard.html",
# #         date_str=date_str,
# #         sheet_name=sheet_name,
# #         rows=rows,
# #     )


# # @app.route("/admin/download")
# # @login_required(role="admin")
# # def download_excel():
# #     return send_file(ATTENDANCE_FILE, as_attachment=True)


# # # ---------------------------------------
# # if __name__ == "__main__":
# #     app.run(debug=True)



# from flask import (
#     Flask, render_template, request,
#     redirect, url_for, session, flash
# )
# from datetime import datetime
# from bson.objectid import ObjectId
# from pymongo import MongoClient
# import os
# from dotenv import load_dotenv

# load_dotenv()

# app = Flask(__name__)
# app.secret_key = "super-secret-key"


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
#     MONGO_URI = "mongodb://localhost:27017/"  # Local DB


# client = MongoClient(MONGO_URI)
# db = client["attendance_system"]

# users_col = db["users"]
# attendance_col = db["attendance"]


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

#             if role and user["role"] != role:
#                 return redirect(url_for("login"))

#             return fn(*args, **kwargs)

#         return wrapper
#     return decorator


# def get_today_record(user_id):
#     today = datetime.now().strftime("%Y-%m-%d")
#     return attendance_col.find_one({"user_id": user_id, "date": today})


# # -----------------------------------------
# # ROUTES
# # -----------------------------------------

# @app.route("/")
# def home():
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     user = users_col.find_one({"_id": ObjectId(session["user_id"])})

#     if user["role"] == "admin":
#         return redirect(url_for("admin_dashboard"))
#     else:
#         return redirect(url_for("intern_dashboard"))


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

#             if user["role"] == "admin":
#                 return redirect(url_for("admin_dashboard"))
#             else:
#                 return redirect(url_for("intern_dashboard"))

#         flash("Invalid username or password", "danger")

#     return render_template("login.html")


# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect(url_for("login"))


# # -----------------------------------------
# # INTERN DASHBOARD
# # -----------------------------------------

# WORK_TYPES = ["Office", "Work From Home", "Field Work", "Other"]


# @app.route("/intern")
# @login_required(role="intern")
# def intern_dashboard():
#     user = users_col.find_one({"_id": ObjectId(session["user_id"])})

#     record = get_today_record(user["_id"])

#     return render_template(
#         "intern_dashboard.html",
#         user=user,
#         record=record,
#         work_types=WORK_TYPES
#     )


# # MARK LOGIN
# @app.route("/intern/mark-login", methods=["POST"])
# @login_required(role="intern")
# def mark_login():
#     user_id = ObjectId(session["user_id"])
#     work_type = request.form["work_type"]
#     today = datetime.now().strftime("%Y-%m-%d")

#     if get_today_record(user_id):
#         flash("Login already marked today!", "warning")
#         return redirect(url_for("intern_dashboard"))

#     attendance_col.insert_one({
#         "user_id": user_id,
#         "date": today,
#         "work_type": work_type,
#         "login_time": datetime.now().strftime("%H:%M:%S"),
#         "logout_time": None,
#         "status": "Present",
#         "hours_worked": None
#     })

#     flash("Login marked!", "success")
#     return redirect(url_for("intern_dashboard"))


# # MARK LOGOUT (Calculate hours worked)
# @app.route("/intern/mark-logout", methods=["POST"])
# @login_required(role="intern")
# def mark_logout():
#     user_id = ObjectId(session["user_id"])
#     today = datetime.now().strftime("%Y-%m-%d")

#     record = attendance_col.find_one({"user_id": user_id, "date": today})

#     if not record:
#         flash("Please mark login first!", "danger")
#         return redirect(url_for("intern_dashboard"))

#     login_time_str = record.get("login_time")
#     logout_time_str = datetime.now().strftime("%H:%M:%S")

#     # Convert times
#     login_dt = datetime.strptime(login_time_str, "%H:%M:%S")
#     logout_dt = datetime.strptime(logout_time_str, "%H:%M:%S")

#     diff = logout_dt - login_dt
#     total_seconds = diff.total_seconds()

#     hours = int(total_seconds // 3600)
#     minutes = int((total_seconds % 3600) // 60)

#     hours_worked = f"{hours}h {minutes}m"

#     attendance_col.update_one(
#         {"user_id": user_id, "date": today},
#         {"$set": {
#             "logout_time": logout_time_str,
#             "hours_worked": hours_worked
#         }}
#     )

#     flash("Logout marked! Hours worked calculated.", "success")
#     return redirect(url_for("intern_dashboard"))


# # -----------------------------------------
# # ADMIN DASHBOARD
# # -----------------------------------------

# @app.route("/admin", methods=["GET", "POST"])
# @login_required(role="admin")
# def admin_dashboard():
#     date = request.form.get("date") or datetime.now().strftime("%Y-%m-%d")

#     records = list(attendance_col.find({"date": date}))

#     # Attach user info
#     for r in records:
#         u = users_col.find_one({"_id": r["user_id"]})
#         r["name"] = u["full_name"]
#         r["username"] = u["username"]

#     return render_template(
#         "admin_dashboard.html",
#         records=records,
#         date=date
#     )


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

#         existing = users_col.find_one({"username": username})
#         if existing:
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
#     app.run(debug=True)



from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)
from datetime import datetime
from bson.objectid import ObjectId
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "super-secret-key"

# -----------------------------------------
# MONGO CONNECTION (LOCAL + ATLAS READY)
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

# -----------------------------------------
# AUTO-CREATE ADMIN USER IF MISSING
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

            # Prevent NoneType errors
            if not user:
                session.clear()
                return redirect(url_for("login"))

            if role and user["role"] != role:
                return redirect(url_for("login"))

            return fn(*args, **kwargs)
        return wrapper
    return decorator

# -----------------------------------------
# UTILS
# -----------------------------------------
def get_today_record(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    return attendance_col.find_one({"user_id": user_id, "date": today})

# -----------------------------------------
# ROUTES
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

    return render_template("intern_dashboard.html",
                           user=user,
                           record=record,
                           work_types=WORK_TYPES)

# Intern Login
@app.route("/intern/mark-login", methods=["POST"])
@login_required(role="intern")
def mark_login():
    user_id = ObjectId(session["user_id"])
    work_type = request.form["work_type"]
    today = datetime.now().strftime("%Y-%m-%d")

    if get_today_record(user_id):
        flash("Login already marked today!", "warning")
        return redirect(url_for("intern_dashboard"))

    attendance_col.insert_one({
        "user_id": user_id,
        "date": today,
        "work_type": work_type,
        "login_time": datetime.now().strftime("%H:%M:%S"),
        "logout_time": None,
        "status": "Present",
        "hours_worked": None
    })

    flash("Login marked!", "success")
    return redirect(url_for("intern_dashboard"))

# Intern Logout
@app.route("/intern/mark-logout", methods=["POST"])
@login_required(role="intern")
def mark_logout():
    user_id = ObjectId(session["user_id"])
    today = datetime.now().strftime("%Y-%m-%d")

    record = attendance_col.find_one({"user_id": user_id, "date": today})

    if not record:
        flash("Please mark login first!", "danger")
        return redirect(url_for("intern_dashboard"))

    login_str = record["login_time"]
    logout_str = datetime.now().strftime("%H:%M:%S")

    login_dt = datetime.strptime(login_str, "%H:%M:%S")
    logout_dt = datetime.strptime(logout_str, "%H:%M:%S")

    diff = logout_dt - login_dt
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60

    attendance_col.update_one(
        {"_id": record["_id"]},
        {"$set": {"logout_time": logout_str, "hours_worked": f"{hours}h {minutes}m"}}
    )

    flash("Logout marked!", "success")
    return redirect(url_for("intern_dashboard"))

# -----------------------------------------
# ADMIN DASHBOARD
# -----------------------------------------

@app.route("/admin", methods=["GET", "POST"])
@login_required(role="admin")
def admin_dashboard():
    date = request.form.get("date") or datetime.now().strftime("%Y-%m-%d")
    records = list(attendance_col.find({"date": date}))

    for r in records:
        u = users_col.find_one({"_id": r["user_id"]})
        r["name"] = u["full_name"]
        r["username"] = u["username"]

    return render_template("admin_dashboard.html", records=records, date=date)

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

        if users_col.find_one({"username": username}):
            flash("Username already exists!", "danger")
            return redirect(url_for("add_intern"))

        users_col.insert_one({
            "full_name": full_name,
            "username": username,
            "password": password,
            "role": "intern"
        })

        flash("Intern added successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("add_intern.html")

# -----------------------------------------
# START APP
# -----------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)