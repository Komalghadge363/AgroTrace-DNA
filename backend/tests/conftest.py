import pytest
import json
from app import create_app, db
from app.models import User, Crop, UserRole

def _persist_and_detach(instance):
    """Persist a model instance and return it with loaded attributes."""
    db.session.add(instance)
    db.session.commit()
    db.session.refresh(instance)
    db.session.expunge(instance)
    return instance

@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's CLI."""
    return app.test_cli_runner()

@pytest.fixture
def sample_user(app):
    """Create a sample user for testing."""
    user = User(
        username='testfarmer',
        email='farmer@test.com',
        full_name='Test Farmer',
        role=UserRole.FARMER.value,
        farm_name='Test Farm'
    )
    user.set_password('testpassword123')
    
    with app.app_context():
        return _persist_and_detach(user)
    
@pytest.fixture
def admin_user(app):
    """Create a sample admin user for testing."""
    user = User(
        username='testadmin',
        email='admin@test.com',
        full_name='Test Admin',
        role=UserRole.ADMIN.value
    )
    user.set_password('adminpassword123')
    
    with app.app_context():
        return _persist_and_detach(user)
    
@pytest.fixture
def auth_token(client, sample_user):
    """Get authentication token for sample user."""
    response = client.post('/api/auth/login', json={
        'username': 'testfarmer',
        'password': 'testpassword123'
    })
    
    return response.get_json()['access_token']

@pytest.fixture
def admin_token(client, admin_user):
    """Get authentication token for admin user."""
    response = client.post('/api/auth/login', json={
        'username': 'testadmin',
        'password': 'adminpassword123'
    })
    
    return response.get_json()['access_token']
