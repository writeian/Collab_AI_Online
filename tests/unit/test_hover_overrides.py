#!/usr/bin/env python3
"""
Test script to verify hover override styles
"""

def test_hover_overrides():
    print("🎯 Testing Hover Override Styles")
    print("=" * 50)
    
    # Test 1: Check for override styles
    print("\n1. Checking hover override styles...")
    try:
        with open('static/css/components.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
            
        if 'hover\\:bg-secondary\\/80:hover' in css_content:
            print("✅ Design system hover override found")
        else:
            print("❌ Design system hover override missing")
            
        if '[class*="hover:bg-secondary"]:hover' in css_content:
            print("✅ Generic secondary hover override found")
        else:
            print("❌ Generic secondary hover override missing")
            
        if '[class*="bg-secondary"]:hover' in css_content:
            print("✅ Aggressive secondary hover override found")
        else:
            print("❌ Aggressive secondary hover override missing")
            
        if '[class*="bg-muted"]:hover' in css_content:
            print("✅ Muted button hover override found")
        else:
            print("❌ Muted button hover override missing")
            
    except Exception as e:
        print(f"❌ Error reading CSS: {e}")
    
    # Test 2: Check CSS version
    print("\n2. Checking CSS version...")
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
            
        if '?v=4.6' in base_content:
            print("✅ CSS version updated to 4.6")
        else:
            print("❌ CSS version not updated to 4.6")
            
    except Exception as e:
        print(f"❌ Error checking CSS version: {e}")
    
    # Test 3: Check for light hover colors
    print("\n3. Checking light hover colors...")
    try:
        if 'rgba(59, 130, 246, 0.1)' in css_content:
            print("✅ Light blue hover color found")
        else:
            print("❌ Light blue hover color missing")
            
        if 'rgba(0, 0, 0, 0.05)' in css_content:
            print("✅ Light gray hover color found")
        else:
            print("❌ Light gray hover color missing")
            
    except Exception as e:
        print(f"❌ Error checking hover colors: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Hover Override Test Complete!")
    print("\n✨ What should work now:")
    print("1. Light blue hover for criterion buttons (overrides dark blue)")
    print("2. Very light gray hover for level toggles")
    print("3. Multiple override strategies to ensure it works")
    print("4. CSS version 4.6 to force cache refresh")
    print("\n🔄 To test:")
    print("1. Hard refresh your browser (Ctrl+F5)")
    print("2. Hover over accordion buttons")
    print("3. Should see light colors instead of dark blue")

if __name__ == "__main__":
    test_hover_overrides() 