#!/usr/bin/env python3
"""
WSGI entry point for production deployment.
This file is used by Gunicorn to serve the Flask application.
"""

import os
import sys

print("Starting Flask application...")
print(f"FLASK_ENV: {os.getenv('FLASK_ENV', 'not set')}")
print(f"SECRET_KEY: {'set' if os.getenv('SECRET_KEY') else 'not set'}")
print(f"DATABASE_URL: {'set' if os.getenv('DATABASE_URL') else 'not set'}")
print(f"PORT: {os.getenv('PORT', 'not set')}")

try:
    from app import create_app
    
    print("Creating Flask application...")
    # Create the Flask application
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    print("Flask app created successfully!")
    
    # Test basic app functionality
    print("Testing app routes...")
    with app.test_client() as client:
        response = client.get('/health')
        print(f"Health check response: {response.status_code}")
    
except Exception as e:
    print(f"Error creating Flask app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    app.run() 