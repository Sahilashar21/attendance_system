# Testing Guide - New Features

Complete testing checklist for all new features in Attendance System v2.0

---

## 🧪 Test Environment Setup

### Prerequisites
- MongoDB running (local or Atlas)
- Flask application running on localhost:5000
- Default admin account created (admin/admin123)
- Web browser with developer console

### Database Reset
```bash
# Backup current database
mongodump --db attendance_system --out ./backup

# Clear test data
use attendance_system
db.users.deleteMany({})
db.attendance.deleteMany({})
db.leaves.deleteMany({})
db.holidays.deleteMany({})

# Recreate default admin
python seed.py
```

---

## ✅ Feature 1: Add Admin

### Test Case 1.1: Create Valid Admin

**Steps:**
1. Login as admin (admin/admin123)
2. Click "Add Admin" button
3. Fill form:
   - Full Name: "Test Admin"
   - Username: "test_admin_001"
   - Password: "test_pass_123"
4. Click "Add Admin" button

**Expected Result:**
- ✅ Success message: "Admin 'test_admin_001' added successfully!"
- ✅ Redirect to admin dashboard
- ✅ New admin appears in database

**Verification:**
```bash
# Check MongoDB
db.users.findOne({"username": "test_admin_001"})
# Should return document with role: "admin"
```

### Test Case 1.2: Duplicate Username

**Steps:**
1. Click "Add Admin" button
2. Enter same username as existing admin
3. Try to submit form

**Expected Result:**
- ✅ Error message: "Username already exists!"
- ✅ Form is not submitted
- ✅ No new user created

### Test Case 1.3: Missing Fields

**Steps:**
1. Click "Add Admin" button
2. Leave Full Name empty
3. Try to submit

**Expected Result:**
- ✅ Error message: "All fields are required!"
- ✅ Form validation prevents submission

### Test Case 1.4: New Admin Login

**Steps:**
1. Create new admin (from Test 1.1)
2. Logout current user
3. Login with new admin credentials
4. Navigate to admin dashboard

**Expected Result:**
- ✅ Login successful
- ✅ Admin dashboard loads
- ✅ All admin features available

---

## ✅ Feature 2: Change Work Type

### Test Case 2.1: Change Office to Work From Home

**Prerequisites:**
- Create test intern
- Mark attendance as "Office"

**Steps:**
1. Go to admin dashboard
2. Select today's date from calendar
3. Find intern with "Present" status
4. Click "Edit" button
5. In Work Type dropdown, select "Work From Home"

**Expected Result:**
- ✅ Dropdown changes instantly
- ✅ Form auto-submits
- ✅ Attendance record updated in database
- ✅ Table refreshes to show "Work From Home"

### Test Case 2.2: Change Work From Home to Office

**Steps:**
1. Same as Test 2.1 but reverse the selection
2. Select "Office" from dropdown

**Expected Result:**
- ✅ Work type updates to "Office"
- ✅ Change persists in database

### Test Case 2.3: Work Type in Reports

**Prerequisites:**
- Change work type from step above

**Steps:**
1. Go to admin dashboard
2. Scroll to "Attendance Records" table
3. Verify work type column shows correct value

**Expected Result:**
- ✅ Report shows updated work type
- ✅ Download Excel includes correct work type

### Test Case 2.4: Unavailable for Absent Records

**Steps:**
1. View a date where intern was absent
2. Look for Edit button

**Expected Result:**
- ✅ No Edit button appears for absent records
- ✅ Edit only available for "Present" status

---

## ✅ Feature 3: Edit Time (Missed Logout)

### Test Case 3.1: Edit Logout Time

**Prerequisites:**
- Intern with incomplete login (no logout)

**Steps:**
1. Admin dashboard, select today's date
2. Find incomplete record
3. Click "Edit" button
4. Enter logout time (e.g., "17:45:00")
5. Click "Save Changes"

**Expected Result:**
- ✅ Success message: "Attendance time updated successfully!"
- ✅ logout_time field is updated
- ✅ hours_worked is auto-calculated
- ✅ Table updates to show new hours

**Verification:**
```bash
# Check MongoDB
db.attendance.findOne({"user_id": ObjectId("..."), "date": "2024-12-20"})
# Should show: logout_time and hours_worked
```

### Test Case 3.2: Auto-Calculate Hours (Same Day)

**Steps:**
1. Edit login: "09:30:00"
2. Edit logout: "17:45:00"
3. Save changes

**Expected Result:**
- ✅ hours_worked = "8h 15m"
- ✅ Calculation shown in table

