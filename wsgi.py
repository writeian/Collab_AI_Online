#!/usr/bin/env python3
"""
WSGI entry point for production deployment.
This file is used by Gunicorn to serve the Flask application.
"""

import os
from app import create_app

# Create the Flask application
app = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == "__main__":
    app.run() 