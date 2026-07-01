from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import config
import os

db = SQLAlchemy()

def create_app(config_name=None):
    """Application factory function"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    cors_origins = app.config['CORS_ORIGINS']
    if app.config.get('DEBUG') or app.config.get('TESTING'):
        cors_origins = '*'
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.crops import crops_bp
    from app.routes.supply_chain import supply_chain_bp
    from app.routes.qr_code import qr_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(crops_bp, url_prefix='/api/crops')
    app.register_blueprint(supply_chain_bp, url_prefix='/api/supply-chain')
    app.register_blueprint(qr_bp, url_prefix='/api/qr')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Register error handlers
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)
    
    @app.route('/api', methods=['GET'])
    @app.route('/api/', methods=['GET'])
    def api_index():
        return {
            'status': 'healthy',
            'message': 'Agrotrace-DNA API is running',
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth',
                'users': '/api/users',
                'crops': '/api/crops',
                'supply_chain': '/api/supply-chain',
                'qr': '/api/qr',
                'admin': '/api/admin'
            }
        }, 200

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'message': 'API is running'}, 200
    
    return app
