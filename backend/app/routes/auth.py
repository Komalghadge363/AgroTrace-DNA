from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import User, UserRole
from app.utils.auth import AuthService, token_required
from app.utils.email import EmailDeliveryError, send_password_reset_otp
from app.utils.google_auth import (
    GoogleAuthError,
    is_google_login_configured,
    verify_google_id_token,
)
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy import or_
import os
import random
import secrets
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

class UserRegistrationSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    full_name = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    role = fields.Str(validate=validate.OneOf([r.value for r in UserRole]), allow_none=True)
    farm_name = fields.Str(allow_none=True)
    farm_size = fields.Float(allow_none=True)
    village = fields.Str(allow_none=True)
    taluka = fields.Str(allow_none=True)
    district = fields.Str(allow_none=True)
    # Distributor / Supplier fields
    gst_number = fields.Str(allow_none=True)
    business_type = fields.Str(allow_none=True)
    license_number = fields.Str(allow_none=True)
    # Admin fields
    department = fields.Str(allow_none=True)
    designation = fields.Str(allow_none=True)
    employee_id = fields.Str(allow_none=True)
    admin_access_code = fields.Str(allow_none=True)

class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    schema = UserRegistrationSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 409
    
    # Create new user
    role = data.get('role', UserRole.FARMER.value)
    
    # Validate admin access code if registering as admin
    if role == UserRole.ADMIN.value:
        expected_code = os.getenv('ADMIN_ACCESS_CODE', 'CROPID-ADMIN-2025')
        provided_code = data.get('admin_access_code', '')
        if provided_code != expected_code:
            return jsonify({'message': 'Invalid Admin Access Code. Contact the system administrator.'}), 403
    
    address_parts = [data.get('village'), data.get('taluka')]
    user = User(
        username=data['username'],
        email=data['email'],
        full_name=data.get('full_name'),
        phone=data.get('phone'),
        role=role,
        farm_name=data.get('farm_name'),
        farm_size=data.get('farm_size'),
        address=', '.join(part for part in address_parts if part) or None,
        city=data.get('district'),
        country='India' if data.get('district') else None,
        # Distributor fields
        gst_number=data.get('gst_number'),
        business_type=data.get('business_type'),
        license_number=data.get('license_number'),
        # Admin fields
        department=data.get('department'),
        designation=data.get('designation'),
        employee_id=data.get('employee_id')
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Registration failed', 'error': str(e)}), 500
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return tokens"""
    schema = UserLoginSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Find user
    identifier = data['username'].strip()
    user = User.query.filter(
        or_(
            User.username == identifier,
            User.email == identifier,
            User.phone == identifier
        )
    ).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401
    
    if not user.is_active:
        return jsonify({'message': 'Account is inactive'}), 403
    
    # Generate tokens
    access_token, refresh_token = AuthService.generate_tokens(user.id)
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token using refresh token"""
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    
    if not refresh_token:
        return jsonify({'message': 'Refresh token is required'}), 400
    
    payload = AuthService.verify_token(refresh_token)
    if not payload or payload.get('type') != 'refresh':
        return jsonify({'message': 'Invalid refresh token'}), 401
    
    user = User.query.get(payload['user_id'])
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    access_token, new_refresh_token = AuthService.generate_tokens(user.id)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': new_refresh_token
    }), 200

@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token():
    """Verify if token is valid"""
    return jsonify({
        'message': 'Token is valid',
        'user': request.user.to_dict()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """Logout user (token blacklisting would be implemented in production)"""
    return jsonify({'message': 'Logout successful'}), 200

class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)

class VerifyOTPSchema(Schema):
    email = fields.Email(required=True)
    otp = fields.Str(required=True, validate=validate.Length(equal=6))
    new_password = fields.Str(required=True, validate=validate.Length(min=8))

class GoogleLoginSchema(Schema):
    credential = fields.Str(required=True)
    requested_role = fields.Str(
        allow_none=True,
        validate=validate.OneOf([
            UserRole.FARMER.value,
            UserRole.DISTRIBUTOR.value,
            UserRole.SUPPLIER.value,
            UserRole.ADMIN.value
        ])
    )


def _normalize_google_signup_role(requested_role):
    if requested_role == UserRole.SUPPLIER.value:
        return UserRole.DISTRIBUTOR.value
    if requested_role in (UserRole.FARMER.value, UserRole.DISTRIBUTOR.value):
        return requested_role
    return UserRole.FARMER.value


@auth_bp.route('/google-config', methods=['GET'])
def google_config():
    enabled = is_google_login_configured()
    return jsonify({
        'enabled': enabled,
        'client_id': current_app.config.get('GOOGLE_CLIENT_ID') if enabled else None
    }), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    schema = ForgotPasswordSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
        
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({'message': 'User with this email not found'}), 404
        
    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    user.reset_otp = otp
    user.reset_otp_expiry = datetime.utcnow() + timedelta(minutes=10)

    try:
        send_password_reset_otp(user.email, otp)
        db.session.commit()
    except EmailDeliveryError as err:
        db.session.rollback()
        return jsonify({'message': str(err)}), 503
    except Exception:
        db.session.rollback()
        current_app.logger.exception('Unexpected error while sending password reset OTP')
        return jsonify({'message': 'Failed to process password reset request'}), 500

    return jsonify({'message': 'OTP sent successfully to your email.'}), 200

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    schema = VerifyOTPSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
        
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
        
    if user.reset_otp != data['otp'] or not user.reset_otp_expiry:
        return jsonify({'message': 'Invalid OTP'}), 400
        
    if datetime.utcnow() > user.reset_otp_expiry:
        return jsonify({'message': 'OTP has expired'}), 400
        
    # Reset password
    user.set_password(data['new_password'])
    user.reset_otp = None
    user.reset_otp_expiry = None
    
    db.session.commit()
    
    return jsonify({'message': 'Password reset successful.'}), 200

@auth_bp.route('/google-login', methods=['POST'])
def google_login():
    schema = GoogleLoginSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400

    try:
        google_user = verify_google_id_token(data['credential'])
    except GoogleAuthError as err:
        return jsonify({'message': str(err)}), 401
    except Exception:
        current_app.logger.exception('Unexpected error while verifying Google credential')
        return jsonify({'message': 'Google sign-in failed'}), 500

    email = google_user['email']
    name = google_user.get('name') or email.split('@')[0]
    requested_role = data.get('requested_role')
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        if requested_role == UserRole.ADMIN.value:
            return jsonify({
                'message': 'Admin Google sign-in is only available for existing admin accounts.'
            }), 403

        username = email.split('@')[0]
        base_username = username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
            
        user = User(
            username=username,
            email=email,
            full_name=name,
            role=_normalize_google_signup_role(requested_role),
            is_verified=True
        )
        user.set_password(secrets.token_urlsafe(16))
        
        db.session.add(user)
        db.session.commit()
    else:
        if requested_role == UserRole.ADMIN.value and user.role != UserRole.ADMIN.value:
            return jsonify({'message': 'This Google account is not linked to an admin user.'}), 403
        
    if not user.is_active:
        return jsonify({'message': 'Account is inactive'}), 403
        
    # Generate tokens
    access_token, refresh_token = AuthService.generate_tokens(user.id)
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200
