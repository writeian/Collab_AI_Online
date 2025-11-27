#!/usr/bin/env python3
"""Check the schema of the room table."""

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
    
    # Get columns for room table
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'room'
        ORDER BY ordinal_position;
    """)
    
    columns = cursor.fetchall()
    print(f"\n✅ Room table has {len(columns)} columns:\n")
    for col in columns:
        col_name, data_type, max_length = col
        length_info = f" ({max_length})" if max_length else ""
        print(f"  - {col_name}: {data_type}{length_info}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")

