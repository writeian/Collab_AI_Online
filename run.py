#!/usr/bin/env python3
"""
run.py
Purpose: Entry point for AI Collab Online (Phase 3)
Status: [ACTIVE]
Created: 2025-01-27
Author: writeian

Entry point to run the application with the new Phase 3 structure
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded environment variables from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed")

# Import and run the application
from main import app

if __name__ == '__main__':
    print("🚀 Starting AI Collab Online (Phase 3)...")
    print("📁 Using new professional src/ directory structure")
    print("🌐 Application will be available at: http://localhost:5000")
    print("🔧 Health check available at: http://localhost:5000/health")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 