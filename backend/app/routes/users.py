from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from app.utils.auth import token_required, role_required, admin_required
from marshmallow import Schema, fields, validate, ValidationError

users_bp = Blueprint('users', __name__)

class UserUpdateSchema(Schema):
    full_name = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    country = fields.Str(allow_none=True)
    postal_code = fields.Str(allow_none=True)
    farm_name = fields.Str(allow_none=True)
    farm_size = fields.Float(allow_none=True)

@users_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get current user's profile"""
    return jsonify({
        'user': request.user.to_dict()
    }), 200

@users_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    """Update current user's profile"""
    schema = UserUpdateSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    user = request.user
    
    # Update fields
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'address' in data:
        user.address = data['address']
    if 'city' in data:
        user.city = data['city']
    if 'country' in data:
        user.country = data['country']
    if 'postal_code' in data:
        user.postal_code = data['postal_code']
    if 'farm_name' in data:
        user.farm_name = data['farm_name']
    if 'farm_size' in data:
        user.farm_size = data['farm_size']
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Update failed', 'error': str(e)}), 500
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    }), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """Get user by ID (admin only or own profile)"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Allow access to own profile or if admin
    if request.user.id != user_id and request.user.role != 'admin':
        return jsonify({'message': 'Access denied'}), 403
    
    return jsonify({
        'user': user.to_dict()
    }), 200

@users_bp.route('', methods=['GET'])
@admin_required
def list_users():
    """List all users (admin only)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role = request.args.get('role', type=str)
    
    query = User.query
    
    if role:
        query = query.filter_by(role=role)
    
    pagination = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'users': [user.to_dict() for user in pagination.items]
    }), 200

@users_bp.route('/<int:user_id>/status', methods=['PATCH'])
@admin_required
def update_user_status(user_id):
    """Update user status (admin only)"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.get_json()
    
    if 'is_active' in data:
        user.is_active = data['is_active']
    if 'is_verified' in data:
        user.is_verified = data['is_verified']
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Update failed', 'error': str(e)}), 500
    
    return jsonify({
        'message': 'User status updated',
        'user': user.to_dict()
    }), 200

@users_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Change user password"""
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'message': 'Current and new passwords are required'}), 400
    
    user = request.user
    
    if not user.check_password(current_password):
        return jsonify({'message': 'Current password is incorrect'}), 401
    
    if len(new_password) < 8:
        return jsonify({'message': 'Password must be at least 8 characters'}), 400
    
    user.set_password(new_password)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Password change failed', 'error': str(e)}), 500
    
    return jsonify({'message': 'Password changed successfully'}), 200
