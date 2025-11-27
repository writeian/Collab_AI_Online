#!/usr/bin/env python3
"""List all tables in Railway Postgres database."""

import psycopg2

DB_CONFIG = {
    'host': 'yamanote.proxy.rlwy.net',
    'port': 36405,
    'database': 'railway',
    'user': 'postgres',
    'password': 'fKCmPKBlRjNFlDKbvdOZXjQTXMlnYyJJ'
}

try:
    print("Connecting to Railway Postgres...")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    print(f"\n✅ Found {len(tables)} tables:\n")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Also check for room table with LIKE
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE '%room%'
        ORDER BY table_name;
    """)
    
    room_tables = cursor.fetchall()
    if room_tables:
        print(f"\n📁 Tables containing 'room':")
        for table in room_tables:
            print(f"  - {table[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")

