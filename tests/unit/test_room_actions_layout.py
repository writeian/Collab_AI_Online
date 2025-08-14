#!/usr/bin/env python3
"""
Test script to verify room actions layout changes.
Checks that settings and invite members icons are properly positioned within Room Info.
"""

import requests
from bs4 import BeautifulSoup
import re

def test_room_actions_layout():
    """Test that room actions are properly positioned within Room Info section."""
    
    # Start a session to maintain login state
    session = requests.Session()
    
    try:
        # First, try to access the login page to get any CSRF tokens
        login_response = session.get('http://127.0.0.1:5000/auth/login')
        login_response.raise_for_status()
        
        # Login (you may need to adjust credentials)
        login_data = {
            'email': 'test@example.com',  # Adjust as needed
            'password': 'password123',     # Adjust as needed
            'csrf_token': 'test'  # We'll handle this properly if needed
        }
        
        login_response = session.post('http://127.0.0.1:5000/auth/login', data=login_data, allow_redirects=True)
        
        # Try to access a room page
        room_response = session.get('http://127.0.0.1:5000/room/4')
        room_response.raise_for_status()
        
        soup = BeautifulSoup(room_response.content, 'html.parser')
        
        print("🔍 Testing room actions layout changes...")
        
        # Check for Room Info section
        room_info_section = soup.find('div', {'id': 'room-info-content'})
        if not room_info_section:
            print("❌ Room Info section not found")
            return False
        
        print("✅ Room Info section found")
        
        # Check for room actions dropdown within Room Info
        room_actions_dropdown = room_info_section.find('div', class_='room-actions-dropdown')
        if not room_actions_dropdown:
            print("❌ Room actions dropdown not found within Room Info")
            return False
        
        print("✅ Room actions dropdown found within Room Info")
        
        # Check for invite members button
        invite_button = room_actions_dropdown.find('a', href=re.compile(r'invite_member'))
        if not invite_button:
            print("❌ Invite members button not found")
            return False
        
        print("✅ Invite members button found")
        
        # Check for settings button
        settings_button = room_actions_dropdown.find('button', onclick='toggleRoomActions()')
        if not settings_button:
            print("❌ Settings button not found")
            return False
        
        print("✅ Settings button found")
        
        # Check that both buttons are in a flex container
        flex_container = room_actions_dropdown.find('div', class_='flex')
        if not flex_container:
            print("❌ Flex container for buttons not found")
            return False
        
        print("✅ Buttons are in flex container")
        
        # Check that invite members is removed from dropdown menu
        dropdown_menu = room_actions_dropdown.find('div', {'id': 'room-actions-menu'})
        if dropdown_menu:
            invite_dropdown_item = dropdown_menu.find('a', href=re.compile(r'invite_member'))
            if invite_dropdown_item:
                print("❌ Invite members still in dropdown menu")
                return False
            else:
                print("✅ Invite members removed from dropdown menu")
        
        print("\n🎉 All room actions layout tests passed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the Flask app is running.")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    test_room_actions_layout() 