# Agrotrace-DNA Backend API

A comprehensive backend API for the Agrotrace-DNA agricultural supply chain tracking system. Built with Flask, featuring JWT authentication, role-based access control, and QR code integration.

## Features

- **User Management**: Registration, authentication, role-based access control
- **Crop Management**: Track crop information, soil parameters, and growth stages
- **Supply Chain Tracking**: Monitor crop movement through the supply chain with environmental data
- **QR Code Generation**: Generate and manage QR codes for crops
- **Admin Dashboard**: System statistics, user management, audit logs
- **JWT Authentication**: Secure token-based authentication with refresh tokens
- **Docker Support**: Complete Docker and Docker Compose setup
- **CI/CD Pipeline**: GitHub Actions workflow for automated testing and deployment

## User Roles

- **Admin**: Full system access, user management, statistics
- **Farmer**: Create and manage crops, view supply chain
- **Consumer**: View public crop information and supply chain
- **Distributor**: Update supply chain status
- **Inspector**: Verify crop quality and certifications

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 12+ (or SQLite for development)
- Redis (optional, for caching)
- Docker & Docker Compose (optional)

### Local Setup

1. Clone the repository:
```bash
git clone <repository>
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

5. Configure database in `.env`:
```
DATABASE_URL=sqlite:///agrotrace.db  # For SQLite development
# or for PostgreSQL:
DATABASE_URL=postgresql://user:password@localhost:5432/agrotrace_db
```

6. Initialize database:
```bash
flask db upgrade
# or for first time:
python run.py
```

7. Run the application:
```bash
python run.py
```

The API will be available at `http://localhost:5000`

- API index: `http://localhost:5000/api`
- Health check: `http://localhost:5000/api/health`

### Docker Setup

1. Build and run with Docker Compose:
```bash
docker-compose up -d
```

2. Access the application:
```
API: http://localhost:5000
Database: postgres://agrotrace:agrotrace_password@localhost:5432/agrotrace_db
Redis: redis://localhost:6379
```

## API Documentation

### Authentication Endpoints

#### Register User
```
POST /api/auth/register
Content-Type: application/json

{
  "username": "farmer1",
  "email": "farmer@example.com",
  "password": "securepassword123",
  "full_name": "John Farmer",
  "role": "farmer",
  "farm_name": "Green Acres Farm"
}
```

#### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "farmer1",
  "password": "securepassword123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...}
}
```

#### Refresh Token
```
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Verify Token
```
GET /api/auth/verify
Authorization: Bearer <access_token>
```

### User Endpoints

#### Get Profile
```
GET /api/users/profile
Authorization: Bearer <access_token>
```

#### Update Profile
```
PUT /api/users/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "Updated Name",
  "phone": "+1234567890",
  "farm_size": 10.5
}
```

#### Change Password
```
POST /api/users/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

### Crop Endpoints

#### Create Crop
```
POST /api/crops
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "crop_type": "Wheat",
  "variety": "Premium Wheat",
  "planting_date": "2024-01-15T10:00:00",
  "soil_type": "Loam",
  "soil_ph": 7.2,
  "area_planted": 5.0,
  "is_organic": true
}
```

#### List Crops
```
GET /api/crops?page=1&per_page=20
Authorization: Bearer <access_token>
```

#### Get Crop Details
```
GET /api/crops/{crop_id}
Authorization: Bearer <access_token>
```

#### Update Crop
```
PUT /api/crops/{crop_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "growth_stage": "Flowering",
  "health_status": "Good",
  "moisture_level": 25.5
}
```

#### Track Crop (Public)
```
GET /api/crops/{crop_id_code}/track
```

### Supply Chain Endpoints

#### Create Record
```
POST /api/supply-chain
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "crop_id": 1,
  "stage": "Harvested",
  "location": "Farm Location",
  "temperature": 25.5,
  "humidity": 60.0,
  "handler_name": "John Handler",
  "notes": "Harvesting completed successfully"
}
```

#### Get Supply Chain History
```
GET /api/supply-chain/crop/{crop_id}
Authorization: Bearer <access_token>
```

#### Public View
```
GET /api/supply-chain/{crop_id_code}/public
```

### QR Code Endpoints

#### Generate QR Code
```
POST /api/qr/generate
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "crop_id": 1
}
```

#### View QR Code
```
GET /api/qr/{crop_id_code}/view
```

#### Download QR Image
```
GET /api/qr/download/{filename}
```

### Admin Endpoints

#### Get Statistics
```
GET /api/admin/statistics
Authorization: Bearer <admin_token>
```

#### Get Audit Logs
```
GET /api/admin/audit-logs?page=1&per_page=50
Authorization: Bearer <admin_token>
```

#### Verify User
```
PATCH /api/admin/users/verify/{user_id}
Authorization: Bearer <admin_token>
```

#### System Health
```
GET /api/admin/health
Authorization: Bearer <admin_token>
```

## Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test
pytest tests/test_auth.py::test_register_user -v
```

