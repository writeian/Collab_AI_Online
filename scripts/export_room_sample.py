#!/usr/bin/env python3
"""Export a sample of rooms from Railway Postgres for description analysis."""

import psycopg2
import csv
import sys
from pathlib import Path

# Railway Postgres connection
DB_CONFIG = {
    'host': 'yamanote.proxy.rlwy.net',
    'port': 36405,
    'database': 'railway',
    'user': 'postgres',
    'password': 'fKCmPKBlRjNFlDKbvdOZXjQTXMlnYyJJ'
}

def export_room_sample(output_file='room_sample.csv', limit=20):
    """Export a sample of rooms to CSV."""
    try:
        # Connect to database
        print(f"Connecting to Railway Postgres...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Query room data
        query = """
            SELECT 
                id,
                name,
                goals,
                description,
                short_description,
                group_size,
                owner_id,
                created_at,
                is_active
            FROM room
            ORDER BY created_at DESC
            LIMIT %s
        """
        
        print(f"Fetching {limit} most recent rooms...")
        cursor.execute(query, (limit,))
        
        # Fetch all rows
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        # Write to CSV
        output_path = Path(__file__).parent.parent / output_file
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
        
        print(f"✅ Exported {len(rows)} rooms to: {output_path}")
        print(f"\nColumns: {', '.join(columns)}")
        
        # Show sample
        print(f"\n📊 Sample (first 3 rows):")
        for i, row in enumerate(rows[:3], 1):
            print(f"\n--- Room {i} ---")
            for col, val in zip(columns, row):
                if col in ['goals', 'description', 'short_description']:
                    val_preview = str(val)[:100] + '...' if val and len(str(val)) > 100 else val
                    print(f"  {col}: {val_preview}")
                elif col != 'id':
                    print(f"  {col}: {val}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return output_path
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Export room sample from Railway Postgres')
    parser.add_argument('-o', '--output', default='room_sample.csv', help='Output CSV file')
    parser.add_argument('-n', '--limit', type=int, default=20, help='Number of rooms to export')
    
    args = parser.parse_args()
    export_room_sample(args.output, args.limit)

