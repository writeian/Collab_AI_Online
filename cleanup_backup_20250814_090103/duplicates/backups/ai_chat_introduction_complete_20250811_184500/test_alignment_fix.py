#!/usr/bin/env python3
"""
Test script to verify the alignment fix for expandable sections.
"""

import requests
from bs4 import BeautifulSoup

def test_alignment_fix():
    """Test the alignment fix for expandable sections."""
    print("🎯 Testing Alignment Fix for Expandable Sections")
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
        
        # Test 1: Check main content container
        print("\n1. Testing Main Content Container:")
        
        main_container = soup.find('div', class_='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8')
        if main_container:
            print("   ✅ Main content container found")
        else:
            print("   ❌ Main content container missing")
            
        # Test 2: Check that all expandable sections are inside main container
        print("\n2. Testing Section Alignment:")
        
        expandable_sections = soup.find_all('div', class_='expandable-section')
        if expandable_sections:
            print(f"   ✅ Found {len(expandable_sections)} expandable sections")
            
            # Check if they're all inside the main container
            all_in_container = True
            for i, section in enumerate(expandable_sections):
                if main_container and section in main_container.descendants:
                    print(f"      - Section {i+1}: Inside main container ✅")
                else:
                    print(f"      - Section {i+1}: Outside main container ❌")
                    all_in_container = False
            
            if all_in_container:
                print("   ✅ All sections properly aligned within main container")
            else:
                print("   ❌ Some sections are outside main container")
        else:
            print("   ❌ No expandable sections found")
            
        # Test 3: Check spacing between sections
        print("\n3. Testing Section Spacing:")
        
        sections_with_mb8 = soup.find_all('div', class_='expandable-section bg-card border border-border rounded-lg mb-8')
        if sections_with_mb8:
            print(f"   ✅ Found {len(sections_with_mb8)} sections with proper spacing (mb-8)")
        else:
            print("   ❌ No sections with proper spacing found")
            
        # Test 4: Check for removed space-y-6 container
        print("\n4. Testing Removed Space Container:")
        
        space_y_6_container = soup.find('div', class_='space-y-6')
        if space_y_6_container:
            print("   ❌ space-y-6 container still exists")
        else:
            print("   ✅ space-y-6 container properly removed")
            
        # Test 5: Check CSS version
        print("\n5. Testing CSS Version:")
        css_links = soup.find_all('link', href=lambda h: h and 'components.css?v=2.7' in h)
        if css_links:
            print("   ✅ Updated CSS version (2.7) found")
        else:
            print("   ❌ Updated CSS version not found")
            
        # Test 6: Show section hierarchy
        print("\n6. Section Hierarchy:")
        if main_container:
            expandable_in_container = main_container.find_all('div', class_='expandable-section')
            print(f"   Found {len(expandable_in_container)} expandable sections in main container:")
            for i, section in enumerate(expandable_in_container):
                header = section.find('h3')
                if header:
                    print(f"      - Section {i+1}: {header.get_text().strip()}")
        
        print("\n" + "=" * 60)
        print("🎯 Alignment Fix Test Complete!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error testing alignment fix: {e}")
        return False

if __name__ == "__main__":
    test_alignment_fix() 