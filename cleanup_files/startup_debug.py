#!/usr/bin/env python3
"""
Debug script to test app startup and identify issues.
"""

import os
import sys

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    try:
        from flask import Flask
        print("✓ Flask imported")
        
        from models import db
        print("✓ SQLAlchemy imported")
        
        from config import config
        print("✓ Config imported")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    try:
        from config import config
        from app import create_app
        
        # Test with production config
        app = create_app('production')
        print("✓ Production config loaded")
        
        # Test environment variables
        print(f"FLASK_ENV: {os.getenv('FLASK_ENV', 'not set')}")
        print(f"SECRET_KEY: {'set' if os.getenv('SECRET_KEY') else 'not set'}")
        print(f"DATABASE_URL: {'set' if os.getenv('DATABASE_URL') else 'not set'}")
        
        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False

def test_database():
    """Test database connection."""
    print("\nTesting database...")
    try:
        from app import create_app
        from models import db
        
        app = create_app('production')
        with app.app_context():
            # Test database connection
            result = db.engine.execute('SELECT 1')
            print("✓ Database connection successful")
            return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def main():
    """Run all tests."""
    print("=== Railway Startup Debug ===\n")
    
    tests = [
        test_imports,
        test_config,
        test_database
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Results: {passed}/{len(tests)} tests passed ===")
    
    if passed == len(tests):
        print("✓ All tests passed! App should start successfully.")
    else:
        print("✗ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main() 