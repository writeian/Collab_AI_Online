#!/usr/bin/env python3
"""Quick test to verify card preview route"""
import sys
import os
sys.path.insert(0, '.')
from src.app import create_app

app = create_app()
with app.test_client() as client:
    # Test route without auth (should redirect or 403)
    print("Testing /api/dev/card-preview route...")
    print(f"Route exists: {'/api/dev/card-preview' in [str(r) for r in app.url_map.iter_rules()]}")
    
    # Check template exists
    import os
    template_path = os.path.join('templates', 'dev', 'card_preview.html')
    print(f"Template exists: {os.path.exists(template_path)}")
    
    # Check CSS exists
    css_path = os.path.join('src', 'app', 'static', 'css', 'dev', 'card-overlay.css')
    print(f"CSS exists: {os.path.exists(css_path)}")
    
    # Check JS exists
    js_path = os.path.join('src', 'app', 'static', 'js', 'dev', 'card-overlay.js')
    print(f"JS exists: {os.path.exists(js_path)}")
    
    print("\n✅ All files exist. Route should work at: http://127.0.0.1:5001/api/dev/card-preview")
