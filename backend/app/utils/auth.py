import jwt
import os
from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify, current_app
from app.models import User

class AuthService:
    """Authentication and JWT management service"""
    
    @staticmethod
    def generate_tokens(user_id):
        """Generate access and refresh tokens"""
        secret_key = current_app.config['JWT_SECRET_KEY']
        algorithm = current_app.config['JWT_ALGORITHM']
        
        # Access token
        access_payload = {
            'user_id': user_id,
            'type': 'access',
            'exp': datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
            'iat': datetime.utcnow()
        }
        
        # Refresh token
        refresh_payload = {
            'user_id': user_id,
            'type': 'refresh',
            'exp': datetime.utcnow() + current_app.config['JWT_REFRESH_TOKEN_EXPIRES'],
            'iat': datetime.utcnow()
        }
        
        access_token = jwt.encode(access_payload, secret_key, algorithm=algorithm)
        refresh_token = jwt.encode(refresh_payload, secret_key, algorithm=algorithm)
        
        return access_token, refresh_token
    
    @staticmethod
    def verify_token(token):
        """Verify and decode JWT token"""
        try:
            secret_key = current_app.config['JWT_SECRET_KEY']
            algorithm = current_app.config['JWT_ALGORITHM']
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def get_token_from_request():
        """Extract token from Authorization header"""
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = AuthService.get_token_from_request()
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        payload = AuthService.verify_token(token)
        if not payload:
            return jsonify({'message': 'Invalid or expired token'}), 401
        
        # Verify it's an access token
        if payload.get('type') != 'access':
            return jsonify({'message': 'Invalid token type'}), 401
        
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'message': 'User not found'}), 401
        
        request.user = user
        return f(*args, **kwargs)
    
    return decorated

def role_required(*roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'user'):
                return jsonify({'message': 'Authentication required'}), 401
            
            if request.user.role not in roles:
                return jsonify({'message': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = AuthService.get_token_from_request()
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        payload = AuthService.verify_token(token)
        if not payload:
            return jsonify({'message': 'Invalid or expired token'}), 401
        
        user = User.query.get(payload['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        
        request.user = user
        return f(*args, **kwargs)
    
    return decorated
