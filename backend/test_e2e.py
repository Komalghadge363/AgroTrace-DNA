import requests, json

BASE = 'http://127.0.0.1:5000/api'

# 1) Login
r = requests.post(f'{BASE}/auth/login', json={'username':'testfarmer99','password':'Test@12345'})
print('LOGIN:', r.status_code)
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 2) Create crop
crop_data = {
    'crop_type': 'Wheat',
    'variety': 'HD-2967',
    'planting_date': '2026-01-15T00:00:00',
    'area_planted': 5.5,
    'soil_ph': 6.8,
    'is_organic': True
}
r2 = requests.post(f'{BASE}/crops', json=crop_data, headers=headers)
print('CROP CREATE:', r2.status_code, r2.text[:500])

if r2.status_code == 201:
    crop = r2.json()['crop']
    code = crop['crop_id_code']
    cid = crop['id']
    print(f'  Crop ID: {cid}, Code: {code}')

    # 3) Track crop (public)
    r3 = requests.get(f'{BASE}/crops/{code}/track')
    print('TRACK:', r3.status_code, r3.text[:300])

    # 4) Supply chain record
    sc = {'crop_id': cid, 'stage': 'Harvested', 'location': 'Kannad Mandi'}
    r4 = requests.post(f'{BASE}/supply-chain', json=sc, headers=headers)
    print('SUPPLY CHAIN:', r4.status_code, r4.text[:300])

    # 5) Public supply chain
    r5 = requests.get(f'{BASE}/supply-chain/{code}/public')
    print('PUBLIC SC:', r5.status_code, r5.text[:300])
else:
    print('Crop creation failed, skipping remaining tests')

# 6) QR generate
if r2.status_code == 201:
    r6 = requests.post(f'{BASE}/qr/generate', json={'crop_id': cid}, headers=headers)
    print('QR GENERATE:', r6.status_code, r6.text[:300])

print('\n=== ALL TESTS COMPLETE ===')
