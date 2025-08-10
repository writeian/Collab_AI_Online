#!/usr/bin/env python3
"""
Test script for the new mode refinement API endpoints.
This tests the draft mode generation and refinement functionality.
"""

import requests
import json

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_GOALS = "To teach the steps of crafting and delivering a professional presentation"

def test_generate_draft_modes():
    """Test the draft mode generation endpoint."""
    print("🧪 Testing draft mode generation...")
    
    url = f"{BASE_URL}/room/generate-draft-modes"
    data = {
        "goals": TEST_GOALS
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
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
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_refine_modes(conversation_id, current_modes):
    """Test the mode refinement endpoint."""
    print("\n🧪 Testing mode refinement...")
    
    url = f"{BASE_URL}/room/refine-modes"
    data = {
        "conversation_id": conversation_id,
        "message": "Add a mode for practicing delivery techniques",
        "current_modes": current_modes
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Modes refined successfully!")
            print(f"AI Response: {result.get('ai_response')}")
            print(f"Refined {len(result.get('modes', []))} modes")
            
            return result
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    """Run the API tests."""
    print("🚀 Testing Mode Refinement API Endpoints")
    print("=" * 50)
    
    # Test 1: Generate draft modes
    draft_result = test_generate_draft_modes()
    
    if draft_result and draft_result.get('modes'):
        # Test 2: Refine modes
        conversation_id = draft_result.get('conversation_id')
        current_modes = draft_result.get('modes')
        
        refine_result = test_refine_modes(conversation_id, current_modes)
        
        if refine_result:
            print("\n✅ All tests passed! API endpoints are working correctly.")
        else:
            print("\n❌ Mode refinement test failed.")
    else:
        print("\n❌ Draft mode generation test failed.")

if __name__ == "__main__":
    main() 