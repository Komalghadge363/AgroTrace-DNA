from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Crop, SupplyChainRecord, AuditLog
from app.utils.auth import admin_required, token_required
from datetime import datetime, timedelta
from sqlalchemy import text, func

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/statistics', methods=['GET'])
@admin_required
def get_statistics():
    """Get platform statistics"""
    total_users = User.query.count()
    farmer_count = User.query.filter_by(role='farmer').count()
    consumer_count = User.query.filter_by(role='consumer').count()
    distributor_count = User.query.filter_by(role='distributor').count()
    inspector_count = User.query.filter_by(role='inspector').count()

    # Crop statistics
    total_crops = Crop.query.count()
    organic_crops = Crop.query.filter_by(is_organic=True).count()

    # Crop type distribution
    crop_distribution = db.session.query(
        Crop.crop_type, func.count(Crop.id)
    ).group_by(Crop.crop_type).order_by(func.count(Crop.id).desc()).limit(10).all()

    # Supply chain statistics
    total_supply_records = SupplyChainRecord.query.count()

    # Crops with QR codes generated
    qr_generated_count = Crop.query.filter(Crop.qr_code_url.isnot(None)).count()

    # Recent registrations (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_farmers_this_week = User.query.filter(
        User.role == 'farmer',
        User.created_at >= week_ago
    ).count()
    new_crops_this_week = Crop.query.filter(
        Crop.created_at >= week_ago
    ).count()

    # Get recent activity
    audit_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()
    
    return jsonify({
        'total_users': total_users,
        'farmer_count': farmer_count,
        'consumer_count': consumer_count,
        'distributor_count': distributor_count,
        'inspector_count': inspector_count,
        'total_crops': total_crops,
        'organic_crops': organic_crops,
        'total_supply_records': total_supply_records,
        'qr_generated_count': qr_generated_count,
        'new_farmers_this_week': new_farmers_this_week,
        'new_crops_this_week': new_crops_this_week,
        'crop_distribution': [
            {'crop_type': ct, 'count': count}
            for ct, count in crop_distribution
        ],
        'recent_activity': [log.to_dict() for log in audit_logs]
    }), 200

@admin_bp.route('/audit-logs', methods=['GET'])
@admin_required
def get_audit_logs():
    """Get audit logs"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    action = request.args.get('action', type=str)
    resource_type = request.args.get('resource_type', type=str)
    
    query = AuditLog.query
    
    if action:
        query = query.filter_by(action=action)
    if resource_type:
        query = query.filter_by(resource_type=resource_type)
    
    pagination = query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=per_page
    )
    
    return jsonify({
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'logs': [log.to_dict() for log in pagination.items]
    }), 200

@admin_bp.route('/users/verify/<int:user_id>', methods=['PATCH'])
@admin_required
def verify_user(user_id):
    """Verify a user account"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user.is_verified = True
    user.verification_token = None
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Verification failed', 'error': str(e)}), 500
    
    return jsonify({
        'message': 'User verified successfully',
        'user': user.to_dict()
    }), 200

@admin_bp.route('/users/<int:user_id>/deactivate', methods=['PATCH'])
@admin_required
def deactivate_user(user_id):
    """Deactivate user account"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user.is_active = False
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Deactivation failed', 'error': str(e)}), 500
    
    return jsonify({
        'message': 'User deactivated',
        'user': user.to_dict()
    }), 200

@admin_bp.route('/health', methods=['GET'])
@admin_required
def system_health():
    """Check system health"""
    try:
        # Test database connection
        result = db.session.execute(text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@admin_bp.route('/logs/create', methods=['POST'])
@token_required
def create_audit_log():
    """Create an audit log entry"""
    data = request.get_json()
    
    log = AuditLog(
        user_id=request.user.id,
        action=data.get('action'),
        resource_type=data.get('resource_type'),
        resource_id=data.get('resource_id'),
        details=data.get('details'),
        ip_address=request.remote_addr
    )
    
    try:
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Log creation failed', 'error': str(e)}), 500
    
    return jsonify({
        'message': 'Audit log created',
        'log': log.to_dict()
    }), 201