**Calculation:**
```
17:45 - 09:30 = 8:15 = 8h 15m ✓
```

### Test Case 3.3: Auto-Calculate Hours (Overnight Shift)

**Prerequisites:**
- Create record with late logout

**Steps:**
1. Set login: "23:30:00"
2. Set logout: "02:00:00" (next day)
3. Save changes

**Expected Result:**
- ✅ System adds 24 hours before calculating
- ✅ hours_worked = "2h 30m"
- ✅ No error message

**Calculation:**
```
02:00 is negative, so add 24 hours
02:00 + 24:00 = 26:00
26:00 - 23:30 = 2:30 = 2h 30m ✓
```

### Test Case 3.4: Edit Only Login Time

**Steps:**
1. Edit login_time only
2. Leave logout_time empty
3. Save changes

**Expected Result:**
- ✅ login_time updates
- ✅ logout_time unchanged
- ✅ hours_worked NOT recalculated

### Test Case 3.5: Historical Record Editing

**Steps:**
1. Select a date from last month
2. Try to edit attendance record
3. Make changes and save

**Expected Result:**
- ✅ Historical records can be edited
- ✅ No date restrictions
- ✅ Useful for corrections

---

## ✅ Feature 4: Leave Management (Enhanced)

### Test Case 4.1: Intern Applies for Leave

**Steps (as Intern):**
1. Login as intern
2. Go to "Leaves" tab
3. Fill leave form:
   - Start Date: "2024-12-25"
   - End Date: "2024-12-27"
   - Reason: "Holiday break"
4. Click "Submit Request"

**Expected Result:**
- ✅ Success message: "Leave application submitted."
- ✅ Redirect to dashboard
- ✅ Leave appears in history as "Pending"

**Verification:**
```bash
db.leaves.findOne({"user_id": ObjectId("..."), "status": "Pending"})
```

### Test Case 4.2: Admin Sees Pending Request

**Steps (as Admin):**
1. Go to admin dashboard
2. Click "Leave Requests" button
3. Find the pending leave

**Expected Result:**
- ✅ Leave request visible
- ✅ Shows: Intern name, dates, reason
- ✅ Shows approval/rejection buttons

### Test Case 4.3: Admin Approves Leave

**Steps:**
1. In "Leave Requests" section
2. Find pending leave
3. Click ✅ (green checkmark)

**Expected Result:**
- ✅ Success message: "Leave request Approved."
- ✅ Attendance records created for all days
- ✅ Leave status changes to "Approved"

**Verification:**
```bash
# Check attendance records created
db.attendance.find({"leave_id": ObjectId("...")})
# Should return 3 records (25, 26, 27)

# Each record should have:
# - work_type: "Leave"
# - status: "Leave - Approved"
# - login_time: "-"
# - logout_time: "-"
```

### Test Case 4.4: Admin Rejects Leave

**Steps:**
1. Submit new leave request
2. Admin clicks ❌ (red X)

**Expected Result:**
- ✅ Success message: "Leave request Rejected."
- ✅ No attendance records created
- ✅ Leave status changes to "Rejected"
- ✅ User can still work those days

### Test Case 4.5: Leave History Shows Status

**Steps (as Intern):**
1. Go to "Leaves" tab
2. View leave history

**Expected Result:**
- ✅ Shows all leave requests
- ✅ Color-coded badges:
  - Green: "Approved"
  - Red: "Rejected"
  - Yellow: "Pending"

---

## ✅ Feature 5: Block Login on Approved Leave

### Test Case 5.1: Cannot Mark Login During Approved Leave

**Prerequisites:**
- Admin approved leave for Dec 25-27

**Steps (as Intern):**
1. Set calendar to Dec 26
2. Login as intern
3. Try to mark login

**Expected Result:**
- ✅ Error message: "You have confirmed leave today! Cannot mark attendance."
- ✅ Mark Login button not visible
- ✅ Redirect to dashboard

### Test Case 5.2: Can Mark Login When Not on Leave

**Steps:**
1. Select Dec 20 (no approved leave)
2. Try to mark login

**Expected Result:**
- ✅ Mark Login button is visible
- ✅ Can select work type
- ✅ Can submit login

### Test Case 5.3: Can Mark Login When Leave is Rejected

**Prerequisites:**
- Rejected leave application

**Steps:**
1. Select date from rejected leave
2. Try to mark login

**Expected Result:**
- ✅ Login is allowed
- ✅ Leave rejection doesn't block work

---

## ✅ Feature 6: Calendar Color Coding

### Test Case 6.1: Green Color for Office Work

