# Agrotrace-DNA — Complete Project Guide

## 🎯 Project Status: FULLY FUNCTIONAL

**Last Updated:** May 23, 2026  
**Overall Completion:** 95% ✅

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [What's Complete](#whats-complete)
3. [Database Structure](#database-structure)
4. [Installation & Setup](#installation--setup)
5. [Running the Project](#running-the-project)
6. [Testing the Complete Workflow](#testing-the-complete-workflow)
7. [API Endpoints Reference](#api-endpoints-reference)
8. [Database Details](#database-details)
9. [Deployment Guide](#deployment-guide)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview

**Agrotrace-DNA** is a comprehensive agricultural supply chain tracking system that provides:

- **Digital Crop Identity**: Unique DNA-based QR codes for every crop batch
- **Soil Intelligence**: Track soil parameters (pH, nitrogen, moisture, potassium, phosphorus)
- **Supply Chain Transparency**: Monitor crop movement from farm to consumer
- **Role-Based Access**: Admin, Farmer, Distributor, Inspector, Consumer roles
- **Complete Traceability**: Every step recorded with timestamps and environmental data
- **Organic Certification**: Track organic status throughout the supply chain

### Key Features
✅ JWT Authentication with refresh tokens  
✅ Role-based access control (5 user roles)  
✅ SQLite/PostgreSQL database  
✅ QR code generation and management  
✅ Audit logging for compliance  
✅ Docker containerization  
✅ CI/CD pipeline (GitHub Actions)  
✅ Comprehensive REST API (27+ endpoints)  

---

## What's Complete

### ✅ Backend (95% Complete)

**Framework & Architecture:**
- Flask web framework with SQLAlchemy ORM
- Modular blueprint-based structure
- Configuration management (dev/test/prod environments)
- CORS enabled for frontend communication
- Error handling middleware
- Audit logging system

**Database Models:**
- **User Model**: Authentication, profiles, farm info, 5 user roles
- **Crop Model**: Crop data, soil parameters, growth stages, QR codes, organic certification
- **SupplyChainRecord Model**: Stage tracking, environmental data, handler info, quality status
- **AuditLog Model**: Activity logging for compliance and security

**Authentication & Security:**
- JWT token-based authentication (access + refresh tokens)
- Password hashing with werkzeug.security
- Token expiration & refresh mechanisms
- Role-based access control decorators
- Authorization middleware

**API Endpoints (27+ Total):**
- **Auth** (5): register, login, logout, refresh, verify
- **Users** (4): profile get/update, user details, password change
- **Crops** (6): CRUD operations + public tracking
- **Supply Chain** (4): record creation, history, updates, public view
- **QR Code** (4): generation, viewing, downloading, image generation
- **Admin** (4): statistics, audit logs, user verification, health check
- **Utility** (1): health check endpoint

**Frontend Files:**
- 8 HTML files for all user workflows
- CSS styling with modern glassmorphism design
- JavaScript with API client library
- Form validation and error handling
- Responsive design for mobile/tablet/desktop
- Loading states and notifications

**Infrastructure:**
- Docker & Docker Compose configuration
- CI/CD pipeline (GitHub Actions)
- Database migrations setup
- Testing framework (Pytest)
- Requirements.txt with all dependencies

### ✅ Frontend (90% Complete)

**Completed:**
- Responsive HTML pages for all modules
- API client library with all methods
- Form validation
- User authentication flow
- Navigation between pages
- Modern UI with gradients and animations

**Location:** `/Agrotrace-DNA-main/` directory

**Pages:**
1. `index.html` - Landing/home page
2. `login.html` - User login with role selection
3. `farmer-registration.html` - Farmer registration form
4. `crop-soil-input.html` - Crop and soil data entry
5. `QR-Generator.html` - QR code generation
6. `supply-chain.html` - Supply chain tracking
7. `consumer-verification.html` - Public crop verification
8. `admin-dashboard.html` - Admin statistics

---

## Database Structure

### 📍 Location
**SQLite:** `backend/instance/agrotrace.db`

### Configuration
- **Development:** SQLite (file-based) in `backend/instance/`
- **Production:** PostgreSQL (via `DATABASE_URL` environment variable)
- **Testing:** In-memory SQLite

### Database Tables

#### 1. **users** Table
```
id (Primary Key)
username (Unique, String)
email (Unique, String)
password_hash (String)
full_name (String)
phone (String)
role (String: admin, farmer, consumer, distributor, inspector)
address (Text)
city (String)
country (String)
postal_code (String)
farm_name (String)
farm_size (Float)
is_active (Boolean)
is_verified (Boolean)
verification_token (String)
created_at (DateTime)
updated_at (DateTime)
```

#### 2. **crops** Table
```
id (Primary Key)
crop_id_code (Unique, String)
farmer_id (Foreign Key → users.id)
crop_type (String)
variety (String)
soil_type (String)
soil_ph (Float)
moisture_level (Float)
nitrogen_level (Float)
phosphorus_level (Float)
potassium_level (Float)
planting_date (DateTime)
expected_harvest_date (DateTime)
area_planted (Float)
growth_stage (String)
health_status (String)
qr_code (String)
qr_code_url (String)
is_organic (Boolean)
certification_details (Text)
created_at (DateTime)
updated_at (DateTime)
harvested_at (DateTime)
```

#### 3. **supply_chain_records** Table
```
id (Primary Key)
crop_id (Foreign Key → crops.id)
user_id (Foreign Key → users.id)
stage (String)
location (String)
temperature (Float)
humidity (Float)
handler_name (String)
handler_role (String)
notes (Text)
quality_status (String)
created_at (DateTime)
updated_at (DateTime)
```

#### 4. **audit_logs** Table
```
id (Primary Key)
user_id (Foreign Key → users.id, nullable)
action (String)
resource_type (String)
resource_id (Integer, nullable)
details (JSON)
ip_address (String)
created_at (DateTime)
```

### Data Relationships
```
User (1) ──→ (Many) Crop
User (1) ──→ (Many) SupplyChainRecord
User (1) ──→ (Many) AuditLog
Crop (1) ──→ (Many) SupplyChainRecord
```

---

## Installation & Setup

### Prerequisites

- **Python 3.11+**
- **Git**
- **pip** (Python package manager)
- **Docker & Docker Compose** (optional, for containerized setup)

### Step 1: Clone/Navigate to Project

```bash
cd d:\Agrotrace-DNA-main
```

### Step 2: Set Up Backend

#### Option A: Using Python Virtual Environment (Recommended)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Option B: Using Docker

```bash
cd backend
docker-compose up -d
```

### Step 3: Configure Environment

```bash
cd backend

# Copy example env file
cp .env.example .env

# Edit .env file with your settings
# Key variables:
# DATABASE_URL=sqlite:///agrotrace.db
# FLASK_ENV=development
# JWT_SECRET_KEY=your-secret-key-here
# SECRET_KEY=your-flask-secret-key
```

### Step 4: Initialize Database

The database is automatically created when the application starts. Tables are created using SQLAlchemy ORM.

```bash
# The database will be created at: backend/instance/agrotrace.db
# When you run: python run.py
```

---

## Running the Project

### Start Backend Server

```bash
cd backend
python run.py
```

**Output:**
```
=== Starting AgroTrace-DNA Backend ===
   API:      http://0.0.0.0:5000/api
   Frontend: http://0.0.0.0:5000/
   Health:   http://0.0.0.0:5000/api/health

 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Access the Application

- **Frontend:** http://localhost:5000/
- **API Base:** http://localhost:5000/api
- **Health Check:** http://localhost:5000/api/health

### Using Docker Compose

```bash
cd backend
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Testing the Complete Workflow

### Test 1: Check API Health

```bash
curl http://localhost:5000/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

### Test 2: User Registration (Farmer)

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "farmer123",
    "email": "farmer@example.com",
    "password": "secure_password_123",
    "full_name": "John Doe",
    "role": "farmer",
    "farm_name": "Doe Farm",
    "farm_size": 50,
    "phone": "9876543210"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "username": "farmer123",
  "email": "farmer@example.com",
  "role": "farmer",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "farmer123",
    "full_name": "John Doe",
    "role": "farmer"
  }
}
```

### Test 3: User Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "farmer123",
    "password": "secure_password_123"
  }'
```

### Test 4: Create a Crop

```bash
curl -X POST http://localhost:5000/api/crops \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "crop_type": "Wheat",
    "variety": "HD 2967",
    "soil_ph": 7.2,
    "moisture_level": 25.5,
    "nitrogen_level": 45,
    "phosphorus_level": 20,
    "potassium_level": 150,
    "planting_date": "2025-10-01",
    "area_planted": 10.5,
    "is_organic": true
  }'
```

### Test 5: Add Supply Chain Record

```bash
curl -X POST http://localhost:5000/api/supply-chain \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "crop_id": 1,
    "stage": "Harvested",
    "location": "Farm A, District XYZ",
    "temperature": 28.5,
    "humidity": 65,
    "handler_name": "Ram Singh",
    "handler_role": "Farmer",
    "quality_status": "Good",
    "notes": "Crop harvested successfully"
  }'
```

### Test 6: Generate QR Code

```bash
curl -X POST http://localhost:5000/api/qr/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "crop_id": 1
  }'
```

### Test 7: View Admin Statistics

```bash
curl -X GET http://localhost:5000/api/admin/statistics \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Test via Frontend

1. **Open Frontend:** http://localhost:5000/
2. **Register:** Click "Register as Farmer" → Fill form → Submit
3. **Login:** Go to login page → Enter credentials
4. **Create Crop:** Navigate to "Crop & Soil Input" → Fill soil data → Submit
5. **View QR:** QR code displays in crop details
6. **Track Supply Chain:** Go to "Supply Chain Tracker" → Add stages
7. **Verify:** As consumer, scan QR to view crop history

---

## API Endpoints Reference

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login user | No |
| POST | `/api/auth/refresh` | Refresh access token | No |
| GET | `/api/auth/verify` | Verify token validity | Yes |
| POST | `/api/auth/logout` | Logout user | Yes |

### User Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| GET | `/api/users/profile` | Get user profile | Yes |
| PUT | `/api/users/profile` | Update profile | Yes |
| GET | `/api/users/<id>` | Get user by ID | Yes (Admin) |
| POST | `/api/users/change-password` | Change password | Yes |

### Crop Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| POST | `/api/crops` | Create new crop | Yes (Farmer) |
| GET | `/api/crops` | List crops (paginated) | Yes |
| GET | `/api/crops/<id>` | Get crop details | Yes |
| PUT | `/api/crops/<id>` | Update crop | Yes (Owner/Admin) |
| DELETE | `/api/crops/<id>` | Delete crop | Yes (Owner/Admin) |
| GET | `/api/crops/<code>/track` | Public crop tracking | No |

### Supply Chain Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| POST | `/api/supply-chain` | Add supply chain record | Yes |
| GET | `/api/supply-chain/crop/<id>` | Get supply chain history | Yes |
| PUT | `/api/supply-chain/<id>` | Update record | Yes |
| GET | `/api/supply-chain/<code>/public` | Public supply chain view | No |

### QR Code Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| POST | `/api/qr/generate` | Generate QR code | Yes |
| GET | `/api/qr/<code>/view` | View QR code | No |
| GET | `/api/qr/download/<filename>` | Download QR image | No |
| POST | `/api/qr/generate-image` | Generate QR without saving | Yes |

### Admin Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| GET | `/api/admin/statistics` | System statistics | Yes (Admin) |
| GET | `/api/admin/audit-logs` | View audit logs | Yes (Admin) |
| PATCH | `/api/admin/users/<id>/verify` | Verify user | Yes (Admin) |
| GET | `/api/admin/health` | System health check | Yes (Admin) |

### Utility Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| GET | `/api/health` | API health check | No |
| GET | `/api/` | API index | No |

---

## Database Details

### Current Database File

**Location:** `backend/instance/agrotrace.db`  
**Type:** SQLite 3  
**Size:** ~100 KB (depending on data)  
**Format:** Binary database file

### Accessing the Database

#### View Database with Python

```python
import sqlite3

conn = sqlite3.connect('backend/instance/agrotrace.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(table[0])

# View users
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
for user in users:
    print(user)

conn.close()
```

#### Using SQLite Command Line

```bash
# Navigate to backend
cd backend

# Open database
sqlite3 instance/agrotrace.db

# View tables
.tables

# View schema
.schema users

# Query data
SELECT * FROM users;

# Exit
.quit
```

### Database Storage Location

```
Agrotrace-DNA-main/
└── backend/
    └── instance/
        └── agrotrace.db  ← Database file
```

### Important Notes

- **Development:** SQLite file is created automatically
- **Production:** Use PostgreSQL via `DATABASE_URL` environment variable
- **Backup:** Regularly backup the `instance/agrotrace.db` file
- **Reset Database:** Delete the file and restart the app to create a fresh database

---

## Deployment Guide

### Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Change all secret keys in `.env`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Set CORS_ORIGINS to your domain
- [ ] Use Gunicorn/uWSGI as WSGI server
- [ ] Set up reverse proxy (Nginx)

### Deploy to Heroku

```bash
cd backend

# Install Heroku CLI
# Create Heroku app
heroku create agrotrace-dna-app

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set DATABASE_URL=postgresql://...
heroku config:set JWT_SECRET_KEY=your-production-key

# Deploy
git push heroku main
```

### Deploy with Docker

```bash
cd backend

# Build image
docker build -t agrotrace-dna:latest .

# Run container
docker run -d \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e DATABASE_URL=postgresql://... \
  agrotrace-dna:latest
```

### Production Environment Variables

```bash
FLASK_ENV=production
FLASK_APP=run.py
SECRET_KEY=generate-a-strong-random-key
JWT_SECRET_KEY=generate-a-strong-random-key
DATABASE_URL=postgresql://user:password@host:5432/agrotrace_db
CORS_ORIGINS=https://yourdomain.com
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
DEBUG=False
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'flask'"

**Solution:**
```bash
# Ensure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install requirements
pip install -r requirements.txt
```

### Issue: "Address already in use" (Port 5000)

**Solution:**
```bash
# On Windows: Find and kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# On Linux/Mac:
lsof -i :5000
kill -9 <PID>
```

### Issue: "Database locked" error

**Solution:**
- Close any other instances of the application
- Delete the database file and restart: `rm backend/instance/agrotrace.db`
- Use PostgreSQL for concurrent access

### Issue: CORS errors in frontend

**Solution:**
```bash
# Update .env
CORS_ORIGINS=http://localhost:3000,http://localhost:5000

# Or for development:
CORS_ORIGINS=*
```

### Issue: JWT token expired

**Solution:**
- Use refresh token endpoint: `POST /api/auth/refresh`
- Increase `JWT_EXPIRATION_HOURS` in `.env`

### Issue: QR code not generating

**Solution:**
```bash
# Ensure PIL is installed
pip install Pillow

# Verify qrcode library
pip install qrcode[pil]

# Restart server
python run.py
```

---

## Key Files

| File | Purpose |
|------|---------|
| `backend/run.py` | Application entry point |
| `backend/config.py` | Configuration management |
| `backend/app/__init__.py` | Flask app factory |
| `backend/app/models/__init__.py` | Database models |
| `backend/app/routes/*.py` | API endpoints |
| `backend/app/utils/*.py` | Helper functions |
| `backend/requirements.txt` | Python dependencies |
| `backend/.env` | Environment variables |
| `backend/instance/agrotrace.db` | SQLite database |
| `Agrotrace-DNA-main/api-client.js` | Frontend API client |
| `Agrotrace-DNA-main/*.html` | Frontend pages |

---

## Project Structure

```
Agrotrace-DNA-main/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── __init__.py          # Database models
│   │   ├── routes/
│   │   │   ├── auth.py              # Authentication endpoints
│   │   │   ├── users.py             # User endpoints
│   │   │   ├── crops.py             # Crop endpoints
│   │   │   ├── supply_chain.py       # Supply chain endpoints
│   │   │   ├── qr_code.py           # QR code endpoints
│   │   │   └── admin.py             # Admin endpoints
│   │   ├── utils/
│   │   │   ├── auth.py              # JWT utilities
│   │   │   ├── errors.py            # Error handlers
│   │   │   └── qr_helper.py         # QR code helpers
│   │   └── __init__.py              # Flask factory
│   ├── tests/
│   │   ├── conftest.py              # Pytest fixtures
│   │   ├── test_auth.py             # Auth tests
│   │   └── test_crops.py            # Crop tests
│   ├── instance/
│   │   └── agrotrace.db             # SQLite database
│   ├── run.py                       # Entry point
│   ├── config.py                    # Configuration
│   ├── requirements.txt             # Dependencies
│   ├── .env                         # Environment variables
│   ├── Dockerfile                   # Docker configuration
│   └── docker-compose.yml           # Docker Compose
│
├── Agrotrace-DNA-main/
│   ├── index.html                   # Landing page
│   ├── login.html                   # Login page
│   ├── farmer-registration.html     # Registration
│   ├── crop-soil-input.html         # Crop input
│   ├── supply-chain.html            # Supply chain
│   ├── QR-Generator.html            # QR generation
│   ├── consumer-verification.html   # Consumer verification
│   ├── admin-dashboard.html         # Admin dashboard
│   ├── api-client.js                # API client library
│   ├── background.js                # Background animations
│   ├── background.css               # Styling
│   └── .vscode/                     # VS Code settings
│
└── COMPLETE_PROJECT_GUIDE.md        # This file
```

---

## Support & Contact

For issues or questions:
1. Check the troubleshooting section
2. Review API endpoint documentation
3. Check server logs: `backend/logs/` directory
4. Verify environment variables in `.env`

---

## License

Agrotrace-DNA © 2026. All rights reserved.

---

**Happy Farming! 🌾**
