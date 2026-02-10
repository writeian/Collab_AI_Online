#!/usr/bin/env python3
"""
Create a test user account for local development

Usage:
    python scripts/create_test_user.py
    
Or with custom credentials:
    python scripts/create_test_user.py testuser test@example.com TestPassword123
"""

import sys
import os

# Ensure we can import from src by adding project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import create_app, db
from src.models import User


def create_test_user(username="testuser", email="test@example.com", password="testpass123", display_name="Test User"):
    """Create a test user account."""
    
    app = create_app()
    
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print("="*60)
            print(f"⚠️  User already exists!")
            print(f"Username: {existing_user.username}")
            print(f"Email: {existing_user.email}")
            print(f"Display Name: {existing_user.display_name}")
            print("="*60)
            print("\nYou can use these credentials to log in:")
            print(f"  • Username: {existing_user.username}")
            print(f"  • Email: {existing_user.email}")
            print(f"\nTo reset password, run:")
            print(f"  python scripts/reset_user_password.py {existing_user.email} NewPassword123")
            return False
        
        # Create new user
        user = User()
        user.username = username
        user.email = email
        user.display_name = display_name
        user.set_password(password)
        user.is_active = True
        
        db.session.add(user)
        db.session.commit()
        
        print("="*60)
        print(f"✅ Test user created successfully!")
        print("="*60)
        print(f"\nLogin Credentials:")
        print(f"  • Username: {username}")
        print(f"  • Email: {email}")
        print(f"  • Password: {password}")
        print(f"  • Display Name: {display_name}")
        print("="*60)
        print(f"\n📝 Next Steps:")
        print(f"1. Start the server: flask run --port 5001")
        print(f"2. Navigate to: http://127.0.0.1:5001/auth/login")
        print(f"3. Log in with the credentials above")
        print(f"4. Test Card View: http://127.0.0.1:5001/api/dev/card-preview")
        print("="*60)
        
        return True


if __name__ == "__main__":
    if len(sys.argv) >= 4:
        username = sys.argv[1]
        email = sys.argv[2]
        password = sys.argv[3]
        display_name = sys.argv[4] if len(sys.argv) >= 5 else username.title()
        create_test_user(username, email, password, display_name)
    else:
        # Use defaults
        print("Creating test user with default credentials...")
        print("(To customize, run: python scripts/create_test_user.py <username> <email> <password> [display_name])\n")
        create_test_user()


