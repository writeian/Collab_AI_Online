#!/usr/bin/env python3
"""
wsgi.py
Purpose: WSGI entry point for AI Collab Online
Status: [ACTIVE]
Created: 2025-01-27
Author: writeian

WSGI entry point for production deployment
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the application
from main import app

if __name__ == "__main__":
    app.run()
