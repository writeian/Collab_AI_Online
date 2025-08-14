#!/usr/bin/env python3
"""
Test script to verify room actions layout changes in the HTML template.
Checks that settings and invite members icons are properly positioned within Room Info.
"""

import re

def test_room_actions_html():
    """Test that the HTML template has the correct room actions layout."""
    
    try:
        with open('templates/room/view.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print("🔍 Testing room actions layout in HTML template...")
        
        # Check for Room Info section
        if 'id="room-info-content"' not in html_content:
            print("❌ Room Info content section not found")
            return False
        
        print("✅ Room Info content section found")
        
        # Check for room actions dropdown within Room Info
        if 'room-actions-dropdown' not in html_content:
            print("❌ Room actions dropdown not found")
            return False
        
        print("✅ Room actions dropdown found")
        
        # Check for invite members button
        if 'href="{{ url_for(\'room.invite_member\', room_id=room.id) }}"' not in html_content:
            print("❌ Invite members button not found")
            return False
        
        print("✅ Invite members button found")
        
        # Check for settings button
        if 'onclick="toggleRoomActions()"' not in html_content:
            print("❌ Settings button not found")
            return False
        
        print("✅ Settings button found")
        
        # Check that both buttons are in a flex container
        if 'flex items-center gap-2' not in html_content:
            print("❌ Flex container for buttons not found")
            return False
        
        print("✅ Buttons are in flex container")
        
        # Check for proper button structure
        button_structure_pattern = r'<div class="flex items-center gap-2">.*?<a href.*?invite_member.*?user-plus.*?</a>.*?<button.*?settings.*?</button>.*?</div>'
        if not re.search(button_structure_pattern, html_content, re.DOTALL):
            print("❌ Button structure not found in correct order")
            return False
        
        print("✅ Button structure is correct")
        
        print("\n🎉 All room actions HTML template tests passed!")
        return True
        
    except FileNotFoundError:
        print("❌ templates/room/view.html file not found")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    test_room_actions_html() 