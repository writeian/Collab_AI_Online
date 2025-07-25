#!/usr/bin/env python3
"""
Test script for Enhanced User Profiles
"""

from app import create_app
from models import db, User
from datetime import datetime

def test_profile_functionality():
    """Test the profile functionality"""
    app = create_app()
    
    with app.app_context():
        print("✅ App created successfully")
        
        # Test database connection
        try:
            db.create_all()
            print("✅ Database tables created")
        except Exception as e:
            print(f"❌ Database error: {e}")
            return
        
        # Test user creation with all fields
        try:
            user = User()
            user.username = "testuser"
            user.email = "test@example.com"
            user.full_name = "Test User"
            user.display_name = "TestUser"
            user.password_hash = "test_hash"
            user.institution = "Test University"
            user.department = "Computer Science"
            user.research_area = "AI/ML"
            user.role = "Researcher"
            user.primary_use_case = "Research"
            user.team_size = "Individual"
            user.heard_from = "Search Engine"
            user.receive_updates = True
            user.contact_for_research = False
            user.created_at = datetime.utcnow()
            
            db.session.add(user)
            db.session.commit()
            print("✅ Test user created with all profile fields")
            
            # Test user retrieval
            retrieved_user = User.query.filter_by(username="testuser").first()
            if retrieved_user:
                print(f"✅ User retrieved: {retrieved_user.display_name}")
                print(f"✅ Institution: {retrieved_user.institution}")
                print(f"✅ Role: {retrieved_user.role}")
                print(f"✅ Receive updates: {retrieved_user.receive_updates}")
            else:
                print("❌ User not found")
                
        except Exception as e:
            print(f"❌ User creation error: {e}")
        
        print("\n🎉 Profile functionality test completed!")

if __name__ == "__main__":
    test_profile_functionality() 