# Attendance Management System 📋

A comprehensive Flask-based attendance tracking system with advanced features for managing employee attendance, leaves, and work schedules.

## ✨ Features

### 👥 User Management
- **Admin Dashboard** - Central control panel for managing all users
- **Multiple Admins** - Create additional admin users with full privileges
- **Intern Management** - Add, edit, and remove intern employees
- **Role-Based Access** - Separate dashboards for admins and interns

### 📍 Attendance Tracking
- **Daily Login/Logout** - Mark work hours with timestamp
- **Work Type Selection** - Office or Work From Home option
- **Time Editing** - Admin can adjust times for missed logouts
- **Auto-Calculation** - Hours worked automatically calculated
- **Early Leaver Detection** - Flag employees who leave early

### 🏖️ Leave Management
- **Leave Application** - Interns can apply for time off
- **Leave Approval** - Admins approve or reject requests
- **Multi-Day Leaves** - Support for leave spanning multiple days
- **Leave History** - Track all leave requests and status
- **Calendar Integration** - Approved leaves visible on calendar

### 📅 Holiday Management
- **Company Holidays** - Define company-wide holidays
- **Holiday Calendar** - Display holidays across the system
- **Holiday Blocking** - Prevent work marking on holidays
- **Multiple Holidays** - Add unlimited holidays throughout the year

### 📊 Reporting & Analytics
- **Monthly Statistics** - Track hours worked per month
- **Attendance History** - View detailed attendance logs
- **Excel Export** - Download attendance reports
- **Individual Profiles** - Detailed employee attendance data
- **Work Location Stats** - Track office vs. remote days

### 🎨 Visual Features
- **Color-Coded Calendar** - 
  - 🟢 Green: Office work or company holidays
  - 🟡 Yellow: Work from home
  - 🔴 Red: Approved leave or absent
- **Interactive Calendar** - Click to view daily records
- **Status Indicators** - Visual badges for attendance status
- **Responsive Design** - Works on desktop and mobile

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MongoDB (local or Atlas)
- Flask 3.1+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
cd attendance_system
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure MongoDB**

Create a `.env` file:
```bash
# Local MongoDB
USE_ATLAS=false
# MONGO_URI will use: mongodb://localhost:27017/

# OR MongoDB Atlas
USE_ATLAS=true
MONGO_ATLAS_USER=your_username
MONGO_ATLAS_PASS=your_password
MONGO_ATLAS_CLUSTER=your_cluster_name
```

5. **Initialize the database**
```bash
python seed.py  # Creates default admin user
```

6. **Run the application**
```bash
python app.py
```

Application will be available at: `http://localhost:5000`

## 📚 Documentation

### Quick Start
See [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) for step-by-step instructions on using all features.

### Features Overview
See [FEATURES_IMPLEMENTED.md](FEATURES_IMPLEMENTED.md) for detailed information about all features.

### API Documentation
See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API endpoint details.

### Database Schema
See [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) for database structure and design.

## 🔐 Default Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`

⚠️ **Important:** Change these credentials in production!

## 📁 Project Structure

```
attendance_system/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── seed.py                        # Database seeder
├── seed2.py                       # Additional seeder
├── static/
│   ├── login.css                 # Login page styles
│   └── style.css                 # Main styles
├── templates/
│   ├── base.html                 # Base template
│   ├── login.html                # Login page
│   ├── admin_dashboard.html      # Admin dashboard
│   ├── admin_intern_profile.html # Intern profile (admin view)
│   ├── intern_dashboard.html     # Intern dashboard
│   └── add_intern.html           # Add intern form
├── FEATURES_IMPLEMENTED.md       # Feature details
├── QUICK_START_GUIDE.md         # Usage guide
├── API_DOCUMENTATION.md         # API reference
└── DATABASE_SCHEMA.md           # Database design
```

## 🌐 Routes

### Public Routes
- `GET /` - Redirect to dashboard (login required)
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /logout` - Logout

### Intern Routes
- `GET /intern` - Intern dashboard
- `POST /intern/mark-login` - Mark work start
- `POST /intern/mark-logout` - Mark work end
- `POST /intern/apply-leave` - Apply for leave

### Admin Routes
- `GET /admin` - Admin dashboard
- `POST /admin/add-intern` - Add new intern
- `POST /admin/add-admin` - Add new admin ⭐
- `POST /admin/update-intern` - Update intern details
- `POST /admin/delete-intern` - Remove intern
- `POST /admin/add-holiday` - Add company holiday
- `POST /admin/delete-holiday` - Remove holiday
- `POST /admin/manage-leave` - Approve/reject leave ⭐
- `POST /admin/change-work-type` - Change Office/WFH ⭐
- `POST /admin/edit-time` - Edit login/logout times ⭐
- `GET /admin/intern-profile/<user_id>` - View intern profile
- `POST /admin/download` - Export daily attendance
- `GET /admin/download-intern-report/<user_id>` - Export intern report

⭐ = New features added in latest version

## 🗄️ Database Collections

### users
```json
{
  "_id": ObjectId,
  "full_name": "John Doe",
  "username": "john_doe",
  "password": "password_hash",
  "role": "admin | intern",
  "daily_hours": 8,
  "joining_date": "2024-01-15",
  "ending_date": "2024-12-31"
}
```

### attendance
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "date": "2024-12-20",
  "work_type": "Office | Work From Home | Leave | Holiday",
  "login_time": "09:30:00",
  "logout_time": "17:45:00",
  "status": "Present | Leave - Approved | Absent",
  "hours_worked": "8h 15m",
  "leave_id": ObjectId
}
```

