#!/usr/bin/env python3
"""
Test to verify form data is being sent correctly
"""

import requests

def test_form_data():
    """Test form data submission"""
    
    print("🧪 Testing Form Data Submission")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Check what happens when we submit form data
    print("\n1. Testing form data submission...")
    
    # Test with AI response enabled
    print("Testing with AI response enabled (ai_response=1)...")
    try:
        response = requests.post(f"{base_url}/chat/1", data={
            "content": "Test message with AI response",
            "ai_response": "1"
        }, allow_redirects=True)
        
        print(f"Response status: {response.status_code}")
        print(f"Response URL: {response.url}")
        
        if "login" in response.url.lower():
            print("ℹ️ Redirected to login (expected)")
        elif response.status_code == 200:
            print("✅ Form submission successful")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing form submission: {e}")
    
    # Test 2: Check the actual form HTML
    print("\n2. Checking form HTML structure...")
    try:
        response = requests.get(f"{base_url}/chat/1", allow_redirects=True)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for toggle elements
            has_toggle = 'ai-response-toggle' in content
            has_ai_response_name = 'name="ai_response"' in content
            has_checked = 'checked' in content
            
            print(f"Form contains toggle ID: {'✅ Yes' if has_toggle else '❌ No'}")
            print(f"Form contains ai_response name: {'✅ Yes' if has_ai_response_name else '❌ No'}")
            print(f"Form contains checked attribute: {'✅ Yes' if has_checked else '❌ No'}")
            
            if has_toggle and has_ai_response_name and has_checked:
                print("✅ Form structure looks correct")
            else:
                print("❌ Form structure has issues")
                
        else:
            print(f"⚠️ Could not access chat page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking form HTML: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Form Data Test Summary:")
    print("- Form submission tested")
    print("- Form HTML structure checked")
    print("\nIf the form structure is correct but AI responses still don't work:")
    print("1. Check browser developer tools for JavaScript errors")
    print("2. Check Flask app logs for backend errors")
    print("3. Verify the user is logged in and has access to the chat")

if __name__ == "__main__":
    test_form_data() 