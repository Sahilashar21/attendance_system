# Quick Start Guide - New Features

## 🔑 How to Use New Features

---

## 1️⃣ **Add New Admin**

### Steps:
1. Login as an existing admin (username: `admin`, password: `admin123`)
2. Go to **Admin Dashboard**
3. Click **"Add Admin"** button (blue button)
4. Fill in the form:
   - Full Name (e.g., "John Manager")
   - Username (e.g., "admin_john")
   - Password (e.g., "secure_pass123")
5. Click **"Add Admin"** button
6. New admin can now login with the provided credentials

✅ New admin will have full admin dashboard access

---

## 2️⃣ **Change User Work Type (Office/WFH)**

### Steps:
1. Go to **Admin Dashboard**
2. Select a date from the calendar
3. View attendance records for that date
4. Find the intern whose work type needs to be changed
5. Click **"Edit"** button for that intern
6. Expand the collapsible section
7. In "Work Type" dropdown, select:
   - **Office** - for office work
   - **Work From Home** - for remote work
8. Selection auto-updates
9. Close the form

✅ Work type is now updated for that day

---

## 3️⃣ **Edit Login/Logout Times**

### Scenario: Employee forgot to mark logout

### Steps:
1. Go to **Admin Dashboard**
2. Select the date (today or any past date)
3. Find the employee record marked as "Present"
4. Click **"Edit"** button
5. In the expanded form, you'll see:
   - **Login Time** field (e.g., "09:30:00")
   - **Logout Time** field (e.g., "17:45:00")
6. Update times as needed (format: HH:MM:SS)
7. Click **"Save Changes"**
8. System automatically recalculates hours worked

✅ Hours are recalculated and saved

**Example:**
```
Login:  09:00:00
Logout: 17:30:00
Auto-Calculated: 8h 30m
```

---

## 4️⃣ **Apply for Leave (Intern)**

### Steps (Intern view):
1. Login as an intern
2. Go to **Intern Dashboard**
3. Scroll down to **"Leaves"** tab
4. Fill in "Apply for Leave" form:
   - **Start Date** - e.g., 2024-12-25
   - **End Date** - e.g., 2024-12-27
   - **Reason** - e.g., "Family emergency"
5. Click **"Submit Request"**

✅ Leave request sent to admin (shows as "Pending")

---

## 5️⃣ **Approve/Reject Leave (Admin)**

### Steps (Admin view):
1. Go to **Admin Dashboard**
2. Click **"Leave Requests"** button
3. View all pending leave requests
4. For each request, see:
   - Intern name
   - Dates (Start → End)
   - Reason
5. Click:
   - ✅ **Green checkmark** to **Approve**
   - ❌ **Red X** to **Reject**

✅ Once approved, intern cannot mark attendance on those days (shows in RED on calendar)

---

## 6️⃣ **View Calendar with Color Coding**

### Calendar Color Legend:

```
🟢 GREEN   = Office work or Company Holiday
🟡 YELLOW  = Work From Home (WFH)
🔴 RED     = Approved Leave or Absent day
🩷 PINK    = Holiday name label
```

### Intern Calendar View:
1. Login as intern
2. Go to **Intern Dashboard**
3. Scroll to **"Attendance Calendar"** section
4. View color-coded calendar:
   - Green dots = Days worked at office
   - Yellow dots = Days worked from home
   - Red dots = Approved leaves (cannot work these days)
   - Red dates = Sundays (blocked)

### Admin Calendar View:
1. Go to **Admin Dashboard**
2. Click on any date in the left calendar
3. Attendance records for that date show on the right
4. Use month selector to navigate months
5. Selected date is highlighted in orange

---

## 7️⃣ **Block Login on Approved Leave Days**

### What Happens:
1. Admin approves leave for 25-27 Dec
2. On those dates, when intern tries to login:
   - Mark Login button is hidden
   - Error message shows: "You have confirmed leave today! Cannot mark attendance."
3. On holidays/Sundays:
   - Same block applies
   - Error: "Cannot mark attendance on a holiday or Sunday!"

✅ System prevents work records on blocked days

---

## 📊 **View Attendance History**

### Intern View:
1. **Attendance History Tab**: All work records for the month
2. **Leaves Tab**: All leave requests with status
3. **Holidays Tab**: List of company holidays
4. **Calendar**: Visual representation of work days

### Admin View:
1. Select date from calendar
2. Table shows all interns' attendance for that day
3. Status indicates: Present, Absent, or Holiday
4. Early Leavers toggle to filter
5. Click intern name to view full profile

---

## 🔧 **Troubleshooting**

### Issue: Cannot see "Add Admin" button
- **Solution**: Make sure you're logged in as an admin

### Issue: Edit button not showing
- **Solution**: Edit button only appears for "Present" records

### Issue: Cannot change work type dropdown
- **Solution**: Make sure the date is in the past (not future)

### Issue: Leave shows as pending after approval
- **Solution**: Refresh the page; calendar needs refresh to show approved leaves

### Issue: Employee can still login on leave day
- **Solution**: Make sure leave status shows "Approved" (not "Pending" or "Rejected")

---

## 💡 **Pro Tips**

1. **Bulk Edit Times**: Edit times one at a time from admin dashboard
2. **Leave Duration**: Can approve multi-day leaves in one action
3. **Work Type**: Can change WFH to Office and vice versa anytime
4. **Hours Calculation**: Always recalculated when times are edited
5. **Export Reports**: Use "Export Excel" to download daily attendance
6. **Calendar Navigation**: Use month selector to view any month

---

## 📱 **Mobile Responsive**

✅ All new features work on mobile:
- Add admin form is responsive
- Edit time fields collapse properly
- Calendar displays correctly
- Leave form is mobile-friendly

---

## 🎯 **Feature Summary**

| Feature | User | Action |
|---------|------|--------|
| Add Admin | Admin | Create new admin user |
| Change Work Type | Admin | Office/WFH toggle |
| Edit Times | Admin | Update login/logout |
| Apply Leave | Intern | Submit leave request |
| Approve Leave | Admin | Approve/Reject leaves |
| View Calendar | Both | Color-coded calendar |
| Block Login | System | Auto-block on approved leave |
| Export Report | Admin | Download Excel file |

---

## 🔒 **Security Notes**

✅ Only admins can add other admins
✅ Only admins can edit attendance times
✅ Only admins can approve leaves
✅ Users cannot access other users' data
✅ All changes are logged in database

---

## ❓ **Need Help?**

If you encounter any issues:
1. Check FEATURES_IMPLEMENTED.md for technical details
2. Verify database connection (MongoDB)
3. Check Flask logs for errors
4. Ensure all required fields are filled before submitting

Happy using the new features! 🎉
