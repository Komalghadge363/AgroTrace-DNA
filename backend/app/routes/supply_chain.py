from flask import Blueprint, request, jsonify
from app import db
from app.models import SupplyChainRecord, Crop
from app.utils.auth import token_required
from marshmallow import Schema, fields, validate, ValidationError

supply_chain_bp = Blueprint('supply_chain', __name__)

class SupplyChainSchema(Schema):
    crop_id = fields.Int(required=True)
    stage = fields.Str(required=True, validate=validate.OneOf([
        'Harvested', 'Processed', 'Packaged', 'Shipped', 'Received', 'Sold'
    ]))
    location = fields.Str(required=True)
    temperature = fields.Float(allow_none=True)
    humidity = fields.Float(allow_none=True)
    handler_name = fields.Str(allow_none=True)
    handler_role = fields.Str(allow_none=True)
    notes = fields.Str(allow_none=True)
    quality_status = fields.Str(allow_none=True, validate=validate.OneOf([
        'Good', 'Fair', 'Poor'
    ]))

@supply_chain_bp.route('', methods=['POST'])
@token_required
def create_supply_chain_record():
    """Create a supply chain record"""
    schema = SupplyChainSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Verify crop exists
    crop = Crop.query.get(data['crop_id'])
    if not crop:
        return jsonify({'message': 'Crop not found'}), 404
    
    # Check authorization
    if request.user.role == 'farmer' and crop.farmer_id != request.user.id:
        return jsonify({'message': 'Access denied'}), 403
    
    record = SupplyChainRecord(
        crop_id=data['crop_id'],
        user_id=request.user.id,
        stage=data['stage'],
        location=data['location'],
        temperature=data.get('temperature'),
        humidity=data.get('humidity'),
        handler_name=data.get('handler_name'),
        handler_role=data.get('handler_role'),
        notes=data.get('notes'),
        quality_status=data.get('quality_status')
    )
    
    try:
        db.session.add(record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create record', 'error': str(e)}), 500
    
    return jsonify({
        'message': 'Supply chain record created',
        'record': record.to_dict()
    }), 201

@supply_chain_bp.route('/crop/<int:crop_id>', methods=['GET'])
@token_required
def get_supply_chain_history(crop_id):
    """Get supply chain history for a crop"""
    crop = Crop.query.get(crop_id)
    
    if not crop:
        return jsonify({'message': 'Crop not found'}), 404
    
    # Check authorization
    if request.user.role == 'farmer' and crop.farmer_id != request.user.id:
        return jsonify({'message': 'Access denied'}), 403
    
    records = SupplyChainRecord.query.filter_by(crop_id=crop_id).order_by(
        SupplyChainRecord.created_at
    ).all()
    
    return jsonify({
        'crop_id': crop_id,
        'total_records': len(records),
        'records': [record.to_dict() for record in records]
    }), 200

@supply_chain_bp.route('/<int:record_id>', methods=['GET'])
@token_required
def get_supply_chain_record(record_id):
    """Get specific supply chain record"""
    record = SupplyChainRecord.query.get(record_id)
    
    if not record:
        return jsonify({'message': 'Record not found'}), 404
    
    # Check authorization
    if request.user.role == 'farmer' and record.crop.farmer_id != request.user.id:
        return jsonify({'message': 'Access denied'}), 403
    
    return jsonify({
        'record': record.to_dict()
    }), 200

@supply_chain_bp.route('/<int:record_id>', methods=['PUT'])
@token_required
def update_supply_chain_record(record_id):
    """Update supply chain record"""
    record = SupplyChainRecord.query.get(record_id)
    
    if not record:
        return jsonify({'message': 'Record not found'}), 404
    
    # Only allow updates by the record creator or admin
    if request.user.id != record.user_id and request.user.role != 'admin':
        return jsonify({'message': 'Access denied'}), 403
    
    schema = SupplyChainSchema(partial=True)
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Update fields
    if 'stage' in data:
        record.stage = data['stage']
    if 'location' in data:
        record.location = data['location']
    if 'temperature' in data:
        record.temperature = data['temperature']
    if 'humidity' in data:
        record.humidity = data['humidity']
    if 'notes' in data:
        record.notes = data['notes']
    if 'quality_status' in data:
        record.quality_status = data['quality_status']
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Update failed', 'error': str(e)}), 500
    
    return jsonify({
        'message': 'Record updated successfully',
        'record': record.to_dict()
    }), 200

@supply_chain_bp.route('/<crop_id_code>/public', methods=['GET'])
def get_supply_chain_public(crop_id_code):
    """Public endpoint to view supply chain history"""
    crop = Crop.query.filter_by(crop_id_code=crop_id_code).first()
    
    if not crop:
        return jsonify({'message': 'Crop not found'}), 404
    
    records = SupplyChainRecord.query.filter_by(crop_id=crop.id).order_by(
        SupplyChainRecord.created_at
    ).all()
    
    return jsonify({
        'crop_id_code': crop_id_code,
        'crop_type': crop.crop_type,
        'farmer': crop.farmer.full_name if crop.farmer else 'Unknown',
        'total_records': len(records),
        'records': [record.to_dict() for record in records]
    }), 200
