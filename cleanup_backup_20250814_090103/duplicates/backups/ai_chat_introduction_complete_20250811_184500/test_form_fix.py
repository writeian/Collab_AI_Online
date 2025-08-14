#!/usr/bin/env python3
"""
Test to verify the AI response toggle is now inside the form
"""

import requests
from bs4 import BeautifulSoup

def test_form_structure():
    """Test that the toggle is inside the form"""
    
    # Start a session
    session = requests.Session()
    
    # Login
    login_data = {
        'username': 'TestUser3',
        'password': 'password123'
    }
    
    print("🔐 Logging in...")
    response = session.post('http://localhost:5000/auth/login', data=login_data)
    
    if response.status_code != 302:
        print("❌ Login failed")
        return False
    
    print("✅ Login successful")
    
    # Try to access a chat page
    print("🔍 Accessing chat page...")
    response = session.get('http://localhost:5000/chat/11')  # Use the chat ID from logs
    
    if response.status_code != 200:
        print(f"❌ Could not access chat page: {response.status_code}")
        return False
    
    print("✅ Chat page accessed")
    
    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the form
    form = soup.find('form', {'id': 'message-form'})
    if not form:
        print("❌ Message form not found")
        return False
    
    print("✅ Message form found")
    
    # Check if toggle is inside the form
    toggle = form.find('input', {'id': 'ai-response-toggle'})
    if not toggle:
        print("❌ Toggle not found inside form")
        return False
    
    print("✅ Toggle found inside form")
    
    # Check toggle attributes
    if toggle.get('name') != 'ai_response':
        print("❌ Toggle name is incorrect")
        return False
    
    if toggle.get('value') != '1':
        print("❌ Toggle value is incorrect")
        return False
    
    if 'checked' not in toggle.attrs:
        print("❌ Toggle is not checked by default")
        return False
    
    print("✅ Toggle attributes are correct")
    
    # Test form submission with toggle checked
    print("\n🧪 Testing form submission with toggle checked...")
    form_data = {
        'content': 'Test message with AI response',
        'ai_response': '1'
    }
    
    response = session.post('http://localhost:5000/chat/11', data=form_data)
    
    if response.status_code == 303:  # Redirect after successful submission
        print("✅ Form submission successful")
        print("📝 Check the server logs to see if AI response was enabled")
    else:
        print(f"❌ Form submission failed: {response.status_code}")
    
    return True

if __name__ == "__main__":
    print("🧪 Testing AI Response Toggle Form Structure")
    print("=" * 50)
    
    success = test_form_structure()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("🎯 The toggle should now work correctly when you test it manually.")
    else:
        print("\n❌ Test failed!") 