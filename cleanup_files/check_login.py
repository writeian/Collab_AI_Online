#!/usr/bin/env python3
"""Check login credentials or create a new test user."""

from app import create_app
from models import db, User
from werkzeug.security import check_password_hash

def check_existing_user():
    """Check the existing user's password."""
    app = create_app()
    
    with app.app_context():
        user = User.query.filter_by(username="TestUser").first()
        if user:
            print(f"✅ Found user: {user.username}")
            print(f"Email: {user.email}")
            print(f"Display name: {user.display_name}")
            
            # Test common passwords
            test_passwords = [
                "password123",
                "password",
                "123456",
                "test",
                "admin",
                "user",
                "TestUser",
                "testuser"
            ]
            
            print("\n🔍 Testing common passwords:")
            for password in test_passwords:
                if user.check_password(password):
                    print(f"✅ Password found: '{password}'")
                    return password
            
            print("❌ None of the common passwords worked.")
            return None
        else:
            print("❌ TestUser not found")
            return None

def create_new_test_user():
    """Create a new test user with known credentials."""
    app = create_app()
    
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username="testuser").first()
        if existing_user:
            print("✅ User 'testuser' already exists")
            return
        
        # Create new user
        new_user = User(
            username="testuser",
            email="test@example.com",
            display_name="Test User"
        )
        new_user.set_password("password123")
        
        db.session.add(new_user)
        db.session.commit()
        
        print("✅ Created new test user:")
        print("  Username: testuser")
        print("  Password: password123")
        print("  Email: test@example.com")

def main():
    """Main function."""
    print("🔍 Login Credentials Check")
    print("=" * 30)
    
    # Try to find existing password
    password = check_existing_user()
    
    if password:
        print(f"\n🎯 Use these credentials:")
        print(f"Username: TestUser")
        print(f"Password: {password}")
    else:
        print("\n📝 Creating new test user...")
        create_new_test_user()
        print(f"\n🎯 Use these credentials:")
        print(f"Username: testuser")
        print(f"Password: password123")

if __name__ == "__main__":
    main() 