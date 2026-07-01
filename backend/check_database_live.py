import sqlite3
import json
import os

print('\n' + '='*70)
print('🌾 AGROTRACE-DNA DATABASE LIVE VERIFICATION 🌾')
print('='*70 + '\n')

# Connect to database
db_path = 'instance/agrotrace.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 1. Check database file
db_size = os.path.getsize(db_path)
print('DATABASE FILE')
print(f'   Location: {db_path}')
print(f'   Size: {db_size} bytes')
print('   Status: ✅ Active\n')

# 2. Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f'TABLES IN DATABASE: {len(tables)} tables')
for table in tables:
    cursor.execute(f'SELECT COUNT(*) as count FROM {table}')
    count = cursor.fetchone()[0]
    print(f'   ✅ {table}: {count} records')
print()

# 3. Users data
print('━'*70)
print('USERS TABLE')
print('━'*70)
cursor.execute('SELECT id, username, email, full_name, role, is_active FROM users')
users = cursor.fetchall()
if users:
    for user in users:
        print(f"   ID: {user['id']} | Username: {user['username']} | Email: {user['email']}")
        print(f"   Name: {user['full_name']} | Role: {user['role']} | Active: {user['is_active']}")
        print()
else:
    print('   No users found')

# 4. Crops data
print('━'*70)
print('CROPS TABLE')
print('━'*70)
cursor.execute('''SELECT id, crop_id_code, farmer_id, crop_type, variety, 
                          soil_ph, planting_date, expected_harvest_date FROM crops''')
crops = cursor.fetchall()
if crops:
    for crop in crops:
        print(f"   ID: {crop['id']} | Code: {crop['crop_id_code']}")
        print(f"   Farmer ID: {crop['farmer_id']} | Type: {crop['crop_type']} | Variety: {crop['variety']}")
        print(f"   Soil pH: {crop['soil_ph']} | Planting: {crop['planting_date']}")
        print(f"   Harvest Expected: {crop['expected_harvest_date']}")
        print()
else:
    print('   No crops found')

# 5. Supply Chain Records
print('━'*70)
print('SUPPLY CHAIN RECORDS TABLE')
print('━'*70)
cursor.execute('''SELECT id, crop_id, user_id, stage, location, 
                          temperature, humidity, handler_name, quality_status FROM supply_chain_records''')
records = cursor.fetchall()
if records:
    for record in records:
        print(f"   ID: {record['id']} | Crop ID: {record['crop_id']} | User ID: {record['user_id']}")
        print(f"   Stage: {record['stage']} | Location: {record['location']}")
        print(f"   Temp: {record['temperature']}°C | Humidity: {record['humidity']}%")
        print(f"   Handler: {record['handler_name']} | Quality: {record['quality_status']}")
        print()
else:
    print('   No supply chain records found')

# 6. Audit Logs
print('━'*70)
print('AUDIT LOGS TABLE')
print('━'*70)
cursor.execute('SELECT COUNT(*) as count FROM audit_logs')
log_count = cursor.fetchone()[0]
print(f'   Total logs: {log_count}')

conn.close()

print('━'*70)
print('✅ DATABASE VERIFICATION COMPLETE')
print('='*70 + '\n')
