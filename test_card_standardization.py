#!/usr/bin/env python3
"""
Test script to verify card standardization and icon positioning.
Checks that all white cards have consistent styling and icons are inside the Room Info card.
"""

import re

def test_card_standardization():
    """Test that white cards are standardized and icons are properly positioned."""
    
    try:
        with open('templates/room/view.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print("🔍 Testing card standardization and icon positioning...")
        
        # Check for Room Info section with proper structure
        if 'id="room-info-content"' not in html_content:
            print("❌ Room Info content section not found")
            return False
        
        print("✅ Room Info content section found")
        
        # Check that icons are inside the Room Info card (not using absolute positioning)
        if 'absolute top-4 right-4' in html_content:
            print("❌ Icons still using absolute positioning outside card")
            return False
        
        print("✅ Icons no longer using absolute positioning")
        
        # Check for proper flex layout in Room Info
        if 'flex items-start justify-between' not in html_content:
            print("❌ Room Info not using proper flex layout")
            return False
        
        print("✅ Room Info using proper flex layout")
        
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
        
        # Check that chat cards use space-y-4 instead of grid
        if 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' in html_content:
            print("❌ Chat cards still using grid layout")
            return False
        
        print("✅ Chat cards using vertical layout (space-y-4)")
        
        # Check that chat cards have consistent styling
        if 'chat-card-large' in html_content:
            print("❌ Chat cards still using old large card class")
            return False
        
        print("✅ Chat cards using standardized styling")
        
        # Check for proper card structure
        card_structure_pattern = r'<div class="expandable-content p-6 pt-0" id="room-info-content">.*?<div class="flex items-start justify-between">.*?<div class="flex-1">.*?<div class="flex items-center gap-2 ml-6">'
        if not re.search(card_structure_pattern, html_content, re.DOTALL):
            print("❌ Room Info card structure not properly organized")
            return False
        
        print("✅ Room Info card structure properly organized")
        
        print("\n🎉 All card standardization tests passed!")
        return True
        
    except FileNotFoundError:
        print("❌ templates/room/view.html file not found")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    test_card_standardization() 