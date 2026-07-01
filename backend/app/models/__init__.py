from app import db
from datetime import datetime
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    FARMER = "farmer"
    CONSUMER = "consumer"
    DISTRIBUTOR = "distributor"
    SUPPLIER = "supplier"
    INSPECTOR = "inspector"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), default=UserRole.FARMER.value, nullable=False)
    
    # Profile information
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(80), nullable=True)
    country = db.Column(db.String(80), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    
    # Farmer specific
    farm_name = db.Column(db.String(120), nullable=True)
    farm_size = db.Column(db.Float, nullable=True)  # in acres
    
    # Distributor / Supplier specific
    gst_number = db.Column(db.String(20), nullable=True)
    business_type = db.Column(db.String(80), nullable=True)
    license_number = db.Column(db.String(80), nullable=True)
    
    # Admin specific
    department = db.Column(db.String(120), nullable=True)
    designation = db.Column(db.String(120), nullable=True)
    employee_id = db.Column(db.String(80), nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # OTP Fields
    reset_otp = db.Column(db.String(6), nullable=True)
    reset_otp_expiry = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    crops = db.relationship('Crop', backref='farmer', lazy=True, foreign_keys='Crop.farmer_id')
    supply_chain_records = db.relationship('SupplyChainRecord', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'farm_name': self.farm_name,
            'farm_size': self.farm_size
        }
        # Include distributor fields if applicable
        if self.role in (UserRole.DISTRIBUTOR.value, UserRole.SUPPLIER.value, 'distributor', 'supplier'):
            data['gst_number'] = self.gst_number
            data['business_type'] = self.business_type
            data['license_number'] = self.license_number
        # Include admin fields if applicable
        if self.role in (UserRole.ADMIN.value, 'admin'):
            data['department'] = self.department
            data['designation'] = self.designation
            data['employee_id'] = self.employee_id
        return data

class Crop(db.Model):
    __tablename__ = 'crops'
    
    id = db.Column(db.Integer, primary_key=True)
    crop_id_code = db.Column(db.String(50), unique=True, nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Crop information
    crop_type = db.Column(db.String(100), nullable=False)  # e.g., Wheat, Rice, Corn
    variety = db.Column(db.String(100), nullable=True)
    
    # Soil & Environmental
    soil_type = db.Column(db.String(100), nullable=True)
    soil_ph = db.Column(db.Float, nullable=True)
    moisture_level = db.Column(db.Float, nullable=True)
    nitrogen_level = db.Column(db.Float, nullable=True)
    phosphorus_level = db.Column(db.Float, nullable=True)
    potassium_level = db.Column(db.Float, nullable=True)
    
    # Planting details
    planting_date = db.Column(db.DateTime, nullable=False)
    expected_harvest_date = db.Column(db.DateTime, nullable=True)
    area_planted = db.Column(db.Float, nullable=True)  # in hectares
    
    # Current status
    growth_stage = db.Column(db.String(50), nullable=True)  # e.g., Germination, Flowering, etc.
    health_status = db.Column(db.String(50), nullable=True)  # Good, Fair, Poor
    
    # QR Code
    qr_code = db.Column(db.String(255), nullable=True)
    qr_code_url = db.Column(db.String(255), nullable=True)
    
    # Certifications
    is_organic = db.Column(db.Boolean, default=False)
    certification_details = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    harvested_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    supply_chain_records = db.relationship('SupplyChainRecord', backref='crop', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'crop_id_code': self.crop_id_code,
            'farmer_id': self.farmer_id,
            'crop_type': self.crop_type,
            'variety': self.variety,
            'planting_date': self.planting_date.isoformat(),
            'growth_stage': self.growth_stage,
            'health_status': self.health_status,
            'is_organic': self.is_organic,
            'qr_code_url': self.qr_code_url,
            'created_at': self.created_at.isoformat()
        }

class SupplyChainRecord(db.Model):
    __tablename__ = 'supply_chain_records'
    
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crops.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Record information
    stage = db.Column(db.String(50), nullable=False)  # e.g., Harvested, Processed, Packaged, Shipped, Received
    location = db.Column(db.String(255), nullable=False)
    temperature = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    
    # Handling details
    handler_name = db.Column(db.String(120), nullable=True)
    handler_role = db.Column(db.String(50), nullable=True)
    
    # Notes & observations
    notes = db.Column(db.Text, nullable=True)
    quality_status = db.Column(db.String(50), nullable=True)  # Good, Fair, Poor
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'crop_id': self.crop_id,
            'user_id': self.user_id,
            'stage': self.stage,
            'location': self.location,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'handler_name': self.handler_name,
            'handler_role': self.handler_role,
            'notes': self.notes,
            'quality_status': self.quality_status,
            'created_at': self.created_at.isoformat()
        }

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'created_at': self.created_at.isoformat()
        }
