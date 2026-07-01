import os
import sys
from flask import send_from_directory
from app import create_app, db
from app.models import User, Crop, SupplyChainRecord, AuditLog

app = create_app(os.getenv('FLASK_ENV', 'development'))

# ──────────────────────────────────────────────
# Serve frontend HTML files from Flask
# ──────────────────────────────────────────────
FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'Agrotrace-DNA-main')
)

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_frontend(filename):
    filepath = os.path.join(FRONTEND_DIR, filename)
    if os.path.isfile(filepath):
        return send_from_directory(FRONTEND_DIR, filename)
    # Fall back to index for SPA-like behavior
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Crop': Crop,
        'SupplyChainRecord': SupplyChainRecord,
        'AuditLog': AuditLog
    }


def seed_database():
    """Create default admin and test farmer accounts."""
    with app.app_context():
        # Create admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@agrotrace.com',
                full_name='System Admin',
                phone='9999999999',
                role='admin',
                is_active=True,
                is_verified=True
            )
            admin.set_password('Admin@12345')
            db.session.add(admin)
            print('  [OK] Admin user created  - username: admin / password: Admin@12345')
        else:
            print('  [INFO] Admin user already exists')

        # Create test farmer
        farmer = User.query.filter_by(username='testfarmer99').first()
        if not farmer:
            farmer = User(
                username='testfarmer99',
                email='farmer@agrotrace.com',
                full_name='Test Farmer',
                phone='9876543210',
                role='farmer',
                farm_name='Green Valley Farm',
                farm_size=5.5,
                address='Kannad, Aurangabad',
                city='Aurangabad',
                country='India',
                is_active=True,
                is_verified=True
            )
            farmer.set_password('Test@12345')
            db.session.add(farmer)
            print('  [OK] Test farmer created - username: testfarmer99 / password: Test@12345')
        else:
            print('  [INFO] Test farmer already exists')

        db.session.commit()
        print('\n  Seed complete. You can now login with either account.')


if __name__ == '__main__':
    # Handle `python run.py seed` command
    if len(sys.argv) > 1 and sys.argv[1] == 'seed':
        print('\n--- Seeding database ---\n')
        seed_database()
        sys.exit(0)

    port = int(os.getenv('SERVER_PORT', 5000))
    host = os.getenv('SERVER_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_ENV') == 'development'

    print(f'\n=== Starting AgroTrace-DNA Backend ===')
    print(f'   API:      http://{host}:{port}/api')
    print(f'   Frontend: http://{host}:{port}/')
    print(f'   Health:   http://{host}:{port}/api/health\n')

    app.run(host=host, port=port, debug=debug)
