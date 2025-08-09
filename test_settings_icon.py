#!/usr/bin/env python3
"""
Test script to verify the simple settings icon implementation.
"""

import requests
from bs4 import BeautifulSoup

def test_settings_icon():
    """Test the simple settings icon implementation."""
    print("⚙️ Testing Simple Settings Icon Implementation")
    print("=" * 60)
    
    # Create a session to maintain login state
    session = requests.Session()
    
    # Login first
    login_url = "http://127.0.0.1:5000/auth/login"
    login_data = {
        'username': 'TestUser3',
        'password': 'password123'
    }
    
    try:
        # Submit login form
        login_response = session.post(login_url, data=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        # Now test the room page
        room_url = "http://127.0.0.1:5000/room/4"
        room_response = session.get(room_url)
        
        if room_response.status_code != 200:
            print(f"❌ Failed to load room page: {room_response.status_code}")
            return False
            
        soup = BeautifulSoup(room_response.text, 'html.parser')
        
        # Test 1: Check for simple settings icon
        print("\n1. Testing Simple Settings Icon:")
        
        # Check for settings icon button
        settings_btn = soup.find('button', class_='settings-icon-btn')
        if settings_btn:
            print("   ✅ Settings icon button found")
        else:
            print("   ❌ Settings icon button missing")
            
        # Check for settings icon
        settings_icon = soup.find('i', attrs={'data-lucide': 'settings'})
        if settings_icon:
            print("   ✅ Settings icon found")
        else:
            print("   ❌ Settings icon missing")
            
        # Test 2: Check for button styling
        print("\n2. Testing Button Styling:")
        
        # Check for title attribute
        if settings_btn and settings_btn.get('title') == 'Room Settings':
            print("   ✅ Tooltip title found")
        else:
            print("   ❌ Tooltip title missing")
            
        # Test 3: Check for dropdown functionality
        print("\n3. Testing Dropdown Functionality:")
        
        # Check for dropdown menu
        dropdown_menu = soup.find('div', id='room-actions-menu')
        if dropdown_menu:
            print("   ✅ Dropdown menu found")
        else:
            print("   ❌ Dropdown menu missing")
            
        # Test 4: Check for CSS version
        print("\n4. Testing CSS Version:")
        css_links = soup.find_all('link', href=lambda h: h and 'components.css?v=2.5' in h)
        if css_links:
            print("   ✅ Updated CSS version (2.5) found")
        else:
            print("   ❌ Updated CSS version not found")
            
        # Test 5: Check for visual improvements
        print("\n5. Testing Visual Improvements:")
        
        # Check that old button classes are not present
        old_btn = soup.find('button', class_='btn btn-outline dropdown-toggle')
        if not old_btn:
            print("   ✅ Old button styling removed")
        else:
            print("   ❌ Old button styling still present")
            
        # Test 6: Show button details
        print("\n6. Button Details:")
        if settings_btn:
            classes = settings_btn.get('class', [])
            print(f"   Button classes: {classes}")
            print(f"   Button onclick: {settings_btn.get('onclick', 'None')}")
            print(f"   Button title: {settings_btn.get('title', 'None')}")
            
            # Check icon size
            icon = settings_btn.find('i')
            if icon:
                icon_classes = icon.get('class', [])
                print(f"   Icon classes: {icon_classes}")
        
        print("\n" + "=" * 60)
        print("🎉 Simple Settings Icon Test Complete!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error testing settings icon: {e}")
        return False

if __name__ == "__main__":
    test_settings_icon() 