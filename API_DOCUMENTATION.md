# API Documentation - New Endpoints

## Overview
This document details the new API endpoints added to the attendance system.

---

## New Endpoints

### 1. Add Admin
**Endpoint:** `POST /admin/add-admin`

**Authentication:** Admin role required

**Request Parameters:**
```json
{
  "full_name": "John Manager",
  "username": "admin_john",
  "password": "secure_password"
}
```

**Response:**
- Success: Redirect to admin dashboard with success message
- Error: Duplicate username → "Username already exists!"
- Error: Missing fields → "All fields are required!"

**Example cURL:**
```bash
curl -X POST http://localhost:5000/admin/add-admin \
  -d "full_name=John Manager&username=admin_john&password=secure_pass"
```

**Database Impact:**
- Creates new document in `users` collection
- Sets `role` to "admin"

---

### 2. Change Work Type
**Endpoint:** `POST /admin/change-work-type`

**Authentication:** Admin role required

**Request Parameters:**
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "date": "2024-12-20",
  "work_type": "Office" | "Work From Home"
}
```

**Response:**
- Success: "Work type updated successfully!"
- Error: "Attendance record not found!"

**Example cURL:**
```bash
curl -X POST http://localhost:5000/admin/change-work-type \
  -d "user_id=507f1f77bcf86cd799439011&date=2024-12-20&work_type=Work%20From%20Home"
```

**Database Impact:**
- Updates `work_type` in attendance record
- Preserves other fields

---

### 3. Edit Time (Missed Logout)
**Endpoint:** `POST /admin/edit-time`

**Authentication:** Admin role required

**Request Parameters:**
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "date": "2024-12-20",
  "login_time": "09:30:00",      // Optional
  "logout_time": "17:45:00"       // Optional
}
```

**Response:**
- Success: "Attendance time updated successfully!"
- Error: "Attendance record not found!"

**Special Behavior:**
- If logout_time is provided, `hours_worked` is auto-calculated
- Handles next-day logout (negative time difference)
- Both fields are optional but at least one must be provided

**Auto-Calculation Logic:**
```
If logout_time provided:
  difference = logout_time - login_time
  If difference < 0:
    difference = difference + 24 hours (next day)
  hours_worked = HhMm format
```

**Example cURL:**
```bash
curl -X POST http://localhost:5000/admin/edit-time \
  -d "user_id=507f1f77bcf86cd799439011&date=2024-12-20&logout_time=18:00:00"
```

**Database Impact:**
- Updates `login_time` if provided
- Updates `logout_time` if provided
- Auto-updates `hours_worked`

---

### 4. Manage Leave (Enhanced)
**Endpoint:** `POST /admin/manage-leave`

**Authentication:** Admin role required

**Request Parameters:**
```json
{
  "leave_id": "507f1f77bcf86cd799439011",
  "action": "Approved" | "Rejected"
}
```

**Response:**
- Success: "Leave request Approved." or "Leave request Rejected."

**Special Behavior (on Approval):**
- Creates attendance records for each day of leave
- Sets `work_type` to "Leave"
- Sets `status` to "Leave - Approved"
- Associates `leave_id` to each record
- Does NOT block previous daily records

**Example cURL:**
```bash
curl -X POST http://localhost:5000/admin/manage-leave \
  -d "leave_id=507f1f77bcf86cd799439011&action=Approved"
```

**Database Impact on Approval:**
```javascript
// For each day from start_date to end_date:
{
  "user_id": ObjectId,
  "date": "YYYY-MM-DD",
  "work_type": "Leave",
  "login_time": "-",
  "logout_time": "-",
  "status": "Leave - Approved",
  "hours_worked": "-",
  "leave_id": ObjectId(leave_id)
}
```

---

## Modified Endpoints

### Mark Login (Enhanced)
**Endpoint:** `POST /intern/mark-login`

**Previous Behavior:** Blocked on holidays/Sundays

**New Behavior:**
- ✅ Checks for approved leave first
- ✅ Blocks if approved leave exists
- ✅ Then checks for holiday/Sunday
- ✅ Then checks for existing record

**New Error Message:**
```
"You have confirmed leave today! Cannot mark attendance."
```

**Request Parameters:**
```json
{
  "work_type": "Office" | "Work From Home"
}
```

**Approval Logic (in order):**
```python
1. Check for approved leave on this date
   - If found: REJECT with error message
   
2. Check if date is holiday or Sunday
   - If yes: REJECT with error message
   
3. Check if record already exists
   - If yes: REJECT with warning
   
4. Create new attendance record
   - Sets login_time to current time
   - Sets status to "Present"
   - Sets logout_time to None
```

---

## Calendar Logic Updates

### Intern Dashboard Calendar
**File:** `app.py` lines 255-280

**Color Display Logic (priority order):**
```python
if attendance exists for date:
    if "home" in work_type:
        color = YELLOW   # Work from home
    elif "leave" in work_type:
        color = RED      # Approved leave
    else:
        color = GREEN    # Office work
        
elif approved leave on this date:
    color = RED         # Approved leave (no attendance record yet)
    
elif is company holiday:
    color = GREEN       # Holiday
    
elif is past date (not in future):
    color = RED         # Absent
```

---

## Request/Response Examples

### Complete Flow: Employee Applies for Leave

