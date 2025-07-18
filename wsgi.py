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

try:
    from app import create_app
    
    # Create the Flask application
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    print("Flask app created successfully!")
    
except Exception as e:
    print(f"Error creating Flask app: {e}")
    sys.exit(1)

if __name__ == "__main__":
    app.run() 