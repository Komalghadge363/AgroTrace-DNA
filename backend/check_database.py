import sqlite3
import json

# Database path
db_path = 'instance/agrotrace.db'

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n" + "="*70)
print("📊 AGROTRACE-DNA DATABASE — DATA CHECK")
print("="*70)

# 1. Check all tables
print("\n1️⃣  DATABASE TABLES:")
print("-" * 70)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"   ✅ {table[0]}: {count} record(s)")

# 2. Check USERS table
print("\n2️⃣  USERS TABLE (Details):")
print("-" * 70)
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

if users:
    for user in users:
        print(f"\n   User ID: {user[0]}")
        print(f"   Username: {user[1]}")
        print(f"   Email: {user[2]}")
        print(f"   Full Name: {user[4]}")
        print(f"   Phone: {user[5]}")
        print(f"   Role: {user[6]}")
        print(f"   Farm Name: {user[11]}")
        print(f"   Farm Size: {user[12]} acres")
        print(f"   Is Active: {user[24]}")
        print(f"   Is Verified: {user[25]}")
        print(f"   Created At: {user[26]}")
else:
    print("   ❌ No users found")

# 3. Check CROPS table
print("\n3️⃣  CROPS TABLE (Details):")
print("-" * 70)
cursor.execute("SELECT * FROM crops")
crops = cursor.fetchall()

if crops:
    for crop in crops:
        print(f"\n   Crop ID: {crop[0]}")
        print(f"   Crop Code: {crop[1]}")
        print(f"   Farmer ID: {crop[2]}")
        print(f"   Crop Type: {crop[3]}")
        print(f"   Variety: {crop[4]}")
        print(f"   Area Planted: {crop[10]} acres")
        print(f"   Planting Date: {crop[11]}")
        print(f"   Expected Harvest: {crop[12]}")
        print(f"   Soil pH: {crop[6]}")
        print(f"   Nitrogen: {crop[8]} kg/ha")
        print(f"   Phosphorus: {crop[9]} kg/ha")
        print(f"   Potassium: {crop[7]} kg/ha")
        print(f"   Soil Type: {crop[5]}")
        print(f"   Growth Stage: {crop[13]}")
        print(f"   Health Status: {crop[14]}")
        print(f"   Is Organic: {crop[15]}")
        print(f"   QR Code URL: {crop[17]}")
        print(f"   Created At: {crop[19]}")
else:
    print("   ❌ No crops found")

# 4. Check SUPPLY_CHAIN_RECORDS table
print("\n4️⃣  SUPPLY CHAIN RECORDS TABLE (Details):")
print("-" * 70)
cursor.execute("SELECT * FROM supply_chain_records")
records = cursor.fetchall()

if records:
    for record in records:
        print(f"\n   Record ID: {record[0]}")
        print(f"   Crop ID: {record[1]}")
        print(f"   User ID: {record[2]}")
        print(f"   Stage: {record[3]}")
        print(f"   Location: {record[4]}")
        print(f"   Temperature: {record[5]}°C")
        print(f"   Humidity: {record[6]}%")
        print(f"   Handler Name: {record[7]}")
        print(f"   Handler Role: {record[8]}")
        print(f"   Notes: {record[9]}")
        print(f"   Quality Status: {record[10]}")
        print(f"   Created At: {record[12]}")
else:
    print("   ❌ No supply chain records found")

# 5. Check AUDIT_LOGS table
print("\n5️⃣  AUDIT LOGS TABLE:")
print("-" * 70)
cursor.execute("SELECT COUNT(*) FROM audit_logs")
count = cursor.fetchone()[0]
print(f"   Total Audit Logs: {count}")

# 6. Database Statistics
print("\n6️⃣  DATABASE STATISTICS:")
print("-" * 70)
cursor.execute("SELECT COUNT(*) FROM users WHERE role='farmer'")
farmers = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
admins = cursor.fetchone()[0]

print(f"   Total Users: {len(users)}")
print(f"   - Farmers: {farmers}")
print(f"   - Admins: {admins}")
print(f"   Total Crops: {len(crops)}")
print(f"   Total Supply Chain Records: {len(records)}")

# 7. Database File Info
print("\n7️⃣  DATABASE FILE INFO:")
print("-" * 70)
import os
db_file = 'instance/agrotrace.db'
if os.path.exists(db_file):
    size = os.path.getsize(db_file)
    print(f"   File: {db_file}")
    print(f"   Size: {size} bytes ({size/1024:.2f} KB)")
    print(f"   Status: ✅ EXISTS")
else:
    print(f"   Status: ❌ FILE NOT FOUND")

print("\n" + "="*70)
print("✅ DATABASE CHECK COMPLETE")
print("="*70 + "\n")

conn.close()
