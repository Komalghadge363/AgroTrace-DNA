from flask import Blueprint, request, jsonify
from app import db
from app.models import Crop, User
from app.utils.auth import token_required, role_required
from app.utils.qr_helper import save_qr_code
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime
import uuid

crops_bp = Blueprint('crops', __name__)

class CropSchema(Schema):
    crop_type = fields.Str(required=True, validate=validate.Length(min=1))
    variety = fields.Str(allow_none=True)
    soil_type = fields.Str(allow_none=True)
    soil_ph = fields.Float(allow_none=True)
    moisture_level = fields.Float(allow_none=True)
    nitrogen_level = fields.Float(allow_none=True)
    phosphorus_level = fields.Float(allow_none=True)
    potassium_level = fields.Float(allow_none=True)
    planting_date = fields.DateTime(required=True)
    expected_harvest_date = fields.DateTime(allow_none=True)
    area_planted = fields.Float(allow_none=True)
    growth_stage = fields.Str(allow_none=True)
    health_status = fields.Str(allow_none=True)
    is_organic = fields.Bool(allow_none=True)
    certification_details = fields.Str(allow_none=True)

@crops_bp.route('', methods=['POST'])
@token_required
@role_required('farmer', 'admin')
def create_crop():
    """Create a new crop record"""
    schema = CropSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Generate unique crop ID
    crop_id_code = f"CROP-{uuid.uuid4().hex[:12].upper()}"
    
    farmer_id = request.user.id if request.user.role == 'farmer' else request.user.id
    
    crop = Crop(
        crop_id_code=crop_id_code,
        farmer_id=farmer_id,
        crop_type=data['crop_type'],
        variety=data.get('variety'),
        soil_type=data.get('soil_type'),
        soil_ph=data.get('soil_ph'),
        moisture_level=data.get('moisture_level'),
        nitrogen_level=data.get('nitrogen_level'),
        phosphorus_level=data.get('phosphorus_level'),
        potassium_level=data.get('potassium_level'),
        planting_date=data['planting_date'],
        expected_harvest_date=data.get('expected_harvest_date'),
        area_planted=data.get('area_planted'),
        growth_stage=data.get('growth_stage', 'Germination'),
        health_status=data.get('health_status', 'Good'),
        is_organic=data.get('is_organic', False),
        certification_details=data.get('certification_details')
    )
    
    # Generate QR code pointing to the live verification page
    qr_data = f"{request.host_url}consumer-verification.html?cropId={crop_id_code}"
    try:
        qr_path, qr_filename = save_qr_code(qr_data)
        crop.qr_code = qr_filename
        crop.qr_code_url = f"/api/qr/download/{qr_filename}"
    except Exception as e:
        print(f"QR code generation error: {e}")
    
    try:
        db.session.add(crop)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create crop', 'error': str(e)}), 500
    
    return jsonify({
        'message': 'Crop created successfully',
        'crop': crop.to_dict()
    }), 201

@crops_bp.route('', methods=['GET'])
@token_required
def list_crops():
    """List crops (filtered by user role)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Crop.query
    
    # Farmers see only their crops
    if request.user.role == 'farmer':
        query = query.filter_by(farmer_id=request.user.id)
    
    pagination = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'crops': [crop.to_dict() for crop in pagination.items]
    }), 200

@crops_bp.route('/<int:crop_id>', methods=['GET'])
@token_required
def get_crop(crop_id):
    """Get crop details"""
    crop = Crop.query.get(crop_id)
    
    if not crop:
        return jsonify({'message': 'Crop not found'}), 404
    
    # Check authorization
    if request.user.role == 'farmer' and crop.farmer_id != request.user.id:
        return jsonify({'message': 'Access denied'}), 403
    
    return jsonify({
        'crop': crop.to_dict()
    }), 200

@crops_bp.route('/<int:crop_id>', methods=['PUT'])
@token_required
def update_crop(crop_id):
    """Update crop information"""
    crop = Crop.query.get(crop_id)
    
    if not crop:
        return jsonify({'message': 'Crop not found'}), 404
    
    # Check authorization
    if request.user.role == 'farmer' and crop.farmer_id != request.user.id:
        return jsonify({'message': 'Access denied'}), 403
    
    schema = CropSchema(partial=True)
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Update fields
    for key, value in data.items():
        if hasattr(crop, key):
            setattr(crop, key, value)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update crop', 'error': str(e)}), 500
    
    return jsonify({
        'message': 'Crop updated successfully',
        'crop': crop.to_dict()
    }), 200

@crops_bp.route('/<int:crop_id>', methods=['DELETE'])
@token_required
@role_required('farmer', 'admin')
def delete_crop(crop_id):
    """Delete crop record"""
    crop = Crop.query.get(crop_id)
    
    if not crop:
        return jsonify({'message': 'Crop not found'}), 404
    
    # Check authorization
    if request.user.role == 'farmer' and crop.farmer_id != request.user.id:
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        db.session.delete(crop)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete crop', 'error': str(e)}), 500
    
    return jsonify({'message': 'Crop deleted successfully'}), 200

@crops_bp.route('/<crop_id_code>/track', methods=['GET'])
def track_crop(crop_id_code):
    """Public endpoint to track crop by crop ID code"""
    crop = Crop.query.filter_by(crop_id_code=crop_id_code).first()
    
    if not crop:
        return jsonify({'message': 'Crop not found'}), 404

    farmer = crop.farmer
    village = None
    taluka = None
    if farmer and farmer.address:
        address_parts = [part.strip() for part in farmer.address.split(',')]
        if address_parts:
            village = address_parts[0] or None
        if len(address_parts) > 1:
            taluka = address_parts[1] or None
    
    return jsonify({
        'crop': {
            **crop.to_dict(),
            'soil_type': crop.soil_type,
            'soil_ph': crop.soil_ph,
            'moisture_level': crop.moisture_level,
            'nitrogen_level': crop.nitrogen_level,
            'phosphorus_level': crop.phosphorus_level,
            'potassium_level': crop.potassium_level,
            'expected_harvest_date': crop.expected_harvest_date.isoformat() if crop.expected_harvest_date else None,
            'area_planted': crop.area_planted,
            'season': crop.certification_details
        },
        'farmer': {
            'name': farmer.full_name,
            'reference': f'FRM-{farmer.id:06d}',
            'farm_name': farmer.farm_name,
            'farm_size': farmer.farm_size,
            'village': village,
            'taluka': taluka,
            'district': farmer.city,
            'registered_since': farmer.created_at.isoformat() if farmer.created_at else None
        } if farmer else None
    }), 200
