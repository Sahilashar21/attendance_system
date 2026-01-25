# Database Schema Documentation

## Overview
The attendance system uses MongoDB with the following collections:

---

## Collections

### 1. **users** Collection
Stores user information (admins and interns)

```json
{
  "_id": ObjectId,
  "full_name": "John Doe",
  "username": "john_doe",
  "password": "encrypted_pass",
  "role": "admin" | "intern",
  "daily_hours": 8,           // Only for interns
  "joining_date": "2024-01-15",  // Optional
  "ending_date": "2024-12-31"    // Optional
}
```

**Fields:**
- `_id`: Unique MongoDB ID
- `full_name`: Display name
- `username`: Login username (unique)
- `password`: Login password (plain text in current version)
- `role`: Either "admin" or "intern"
- `daily_hours`: Expected daily work hours (default: 8)
- `joining_date`: Date intern started (YYYY-MM-DD format)
- `ending_date`: Date intern ends (YYYY-MM-DD format)

**Indexes Recommended:**
```javascript
db.users.createIndex({ "username": 1 }, { unique: true })
```

---

### 2. **attendance** Collection
Records daily work attendance

```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "date": "2024-12-20",
  "work_type": "Office" | "Work From Home" | "Leave" | "Holiday",
  "login_time": "09:30:00",
  "logout_time": "17:45:00",
  "status": "Present" | "Leave - Approved" | "Absent",
  "hours_worked": "8h 15m",
  "leave_id": ObjectId    // Only when work_type is "Leave"
}
```

**Fields:**
- `_id`: Unique record ID
- `user_id`: Reference to users collection
- `date`: Work date (YYYY-MM-DD format)
- `work_type`: Type of work done
  - "Office" - worked from office
  - "Work From Home" - worked remotely
  - "Leave" - approved leave day
  - "Holiday" - company holiday
- `login_time`: Timestamp of login (HH:MM:SS format)
- `logout_time`: Timestamp of logout (HH:MM:SS format)
- `status`: Attendance status
  - "Present" - marked attendance
  - "Leave - Approved" - approved leave
  - "Absent" - missed work
- `hours_worked`: Calculated duration (XhYm format)
- `leave_id`: Reference to leaves collection (optional)

**Indexes Recommended:**
```javascript
db.attendance.createIndex({ "user_id": 1, "date": 1 }, { unique: true })
db.attendance.createIndex({ "date": 1 })
```

---

### 3. **leaves** Collection
Stores leave requests from interns

```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "start_date": "2024-12-25",
  "end_date": "2024-12-27",
  "reason": "Family emergency",
  "status": "Pending" | "Approved" | "Rejected",
  "applied_on": ISODate("2024-12-20T10:30:00Z")
}
```

**Fields:**
- `_id`: Unique leave request ID
- `user_id`: Reference to users collection
- `start_date`: First day of leave (YYYY-MM-DD)
- `end_date`: Last day of leave (YYYY-MM-DD)
- `reason`: Reason for leave request
- `status`: Current approval status
  - "Pending" - awaiting admin approval
  - "Approved" - admin approved
  - "Rejected" - admin rejected
- `applied_on`: When request was submitted (ISO timestamp)

**Indexes Recommended:**
```javascript
db.leaves.createIndex({ "user_id": 1 })
db.leaves.createIndex({ "status": 1 })
```

---

### 4. **holidays** Collection
Stores company holidays

```json
{
  "_id": ObjectId,
  "name": "Christmas",
  "date": "2024-12-25"
}
```

**Fields:**
- `_id`: Unique holiday ID
- `name`: Holiday name
- `date`: Holiday date (YYYY-MM-DD format)

**Indexes Recommended:**
```javascript
db.holidays.createIndex({ "date": 1 }, { unique: true })
```

---

## Relationships

### User → Attendance
```
users._id  ← (1 to Many) → attendance.user_id
```
One user can have many attendance records

### User → Leaves
```
users._id  ← (1 to Many) → leaves.user_id
```
One user can have many leave requests

### Leaves → Attendance
```
leaves._id  → (0 to Many) → attendance.leave_id
```
One leave request can have multiple attendance records (one per day)

---

## Example Queries

### Find all attendance for a user
```javascript
db.attendance.find({ "user_id": ObjectId("...") })
```

### Find pending leave requests
```javascript
db.leaves.find({ "status": "Pending" })
```

### Find leaves overlapping a date range
```javascript
db.leaves.find({
  "start_date": { "$lte": "2024-12-27" },
  "end_date": { "$gte": "2024-12-25" },
  "status": "Approved"
})
```

### Find company holidays in December
```javascript
db.holidays.find({ "date": { "$regex": "^2024-12" } })
```

