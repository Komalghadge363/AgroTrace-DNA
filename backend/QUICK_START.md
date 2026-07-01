# Quick Start Guide - Agrotrace-DNA Backend

Get the backend up and running in 5 minutes!

## Option 1: Using Docker (Recommended)

### Prerequisites
- Docker & Docker Compose installed

### Steps

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create .env file**
```bash
cp .env.example .env
```

3. **Start services**
```bash
docker-compose up -d
```

4. **Verify it's running**
```bash
curl http://localhost:5000/api/health
```

✅ **Done!** Backend is running at `http://localhost:5000`

**Access:**
- API: http://localhost:5000
- API index: http://localhost:5000/api
- Database: postgres://agrotrace:agrotrace_password@localhost:5432/agrotrace_db

## Option 2: Local Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL or SQLite

### Steps

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create .env file**
```bash
cp .env.example .env
```

5. **Edit .env for local development** (optional)
```
FLASK_ENV=development
DATABASE_URL=sqlite:///agrotrace.db
SECRET_KEY=dev-key-12345
JWT_SECRET_KEY=jwt-dev-key-12345
DEBUG=True
```

6. **Run the application**
```bash
python run.py
```

✅ **Done!** Backend is running at `http://localhost:5000`

## First Steps

### 1. Test the API
```bash
# Health check
curl http://localhost:5000/api/health
```

### 2. Create Admin User

**Option A: Using Python Shell**
```bash
python
>>> from app import db, create_app
>>> from app.models import User, UserRole
>>> app = create_app()
>>> with app.app_context():
...     admin = User(
...         username='admin',
...         email='admin@example.com',
...         full_name='Administrator',
...         role=UserRole.ADMIN.value
...     )
...     admin.set_password('admin123')
...     db.session.add(admin)
...     db.session.commit()
>>> exit()
```

**Option B: Using API**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123",
    "full_name": "Administrator",
    "role": "admin"
  }'
```

### 3. Login and Get Token
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": { "id": 1, "username": "admin", ... }
}
```

### 4. Test Protected Endpoint
```bash
curl http://localhost:5000/api/users/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## Key API Endpoints

### Authentication
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/verify` - Verify token

### Users
- `GET /api/users/profile` - Get profile
- `PUT /api/users/profile` - Update profile
- `POST /api/users/change-password` - Change password

### Crops
- `POST /api/crops` - Create crop
- `GET /api/crops` - List crops
- `GET /api/crops/{id}` - Get crop details
- `PUT /api/crops/{id}` - Update crop
- `DELETE /api/crops/{id}` - Delete crop
- `GET /api/crops/{crop_id_code}/track` - Public tracking

### Supply Chain
- `POST /api/supply-chain` - Add record
- `GET /api/supply-chain/crop/{crop_id}` - Get history
- `GET /api/supply-chain/{crop_id_code}/public` - Public history

### QR Code
- `POST /api/qr/generate` - Generate QR code
- `GET /api/qr/{crop_id_code}/view` - View QR code
- `GET /api/qr/download/{filename}` - Download image

### Admin (requires admin token)
- `GET /api/admin/statistics` - System statistics
- `GET /api/admin/audit-logs` - Audit logs
- `GET /api/admin/health` - System health

## Running Tests

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test
pytest tests/test_auth.py::test_register_user -v
```

## Project Structure

```
backend/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   ├── utils/           # Helper functions
│   └── __init__.py      # App factory
├── tests/               # Test suite
├── .github/workflows/   # CI/CD
├── config.py            # Configuration
├── run.py               # Entry point
├── requirements.txt     # Dependencies
├── Dockerfile           # Container image
├── docker-compose.yml   # Multi-container setup
├── .env.example         # Environment template
├── README.md            # Full documentation
├── DEPLOYMENT.md        # Deployment guide
├── FRONTEND_INTEGRATION.md # Frontend guide
└── QUICK_START.md       # This file
```

## Troubleshooting

### Port 5000 already in use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>
```

### Database connection error
```bash
# Check PostgreSQL is running (if using PostgreSQL)
# Update DATABASE_URL in .env file
# Use SQLite for development: DATABASE_URL=sqlite:///agrotrace.db
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Permission denied (Docker)
```bash
# Add current user to docker group (Linux)
sudo usermod -aG docker $USER
```

## Next Steps

1. ✅ Backend is running
2. 📖 Read [README.md](README.md) for full API documentation
3. 🔌 Check [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md) to connect frontend
4. 🚀 Read [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
5. 🧪 Write tests for your custom endpoints
6. 📊 View admin statistics at `/api/admin/statistics`

## Common Commands

```bash
# Start backend (Docker)
docker-compose up -d

# Stop backend (Docker)
docker-compose down

# View logs (Docker)
docker-compose logs -f web

# Access database (Docker)
docker-compose exec postgres psql -U agrotrace -d agrotrace_db

# Start backend (Local)
python run.py

# Run tests
pytest -v

# Format code
black app/

# Lint code
flake8 app/

# Create new admin user
python -c "from app import create_app, db; from app.models import User; app = create_app(); ctx = app.app_context(); ctx.push(); u = User(username='admin', email='admin@test.com', role='admin'); u.set_password('pass'); db.session.add(u); db.session.commit()"
```

## Environment Variables Quick Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `FLASK_ENV` | Environment mode | `development`, `production` |
| `DATABASE_URL` | Database connection | `sqlite:///app.db` or PostgreSQL URL |
| `SECRET_KEY` | Flask secret | Random string |
| `JWT_SECRET_KEY` | JWT signing key | Random string |
| `JWT_EXPIRATION_HOURS` | Token expiry | `24` |
| `DEBUG` | Debug mode | `True` or `False` |
| `CORS_ORIGINS` | Allowed domains | `http://localhost:3000` |

## Support & Help

- 📖 Full docs: [README.md](README.md)
- 🔌 Frontend integration: [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md)
- 🚀 Deployment: [DEPLOYMENT.md](DEPLOYMENT.md)
- 🐛 Report issues on GitHub

---

**Happy coding! 🎉**