### leaves
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "start_date": "2024-12-25",
  "end_date": "2024-12-27",
  "reason": "Family vacation",
  "status": "Pending | Approved | Rejected",
  "applied_on": ISODate
}
```

### holidays
```json
{
  "_id": ObjectId,
  "name": "Christmas",
  "date": "2024-12-25"
}
```

## 🔧 Configuration

### timezone
The system uses IST (Asia/Kolkata) timezone by default.
To change, modify in app.py:
```python
IST = pytz.timezone("Your/Timezone")
```

### Daily Work Hours
Default: 8 hours per day
Can be set individually for each intern

### Date Formats
- Dates: `YYYY-MM-DD`
- Times: `HH:MM:SS` (24-hour format)
- Hours: `XhYm` (e.g., "8h 30m")

## 📊 Features in Detail

### Admin Can Add Admins
- Navigate to "Add Admin" section in admin dashboard
- Fill form with full name, username, and password
- New admin gets full system access immediately

### Work Type Management
- Admin can change office/WFH status after attendance is marked
- Changes are reflected in monthly reports
- Supports mid-month adjustments

### Time Editing
- Admin can edit login/logout times for any day
- Hours are auto-calculated when logout time is changed
- Handles next-day logouts automatically
- Useful for: forgotten logouts, manual corrections

### Leave Approval System
- Interns apply for leaves with start/end dates
- Admin reviews in "Leave Requests" section
- Approval creates attendance records for those days
- Approved leaves block user login on those days
- Rejected leaves have no impact on calendar

### Calendar Color Coding
- **Green** = Office work / Company holiday
- **Yellow** = Work from home
- **Red** = Approved leave / Absent day
- Color legend visible on calendar

## 🚨 Common Issues & Solutions

### Cannot add admin
- ✅ Ensure you're logged in as admin
- ✅ Check username is unique
- ✅ Fill all required fields

### Leave not blocking login
- ✅ Verify leave status is "Approved" (not "Pending")
- ✅ Refresh page to reload calendar
- ✅ Check date range is correct

### Hours not calculating correctly
- ✅ Ensure time format is HH:MM:SS
- ✅ Verify login_time < logout_time
- ✅ For overnight shifts, system auto-adds 24 hours

### Cannot see edited times
- ✅ Admin changes don't show in real-time
- ✅ Refresh the page
- ✅ Go back and view the date again

## 📈 Performance Tips

### Database Optimization
- Create indexes for frequent queries
- Archive old records monthly
- Clean up rejected leave requests quarterly

### UI Responsiveness
- Calendar loads month by month
- Large attendance reports may take time
- Use export for offline analysis

## 🔒 Security Features

✅ Role-based access control
✅ Session-based authentication
✅ MongoDB injection protection
✅ User ownership verification
✅ Leave approval prevents unauthorized work

## 🌟 New Features in v2.0

1. **Multiple Admin Support** - Create additional admins
2. **Work Type Changes** - Modify office/WFH status
3. **Time Editing** - Adjust missed logouts
4. **Enhanced Leaves** - Better leave management
5. **Color Calendar** - Visual calendar improvements
6. **Auto Calculations** - Smart hour calculations

## 📱 Browser Support

- ✅ Chrome/Chromium 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Android)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📝 License

This project is proprietary. Use only with proper authorization.

## 📞 Support

For issues or questions:
1. Check documentation files
2. Review API documentation
3. Check database schema
4. Examine Flask logs

## 🎯 Roadmap

### Planned Features
- [ ] Email notifications for leave approvals
- [ ] Monthly payroll integration
- [ ] Department-wise reports
- [ ] Geolocation attendance
- [ ] Biometric integration
- [ ] Mobile app (native)
- [ ] Advanced analytics dashboard

## 📊 Version Information

- **Current Version:** 2.0
- **Python Version:** 3.8+
- **Flask Version:** 3.1.2
- **Database:** MongoDB 4.0+

## 🙏 Acknowledgments

Built with:
- Flask - Web framework
- MongoDB - Database
- Bootstrap 5 - UI Framework
- Chart.js - Analytics visualization
- FontAwesome - Icons

---

## 🎉 Quick Links

- [Features Guide](FEATURES_IMPLEMENTED.md)
- [Quick Start](QUICK_START_GUIDE.md)
- [API Docs](API_DOCUMENTATION.md)
- [DB Schema](DATABASE_SCHEMA.md)

---

**Last Updated:** December 2024
**Maintainer:** Attendance System Team

For the latest updates and detailed information, please refer to the documentation files included in the project.
