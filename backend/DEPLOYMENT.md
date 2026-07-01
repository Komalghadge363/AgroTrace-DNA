# Agrotrace-DNA Backend - Deployment Guide

## Environment Setup

### Development Environment

```bash
# Copy environment template
cp .env.example .env

# Edit for development
FLASK_ENV=development
DATABASE_URL=sqlite:///agrotrace_dev.db
SECRET_KEY=dev-secret-key-12345
JWT_SECRET_KEY=jwt-secret-key-12345
DEBUG=True
```

### Staging Environment

```bash
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@staging-db:5432/agrotrace
SECRET_KEY=<generate-strong-key>
JWT_SECRET_KEY=<generate-strong-key>
DEBUG=False
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=staging@example.com
MAIL_PASSWORD=<app-password>
```

### Production Environment

```bash
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@prod-db:5432/agrotrace
SECRET_KEY=<generate-very-strong-key>
JWT_SECRET_KEY=<generate-very-strong-key>
DEBUG=False
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
MAIL_SERVER=smtp.gmail.com
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
```

## Generate Strong Keys

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Docker Deployment

### Build Image

```bash
docker build -t agrotrace-api:latest .
```

### Run with Docker Compose

```bash
docker-compose up -d
```

### Access Services

- API: http://localhost:5000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Database Setup

### Initialize Database

```bash
# Create tables
python run.py

# Or manually with Flask CLI
flask shell
>>> from app import db
>>> db.create_all()
```

### Create Admin User

```bash
flask shell
>>> from app.models import User, UserRole
>>> from app import db
>>> admin = User(
...     username='admin',
...     email='admin@example.com',
...     full_name='Administrator',
...     role=UserRole.ADMIN.value
... )
>>> admin.set_password('strong_password_here')
>>> db.session.add(admin)
>>> db.session.commit()
```

## Monitoring

### Health Check

```bash
curl http://localhost:5000/api/health
```

### Admin Statistics

```bash
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/admin/statistics
```

### View Logs

```bash
docker logs agrotrace-api
tail -f logs/app.log
```

## Backup & Restore

### Backup Database

```bash
# PostgreSQL
pg_dump agrotrace_db > backup.sql

# Docker
docker exec postgres pg_dump -U agrotrace agrotrace_db > backup.sql
```

### Restore Database

```bash
psql agrotrace_db < backup.sql
```

## Scaling Considerations

1. **Database**: Use connection pooling, replicas for read operations
2. **Cache**: Implement Redis caching for frequently accessed data
3. **Queue**: Use Celery for async tasks
4. **Load Balancing**: Use Nginx or HAProxy
5. **CDN**: Serve static assets and QR codes
6. **Monitoring**: Implement Prometheus/Grafana

## Security Hardening

1. **Enable HTTPS**: Use Let's Encrypt certificates
2. **Rate Limiting**: Implement Flask-Limiter
3. **CORS**: Restrict to specific domains
4. **API Keys**: Use for external integrations
5. **Audit Logging**: Log all sensitive operations
6. **Data Encryption**: Encrypt sensitive fields
7. **Backup**: Regular encrypted backups
