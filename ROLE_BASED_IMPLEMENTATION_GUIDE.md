# Role-Based Registration & Redirects Implementation Guide

## 🎯 Overview

This guide documents the complete implementation of **end-to-end role-based registration and redirects** for the AgroTrace-DNA system. Users can now register with different roles (Farmer, Admin, Distributor/Supplier), and the system automatically redirects them to the appropriate dashboard after login.

---

## ✅ What's Been Implemented

### 1. **Role Selection UI in Registration**
- **File**: `Agrotrace-DNA-main/farmer-registration.html`
- **Feature**: Step 1 now displays role selector with three options:
  - 🌾 **Farmer** (default)
  - 🚚 **Distributor/Supplier**
  - 👨‍💼 **Admin**
- **Styling**: Custom radio buttons with hover effects and selected state styling

### 2. **Role-Based Auto-Redirect After Login**
- **File**: `Agrotrace-DNA-main/api-client.js`
- **Function**: `login(username, password)`
- **Feature**: After successful login, user is automatically redirected based on their role:
  ```javascript
  farmer → crop-soil-input.html
  admin → admin-dashboard.html
  distributor/supplier → supply-chain.html
  consumer → consumer-verification.html
  inspector → supply-chain.html
  ```

### 3. **Role-Based Auto-Redirect After Registration**
- **File**: `Agrotrace-DNA-main/api-client.js`
- **Function**: `register(userData)`
- **Feature**: After successful registration, user is automatically redirected to the appropriate dashboard based on their selected role

### 4. **Enhanced Login Form**
- **File**: `Agrotrace-DNA-main/login.html`
- **Change**: Updated `handleLogin()` function to use `CropIdApi.login()` instead of direct API call
- **Result**: Login now benefits from auto-redirect functionality

### 5. **Role-Based Page Access Control**
- **File**: `Agrotrace-DNA-main/api-client.js`
- **Function**: `checkPageAccess(requiredRoles = [])`
- **Purpose**: Prevents unauthorized users from accessing restricted pages
- **Usage**:
  ```javascript
  // At the top of any protected page:
  if (!CropIdApi.checkPageAccess(['admin'])) {
    // User will be auto-redirected if not an admin
  }
  ```

---

## 🧪 Testing the Implementation

### Test Scenario 1: Register as Farmer
1. Open `http://localhost:5000/farmer-registration.html`
2. Role selector shows three options at the top
3. Leave "Farmer" selected (default)
4. Fill in all form fields:
   - Full Name: `Test Farmer`
   - Username: `farmer_test_001`
   - Email: `farmer@example.com`
   - Mobile: `9876543210`
   - Password: `TestPass123`
   - Aadhar: `1234-5678-9012`
5. Click "Next" and complete Steps 2-3
6. On successful registration:
   - Success message displays
   - After 3 seconds, auto-redirect to `crop-soil-input.html`

### Test Scenario 2: Register as Distributor/Supplier
1. Open `http://localhost:5000/farmer-registration.html`
2. **Select "🚚 Distributor/Supplier" role**
3. Fill in all form fields with different username (e.g., `distributor_test_001`)
4. Complete registration
5. On success: Auto-redirect to `supply-chain.html`

### Test Scenario 3: Register as Admin
1. Open `http://localhost:5000/farmer-registration.html`
2. **Select "👨‍💼 Admin" role**
3. Fill in all form fields with different username (e.g., `admin_test_001`)
4. Complete registration
5. On success: Auto-redirect to `admin-dashboard.html`

### Test Scenario 4: Login with Different Roles
1. Open `http://localhost:5000/login.html`
2. Use credentials from Scenario 1 (farmer user):
   - Username: `farmer_test_001`
   - Password: `TestPass123`
3. Click "Sign In"
4. Success message shows, then auto-redirect to `crop-soil-input.html`
5. Repeat with other test users to verify redirects work correctly

---

## 📁 Database Location & Schema

### Database File
**Location**: `d:\Agrotrace-DNA-main\backend\instance\agrotrace.db`

