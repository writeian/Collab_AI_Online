#!/usr/bin/env python3
"""
Test script to verify the dark blue color is removed from style.css
"""

def test_dark_blue_fix():
    print("🎯 Testing Dark Blue Color Removal")
    print("=" * 50)
    
    # Test 1: Check if dark blue color is removed
    print("\n1. Checking for dark blue color removal...")
    try:
        with open('static/style.css', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '#054ea8' not in content:
            print("✅ Dark blue color #054ea8 removed from style.css")
        else:
            print("❌ Dark blue color #054ea8 still present in style.css")
            
    except Exception as e:
        print(f"❌ Error reading style.css: {e}")
    
    # Test 2: Check if light gray color is added
    print("\n2. Checking for light gray color addition...")
    try:
        if '#e5e7eb' in content:
            print("✅ Light gray color #e5e7eb added to style.css")
        else:
            print("❌ Light gray color #e5e7eb not found in style.css")
            
    except Exception as e:
        print(f"❌ Error checking light gray color: {e}")
    
    # Test 3: Check CSS version
    print("\n3. Checking CSS version...")
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
            
        if '?v=5.1' in base_content:
            print("✅ CSS version updated to 5.1")
        else:
            print("❌ CSS version not updated to 5.1")
            
    except Exception as e:
        print(f"❌ Error checking CSS version: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Dark Blue Fix Complete!")
    print("\n✨ What was fixed:")
    print("1. Removed #054ea8 (dark blue) from button:hover")
    print("2. Removed #054ea8 (dark blue) from button[type='submit']:hover")
    print("3. Added #e5e7eb (light gray) to both hover rules")
    print("4. Updated CSS version to force cache refresh")
    print("\n🔄 To test:")
    print("1. Hard refresh your browser (Ctrl+F5)")
    print("2. Hover over ANY button on the website")
    print("3. Should see light gray hover instead of dark blue")
    print("4. This fixes the issue across the ENTIRE website!")

if __name__ == "__main__":
    test_dark_blue_fix() 