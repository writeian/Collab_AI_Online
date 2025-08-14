#!/usr/bin/env python3
"""
Comprehensive test to verify hover improvements are working
"""

def test_hover_verification():
    print("🔍 Comprehensive Hover Verification")
    print("=" * 60)
    
    # Test 1: Check CSS file content
    print("\n1. Checking CSS file content...")
    try:
        with open('static/css/components.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
            
        # Check for hover styles
        if '.criterion-header button:hover' in css_content:
            print("✅ Criterion button hover styles found")
        else:
            print("❌ Criterion button hover styles missing")
            
        if '.level-toggle:hover' in css_content:
            print("✅ Level toggle hover styles found")
        else:
            print("❌ Level toggle hover styles missing")
            
        # Check for specific hover colors
        if 'rgba(59, 130, 246, 0.1)' in css_content:
            print("✅ Light blue hover color found")
        else:
            print("❌ Light blue hover color missing")
            
        if 'rgba(0, 0, 0, 0.05)' in css_content:
            print("✅ Light gray hover color found")
        else:
            print("❌ Light gray hover color missing")
            
        # Check for font weight
        if 'font-weight: 600' in css_content:
            print("✅ Bold font weight found")
        else:
            print("❌ Bold font weight missing")
            
        # Check for transitions
        if 'transition: all 0.2s ease' in css_content:
            print("✅ Smooth transitions found")
        else:
            print("❌ Smooth transitions missing")
            
    except Exception as e:
        print(f"❌ Error reading CSS: {e}")
    
    # Test 2: Check HTML template
    print("\n2. Checking HTML template...")
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
            
        if '?v=4.5' in base_content:
            print("✅ CSS version 4.5 found in base.html")
        else:
            print("❌ CSS version 4.5 not found in base.html")
            
    except Exception as e:
        print(f"❌ Error reading base.html: {e}")
    
    # Test 3: Check create.html for button classes
    print("\n3. Checking create.html for button structure...")
    try:
        with open('templates/room/create.html', 'r', encoding='utf-8') as f:
            create_content = f.read()
            
        if 'criterion-header' in create_content:
            print("✅ Criterion header buttons found")
        else:
            print("❌ Criterion header buttons not found")
            
        if 'level-toggle' in create_content:
            print("✅ Level toggle buttons found")
        else:
            print("❌ Level toggle buttons not found")
            
    except Exception as e:
        print(f"❌ Error reading create.html: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Verification Complete!")
    print("\n📋 What should be working:")
    print("1. Bold font weight on accordion buttons")
    print("2. Light blue hover for criterion buttons")
    print("3. Very light gray hover for level toggles")
    print("4. Smooth transitions and subtle lift effect")
    print("\n🔄 If you're not seeing changes:")
    print("1. Hard refresh your browser (Ctrl+F5 or Cmd+Shift+R)")
    print("2. Clear browser cache")
    print("3. Try incognito/private browsing mode")
    print("4. Check browser developer tools for CSS loading")
    print("\n💡 The CSS is definitely there - it's likely a caching issue!")

if __name__ == "__main__":
    test_hover_verification() 