#!/usr/bin/env python3
"""
Test script to verify the new room layout implementation.
Checks for redesigned components and structure.
"""

import requests
from bs4 import BeautifulSoup
import re

def test_room_layout():
    """Test the new room layout implementation."""
    print("🧪 Testing New Room Layout Implementation")
    print("=" * 50)
    
    # Test room page
    url = "http://127.0.0.1:5000/room/4"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Failed to load room page: {response.status_code}")
            return False
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Test 1: Check for new layout structure
        print("\n1. Testing Layout Structure:")
        
        # Check for Quick Stats section
        quick_stats = soup.find('h3', string=re.compile(r'Quick Stats', re.I))
        if quick_stats:
            print("   ✅ Quick Stats section found")
        else:
            print("   ❌ Quick Stats section missing")
            
        # Check for redesigned chat section
        chat_section = soup.find('h3', string=re.compile(r'Existing Chats', re.I))
        if chat_section:
            print("   ✅ Existing Chats section found")
        else:
            print("   ❌ Existing Chats section missing")
            
        # Check for room members section
        members_section = soup.find('h3', string=re.compile(r'Room Members', re.I))
        if members_section:
            print("   ✅ Room Members section found")
        else:
            print("   ❌ Room Members section missing")
            
        # Test 2: Check for chat cards
        print("\n2. Testing Chat Cards:")
        chat_cards = soup.find_all('div', class_='chat-card')
        if chat_cards:
            print(f"   ✅ Found {len(chat_cards)} chat card(s)")
            for i, card in enumerate(chat_cards[:3]):  # Show first 3
                title = card.find('h4')
                if title:
                    print(f"      - Card {i+1}: {title.get_text().strip()}")
        else:
            print("   ❌ No chat cards found")
            
        # Test 3: Check for member items with avatars
        print("\n3. Testing Member Items:")
        member_items = soup.find_all('div', class_='member-item')
        if member_items:
            print(f"   ✅ Found {len(member_items)} member item(s)")
            for i, item in enumerate(member_items[:3]):  # Show first 3
                name = item.find('p', class_='member-name')
                if name:
                    print(f"      - Member {i+1}: {name.get_text().strip()}")
        else:
            print("   ❌ No member items found")
            
        # Test 4: Check for achievements section
        print("\n4. Testing Achievements Section:")
        achievements_section = soup.find('h3', string=re.compile(r'Your Achievements', re.I))
        if achievements_section:
            print("   ✅ Achievements section found")
            achievement_badges = soup.find_all('div', class_='achievement-badge')
            if achievement_badges:
                print(f"   ✅ Found {len(achievement_badges)} achievement badge(s)")
            else:
                print("   ℹ️  No achievement badges found (user may not have achievements)")
        else:
            print("   ❌ Achievements section missing")
            
        # Test 5: Check for responsive design classes
        print("\n5. Testing Responsive Design:")
        grid_classes = soup.find_all('div', class_=re.compile(r'grid.*grid-cols'))
        if grid_classes:
            print("   ✅ Grid layout classes found")
        else:
            print("   ❌ Grid layout classes missing")
            
        # Test 6: Check for updated CSS version
        print("\n6. Testing CSS Version:")
        css_links = soup.find_all('link', href=re.compile(r'components\.css\?v=2\.2'))
        if css_links:
            print("   ✅ Updated CSS version (2.2) found")
        else:
            print("   ❌ Updated CSS version not found")
            
        # Test 7: Check for room actions dropdown
        print("\n7. Testing Room Actions Dropdown:")
        dropdown = soup.find('button', onclick='toggleRoomActions()')
        if dropdown:
            print("   ✅ Room actions dropdown found")
        else:
            print("   ❌ Room actions dropdown missing")
            
        print("\n" + "=" * 50)
        print("🎉 Room Layout Test Complete!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error testing room layout: {e}")
        return False

if __name__ == "__main__":
    test_room_layout() 