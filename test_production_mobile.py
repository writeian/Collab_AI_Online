#!/usr/bin/env python3
"""
Production Mobile Testing Script
Tests mobile functionality that might break in production environments
"""

import requests
import json
import sys
from urllib.parse import urljoin

def test_production_mobile_features(base_url):
    """Test mobile features that might fail in production"""
    
    print("🔍 Testing Mobile Features for Production Deployment")
    print("=" * 60)
    
    tests = [
        {
            "name": "CSS Loading",
            "url": "/static/css/components.css",
            "expected": "mobile navigation styles",
            "check": lambda r: "mobile-menu-button" in r.text
        },
        {
            "name": "JavaScript Loading", 
            "url": "/static/landing.js",
            "expected": "JavaScript files load",
            "check": lambda r: r.status_code == 200
        },
        {
            "name": "Mobile Menu HTML",
            "url": "/",
            "expected": "Mobile menu button exists",
            "check": lambda r: "mobile-menu-button" in r.text or "mobile-menu-overlay" in r.text
        },
        {
            "name": "Navigation Structure",
            "url": "/room/",
            "expected": "Home navigation exists",
            "check": lambda r: "room.index" in r.text or "Home" in r.text
        },
        {
            "name": "Responsive CSS",
            "url": "/static/css/components.css",
            "expected": "Mobile media queries present",
            "check": lambda r: "@media (max-width: 768px)" in r.text
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            url = urljoin(base_url, test["url"])
            response = requests.get(url, timeout=10)
            
            if test["check"](response):
                print(f"✅ {test['name']}: {test['expected']}")
                passed += 1
            else:
                print(f"❌ {test['name']}: Failed - {test['expected']}")
                failed += 1
                
        except Exception as e:
            print(f"❌ {test['name']}: Error - {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("\n🚨 CRITICAL: Mobile features may not work in production!")
        print("   - Check static asset serving")
        print("   - Verify CSS/JS compression settings")
        print("   - Test mobile menu functionality")
        return False
    else:
        print("\n✅ All mobile features should work in production")
        return True

def test_railway_specific_issues():
    """Test Railway-specific potential issues"""
    
    print("\n🔧 Railway-Specific Tests")
    print("=" * 40)
    
    # Test environment variable handling
    import os
    env_vars = [
        "FLASK_ENV",
        "DATABASE_URL", 
        "SECRET_KEY"
    ]
    
    missing_vars = []
    for var in env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   These are required for Railway deployment")
    else:
        print("✅ All required environment variables are set")
    
    # Test database connectivity
    try:
        from app import create_app
        from models import db
        
        app = create_app()
        with app.app_context():
            # Use the newer SQLAlchemy syntax
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            print("✅ Database connectivity works")
    except Exception as e:
        print(f"❌ Database connectivity failed: {str(e)}")

def main():
    """Main test function"""
    
    if len(sys.argv) < 2:
        print("Usage: python test_production_mobile.py <base_url>")
        print("Example: python test_production_mobile.py http://localhost:5000")
        sys.exit(1)
    
    base_url = sys.argv[1]
    
    # Test mobile features
    mobile_ok = test_production_mobile_features(base_url)
    
    # Test Railway-specific issues
    test_railway_specific_issues()
    
    if not mobile_ok:
        print("\n🚨 RECOMMENDATIONS:")
        print("1. Test mobile menu functionality manually")
        print("2. Verify CSS loads correctly in production")
        print("3. Check JavaScript execution in mobile browsers")
        print("4. Test touch interactions on actual mobile devices")
        sys.exit(1)
    else:
        print("\n✅ Mobile features should work correctly in production")

if __name__ == "__main__":
    main() 