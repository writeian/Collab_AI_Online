#!/usr/bin/env python3
"""
Test script to verify hover fix at the source level
"""

def test_hover_fix_source():
    print("🎯 Testing Hover Fix at Source Level")
    print("=" * 50)
    
    # Test 1: Check HTML template changes
    print("\n1. Checking HTML template changes...")
    try:
        with open('templates/room/create.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'hover:bg-blue-100' in content:
            print("✅ Criterion button hover changed to light blue")
        else:
            print("❌ Criterion button hover not changed")
            
        if 'hover:bg-gray-50' in content:
            print("✅ Level toggle hover changed to light gray")
        else:
            print("❌ Level toggle hover not changed")
            
        if 'hover:bg-gray-100' in content:
            print("✅ Edit/Cancel button hover changed to light gray")
        else:
            print("❌ Edit/Cancel button hover not changed")
            
        # Check that old dark hover classes are removed
        if 'hover:bg-secondary/80' not in content:
            print("✅ Dark secondary hover removed")
        else:
            print("❌ Dark secondary hover still present")
            
        if 'hover:bg-muted/40' not in content:
            print("✅ Dark muted hover removed")
        else:
            print("❌ Dark muted hover still present")
            
    except Exception as e:
        print(f"❌ Error reading create.html: {e}")
    
    # Test 2: Check CSS overrides removed
    print("\n2. Checking CSS overrides removed...")
    try:
        with open('static/css/components.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
            
        if 'hover\\:bg-secondary\\/80:hover' not in css_content:
            print("✅ CSS overrides removed")
        else:
            print("❌ CSS overrides still present")
            
        if 'rgba(59, 130, 246, 0.1)' not in css_content:
            print("✅ Custom hover colors removed from CSS")
        else:
            print("❌ Custom hover colors still in CSS")
            
    except Exception as e:
        print(f"❌ Error reading CSS: {e}")
    
    # Test 3: Check CSS version
    print("\n3. Checking CSS version...")
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
            
        if '?v=4.7' in base_content:
            print("✅ CSS version updated to 4.7")
        else:
            print("❌ CSS version not updated to 4.7")
            
    except Exception as e:
        print(f"❌ Error checking CSS version: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Source-Level Hover Fix Complete!")
    print("\n✨ What was fixed:")
    print("1. Changed 'hover:bg-secondary/80' to 'hover:bg-blue-100' for criterion buttons")
    print("2. Changed 'hover:bg-muted/40' to 'hover:bg-gray-50' for level toggles")
    print("3. Changed 'hover:bg-secondary/80' to 'hover:bg-gray-100' for edit/cancel buttons")
    print("4. Removed all CSS overrides (no more !important rules)")
    print("5. Updated CSS version to force cache refresh")
    print("\n🔄 To test:")
    print("1. Hard refresh your browser (Ctrl+F5)")
    print("2. Hover over accordion buttons")
    print("3. Should see light blue and light gray hover effects")
    print("4. No more dark blue hover!")

if __name__ == "__main__":
    test_hover_fix_source() 