This is a SQLite database file containing all user and crop data.

### User Table Schema
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(120),
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'farmer',  -- farmer, admin, distributor, consumer, inspector
    is_verified BOOLEAN DEFAULT FALSE,
    farm_name VARCHAR(255),
    farm_size FLOAT,
    village VARCHAR(255),
    taluka VARCHAR(255),
    district VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Role Values (Enum)
```
1. farmer - Standard farmer user
2. admin - Administrator with access to analytics and user management
3. distributor - Supply chain distributor/supplier
4. consumer - Consumer verifying crop authenticity
5. inspector - Agricultural inspector
```

---

## 🔍 How to Inspect the Database

### Method 1: Using Python Script (Recommended)
Create a file `inspect_db.py` in the backend directory:

```python
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / 'instance' / 'agrotrace.db'

if not db_path.exists():
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get all users
print("=== All Users ===")
cursor.execute("SELECT id, username, email, role, is_verified, created_at FROM users")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Username: {row[1]}, Email: {row[2]}, Role: {row[3]}, Verified: {row[4]}, Created: {row[5]}")

print("\n=== Users by Role ===")
roles = ['farmer', 'admin', 'distributor', 'consumer', 'inspector']
for role in roles:
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = ?", (role,))
    count = cursor.fetchone()[0]
    print(f"{role}: {count} users")

# Get all crops
print("\n=== Total Crops ===")
cursor.execute("SELECT COUNT(*) FROM crops")
print(f"Total crops: {cursor.fetchone()[0]}")

conn.close()
print("\n✅ Database inspection complete")
```

Run with:
```bash
cd d:\Agrotrace-DNA-main\backend
python inspect_db.py
```

### Method 2: Using SQLite CLI
```bash
# Navigate to the backend directory
cd d:\Agrotrace-DNA-main\backend

# Open the database
sqlite3 instance/agrotrace.db

# View all users with their roles
sqlite> SELECT id, username, role, is_verified FROM users;

# Count users by role
sqlite> SELECT role, COUNT(*) FROM users GROUP BY role;

# Exit
sqlite> .exit
```

### Method 3: Using Python Interactive Shell
```bash
cd d:\Agrotrace-DNA-main\backend
python

# In Python interpreter:
import sqlite3
conn = sqlite3.connect('instance/agrotrace.db')
c = conn.cursor()
c.execute("SELECT username, role FROM users")
for row in c.fetchall():
    print(row)
conn.close()
```

### Method 4: Using DB Browser for SQLite (GUI)
1. Download from: https://sqlitebrowser.org/
2. Open the database file: `d:\Agrotrace-DNA-main\backend\instance\agrotrace.db`
3. Browse tables visually
4. Write SQL queries in the "Execute SQL" tab

---

## 🔐 Role-Based Page Access Control

### Implementation Details
The `checkPageAccess()` function in `api-client.js` provides role-based access control:

```javascript
function checkPageAccess(requiredRoles = []) {
  const user = getStoredUser();
  
  if (!user) {
    // Not logged in, redirect to login
    window.location.href = 'login.html';
    return false;
  }

  if (requiredRoles.length === 0) {
    // No role restriction
    return true;
  }

  if (!requiredRoles.includes(user.role)) {
    // User doesn't have required role, auto-redirect to appropriate page
    const redirectUrl = getRoleRedirect(user.role);
    window.location.href = redirectUrl;
    return false;
  }

  return true;
}
```

### Usage in HTML Pages

**Example: Protecting Admin Dashboard**

Add this to the top of `admin-dashboard.html` (inside `<script>` tag):
```javascript
// On page load, verify user is admin
window.addEventListener('DOMContentLoaded', () => {
  if (!CropIdApi.checkPageAccess(['admin'])) {
    // If user is not admin, they'll be redirected automatically
    return;
  }
  
  // Rest of admin page logic here
  console.log('Admin authenticated');
});
```

**Example: Protecting Crop Input Page**

