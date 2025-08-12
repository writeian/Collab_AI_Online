#!/usr/bin/env python3
"""
Test script for the mode refinement API endpoints with authentication.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"
TEST_GOALS = "To teach the steps of crafting and delivering a professional presentation"

def login_and_get_session():
    """Login and get a session for testing."""
    print("🔐 Logging in...")
    
    # First, try to login
    login_data = {
        "username": "TestUser3",  # Using one of the test users we know exists
        "password": "password123"  # Common test password
    }
    
    session = requests.Session()
    
    try:
        # Get the login page first to get any CSRF tokens if needed
        login_page = session.get(f"{BASE_URL}/auth/login")
        
        # Submit login form
        login_response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
        
        if login_response.status_code == 302:  # Redirect after successful login
            print("✅ Login successful!")
            return session
        else:
            print(f"❌ Login failed. Status: {login_response.status_code}")
            print(f"Response: {login_response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Login exception: {e}")
        return None

def test_generate_draft_modes_with_auth(session):
    """Test the draft mode generation endpoint with authentication."""
    print("\n🧪 Testing draft mode generation with auth...")
    
    url = f"{BASE_URL}/room/generate-draft-modes"
    data = {
        "goals": TEST_GOALS
    }
    
    try:
        response = session.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ Draft modes generated successfully!")
                print(f"Generated {len(result.get('modes', []))} modes")
                print(f"Conversation ID: {result.get('conversation_id')}")
                
                # Display the first mode as example
                if result.get('modes'):
                    first_mode = result['modes'][0]
                    print(f"\nExample Mode:")
                    print(f"  Label: {first_mode['label']}")
                    print(f"  Prompt: {first_mode['prompt'][:100]}...")
                
                return result
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Response content: {response.text[:200]}...")
                return None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_refine_modes_with_auth(session, conversation_id, current_modes):
    """Test the mode refinement endpoint with authentication."""
    print("\n🧪 Testing mode refinement with auth...")
    
    url = f"{BASE_URL}/room/refine-modes"
    data = {
        "conversation_id": conversation_id,
        "message": "Add a mode for practicing delivery techniques",
        "current_modes": current_modes
    }
    
    try:
        response = session.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ Modes refined successfully!")
                print(f"AI Response: {result.get('ai_response')}")
                print(f"Refined {len(result.get('modes', []))} modes")
                
                return result
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Response content: {response.text[:200]}...")
                return None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    """Run the authenticated API tests."""
    print("🚀 Testing Mode Refinement API Endpoints (with Authentication)")
    print("=" * 60)
    
    # Step 1: Login
    session = login_and_get_session()
    
    if not session:
        print("❌ Cannot proceed without authentication")
        return
    
    # Step 2: Test draft mode generation
    draft_result = test_generate_draft_modes_with_auth(session)
    
    if draft_result and draft_result.get('modes'):
        # Step 3: Test mode refinement
        conversation_id = draft_result.get('conversation_id')
        current_modes = draft_result.get('modes')
        
        refine_result = test_refine_modes_with_auth(session, conversation_id, current_modes)
        
        if refine_result:
            print("\n✅ All tests passed! API endpoints are working correctly.")
        else:
            print("\n❌ Mode refinement test failed.")
    else:
        print("\n❌ Draft mode generation test failed.")

if __name__ == "__main__":
    main() 