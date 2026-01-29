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
    
    # Check for approved leave today
    leave_today = leaves_col.find_one({
        "user_id": user["_id"],
        "start_date": {"$lte": today_str},
        "end_date": {"$gte": today_str},
        "status": "Approved"
    })

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

            # Check if user has approved leave on this date
            leave_on_date = leaves_col.find_one({
                "user_id": user["_id"],
                "start_date": {"$lte": date_str},
                "end_date": {"$gte": date_str},
                "status": "Approved"
            })

            is_leave = False

            if date_str in attendance_map:
                wt = attendance_map[date_str].lower()
                if "home" in wt:
                    circle_color = "yellow"
                    tooltip = "Work From Home"
                elif "leave" in wt:
                    circle_color = None
                    is_leave = True
                    tooltip = "Approved Leave"
                else:
                    circle_color = "green"
                    tooltip = "Office"
            elif leave_on_date:
                # Approved leave - show in green cell
                circle_color = None
                is_leave = True
                tooltip = "Approved Leave"
            elif is_holiday:
                # Holiday - show in green
                circle_color = "green"
                tooltip = f"Holiday: {holiday_name}"
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
                "is_leave": is_leave,
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
                           leave_today=leave_today,
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

    # Check if today is a confirmed leave
    leave_today = leaves_col.find_one({
        "user_id": user_id,
        "start_date": {"$lte": today},
        "end_date": {"$gte": today},
        "status": "Approved"
    })
    
    if leave_today:
        flash("You have confirmed leave today! Cannot mark attendance.", "danger")
        return redirect(url_for("intern_dashboard"))

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

@app.route("/admin", methods=["GET", "POST"])
@login_required(role="admin")
def admin_dashboard():
    # 1. Determine Selected Date (GET param preferred for links)
    date = request.args.get("date")
    if not date:
        date = request.form.get("date") or now_ist().strftime("%Y-%m-%d")

    # Get all interns
    interns = list(users_col.find({"role": "intern"}))
    
    # Get All Leaves (History)
    all_leaves = list(leaves_col.find({}).sort("_id", -1))
    pending_count = 0
    for l in all_leaves:
        u = users_col.find_one({"_id": l["user_id"]})
        if u:
            l["intern_name"] = u["full_name"]
        if l.get("status") == "Pending":
            pending_count += 1

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
        ending_date = intern.get("ending_date")
        
        # Filter out interns who haven't joined yet based on the selected date
        if joining_date and date < joining_date:
            continue

        # Filter out interns whose contract has ended relative to the selected date
        if ending_date and date > ending_date:
            continue

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
            if date > today_str:
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
                           leaves=all_leaves,
                           pending_count=pending_count)


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
    chart_labels = []
    chart_data = []

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

                # Chart Data
                float_hours = h + (m / 60)
                chart_labels.append(r["date"][8:])
                chart_data.append(round(float_hours, 2))
            except: pass

    # Reverse for chronological order
    chart_labels.reverse()
    chart_data.reverse()

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
                           standard_hours_str=standard_hours_str,
                           chart_labels=chart_labels,
                           chart_data=chart_data)


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