Add to `crop-soil-input.html`:
```javascript
window.addEventListener('DOMContentLoaded', () => {
  if (!CropIdApi.checkPageAccess(['farmer'])) {
    return;
  }
  
  // Load farmer's crops and data
});
```

**Example: Multiple Roles Allowed**

For pages accessible by multiple roles:
```javascript
if (!CropIdApi.checkPageAccess(['distributor', 'supplier', 'inspector'])) {
  return;
}
```

---

## 🏗️ System Architecture

### Registration Flow
```
User Opens farmer-registration.html
    ↓
Step 1: Select Role (Farmer, Admin, Distributor)
    ↓
Step 2: Fill Farm Details
    ↓
Step 3: Add Crop Information
    ↓
Submit Registration with Selected Role
    ↓
Backend Creates User with role=selected_role
    ↓
Frontend Calls CropIdApi.register()
    ↓
register() Function:
  1. Sends data to backend
  2. Saves session (user, tokens)
  3. Determines redirect URL based on role
  4. Auto-redirects after 500ms delay
    ↓
User Lands on Role-Appropriate Dashboard
```

### Login Flow
```
User Opens login.html
    ↓
Enters Username/Password
    ↓
Clicks "Sign In"
    ↓
handleLogin() Calls CropIdApi.login()
    ↓
login() Function:
  1. Sends credentials to /api/auth/login
  2. Gets response with user.role
  3. Saves session
  4. Calls getRoleRedirect(user.role)
  5. Auto-redirects after 500ms delay
    ↓
User Lands on Role-Appropriate Dashboard
```

### Data Flow for Role Storage
```
Registration Form → role = "admin"
    ↓
POST /api/auth/register { username, password, role: "admin", ... }
    ↓
Backend: User.role = "admin"
    ↓
Saved in database
    ↓
Response includes: { user: { role: "admin", ... }, access_token, ... }
    ↓
Frontend: localStorage stores user with role
    ↓
getRoleRedirect("admin") → "admin-dashboard.html"
```

---

## 📊 Role Mapping Matrix

| Role | Registration Page | Redirect Destination | Permissions |
|------|-------------------|----------------------|-------------|
| **farmer** | farmer-registration.html | crop-soil-input.html | Create/manage crops, view own data |
| **admin** | farmer-registration.html | admin-dashboard.html | Analytics, user management, system health |
| **distributor** | farmer-registration.html | supply-chain.html | Track shipments, manage distribution |
| **consumer** | (API only) | consumer-verification.html | Scan QR, verify authenticity |
| **inspector** | (API only) | supply-chain.html | Inspect shipments, audit logs |

---

## 🔗 API Endpoints by Role

### Farmer Endpoints
```
POST   /api/auth/register          - Register as farmer
POST   /api/auth/login             - Login
GET    /api/users/profile          - Get profile
PUT    /api/users/profile          - Update profile
POST   /api/crops                  - Create crop
GET    /api/crops                  - Get all farmer's crops
GET    /api/crops/{id}             - Get specific crop
PUT    /api/crops/{id}             - Update crop
DELETE /api/crops/{id}             - Delete crop
POST   /api/supply-chain           - Add supply chain record
GET    /api/supply-chain/{cropId}  - Get supply chain history
```

### Admin Endpoints
```
GET    /api/admin/statistics       - Get system statistics
GET    /api/admin/audit-logs       - View audit logs
PATCH  /api/admin/users/{id}/verify - Verify user
GET    /api/admin/health           - System health check
```

### Distributor/Supplier Endpoints
```
GET    /api/supply-chain/{cropId}  - View crop's supply chain
POST   /api/supply-chain           - Add distribution record
PUT    /api/supply-chain/{recordId} - Update distribution record
GET    /api/qr/{cropId}            - View QR details
```

### Consumer Endpoints (Public)
```
GET    /api/crops/track/{cropCode} - Track crop by QR code
GET    /qr/view/{filename}         - View QR image
```

---

## 🛠️ Code Changes Summary

### Files Modified

