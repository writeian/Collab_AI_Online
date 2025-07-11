#!/usr/bin/env python3
"""Check database and create test user if needed."""

from app import create_app
from models import db, User

def check_database():
    app = create_app()
    
    with app.app_context():
        # Check existing users
        users = User.query.all()
        print(f"Found {len(users)} users in database:")
        
        for user in users:
            print(f"  - {user.username} ({user.email}) - Created: {user.created_at}")
        
        # Create test user if none exist
        if not users:
            print("\nNo users found. Creating test user...")
            
            test_user = User(
                username="testuser",
                email="test@example.com",
                display_name="Test User"
            )
            test_user.set_password("password123")
            
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Created test user:")
            print("  Username: testuser")
            print("  Password: password123")
            print("  Email: test@example.com")
        else:
            print("\n✅ Database has existing users. You can use any of these to login.")

if __name__ == "__main__":
    check_database() 