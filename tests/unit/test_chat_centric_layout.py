#!/usr/bin/env python3
"""
Test script to verify the new chat-centric layout implementation.
"""

import requests
from bs4 import BeautifulSoup

def test_chat_centric_layout():
    """Test the new chat-centric layout implementation."""
    print("🧪 Testing Chat-Centric Layout Implementation")
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
        
        # Test 1: Check for chat-centric layout
        print("\n1. Testing Chat-Centric Layout:")
        
        # Check for "Your Chats" hero section
        your_chats = soup.find('h2', string=lambda text: text and 'Your Chats' in text)
        if your_chats:
            print("   ✅ 'Your Chats' hero section found")
        else:
            print("   ❌ 'Your Chats' hero section missing")
            
        # Check for large chat cards
        chat_cards_large = soup.find_all('div', class_='chat-card-large')
        if chat_cards_large:
            print(f"   ✅ Found {len(chat_cards_large)} large chat card(s)")
            for i, card in enumerate(chat_cards_large[:3]):
                title = card.find('h3')
                if title:
                    print(f"      - Card {i+1}: {title.get_text().strip()}")
        else:
            print("   ❌ No large chat cards found")
            
        # Test 2: Check for expandable sections
        print("\n2. Testing Expandable Sections:")
        
        expandable_sections = soup.find_all('div', class_='expandable-section')
        if expandable_sections:
            print(f"   ✅ Found {len(expandable_sections)} expandable section(s)")
            
            # Check for specific sections
            achievements_section = soup.find('h3', string=lambda text: text and 'Your Achievements' in text)
            if achievements_section:
                print("   ✅ Achievements section found")
            else:
                print("   ❌ Achievements section missing")
                
            members_section = soup.find('h3', string=lambda text: text and 'Room Members' in text)
            if members_section:
                print("   ✅ Room Members section found")
            else:
                print("   ❌ Room Members section missing")
                
            stats_section = soup.find('h3', string=lambda text: text and 'Room Stats' in text)
            if stats_section:
                print("   ✅ Room Stats section found")
            else:
                print("   ❌ Room Stats section missing")
        else:
            print("   ❌ No expandable sections found")
            
        # Test 3: Check for unread badges
        print("\n3. Testing Unread Badges:")
        unread_badges = soup.find_all('span', class_='unread-badge')
        if unread_badges:
            print(f"   ✅ Found {len(unread_badges)} unread badge(s)")
        else:
            print("   ℹ️  No unread badges found (may be normal)")
            
        # Test 4: Check for responsive grid
        print("\n4. Testing Responsive Grid:")
        responsive_grid = soup.find('div', class_=lambda c: c and 'grid-cols-1' in c and 'xl:grid-cols-4' in c)
        if responsive_grid:
            print("   ✅ Responsive grid layout found")
        else:
            print("   ❌ Responsive grid layout missing")
            
        # Test 5: Check for new CSS version
        print("\n5. Testing CSS Version:")
        css_links = soup.find_all('link', href=lambda h: h and 'components.css?v=2.3' in h)
        if css_links:
            print("   ✅ Updated CSS version (2.3) found")
        else:
            print("   ❌ Updated CSS version not found")
            
        # Test 6: Check for JavaScript functions
        print("\n6. Testing JavaScript Functions:")
        toggle_section = soup.find('script', string=lambda s: s and 'toggleSection' in s)
        if toggle_section:
            print("   ✅ toggleSection function found")
        else:
            print("   ❌ toggleSection function missing")
            
        # Test 7: Show content preview
        print("\n7. Content Preview:")
        chat_titles = soup.find_all('h3', class_=lambda c: c and 'text-lg' in c)
        if chat_titles:
            print(f"   Found {len(chat_titles)} chat titles:")
            for i, title in enumerate(chat_titles[:3]):
                print(f"      - {title.get_text().strip()}")
        
        print("\n" + "=" * 60)
        print("🎉 Chat-Centric Layout Test Complete!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error testing chat-centric layout: {e}")
        return False

if __name__ == "__main__":
    test_chat_centric_layout() 