**Step 1: Intern applies for leave**
```bash
POST /intern/apply-leave
{
  "start_date": "2024-12-25",
  "end_date": "2024-12-27",
  "reason": "Family vacation"
}
```
Response: Redirect to intern_dashboard
Database: Creates leave document with status="Pending"

**Step 2: Admin views pending requests**
```bash
GET /admin (check pending_leaves in context)
```
Response: Displays leave in "Leave Requests" section

**Step 3: Admin approves leave**
```bash
POST /admin/manage-leave
{
  "leave_id": "607f1f77bcf86cd799439011",
  "action": "Approved"
}
```
Response: "Leave request Approved."
Database:
- Updates leave.status = "Approved"
- Creates 3 attendance records (25th, 26th, 27th)

**Step 4: Intern tries to login on leave day**
```bash
POST /intern/mark-login
{
  "work_type": "Office"
}
```
Response: "You have confirmed leave today! Cannot mark attendance."
Action: Redirect to intern_dashboard

**Step 5: Intern views calendar**
```bash
GET /intern
```
Response: Dec 25-27 show RED dots for "Approved Leave"

---

## Error Handling

### Standard Error Responses

| Code | Message | Cause |
|------|---------|-------|
| 500 | "Username already exists!" | Duplicate username |
| 500 | "All fields are required!" | Missing form fields |
| 500 | "Attendance record not found!" | user_id or date invalid |
| 500 | "You have confirmed leave today!" | Approved leave exists |
| 500 | "Cannot mark attendance on holiday!" | Sunday or holiday date |
| 500 | "Login already marked today!" | Duplicate login attempt |

---

## Rate Limiting
None currently implemented. Consider adding for production:
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: session.get('user_id'))

@app.route('/admin/edit-time', methods=['POST'])
@limiter.limit("10 per hour")
def edit_time():
    ...
```

---

## Authentication

All endpoints require:
1. Valid session with `user_id`
2. Specific role (admin or intern)

**Role Requirements:**
- `/admin/*` → Requires `role="admin"`
- `/intern/*` → Requires `role="intern"`

**Session Management:**
```python
# Valid session
session["user_id"] = str(user["_id"])

# Invalid session triggers
redirect(url_for("login"))
```

---

## Data Format Specifications

### Date Format
```
YYYY-MM-DD (2024-12-25)
Required for: date, start_date, end_date
```

### Time Format
```
HH:MM:SS (09:30:00)
Required for: login_time, logout_time
24-hour format
Timezone: IST (Asia/Kolkata)
```

### Hours Format
```
XhYm (8h 30m)
Auto-generated, read-only
Examples: 1h 0m, 8h 45m, 12h 15m
```

### ObjectId Format
```
507f1f77bcf86cd799439011
MongoDB ObjectId
24 character hex string
```

---

## Security Considerations

### Input Validation
```python
✅ Username uniqueness check
✅ Role validation
✅ Date format validation
✅ Time format validation
✅ User ownership verification
```

### Injection Prevention
```python
✅ Using MongoDB queries (not SQL)
✅ No raw string concatenation
✅ Form data validated before use
```

### Authorization
```python
✅ Role-based access control
✅ User cannot modify other users' data
✅ Admin-only operations protected
```

---

## Testing Recommendations

### Unit Tests
```python
def test_add_admin_valid():
    # Test successful admin creation
    
def test_add_admin_duplicate_username():
    # Test username uniqueness
    
def test_change_work_type():
    # Test work type update
    
def test_edit_time_calculation():
    # Test hours auto-calculation
    
def test_block_login_on_leave():
    # Test approved leave blocks login
```

### Integration Tests
```python
def test_complete_leave_flow():
    # Apply → Approve → Block login → Calendar update
    
def test_time_edit_with_hours_calc():
    # Edit time and verify hours
    
def test_admin_creation():
    # Create admin and verify login
```

---

## Performance Metrics

### Expected Response Times
- Add Admin: < 100ms
- Change Work Type: < 50ms
- Edit Time: < 100ms (includes calculation)
- Manage Leave: < 500ms (creates multiple records)

### Database Load
- Add Admin: 1 write operation
- Change Work Type: 1 update operation
- Edit Time: 1 update operation
- Manage Leave: 1 update + N insert operations (N = days of leave)

---

## Version History

### Version 2.0 (Current)
- ✅ Add admin functionality
- ✅ Change work type
- ✅ Edit times with auto-calculation
- ✅ Enhanced leave management
- ✅ Calendar color coding
- ✅ Leave approval blocking

### Version 1.0 (Previous)
- Basic attendance marking
- Holiday management
- Leave application
- Basic admin dashboard

---

## Future API Endpoints

### Planned (Not Yet Implemented)
- `GET /admin/report/monthly` - Monthly report generation
- `POST /admin/leave/bulk-approve` - Bulk leave approval
- `GET /admin/audit-log` - Attendance change history
- `POST /admin/attendance/import` - Bulk attendance import
- `DELETE /admin/attendance/{id}` - Delete attendance record

---

## Support & Documentation

For issues or clarifications:
1. Check FEATURES_IMPLEMENTED.md
2. Review QUICK_START_GUIDE.md
3. Check DATABASE_SCHEMA.md
4. Review app.py source code
5. Check Flask error logs

---

## License & Usage

This API is part of the Attendance Management System.
For commercial use, ensure proper licensing agreement.

Document Version: 1.0
Last Updated: 2024-12-20
Maintainer: [Your Name/Team]
