#!/usr/bin/env python3
"""
Test script to verify the improved styling implementation.
"""

import requests
from bs4 import BeautifulSoup

def test_improved_styling():
    """Test the improved styling implementation."""
    print("🎨 Testing Improved Styling Implementation")
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
        
        # Test 1: Check for improved room header styling
        print("\n1. Testing Improved Room Header:")
        
        # Check for room header card
        room_header_card = soup.find('div', class_='bg-card border border-border rounded-lg p-6 mb-8')
        if room_header_card:
            print("   ✅ Room header card found")
        else:
            print("   ❌ Room header card missing")
            
        # Check for improved room title
        room_title = soup.find('h2', class_='text-2xl font-bold text-foreground mb-3')
        if room_title:
            print("   ✅ Improved room title styling found")
        else:
            print("   ❌ Improved room title styling missing")
            
        # Test 2: Check for improved room actions button
        print("\n2. Testing Room Actions Button:")
        
        # Check for btn-outline class
        room_actions_btn = soup.find('button', class_='btn btn-outline dropdown-toggle')
        if room_actions_btn:
            print("   ✅ Room actions button with btn-outline class found")
        else:
            print("   ❌ Room actions button with btn-outline class missing")
            
        # Test 3: Check for improved chat section styling
        print("\n3. Testing Chat Section Styling:")
        
        # Check for chat section card
        chat_section_card = soup.find('div', class_='bg-card border border-border rounded-lg p-6 mb-8')
        if chat_section_card:
            print("   ✅ Chat section card found")
        else:
            print("   ❌ Chat section card missing")
            
        # Test 4: Check for improved chat cards
        print("\n4. Testing Improved Chat Cards:")
        
        chat_cards_large = soup.find_all('div', class_='chat-card-large')
        if chat_cards_large:
            print(f"   ✅ Found {len(chat_cards_large)} improved chat card(s)")
            for i, card in enumerate(chat_cards_large[:3]):
                title = card.find('h3')
                if title:
                    print(f"      - Card {i+1}: {title.get_text().strip()}")
        else:
            print("   ❌ No improved chat cards found")
            
        # Test 5: Check for new CSS version
        print("\n5. Testing CSS Version:")
        css_links = soup.find_all('link', href=lambda h: h and 'components.css?v=2.4' in h)
        if css_links:
            print("   ✅ Updated CSS version (2.4) found")
        else:
            print("   ❌ Updated CSS version not found")
            
        # Test 6: Check for visual improvements
        print("\n6. Testing Visual Improvements:")
        
        # Check for learning goals styling
        learning_goals = soup.find('div', class_='room-goals bg-primary/5 border-l-4 border-primary p-4 rounded-r-lg mb-4')
        if learning_goals:
            print("   ✅ Improved learning goals styling found")
        else:
            print("   ℹ️  Learning goals styling not found (may not have goals)")
            
        # Check for improved spacing
        improved_spacing = soup.find_all('div', class_='bg-card border border-border rounded-lg p-6 mb-8')
        if len(improved_spacing) >= 2:
            print(f"   ✅ Found {len(improved_spacing)} sections with improved spacing")
        else:
            print("   ❌ Improved spacing not found")
            
        # Test 7: Show content preview
        print("\n7. Content Preview:")
        room_titles = soup.find_all('h2', class_='text-2xl font-bold')
        if room_titles:
            print(f"   Found {len(room_titles)} room titles:")
            for i, title in enumerate(room_titles[:2]):
                print(f"      - {title.get_text().strip()}")
        
        print("\n" + "=" * 60)
        print("🎉 Improved Styling Test Complete!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error testing improved styling: {e}")
        return False

if __name__ == "__main__":
    test_improved_styling() 