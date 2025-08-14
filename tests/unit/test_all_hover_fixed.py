#!/usr/bin/env python3
"""
Test script to verify all dark hover classes are removed
"""

def test_all_hover_fixed():
    print("🎯 Testing All Dark Hover Classes Removed")
    print("=" * 50)
    
    # Test 1: Check for any remaining dark hover classes
    print("\n1. Checking for remaining dark hover classes...")
    try:
        with open('templates/room/create.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'hover:bg-secondary/80' not in content:
            print("✅ All hover:bg-secondary/80 classes removed")
        else:
            print("❌ hover:bg-secondary/80 classes still present")
            
        if 'hover:bg-secondary/90' not in content:
            print("✅ All hover:bg-secondary/90 classes removed")
        else:
            print("❌ hover:bg-secondary/90 classes still present")
            
        if 'hover:bg-muted/40' not in content:
            print("✅ All hover:bg-muted/40 classes removed")
        else:
            print("❌ hover:bg-muted/40 classes still present")
            
    except Exception as e:
        print(f"❌ Error reading create.html: {e}")
    
    # Test 2: Check for light hover classes
    print("\n2. Checking for light hover classes...")
    try:
        if 'hover:bg-blue-100' in content:
            print("✅ Light blue hover for criterion buttons")
        else:
            print("❌ Light blue hover not found")
            
        if 'hover:bg-gray-50' in content:
            print("✅ Light gray hover for level toggles")
        else:
            print("❌ Light gray hover for level toggles not found")
            
        if 'hover:bg-gray-100' in content:
            print("✅ Light gray hover for other buttons")
        else:
            print("❌ Light gray hover for other buttons not found")
            
    except Exception as e:
        print(f"❌ Error checking light hover classes: {e}")
    
    # Test 3: Check CSS version
    print("\n3. Checking CSS version...")
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
            
        if '?v=4.8' in base_content:
            print("✅ CSS version updated to 4.8")
        else:
            print("❌ CSS version not updated to 4.8")
            
    except Exception as e:
        print(f"❌ Error checking CSS version: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 All Dark Hover Classes Should Be Fixed!")
    print("\n✨ What was fixed:")
    print("1. All 'hover:bg-secondary/80' → 'hover:bg-gray-100'")
    print("2. All 'hover:bg-secondary/90' → 'hover:bg-gray-100'")
    print("3. All 'hover:bg-muted/40' → 'hover:bg-gray-50'")
    print("4. Updated CSS version to force cache refresh")
    print("\n🔄 To test:")
    print("1. Hard refresh your browser (Ctrl+F5)")
    print("2. Hover over ALL buttons on the page")
    print("3. Should see light colors instead of dark blue")
    print("4. No more dark blue hover anywhere!")

if __name__ == "__main__":
    test_all_hover_fixed() 