#!/usr/bin/env python3
"""
Test script to verify that action icons are positioned within the white card.
Checks that the icons are in the upper-right corner of the Room Info section.
"""

import re

def test_icons_in_card():
    """Test that the action icons are properly positioned within the white card."""
    
    try:
        with open('templates/room/view.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print("🔍 Testing icon positioning within white card...")
        
        # Check for Room Info section
        if 'id="room-info-content"' not in html_content:
            print("❌ Room Info content section not found")
            return False
        
        print("✅ Room Info content section found")
        
        # Check for absolute positioning
        if 'absolute top-4 right-4' not in html_content:
            print("❌ Icons not positioned absolutely in upper-right corner")
            return False
        
        print("✅ Icons positioned absolutely in upper-right corner")
        
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
        
        # Check for proper structure with relative container
        if 'relative' not in html_content:
            print("❌ Container not set to relative positioning")
            return False
        
        print("✅ Container set to relative positioning")
        
        # Check for content padding to avoid overlap
        if 'pr-20' not in html_content:
            print("❌ Content padding not added to avoid icon overlap")
            return False
        
        print("✅ Content padding added to avoid icon overlap")
        
        # Check that icons are within the expandable content
        icon_pattern = r'<div class="expandable-content.*?relative".*?<div class="absolute top-4 right-4'
        if not re.search(icon_pattern, html_content, re.DOTALL):
            print("❌ Icons not properly nested within expandable content")
            return False
        
        print("✅ Icons properly nested within expandable content")
        
        print("\n🎉 All icon positioning tests passed!")
        return True
        
    except FileNotFoundError:
        print("❌ templates/room/view.html file not found")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    test_icons_in_card() 