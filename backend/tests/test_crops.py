from datetime import datetime, timedelta

def test_create_crop(client, auth_token, sample_user, app):
    """Test crop creation."""
    response = client.post('/api/crops', 
        json={
            'crop_type': 'Wheat',
            'variety': 'Premium Wheat',
            'planting_date': datetime.utcnow().isoformat(),
            'soil_type': 'Loam',
            'area_planted': 5.0
        },
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['crop']['crop_type'] == 'Wheat'
    assert 'crop_id_code' in data['crop']

def test_list_crops(client, auth_token):
    """Test listing crops."""
    response = client.get('/api/crops', headers={
        'Authorization': f'Bearer {auth_token}'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'crops' in data
    assert 'total' in data

def test_get_crop(client, auth_token, sample_user, app):
    """Test getting a specific crop."""
    # Create a crop first
    from app.models import Crop
    from app import db
    
    with app.app_context():
        crop = Crop(
            crop_id_code='TEST-CROP-001',
            farmer_id=sample_user.id,
            crop_type='Rice',
            planting_date=datetime.utcnow()
        )
        db.session.add(crop)
        db.session.commit()
        crop_id = crop.id
    
    response = client.get(f'/api/crops/{crop_id}', headers={
        'Authorization': f'Bearer {auth_token}'
    })
    
    assert response.status_code == 200
    assert response.get_json()['crop']['crop_type'] == 'Rice'

def test_track_crop_public(client):
    """Test public crop tracking endpoint."""
    response = client.get('/api/crops/NONEXISTENT/track')
    assert response.status_code == 404

def test_track_crop_public_success(client, sample_user, app):
    """Test public crop tracking data shape."""
    from app.models import Crop
    from app import db

    with app.app_context():
      crop = Crop(
          crop_id_code='TEST-PUBLIC-001',
          farmer_id=sample_user.id,
          crop_type='Wheat',
          variety='HD-2967',
          soil_type='Black Cotton Soil',
          soil_ph=6.5,
          moisture_level=38,
          nitrogen_level=45,
          phosphorus_level=32,
          potassium_level=58,
          planting_date=datetime.utcnow(),
          area_planted=2.5,
          certification_details='Kharif 2026'
      )
      db.session.add(crop)
      db.session.commit()

    response = client.get('/api/crops/TEST-PUBLIC-001/track')
    assert response.status_code == 200
    data = response.get_json()
    assert data['crop']['crop_id_code'] == 'TEST-PUBLIC-001'
    assert data['crop']['soil_ph'] == 6.5
    assert data['farmer']['name'] == 'Test Farmer'

def test_public_supply_chain_includes_handler_details(client, sample_user, app):
    """Test public supply chain endpoint returns handler fields."""
    from app.models import Crop, SupplyChainRecord
    from app import db

    with app.app_context():
        crop = Crop(
            crop_id_code='TEST-SC-001',
            farmer_id=sample_user.id,
            crop_type='Tomato',
            planting_date=datetime.utcnow()
        )
        db.session.add(crop)
        db.session.commit()

        record = SupplyChainRecord(
            crop_id=crop.id,
            user_id=sample_user.id,
            stage='Shipped',
            location='Pune Warehouse',
            temperature=18.5,
            humidity=62.0,
            handler_name='FreshRoute Logistics',
            handler_role='Distributor',
            notes='Loaded for outbound dispatch',
            quality_status='Good'
        )
        db.session.add(record)
        db.session.commit()

    response = client.get('/api/supply-chain/TEST-SC-001/public')
    assert response.status_code == 200
    data = response.get_json()
    assert data['total_records'] == 1
    assert data['records'][0]['handler_name'] == 'FreshRoute Logistics'
    assert data['records'][0]['handler_role'] == 'Distributor'
