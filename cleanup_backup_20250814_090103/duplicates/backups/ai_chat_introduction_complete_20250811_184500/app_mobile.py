#!/usr/bin/env python3
"""
Mobile-friendly Flask app for testing on public WiFi
"""

from app import app

if __name__ == "__main__":
    print("📱 Starting mobile-friendly Flask app...")
    print("🌐 Access on your computer: http://127.0.0.1:8080")
    print("📱 Try on your phone: http://192.168.5.98:8080")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 50)
    
    # Run on port 8080 instead of 5000
    app.run(host='0.0.0.0', port=8080, debug=True) 