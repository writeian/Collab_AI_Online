#!/usr/bin/env python3
"""
Debug script to check what's actually being served by the room page.
"""

import requests
from bs4 import BeautifulSoup

def debug_room_page():
    """Debug the room page content."""
    print("🔍 Debugging Room Page Content")
    print("=" * 50)
    
    url = "http://127.0.0.1:5000/room/4"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for specific elements
            print("\n🔍 Looking for key elements:")
            
            # Check for Quick Stats
            quick_stats = soup.find('h3', string=lambda text: text and 'Quick Stats' in text)
            if quick_stats:
                print("✅ Quick Stats found")
                print(f"   Text: {quick_stats.get_text().strip()}")
            else:
                print("❌ Quick Stats not found")
                
            # Check for Existing Chats
            existing_chats = soup.find('h3', string=lambda text: text and 'Existing Chats' in text)
            if existing_chats:
                print("✅ Existing Chats found")
                print(f"   Text: {existing_chats.get_text().strip()}")
            else:
                print("❌ Existing Chats not found")
                
            # Check for Room Members
            room_members = soup.find('h3', string=lambda text: text and 'Room Members' in text)
            if room_members:
                print("✅ Room Members found")
                print(f"   Text: {room_members.get_text().strip()}")
            else:
                print("❌ Room Members not found")
                
            # Check for chat cards
            chat_cards = soup.find_all('div', class_='chat-card')
            print(f"\n📋 Chat Cards: {len(chat_cards)} found")
            
            # Check for member items
            member_items = soup.find_all('div', class_='member-item')
            print(f"👥 Member Items: {len(member_items)} found")
            
            # Check for achievements
            achievements = soup.find('h3', string=lambda text: text and 'Achievements' in text)
            if achievements:
                print("🏆 Achievements found")
            else:
                print("❌ Achievements not found")
                
            # Check for grid layout
            grids = soup.find_all('div', class_=lambda c: c and 'grid' in c)
            print(f"📐 Grid layouts: {len(grids)} found")
            
            # Show some of the actual HTML structure
            print("\n📄 HTML Structure Preview:")
            main_content = soup.find('div', class_='max-w-7xl')
            if main_content:
                # Show first 500 characters of the main content
                content_text = str(main_content)[:500]
                print(content_text + "..." if len(str(main_content)) > 500 else content_text)
            else:
                print("❌ Main content container not found")
                
        else:
            print(f"❌ Failed to load page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_room_page() 