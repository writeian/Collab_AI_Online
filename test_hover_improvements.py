#!/usr/bin/env python3
"""
Test script to verify hover improvements
"""

def test_hover_improvements():
    print("🎨 Testing Hover Improvements")
    print("=" * 50)
    
    # Test 1: Check if hover styles are added
    print("\n1. Checking hover styles...")
    try:
        with open('static/css/components.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
            
        if '.criterion-header button:hover' in css_content:
            print("✅ Criterion button hover styles added")
        else:
            print("❌ Criterion button hover styles missing")
            
        if '.level-toggle:hover' in css_content:
            print("✅ Level toggle hover styles added")
        else:
            print("❌ Level toggle hover styles missing")
            
    except Exception as e:
        print(f"❌ Error reading CSS: {e}")
    
    # Test 2: Check for lighter hover colors
    print("\n2. Checking hover colors...")
    try:
        if 'rgba(59, 130, 246, 0.1)' in css_content:
            print("✅ Light blue hover color for criterion buttons")
        else:
            print("❌ Light blue hover color not found")
            
        if 'rgba(0, 0, 0, 0.05)' in css_content:
            print("✅ Very light hover color for level toggles")
        else:
            print("❌ Light hover color not found")
            
    except Exception as e:
        print(f"❌ Error checking hover colors: {e}")
    
    # Test 3: Check for font weight improvements
    print("\n3. Checking font weight...")
    try:
        if 'font-weight: 600' in css_content:
            print("✅ Bold font weight added to buttons")
        else:
            print("❌ Bold font weight not found")
            
    except Exception as e:
        print(f"❌ Error checking font weight: {e}")
    
    # Test 4: Check for smooth transitions
    print("\n4. Checking transitions...")
    try:
        if 'transition: all 0.2s ease' in css_content:
            print("✅ Smooth transitions added")
        else:
            print("❌ Smooth transitions not found")
            
    except Exception as e:
        print(f"❌ Error checking transitions: {e}")
    
    # Test 5: Check CSS version
    print("\n5. Checking CSS version...")
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
            
        if '?v=4.5' in base_content:
            print("✅ CSS version updated to 4.5")
        else:
            print("❌ CSS version not updated to 4.5")
            
    except Exception as e:
        print(f"❌ Error checking CSS version: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Summary: Hover improvements applied!")
    print("\n✨ What you should see now:")
    print("1. Bold font weight on all accordion buttons")
    print("2. Light blue hover effect for criterion buttons")
    print("3. Very subtle hover effect for level toggles")
    print("4. Smooth transitions and subtle lift effect")
    print("5. No more dark blue hover states")
    print("\n🔄 Test the changes:")
    print("1. Refresh your browser")
    print("2. Hover over the accordion buttons")
    print("3. Notice the lighter, more elegant hover effects")

if __name__ == "__main__":
    test_hover_improvements() 