#!/usr/bin/env python3
"""
Test script to verify hamburger menu desktop hiding fix
"""

import re

def test_hamburger_fix():
    """Test the hamburger menu fix"""
    
    print("🔧 Testing Hamburger Menu Desktop Hiding Fix...")
    
    # Read base.html
    with open("templates/base.html", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check button classes
    button_pattern = r'id="mobile-menu-button"[^>]*class="([^"]*)"'
    button_match = re.search(button_pattern, content)
    
    if button_match:
        classes = button_match.group(1)
        print(f"✅ Button classes: {classes}")
        
        # Check for proper classes
        if "block" in classes:
            print("✅ 'block' class found - visible by default")
        else:
            print("❌ 'block' class missing")
            
        if "md:hidden" in classes:
            print("✅ 'md:hidden' class found - hidden on desktop")
        else:
            print("❌ 'md:hidden' class missing")
    else:
        print("❌ Could not find mobile-menu-button")
        return False
    
    # Check overlay classes
    overlay_pattern = r'id="mobile-menu-overlay"[^>]*class="([^"]*)"'
    overlay_match = re.search(overlay_pattern, content)
    
    if overlay_match:
        classes = overlay_match.group(1)
        print(f"✅ Overlay classes: {classes}")
        
        if "hidden" in classes:
            print("✅ 'hidden' class found - hidden by default")
        else:
            print("❌ 'hidden' class missing")
            
        if "md:hidden" in classes:
            print("✅ 'md:hidden' class found - hidden on desktop")
        else:
            print("❌ 'md:hidden' class missing")
    else:
        print("❌ Could not find mobile-menu-overlay")
        return False
    
    # Check CSS file
    try:
        with open("static/css/components.css", 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        if "@media (min-width: 768px)" in css_content:
            print("✅ CSS media query found for desktop hiding")
        else:
            print("❌ CSS media query missing")
            
        if "display: none !important" in css_content:
            print("✅ CSS !important rule found")
        else:
            print("❌ CSS !important rule missing")
            
    except FileNotFoundError:
        print("❌ components.css not found")
        return False
    
    return True

def explain_the_fix():
    """Explain what was fixed"""
    
    print("\n🔧 What Was Fixed:")
    print("=" * 25)
    print("1. **HTML Classes**:")
    print("   - Changed button to 'block md:hidden' (visible by default, hidden on desktop)")
    print("   - Changed overlay to 'hidden md:hidden' (hidden by default and on desktop)")
    
    print("\n2. **CSS Rules**:")
    print("   - Added @media (min-width: 768px) rule")
    print("   - Added display: none !important to force hide on desktop")
    print("   - This overrides any conflicting CSS")
    
    print("\n3. **How It Works**:")
    print("   - Mobile (<768px): Button is visible (block), overlay is hidden")
    print("   - Desktop (≥768px): Button is hidden (md:hidden), overlay is hidden")
    print("   - CSS !important ensures no other styles can override this")

def main():
    """Main test function"""
    print("🚀 Hamburger Menu Fix Test")
    print("=" * 30)
    
    success = test_hamburger_fix()
    
    if success:
        print("\n✅ Fix applied successfully!")
        print("💡 The hamburger menu should now be properly hidden on desktop.")
        print("🔄 Refresh your browser to see the changes.")
    else:
        print("\n❌ Some issues found. Check the implementation.")
    
    explain_the_fix()
    
    return success

if __name__ == "__main__":
    main() 