# -----------------------------------------
# DELETE INTERN
# -----------------------------------------
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
# ADD ADMIN
# -----------------------------------------
@app.route("/admin/add-admin", methods=["POST"])
@login_required(role="admin")
def add_admin():
    full_name = request.form.get("full_name", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not full_name or not username or not password:
        flash("All fields are required!", "danger")
        return redirect(url_for("admin_dashboard"))

    if users_col.find_one({"username": username}):
        flash("Username already exists!", "danger")
        return redirect(url_for("admin_dashboard"))

    users_col.insert_one({
        "full_name": full_name,
        "username": username,
        "password": password,
        "role": "admin"
    })

    flash(f"Admin '{username}' added successfully!", "success")
    return redirect(url_for("admin_dashboard"))


# -----------------------------------------
# CHANGE WORK TYPE
# -----------------------------------------
@app.route("/admin/change-work-type", methods=["POST"])
@login_required(role="admin")
def change_work_type():
    user_id = request.form.get("user_id")
    date = request.form.get("date")
    work_type = request.form.get("work_type")

    record = attendance_col.find_one({"user_id": ObjectId(user_id), "date": date})
    if not record:
        flash("Attendance record not found!", "danger")
        return redirect(url_for("admin_dashboard", date=date))

    attendance_col.update_one(
        {"_id": record["_id"]},
        {"$set": {"work_type": work_type}}
    )

    flash("Work type updated successfully!", "success")
    return redirect(url_for("admin_dashboard", date=date))


# -----------------------------------------
# EDIT TIME (Forgot Logout)
# -----------------------------------------
@app.route("/admin/edit-time", methods=["POST"])
@login_required(role="admin")
def edit_time():
    user_id = request.form.get("user_id")
    date = request.form.get("date")
    login_time = request.form.get("login_time")
    logout_time = request.form.get("logout_time")

    record = attendance_col.find_one({"user_id": ObjectId(user_id), "date": date})
    if not record:
        flash("Attendance record not found!", "danger")
        return redirect(url_for("admin_dashboard", date=date))

    update_data = {}
    
    # Helper to ensure HH:MM:SS format
    def format_time(t):
        if not t: return None
        t = t.strip()
        # Handle HH:MM (5 chars) or H:MM (4 chars)
        if len(t) <= 5 and ":" in t: return t + ":00"
        return t

    login_time = format_time(login_time)
    logout_time = format_time(logout_time)
    
    if login_time:
        update_data["login_time"] = login_time
    
    if logout_time:
        update_data["logout_time"] = logout_time
        
    # Calculate hours if we have both times (either new or existing)
    final_login = login_time if login_time else record.get("login_time")
    final_logout = logout_time if logout_time else record.get("logout_time")
    
    # Handle case where existing logout might be "-" or None
    if final_logout == "-": final_logout = None

    if final_login and final_logout:
        try:
            login_dt = datetime.strptime(final_login, "%H:%M:%S")
            logout_dt = datetime.strptime(final_logout, "%H:%M:%S")
            diff = logout_dt - login_dt
            
            # Handle case where logout is next day
            if diff.total_seconds() < 0:
                diff = timedelta(hours=24) + diff
            
            hours = int(diff.total_seconds() // 3600)
            minutes = int((diff.total_seconds() % 3600) // 60)
            update_data["hours_worked"] = f"{hours}h {minutes}m"
        except Exception as e:
            print(f"Error calculating hours: {e}")
            pass

    if update_data:
        attendance_col.update_one({"_id": record["_id"]}, {"$set": update_data})
        flash("Attendance time updated successfully!", "success")

    return redirect(url_for("admin_dashboard", date=date))


# -----------------------------------------
# COMPLETED INTERNSHIPS
# -----------------------------------------
@app.route("/admin/completed-internships")
@login_required(role="admin")
def completed_internships():
    today = now_ist().strftime("%Y-%m-%d")
    
    # Find interns whose ending_date has passed and have both joining and ending dates
    completed_interns = list(users_col.find({
        "role": "intern",
        "joining_date": {"$exists": True, "$ne": ""},
        "ending_date": {"$exists": True, "$ne": "", "$lt": today}
    }).sort("ending_date", -1))
    
    # Add stats for each intern
    for intern in completed_interns:
        user_id = intern["_id"]
        
        # Calculate total hours worked
        records = list(attendance_col.find({"user_id": user_id}))
        total_minutes = 0
        days_worked = 0
        
        for r in records:
            if r.get("hours_worked") and r.get("hours_worked") != "-":
                try:
                    parts = r["hours_worked"].split(" ")
                    h = int(parts[0].replace("h", ""))
                    m = int(parts[1].replace("m", ""))
                    total_minutes += (h * 60) + m
                    days_worked += 1
                except:
                    pass
        
        intern["total_hours"] = f"{total_minutes // 60}h {total_minutes % 60}m"
        intern["days_worked"] = days_worked
        intern["joining_date"] = intern.get("joining_date", "N/A")
        intern["ending_date"] = intern.get("ending_date", "N/A")
    
    # --- Summary Stats Calculation ---
    total_completed = len(completed_interns)
    total_days_all_interns = sum(intern.get('days_worked', 0) for intern in completed_interns)
    avg_days_worked = (total_days_all_interns / total_completed) if total_completed > 0 else 0

    total_minutes_all_interns = 0
    for intern in completed_interns:
        if 'total_hours' in intern and 'h' in intern['total_hours']:
            try:
                parts = intern["total_hours"].split(" ")
                h = int(parts[0].replace("h", ""))
                m = int(parts[1].replace("m", ""))
                total_minutes_all_interns += (h * 60) + m
            except (ValueError, IndexError):
                pass # Or log the error
    total_hours_all_str = f"{total_minutes_all_interns // 60}h {total_minutes_all_interns % 60}m"

    return render_template("completed_internships.html",
                           completed_interns=completed_interns,
                           total_completed=total_completed,
                           avg_days_worked=avg_days_worked,
                           total_hours_all_str=total_hours_all_str)


# -----------------------------------------
# TODAY'S LIVE TIMERS
# -----------------------------------------
@app.route("/admin/today-timers")
@login_required(role="admin")
def today_timers():
    today = now_ist().strftime("%Y-%m-%d")

    # Get today's attendance records (those who logged in)
    today_records = list(attendance_col.find({"date": today, "status": "Present"}))

    # Build user data with timers
    todays_users = []
    for record in today_records:
        user = users_col.find_one({"_id": record["user_id"]})
        if user:
            daily_hours = int(user.get("daily_hours", 8))
            login_time = record.get("login_time", "")
            logout_time = record.get("logout_time")
            hours_worked = record.get("hours_worked")

            todays_users.append({
                "user_id": str(user["_id"]),
                "full_name": user["full_name"],
                "username": user["username"],
                "login_time": login_time,
                "logout_time": logout_time,
                "hours_worked": hours_worked,
                "work_type": record.get("work_type", "-"),
                "daily_hours": daily_hours
            })

    # Sort by logged out status first (active on top), then by login time
    todays_users.sort(key=lambda x: (x['logout_time'] is not None, x['login_time']))

    return render_template("today_timers.html", todays_users=todays_users, today=today)


# -----------------------------------------
# CONFIRM/REJECT LEAVE WITH COLOR DISPLAY
# -----------------------------------------
@app.route("/admin/manage-leave", methods=["POST"])
@login_required(role="admin")
def manage_leave():
    leave_id = request.form.get("leave_id")
    action = request.form.get("action")  # 'Approved' or 'Rejected'
    
    if action in ["Approved", "Rejected"]:
        leave = leaves_col.find_one({"_id": ObjectId(leave_id)})
        
        if not leave:
            flash("Leave request not found!", "danger")
            return redirect(url_for("admin_dashboard"))
        
        leaves_col.update_one({"_id": ObjectId(leave_id)}, {"$set": {"status": action}})
        
        if action == "Approved":
            # Add to attendance records with Holiday status for leave display
            user_id = leave["user_id"]
            start_dt = datetime.strptime(leave["start_date"], "%Y-%m-%d")
            end_dt = datetime.strptime(leave["end_date"], "%Y-%m-%d")
            
            current_dt = start_dt
            while current_dt <= end_dt:
                date_str = current_dt.strftime("%Y-%m-%d")
                # Check if record already exists
                existing = attendance_col.find_one({"user_id": user_id, "date": date_str})
                if not existing:
                    attendance_col.insert_one({
                        "user_id": user_id,
                        "date": date_str,
                        "work_type": "Leave",
                        "login_time": "-",
                        "logout_time": "-",
                        "status": "Leave - Approved",
                        "hours_worked": "-",
                        "leave_id": ObjectId(leave_id)
                    })
                current_dt += timedelta(days=1)
        
        elif action == "Rejected":
            # If rejecting, remove any attendance records previously created for this leave
            attendance_col.delete_many({"leave_id": ObjectId(leave_id)})
        
        flash(f"Leave request {action}.", "success")
    
    return redirect(url_for("admin_dashboard"))


# -----------------------------------------
# DELETE LEAVE REQUEST
# -----------------------------------------
@app.route("/admin/delete-leave", methods=["POST"])
@login_required(role="admin")
def delete_leave():
    leave_id = request.form.get("leave_id")
    if leave_id:
        # First, delete any attendance records that were created for this leave
        attendance_col.delete_many({"leave_id": ObjectId(leave_id)})
        
        # Then, delete the leave request itself
        leaves_col.delete_one({"_id": ObjectId(leave_id)})
        
        flash("Leave request has been permanently deleted.", "success")
    else:
        flash("Could not delete leave request: ID missing.", "warning")
        
    return redirect(url_for("admin_dashboard"))


# -----------------------------------------
# START SERVER
# -----------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
