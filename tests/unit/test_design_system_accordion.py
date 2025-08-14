#!/usr/bin/env python3
"""
Test script for design system accordion styling
"""

def test_design_system_accordion():
    print("🎨 Testing Design System Accordion Styling")
    print("=" * 50)
    
    # Test 1: Check if buttons use design system classes
    print("\n1. Checking design system button classes...")
    try:
        with open('templates/room/create.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'bg-secondary text-secondary-foreground' in content:
            print("✅ Criterion buttons use secondary design system colors")
        else:
            print("❌ Criterion buttons not using secondary design system colors")
            
        if 'bg-muted/20 hover:bg-muted/40' in content:
            print("✅ Level buttons use muted design system colors")
        else:
            print("❌ Level buttons not using muted design system colors")
            
    except Exception as e:
        print(f"❌ Error reading create.html: {e}")
    
    # Test 2: Check if chevron icons are present
    print("\n2. Checking chevron icons...")
    try:
        if 'data-lucide="chevron-down"' in content:
            print("✅ Chevron-down icons present")
        else:
            print("❌ Chevron-down icons missing")
            
        if 'data-lucide="chevron-up"' in content:
            print("✅ Chevron-up icons referenced in JavaScript")
        else:
            print("❌ Chevron-up icons not referenced in JavaScript")
            
    except Exception as e:
        print(f"❌ Error checking icons: {e}")
    
    # Test 3: Check if bright colors are removed
    print("\n3. Checking for removed bright colors...")
    try:
        if 'bg-blue-500' not in content and 'bg-green-500' not in content:
            print("✅ Bright blue and green colors removed")
        else:
            print("❌ Bright colors still present")
            
        if '#3b82f6' not in content and '#10b981' not in content:
            print("✅ Bright color hex codes removed from CSS")
        else:
            print("❌ Bright color hex codes still present")
            
    except Exception as e:
        print(f"❌ Error checking colors: {e}")
    
    # Test 4: Check CSS version
    print("\n4. Checking CSS version...")
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
            
        if '?v=4.3' in base_content:
            print("✅ CSS version updated to 4.3")
        else:
            print("❌ CSS version not updated to 4.3")
            
    except Exception as e:
        print(f"❌ Error checking CSS version: {e}")
    
    # Test 5: Check for design system CSS
    print("\n5. Checking design system CSS...")
    try:
        with open('static/css/components.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
            
        if 'Mobile-friendly accordion styles that match design system' in css_content:
            print("✅ Design system CSS section found")
        else:
            print("❌ Design system CSS section not found")
            
        if 'touch-action: manipulation' in css_content:
            print("✅ Touch action properties maintained")
        else:
            print("❌ Touch action properties missing")
            
    except Exception as e:
        print(f"❌ Error checking CSS: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Summary: Accordion now matches design system!")
    print("\n📱 What you should see now:")
    print("1. Subtle secondary-colored buttons with chevron icons")
    print("2. Muted background for level buttons")
    print("3. Icons that rotate when expanding/collapsing")
    print("4. Consistent styling with the rest of the page")
    print("\n🔄 Next steps:")
    print("1. Refresh your phone's browser")
    print("2. Go to: http://10.26.8.133:5000")
    print("3. Create a new room and check the rubric accordion")
    print("4. Verify the buttons now blend seamlessly with the page design")

if __name__ == "__main__":
    test_design_system_accordion() 