## Environment Variables

Key environment variables in `.env`:

```
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key
DEBUG=True

# Database
DATABASE_URL=sqlite:///agrotrace.db

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Mail (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## Database Models

### User
- id, username, email, password_hash
- full_name, phone, role
- address, city, country, postal_code
- farm_name, farm_size (for farmers)
- is_active, is_verified
- created_at, updated_at

### Crop
- id, crop_id_code, farmer_id
- crop_type, variety
- soil parameters (pH, moisture, nitrogen, phosphorus, potassium)
- planting_date, expected_harvest_date, harvested_at
- growth_stage, health_status
- qr_code, qr_code_url
- is_organic, certification_details

### SupplyChainRecord
- id, crop_id, user_id
- stage, location
- temperature, humidity
- handler_name, handler_role
- notes, quality_status
- created_at, updated_at

### AuditLog
- id, user_id, action
- resource_type, resource_id
- details, ip_address
- created_at

## CI/CD Pipeline

The GitHub Actions workflow includes:

1. **Testing**: Runs pytest on every push and PR
2. **Code Quality**: Linting with flake8, black, pylint
3. **Security**: Trivy vulnerability scanning
4. **Docker Build**: Builds and pushes Docker image
5. **Staging Deployment**: Auto-deploys to staging on develop branch
6. **Production Deployment**: Auto-deploys to production on main branch

### Required GitHub Secrets

```
DEPLOY_KEY: SSH private key for deployment
STAGING_HOST: Staging server hostname
PROD_HOST: Production server hostname
DEPLOY_USER: Deployment user
```

## Project Structure

```
backend/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   │   ├── auth.py      # Authentication
│   │   ├── users.py     # User management
│   │   ├── crops.py     # Crop endpoints
│   │   ├── supply_chain.py
│   │   ├── qr_code.py
│   │   └── admin.py
│   ├── utils/           # Helper functions
│   │   ├── auth.py      # JWT utilities
│   │   ├── errors.py    # Error handling
│   │   └── qr_helper.py # QR code generation
│   └── __init__.py      # App factory
├── tests/               # Test suite
├── .github/workflows/   # CI/CD configuration
├── config.py            # Configuration
├── run.py               # Application entry point
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container image
├── docker-compose.yml   # Multi-container setup
├── .env.example         # Environment template
└── README.md            # This file
```

## Security Considerations

- **Passwords**: Hashed using werkzeug.security
- **Tokens**: JWT with configurable expiration
- **CORS**: Configured whitelist of allowed origins
- **HTTPS**: Enforced in production
- **Database**: SQL injection prevented with SQLAlchemy ORM
- **Rate Limiting**: Should be added in production
- **Input Validation**: Marshmallow schemas for all inputs

## Development

### Creating Database Migration
```bash
flask db init
flask db migrate -m "Description"
flask db upgrade
```

### Adding New Endpoint
1. Create route in `app/routes/`
2. Use decorators: `@token_required`, `@admin_required`
3. Add tests in `tests/`
4. Update this README

### Running in Development Mode
```bash
FLASK_ENV=development python run.py
```

## Production Deployment

1. Set all environment variables
2. Use PostgreSQL for database
3. Set `DEBUG=False`
4. Use strong `SECRET_KEY` and `JWT_SECRET_KEY`
5. Enable HTTPS
6. Configure proper CORS origins
7. Set up logging and monitoring
8. Use Gunicorn/uWSGI with multiple workers

## Troubleshooting

### Database connection errors
- Check `DATABASE_URL` is correct
- Ensure PostgreSQL is running
- Verify credentials

### Token errors
- Check `JWT_SECRET_KEY` is set
- Verify token not expired
- Check Authorization header format

### CORS errors
- Add frontend URL to `CORS_ORIGINS`
- Ensure origin is correct in browser requests

## Contributing

1. Create feature branch: `git checkout -b feature/feature-name`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/feature-name`
4. Create Pull Request
5. Ensure all tests pass in CI/CD

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the GitHub repository.