**Prerequisites:**
- Attendance record with work_type: "Office"

**Steps (Intern view):**
1. Go to calendar
2. Check date with office work

**Expected Result:**
- ✅ 🟢 Green dot visible
- ✅ Tooltip shows "Office"
- ✅ Legend shows: Green = Office/Holiday

### Test Case 6.2: Yellow Color for Work From Home

**Prerequisites:**
- Attendance record with work_type: "Work From Home"

**Steps:**
1. Check calendar for WFH day

**Expected Result:**
- ✅ 🟡 Yellow dot visible
- ✅ Tooltip shows "Work From Home"

### Test Case 6.3: Red Color for Approved Leave

**Prerequisites:**
- Approved leave for Dec 25-27

**Steps:**
1. Check calendar for leave dates

**Expected Result:**
- ✅ 🔴 Red dot visible
- ✅ Tooltip shows "Approved Leave"
- ✅ Covers all days of leave

### Test Case 6.4: Red Color for Absent Days

**Prerequisites:**
- No attendance record for past date (not weekend)

**Steps:**
1. Check calendar for absent date

**Expected Result:**
- ✅ 🔴 Red dot visible
- ✅ Tooltip shows "Absent"

### Test Case 6.5: Color Legend Visible

**Steps (Intern Dashboard):**
1. Scroll to calendar section
2. Look for color legend

**Expected Result:**
- ✅ Legend box visible above calendar
- ✅ Shows all 3 colors with meanings:
  - Green dot: Office/Holiday
  - Yellow dot: Work From Home
  - Red dot: Approved Leave/Absent

### Test Case 6.6: Holiday Blocking

**Prerequisites:**
- Company holiday added for Dec 25

**Steps:**
1. Try to mark login on holiday
2. Check calendar for holiday date

**Expected Result:**
- ✅ Cannot mark login
- ✅ Error: "Cannot mark attendance on a holiday or Sunday!"
- ✅ Calendar may show holiday label

### Test Case 6.7: Sunday Blocking

**Steps:**
1. Select a Sunday
2. Try to mark login

**Expected Result:**
- ✅ Cannot mark login
- ✅ Error: "Cannot mark attendance on a holiday or Sunday!"
- ✅ Sunday shows in red on calendar

---

## 🔄 Integration Tests

### Test Case I.1: Complete Leave Flow

**Scenario:** End-to-end leave request process

**Steps:**
1. Intern applies for 3-day leave
2. Admin approves
3. Check calendar shows red dots
4. Try to login on leave day
5. Verify blocked
6. Check attendance report

**Expected Result:**
- ✅ All 3 days show red dots
- ✅ Login blocked with error
- ✅ Report shows "Leave - Approved"
- ✅ Hours show "-"

### Test Case I.2: Time Correction Workflow

**Scenario:** Employee forgets to logout, admin fixes it

**Steps:**
1. Create attendance with login only
2. Admin edits logout time
3. Hours auto-calculated
4. Export report
5. Check calculations in Excel

**Expected Result:**
- ✅ Hours correctly calculated
- ✅ Excel shows updated hours
- ✅ Monthly total includes corrected hours

### Test Case I.3: Work Type Change with Leave

**Scenario:** Change work type after approving leave

**Steps:**
1. Employee works but doesn't mark logout
2. Admin edits time (17:45)
3. Admin changes work type to WFH
4. Check calendar shows yellow
5. Verify hours calculated

**Expected Result:**
- ✅ Calendar shows yellow (WFH)
- ✅ Hours calculated correctly
- ✅ Report shows WFH with hours

### Test Case I.4: Multi-Admin Verification

**Scenario:** Multiple admins making changes

**Steps:**
1. Admin1 creates Admin2
2. Admin2 approves leave
3. Admin1 edits times
4. Check changes persist
5. Both can see updates

**Expected Result:**
- ✅ Admin2 created successfully
- ✅ Leave approval works
- ✅ Time edits apply
- ✅ All changes visible to both admins

---

## 🚨 Error Handling Tests

### Test Case E.1: Invalid Time Format

**Steps:**
1. Try to edit time with invalid format
2. Enter: "25:00:00" (invalid hour)
3. Try to save

**Expected Result:**
- ✅ Appropriate error handling
- ✅ Form validation catches error
- ✅ No invalid data saved

### Test Case E.2: Past Date with Future Time

**Steps:**
1. Select past date
2. Set logout before login (e.g., 09:00 to 08:00)
3. Save changes

**Expected Result:**
- ✅ System detects invalid time
- ✅ Either shows error or adds 24 hours
- ✅ No negative hours

