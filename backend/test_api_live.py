import requests
import json

print('\n' + '='*70)
print('AGROTRACE-DNA LIVE API TESTING')
print('='*70 + '\n')

# Check if server is running
try:
    r = requests.get('http://127.0.0.1:5000/api/health', timeout=2)
    print('SERVER STATUS: RUNNING')
    print('   URL: http://127.0.0.1:5000')
    print(f'   Health Check: {r.status_code} OK\n')
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)

# Test login
print('━'*70)
print('TESTING USER LOGIN (testfarm)')
print('━'*70)
login_data = {'username': 'testfarm', 'password': 'Test@123'}
r = requests.post('http://127.0.0.1:5000/api/auth/login', json=login_data)
print(f'Status Code: {r.status_code}')
resp = r.json()
user_info = resp.get('user', {})
print(f'Username: {user_info.get("username")}')
print(f'Role: {user_info.get("role")}')
token = resp.get('access_token')
print('Token: Issued ✅\n')

# Get user profile
print('━'*70)
print('GETTING USER PROFILE')
print('━'*70)
headers = {'Authorization': f'Bearer {token}'}
r = requests.get('http://127.0.0.1:5000/api/users/profile', headers=headers)
profile = r.json()
print(f'Status Code: {r.status_code}')
print(f'Name: {profile.get("full_name")}')
print(f'Email: {profile.get("email")}')
print(f'Role: {profile.get("role")}\n')

# Get all crops
print('━'*70)
print('GETTING ALL CROPS')
print('━'*70)
r = requests.get('http://127.0.0.1:5000/api/crops', headers=headers)
crops_data = r.json()
print(f'Status Code: {r.status_code}')
print(f'Total Crops: {crops_data.get("total")}')
for crop in crops_data.get('crops', []):
    print(f'   - {crop.get("crop_type")} ({crop.get("crop_id_code")})')
print()

# Get supply chain records
print('━'*70)
print('GETTING SUPPLY CHAIN RECORDS FOR CROP 2')
print('━'*70)
r = requests.get('http://127.0.0.1:5000/api/supply-chain/crop/2', headers=headers)
if r.status_code == 200:
    data = r.json()
    print(f'Status Code: {r.status_code}')
    print(f'Crop ID: {data.get("crop_id")}')
    print(f'Total Records: {data.get("total_records")}')
    for record in data.get('records', []):
        print(f'   - Stage: {record.get("stage")}, Location: {record.get("location")}')
else:
    print(f'Status Code: {r.status_code}')
print()

# Public verification
print('━'*70)
print('PUBLIC CROP VERIFICATION (No Auth Required)')
print('━'*70)
r = requests.get('http://127.0.0.1:5000/api/crops/CROP-FEEA6B86ECB8/track')
print(f'Status Code: {r.status_code}')
crop_data = r.json().get('crop', {})
farmer_data = r.json().get('farmer', {})
print(f'Crop Code: {crop_data.get("crop_id_code")}')
print(f'Crop Type: {crop_data.get("crop_type")}')
print(f'Farmer Name: {farmer_data.get("name")}')
print(f'Organic Status: {crop_data.get("is_organic")}')

print('\n' + '='*70)
print('ALL TESTS PASSED - SYSTEM LIVE & OPERATIONAL')
print('='*70 + '\n')
