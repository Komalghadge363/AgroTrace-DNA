from datetime import datetime, timedelta

from app import db
from app.models import User, UserRole


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'healthy'

def test_api_index(client):
    """Test API index endpoint."""
    response = client.get('/api')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['endpoints']['health'] == '/api/health'

def test_login_get_not_allowed_returns_json(client):
    """Test POST-only auth routes return JSON on GET."""
    response = client.get('/api/auth/login')
    assert response.status_code == 405
    data = response.get_json()
    assert data['status'] == 405
    assert 'POST' in data['allowed_methods']

def test_register_user(client):
    """Test user registration."""
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'email': 'newuser@test.com',
        'password': 'newpassword123',
        'full_name': 'New User',
        'phone': '9876543210',
        'role': 'farmer',
        'farm_name': 'Green Farm',
        'farm_size': 5.5,
        'village': 'Paithan',
        'taluka': 'Paithan',
        'district': 'Aurangabad'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['user']['username'] == 'newuser'
    assert data['user']['email'] == 'newuser@test.com'
    assert data['user']['farm_name'] == 'Green Farm'
    assert data['user']['phone'] == '9876543210'

def test_register_duplicate_username(client, sample_user):
    """Test registration with duplicate username."""
    response = client.post('/api/auth/register', json={
        'username': 'testfarmer',
        'email': 'different@test.com',
        'password': 'password123'
    })
    
    assert response.status_code == 409
    assert 'already exists' in response.get_json()['message']

def test_login_success(client, sample_user):
    """Test successful login."""
    response = client.post('/api/auth/login', json={
        'username': 'testfarmer',
        'password': 'testpassword123'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data

def test_login_wrong_password(client, sample_user):
    """Test login with wrong password."""
    response = client.post('/api/auth/login', json={
        'username': 'testfarmer',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401

def test_login_with_email(client, sample_user):
    """Test successful login with email identifier."""
    response = client.post('/api/auth/login', json={
        'username': 'farmer@test.com',
        'password': 'testpassword123'
    })

    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data


def test_forgot_password_sends_otp_email(client, sample_user, monkeypatch, app):
    sent = {}

    def fake_send_password_reset_otp(email, otp):
        sent['email'] = email
        sent['otp'] = otp

    monkeypatch.setattr(
        'app.routes.auth.send_password_reset_otp',
        fake_send_password_reset_otp
    )

    response = client.post('/api/auth/forgot-password', json={
        'email': 'farmer@test.com'
    })

    assert response.status_code == 200
    assert sent['email'] == 'farmer@test.com'
    assert len(sent['otp']) == 6

    with app.app_context():
        user = User.query.filter_by(email='farmer@test.com').first()
        assert user.reset_otp == sent['otp']
        assert user.reset_otp_expiry is not None


def test_verify_otp_resets_password(client, sample_user, app):
    with app.app_context():
        user = User.query.filter_by(email='farmer@test.com').first()
        user.reset_otp = '123456'
        user.reset_otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()

    response = client.post('/api/auth/verify-otp', json={
        'email': 'farmer@test.com',
        'otp': '123456',
        'new_password': 'UpdatedPass123'
    })

    assert response.status_code == 200

    login_response = client.post('/api/auth/login', json={
        'username': 'farmer@test.com',
        'password': 'UpdatedPass123'
    })
    assert login_response.status_code == 200


def test_google_config_returns_disabled_when_missing(client):
    response = client.get('/api/auth/google-config')
    assert response.status_code == 200
    data = response.get_json()
    assert data['enabled'] is False
    assert data['client_id'] is None


def test_google_login_existing_admin_account(client, admin_user, monkeypatch):
    monkeypatch.setattr(
        'app.routes.auth.verify_google_id_token',
        lambda credential: {
            'email': 'admin@test.com',
            'name': 'Admin User',
            'aud': 'test-client-id',
            'iss': 'https://accounts.google.com',
            'email_verified': 'true'
        }
    )

    response = client.post('/api/auth/google-login', json={
        'credential': 'google-jwt',
        'requested_role': UserRole.ADMIN.value
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data['user']['role'] == UserRole.ADMIN.value


def test_google_login_new_admin_is_blocked(client, monkeypatch):
    monkeypatch.setattr(
        'app.routes.auth.verify_google_id_token',
        lambda credential: {
            'email': 'new-admin@test.com',
            'name': 'New Admin',
            'aud': 'test-client-id',
            'iss': 'https://accounts.google.com',
            'email_verified': 'true'
        }
    )

    response = client.post('/api/auth/google-login', json={
        'credential': 'google-jwt',
        'requested_role': UserRole.ADMIN.value
    })

    assert response.status_code == 403

def test_get_profile(client, auth_token):
    """Test getting user profile."""
    response = client.get('/api/users/profile', headers={
        'Authorization': f'Bearer {auth_token}'
    })
    
    assert response.status_code == 200
    assert response.get_json()['user']['username'] == 'testfarmer'

def test_update_profile(client, auth_token):
    """Test updating user profile."""
    response = client.put('/api/users/profile', 
        json={'full_name': 'Updated Name'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    assert response.get_json()['user']['full_name'] == 'Updated Name'

def test_token_required(client):
    """Test that endpoints require token."""
    response = client.get('/api/users/profile')
    assert response.status_code == 401

def test_admin_access(client, auth_token):
    """Test that non-admin users cannot access admin endpoints."""
    response = client.get('/api/admin/statistics', headers={
        'Authorization': f'Bearer {auth_token}'
    })
    assert response.status_code == 403

def test_admin_access_allowed(client, admin_token):
    """Test that admin users can access admin endpoints."""
    response = client.get('/api/admin/statistics', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    assert response.status_code == 200
