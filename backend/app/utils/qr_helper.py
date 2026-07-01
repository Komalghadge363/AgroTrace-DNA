import qrcode
from io import BytesIO
import uuid
import os

def generate_qr_code(data):
    """Generate QR code from data"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def save_qr_code(data, folder=None):
    """Generate and save QR code"""
    if folder is None:
        # Use absolute path to uploads folder: backend/app/uploads
        # __file__ = backend/app/utils/qr_helper.py
        current_dir = os.path.dirname(os.path.abspath(__file__))  # backend/app/utils
        app_dir = os.path.dirname(current_dir)  # backend/app
        folder = os.path.join(app_dir, 'uploads')
    
    # Ensure folder exists
    os.makedirs(folder, exist_ok=True)
    
    img = generate_qr_code(data)
    filename = f"qr_{uuid.uuid4().hex}.png"
    filepath = os.path.join(folder, filename)
    img.save(filepath)
    return filepath, filename
