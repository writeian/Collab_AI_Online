#!/usr/bin/env python3
"""
Manual database migration script for Railway
Run this script to create achievement tables
"""

import os
import sys
from flask import Flask
from models import db, User, UserModeUsage, Achievement

# Set up environment
os.environ['FLASK_ENV'] = 'production'

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

def migrate_database():
    """Migrate database to add achievement tables"""
    try:
        with app.app_context():
            print("Starting database migration...")
            
            # Create all tables
            db.create_all()
            print("✓ All tables created")
            
            # Check if achievement tables exist
            with db.engine.connect() as conn:
                result = conn.execute(db.text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name IN ('user_mode_usage', 'achievement')
                """))
                existing_tables = [row[0] for row in result.fetchall()]
                
                print(f"Existing tables: {existing_tables}")
                
                missing_tables = []
                if 'user_mode_usage' not in existing_tables:
                    missing_tables.append('user_mode_usage')
                if 'achievement' not in existing_tables:
                    missing_tables.append('achievement')
                
                if missing_tables:
                    print(f"Creating missing tables: {missing_tables}")
                    if 'user_mode_usage' in missing_tables:
                        UserModeUsage.__table__.create(db.engine, checkfirst=True)
                        print("✓ user_mode_usage table created")
                    if 'achievement' in missing_tables:
                        Achievement.__table__.create(db.engine, checkfirst=True)
                        print("✓ achievement table created")
                else:
                    print("✓ All achievement tables already exist")
                
                # Check achievement count
                result = conn.execute(db.text("SELECT COUNT(*) FROM achievement"))
                achievement_count = result.fetchone()[0]
                print(f"Total achievements in database: {achievement_count}")
                
                # Check usage count
                result = conn.execute(db.text("SELECT COUNT(*) FROM user_mode_usage"))
                usage_count = result.fetchone()[0]
                print(f"Total mode usage records: {usage_count}")
                
            print("✅ Migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("Manual Database Migration Script")
    print("=" * 40)
    
    # Check if DATABASE_URL is set
    if not os.getenv('DATABASE_URL'):
        print("❌ DATABASE_URL environment variable not set")
        sys.exit(1)
    
    print(f"Database URL: {os.getenv('DATABASE_URL').replace(os.getenv('DATABASE_URL').split('@')[1], '***') if '@' in os.getenv('DATABASE_URL') else os.getenv('DATABASE_URL')}")
    
    success = migrate_database()
    if success:
        print("\n🎉 Migration completed! Achievements should now work.")
    else:
        print("\n💥 Migration failed. Check the error messages above.")
        sys.exit(1) 