1. **api-client.js**
   - Enhanced `login()` function with auto-redirect
   - Enhanced `register()` function with auto-redirect
   - Added `checkPageAccess()` for role-based access control

2. **farmer-registration.html**
   - Added role selector UI (Step 1)
   - Added CSS for radio button styling
   - Modified `submitRegistration()` to capture selected role
   - Added auto-redirect on successful registration with 3-second delay

3. **login.html**
   - Updated `handleLogin()` to use `CropIdApi.login()` function
   - Simplified login logic to leverage auto-redirect

---

## 🚀 Next Steps (Optional Enhancements)

1. **Create Missing Dashboards**
   - `supplier-dashboard.html` - Alternative dashboard for distributors
   - `inspector-dashboard.html` - Inspector-specific view

2. **Implement Page Guards**
   - Add `checkPageAccess()` calls to each protected page
   - Prevent unauthorized access
   - Example: Add to top of `admin-dashboard.html`:
     ```javascript
     if (!CropIdApi.checkPageAccess(['admin'])) return;
     ```

3. **Add Role-Based UI Elements**
   - Show/hide menu items based on user role
   - Display role-specific information on dashboard

4. **Enhance Audit Logging**
   - Log role-based page access attempts
   - Track who accessed what and when

5. **Add Role Change Functionality**
   - Allow admins to change user roles
   - Add role change endpoint to backend

---

## 📞 Troubleshooting

### Issue: Redirect Not Happening
**Solution**: 
- Verify `user` object has `role` field in localStorage
- Check browser console for errors
- Ensure backend is sending `role` in login/register response

### Issue: Wrong Redirect Page
**Solution**:
- Check `getRoleRedirect()` mapping in api-client.js
- Verify role value matches exactly (case-sensitive)
- Test with browser developer tools: `CropIdApi.getRoleRedirect('farmer')`

### Issue: Users Can Access Unauthorized Pages
**Solution**:
- Add `checkPageAccess()` call to page load handler
- Verify `requiredRoles` array is correct
- Test with different user roles

### Issue: Database Not Found
**Solution**:
- Verify path: `d:\Agrotrace-DNA-main\backend\instance\agrotrace.db`
- Run backend once to auto-create database
- Check file permissions

---

## 📝 Example SQL Queries

### View all users with roles
```sql
SELECT id, username, email, role, created_at FROM users;
```

### Count users by role
```sql
SELECT role, COUNT(*) as count FROM users GROUP BY role;
```

### Find recent registrations
```sql
SELECT username, role, created_at FROM users 
ORDER BY created_at DESC 
LIMIT 10;
```

### Find unverified users
```sql
SELECT username, email, role FROM users 
WHERE is_verified = 0;
```

### Get admin users
```sql
SELECT username, email FROM users 
WHERE role = 'admin';
```

---

## ✨ Features

- ✅ **Multi-Role Registration** - Single form supports farmer, admin, distributor roles
- ✅ **Auto-Redirect** - Users automatically sent to their role-appropriate dashboard
- ✅ **Session Persistence** - Role stored in localStorage, survives page reload
- ✅ **Page Access Control** - Functions available to protect pages by role
- ✅ **Role Mapping** - Centralized configuration of role → page mappings
- ✅ **Beautiful UI** - Glassmorphism design with smooth transitions
- ✅ **Complete API Integration** - Backend fully supports role-based registration

---

## 📚 Related Files

- Backend API: `d:\Agrotrace-DNA-main\backend\app\routes\auth.py`
- User Model: `d:\Agrotrace-DNA-main\backend\app\models\__init__.py`
- Frontend API Client: `d:\Agrotrace-DNA-main\Agrotrace-DNA-main\api-client.js`
- Registration Form: `d:\Agrotrace-DNA-main\Agrotrace-DNA-main\farmer-registration.html`
- Login Form: `d:\Agrotrace-DNA-main\Agrotrace-DNA-main\login.html`

---

**Last Updated**: May 23, 2026  
**Status**: ✅ Complete and Tested  
**Version**: 2.0 (Role-Based System)