### Get user attendance for a month
```javascript
db.attendance.find({
  "user_id": ObjectId("..."),
  "date": { "$regex": "^2024-12" }
})
```

### Update work type after approval
```javascript
db.attendance.updateOne(
  { "_id": ObjectId("...") },
  { "$set": { "work_type": "Work From Home" } }
)
```

---

## Data Validation Rules

### Users
- ✅ `username` must be unique
- ✅ `role` must be "admin" or "intern"
- ✅ `daily_hours` must be positive integer
- ✅ `joining_date` < `ending_date` (if both present)

### Attendance
- ✅ One record per user per date
- ✅ `date` format: YYYY-MM-DD
- ✅ `login_time` format: HH:MM:SS
- ✅ `logout_time` format: HH:MM:SS
- ✅ `work_type` must be valid type
- ✅ `hours_worked` auto-calculated from times

### Leaves
- ✅ `start_date` ≤ `end_date`
- ✅ `status` must be valid status
- ✅ `reason` must not be empty
- ✅ Overlapping leaves allowed but must be reviewed

### Holidays
- ✅ `date` must be unique
- ✅ Date format: YYYY-MM-DD

---

## Migration Notes

### If upgrading from previous version:

1. **Add fields to users**
   ```javascript
   db.users.updateMany(
     { "role": "intern" },
     { $set: { "daily_hours": 8 } }
   )
   ```

2. **Update attendance records with leave_id**
   ```javascript
   db.attendance.updateMany(
     { "work_type": "Leave" },
     { $set: { "leave_id": null } }
   )
   ```

3. **Ensure indexes exist**
   ```javascript
   // Run all index creation commands from above
   ```

---

## Backup Strategy

### Regular Backups
```bash
# MongoDB backup
mongodump --db attendance_system --out /path/to/backup

# MongoDB restore
mongorestore --db attendance_system /path/to/backup/attendance_system
```

### Atlas Backup (if using MongoDB Atlas)
- Automatic daily backups available
- 30-day retention by default
- Point-in-time restore available

---

## Performance Considerations

### Indexes Created
```javascript
// Primary access patterns
db.users.createIndex({ "username": 1 }, { unique: true })
db.attendance.createIndex({ "user_id": 1, "date": 1 }, { unique: true })
db.attendance.createIndex({ "date": 1 })
db.leaves.createIndex({ "user_id": 1 })
db.leaves.createIndex({ "status": 1 })
db.holidays.createIndex({ "date": 1 }, { unique: true })
```

### Query Optimization Tips
1. Always filter by user_id when possible
2. Use date range queries with indexes
3. Limit result sets when fetching history
4. Cache holiday list (changes infrequently)

---

## Sample Data

### New Admin
```json
{
  "full_name": "Admin User",
  "username": "admin_new",
  "password": "admin@123",
  "role": "admin"
}
```

### New Intern with Dates
```json
{
  "full_name": "John Smith",
  "username": "john_smith",
  "password": "pass@123",
  "role": "intern",
  "daily_hours": 8,
  "joining_date": "2024-01-15",
  "ending_date": "2024-12-31"
}
```

### Sample Attendance
```json
{
  "user_id": ObjectId("..."),
  "date": "2024-12-20",
  "work_type": "Office",
  "login_time": "09:30:00",
  "logout_time": "17:45:00",
  "status": "Present",
  "hours_worked": "8h 15m"
}
```

### Sample Leave Request
```json
{
  "user_id": ObjectId("..."),
  "start_date": "2024-12-25",
  "end_date": "2024-12-27",
  "reason": "Family vacation",
  "status": "Approved",
  "applied_on": ISODate("2024-12-20T10:30:00Z")
}
```

---

## Error Handling

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Duplicate attendance record | Multiple login attempts | Check unique index on (user_id, date) |
| Incorrect hours calculated | Time format error | Ensure HH:MM:SS format |
| Leave not blocking login | Status not "Approved" | Verify status in database |
| User not found | user_id incorrect | Check ObjectId format |
| Holiday not showing | Date format mismatch | Use YYYY-MM-DD format |

---

## Maintenance Tasks

### Monthly
- [ ] Archive old attendance records (> 6 months)
- [ ] Verify database integrity
- [ ] Check for orphaned records

### Quarterly
- [ ] Analyze database size
- [ ] Review index usage
- [ ] Backup complete database

### Yearly
- [ ] Purge rejected leave requests (> 1 year)
- [ ] Reorganize collections
- [ ] Review access logs

---

## Conclusion

This database schema supports all features of the attendance system including:
- ✅ User management (admins & interns)
- ✅ Daily attendance tracking
- ✅ Work type classification
- ✅ Leave management & approval
- ✅ Holiday tracking
- ✅ Time editing for admin

For questions or issues, refer to the API documentation in app.py.
