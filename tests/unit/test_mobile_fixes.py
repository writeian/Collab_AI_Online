#!/usr/bin/env python3
"""
Test mobile navigation and AI toggle fixes
"""

import requests
from bs4 import BeautifulSoup

def test_mobile_fixes():
    """Test that mobile navigation and toggle work correctly"""
    
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
    
    # Access a chat page
    print("🔍 Accessing chat page...")
    response = session.get('http://localhost:5000/chat/9')
    
    if response.status_code != 200:
        print("❌ Could not access chat page")
        return False
    
    print("✅ Chat page accessed successfully")
    
    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Test 1: Check mobile navigation
    print("\n📱 Testing mobile navigation...")
    nav = soup.find('nav')
    if nav:
        nav_classes = nav.get('class', [])
        print(f"✅ Navigation found with classes: {nav_classes}")
        
        # Check for responsive classes
        if 'space-x-2' in nav_classes and 'sm:space-x-4' in nav_classes:
            print("✅ Mobile-responsive spacing found")
        else:
            print("❌ Mobile-responsive spacing missing")
    else:
        print("❌ Navigation not found")
    
    # Test 2: Check AI toggle for duplicate text
    print("\n🤖 Testing AI toggle...")
    toggle_label = soup.find('label', {'for': 'ai-response-toggle'})
    if toggle_label:
        label_text = toggle_label.get_text(strip=True)
        print(f"✅ Toggle label found: '{label_text}'")
        
        # Check for duplicate text
        if label_text == "🤖 AI Response":
            print("✅ No duplicate text found")
        else:
            print(f"❌ Unexpected label text: '{label_text}'")
    else:
        print("❌ AI toggle label not found")
    
    # Test 3: Check for duplicate span elements
    toggle_spans = soup.find_all('span', class_='text-xs text-muted-foreground')
    duplicate_spans = [span for span in toggle_spans if 'Uncheck to send message' in span.get_text()]
    
    if len(duplicate_spans) == 0:
        print("✅ No duplicate toggle text spans found")
    else:
        print(f"❌ Found {len(duplicate_spans)} duplicate text spans")
    
    print("\n✅ Mobile fixes test completed!")
    return True

if __name__ == "__main__":
    test_mobile_fixes() 