#!/usr/bin/env python3
"""
Debug script to see what the API endpoints are actually returning.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"
TEST_GOALS = "To teach the steps of crafting and delivering a professional presentation"

def debug_generate_draft_modes():
    """Debug the draft mode generation endpoint."""
    print("🔍 Debugging draft mode generation...")
    
    url = f"{BASE_URL}/room/generate-draft-modes"
    data = {
        "goals": TEST_GOALS
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Raw Response Text: {repr(response.text)}")
        print(f"Response Length: {len(response.text)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ JSON parsed successfully: {result}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Response content: {response.text}")
        else:
            print(f"❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    debug_generate_draft_modes() 