### Test Case E.3: Overlapping Leaves

**Steps:**
1. Create leave for Dec 1-5
2. Create another leave for Dec 3-7
3. Admin approves both

**Expected Result:**
- ✅ No errors
- ✅ Overlapping days don't cause issues
- ✅ Both leaves show as approved

### Test Case E.4: Deleted User Reference

**Steps:**
1. Create leave
2. Admin approves
3. Delete intern
4. Check leave record

**Expected Result:**
- ✅ Orphaned records handled gracefully
- ✅ No system errors
- ✅ Database consistency maintained

---

## 📊 Reporting Tests

### Test Case R.1: Excel Export Includes All Data

**Steps:**
1. Go to admin dashboard
2. Select specific date
3. Click "Export Excel"
4. Open downloaded file

**Expected Result:**
- ✅ File downloads successfully
- ✅ Contains all records
- ✅ Shows: Name, Username, Work Type, Times, Hours, Status
- ✅ Updated times and work types reflected

### Test Case R.2: Intern Report Generation

**Steps:**
1. View intern profile
2. Click "Download Report"

**Expected Result:**
- ✅ All attendance records included
- ✅ Correct date range
- ✅ Hours calculated correctly
- ✅ Work types visible

---

## 🔒 Security Tests

### Test Case S.1: Intern Cannot Add Admin

**Steps:**
1. Login as intern
2. Try to navigate to `/admin/add-admin`
3. Try to POST to endpoint directly

**Expected Result:**
- ✅ Access denied
- ✅ Redirected to login or dashboard
- ✅ No admin created

### Test Case S.2: Cannot View Other User Data

**Steps:**
1. Login as Intern A
2. Try to access Intern B's profile
3. Try to edit Intern B's times

**Expected Result:**
- ✅ Access denied
- ✅ No data leaked
- ✅ System remains secure

### Test Case S.3: Session Validation

**Steps:**
1. Login successfully
2. Clear session cookies
3. Try to access protected route

**Expected Result:**
- ✅ Redirected to login
- ✅ Session required for all operations
- ✅ No data access without session

---

## 🎯 Performance Tests

### Test Case P.1: Large Attendance Data

**Steps:**
1. Create 1000+ attendance records
2. Load admin dashboard
3. View calendar

**Expected Result:**
- ✅ Page loads in < 3 seconds
- ✅ No timeout errors
- ✅ Responsive UI

### Test Case P.2: Bulk Leave Approval

**Steps:**
1. Create 10+ pending leave requests
2. Approve multiple sequentially
3. Check database

**Expected Result:**
- ✅ Each approval completes quickly
- ✅ Attendance records created properly
- ✅ No race conditions

---

## ✅ Sign-Off Checklist

After completing all tests, verify:

- [ ] Feature 1: Add Admin - All tests passed
- [ ] Feature 2: Change Work Type - All tests passed
- [ ] Feature 3: Edit Time - All tests passed
- [ ] Feature 4: Leave Management - All tests passed
- [ ] Feature 5: Block Login on Leave - All tests passed
- [ ] Feature 6: Calendar Colors - All tests passed
- [ ] Integration Tests - All passed
- [ ] Error Handling - Appropriate
- [ ] Security - No vulnerabilities found
- [ ] Performance - Acceptable response times

---

## 📝 Test Report Template

```
Date: [Date]
Tester: [Name]
Version: 2.0

Feature 1: Add Admin
- Test 1.1: ✅ PASSED / ❌ FAILED
- Test 1.2: ✅ PASSED / ❌ FAILED
- Test 1.3: ✅ PASSED / ❌ FAILED
- Test 1.4: ✅ PASSED / ❌ FAILED

[Continue for all features...]

Overall Status: ✅ APPROVED / ⚠️ NEEDS FIXES

Issues Found:
1. [Issue description]
2. [Issue description]

Sign-Off: _______________
```

---

## 🐛 Bug Report Format

If you find issues:

```
Title: [Brief description]
Severity: Critical / High / Medium / Low
Feature: [Feature name]

Steps to Reproduce:
1. Step 1
2. Step 2

Expected Result:
[What should happen]

Actual Result:
[What actually happened]

Environment:
- Browser: 
- OS: 
- Database:
```

---

## 📞 Support

For testing assistance, review:
- FEATURES_IMPLEMENTED.md
- QUICK_START_GUIDE.md
- API_DOCUMENTATION.md
- DATABASE_SCHEMA.md

---

**Testing Completed:** _______
**Tester Name:** _______
**Version:** 2.0
**Date:** _______
