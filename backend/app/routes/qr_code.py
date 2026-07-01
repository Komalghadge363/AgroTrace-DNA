from flask import Blueprint, request, jsonify, send_file
from app import db
from app.models import Crop
from app.utils.auth import token_required
from app.utils.qr_helper import save_qr_code, generate_qr_code
from io import BytesIO
import os

qr_bp = Blueprint('qr', __name__)

@qr_bp.route('/generate', methods=['POST'])
@token_required
def generate_qr():
    """Generate QR code for a crop"""
    data = request.get_json()
    crop_id = data.get('crop_id')
    
    if not crop_id:
        return jsonify({'message': 'crop_id is required'}), 400
    
    crop = Crop.query.get(crop_id)
    if not crop:
        return jsonify({'message': 'Crop not found'}), 404
    
    # Check authorization
    if request.user.role == 'farmer' and crop.farmer_id != request.user.id:
        return jsonify({'message': 'Access denied'}), 403
    
    # Generate QR code
    qr_data = f"https://agrotrace.com/crop/{crop.crop_id_code}"
    
    try:
        qr_path, qr_filename = save_qr_code(qr_data)
        crop.qr_code = qr_filename
        crop.qr_code_url = f"/api/qr/download/{qr_filename}"
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to generate QR code', 'error': str(e)}), 500
    
    return jsonify({
        'message': 'QR code generated successfully',
        'qr_code_url': crop.qr_code_url,
        'crop_id': crop.id,
        'crop_id_code': crop.crop_id_code
    }), 200

@qr_bp.route('/download/<filename>', methods=['GET'])
def download_qr(filename):
    """Download QR code image"""
    try:
        # Use absolute path to uploads folder: backend/app/uploads
        # __file__ = backend/app/routes/qr_code.py
        routes_dir = os.path.dirname(os.path.abspath(__file__))  # backend/app/routes
        app_dir = os.path.dirname(routes_dir)  # backend/app
        uploads_dir = os.path.join(app_dir, 'uploads')
        file_path = os.path.join(uploads_dir, filename)
        
        # Security check: ensure file is within uploads directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(uploads_dir)):
            return jsonify({'message': 'Invalid file path'}), 400
        
        if not os.path.exists(file_path):
            return jsonify({'message': 'File not found'}), 404
        
        return send_file(file_path, mimetype='image/png')
    except Exception as e:
        return jsonify({'message': 'Error downloading file', 'error': str(e)}), 500

@qr_bp.route('/<crop_id_code>/view', methods=['GET'])
def view_qr(crop_id_code):
    """View QR code for a crop"""
    crop = Crop.query.filter_by(crop_id_code=crop_id_code).first()
    
    if not crop:
        return jsonify({'message': 'Crop not found'}), 404
    
    if not crop.qr_code_url:
        return jsonify({'message': 'QR code not generated for this crop'}), 404
    
    return jsonify({
        'crop_id_code': crop_id_code,
        'qr_code_url': crop.qr_code_url,
        'crop_type': crop.crop_type
    }), 200

@qr_bp.route('/generate-image', methods=['POST'])
def generate_qr_image():
    """Generate and return QR code image without saving"""
    data = request.get_json()
    qr_data = data.get('data')
    
    if not qr_data:
        return jsonify({'message': 'data field is required'}), 400
    
    try:
        img = generate_qr_code(qr_data)
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return jsonify({'message': 'Failed to generate QR code', 'error': str(e)}), 500
