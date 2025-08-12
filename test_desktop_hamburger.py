#!/usr/bin/env python3
"""
Test script to check if hamburger menu is properly hidden on desktop
"""

import os
import re

def check_hamburger_visibility():
    """Check if hamburger menu has proper desktop hiding classes"""
    
    print("🔍 Checking Hamburger Menu Desktop Visibility...")
    
    # Read base.html
    with open("templates/base.html", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the hamburger menu button
    button_pattern = r'id="mobile-menu-button"[^>]*class="([^"]*)"'
    button_match = re.search(button_pattern, content)
    
    if button_match:
        classes = button_match.group(1)
        print(f"✅ Hamburger button classes: {classes}")
        
        # Check for md:hidden class
        if "md:hidden" in classes:
            print("✅ md:hidden class found - should hide on desktop (≥768px)")
        else:
            print("❌ md:hidden class missing!")
            return False
        
        # Check for other visibility classes
        if "hidden" in classes:
            print("⚠️  'hidden' class found - this might cause issues")
        if "block" in classes:
            print("⚠️  'block' class found - this might override md:hidden")
        if "flex" in classes:
            print("⚠️  'flex' class found - this might override md:hidden")
            
    else:
        print("❌ Could not find mobile-menu-button")
        return False
    
    # Check the overlay
    overlay_pattern = r'id="mobile-menu-overlay"[^>]*class="([^"]*)"'
    overlay_match = re.search(overlay_pattern, content)
    
    if overlay_match:
        classes = overlay_match.group(1)
        print(f"✅ Mobile overlay classes: {classes}")
        
        if "md:hidden" in classes:
            print("✅ Overlay has md:hidden class")
        else:
            print("❌ Overlay missing md:hidden class!")
            return False
    else:
        print("❌ Could not find mobile-menu-overlay")
        return False
    
    return True

def check_tailwind_loading():
    """Check if Tailwind CSS is properly loaded"""
    
    print("\n🎨 Checking Tailwind CSS Loading...")
    
    with open("templates/base.html", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for Tailwind CDN
    if "cdn.tailwindcss.com" in content:
        print("✅ Tailwind CSS CDN found")
    else:
        print("❌ Tailwind CSS CDN not found!")
        return False
    
    # Check for custom CSS files
    css_files = [
        "globals.css",
        "components.css", 
        "style.css"
    ]
    
    for css_file in css_files:
        if css_file in content:
            print(f"✅ {css_file} referenced")
        else:
            print(f"⚠️  {css_file} not referenced")
    
    return True

def check_css_conflicts():
    """Check for potential CSS conflicts"""
    
    print("\n🔧 Checking for CSS Conflicts...")
    
    # Check components.css for mobile menu styles
    if os.path.exists("static/css/components.css"):
        with open("static/css/components.css", 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Look for mobile menu styles that might override Tailwind
        mobile_styles = [
            "#mobile-menu-button",
            "#mobile-menu-overlay",
            "md:hidden",
            "display:",
            "visibility:"
        ]
        
        for style in mobile_styles:
            if style in css_content:
                print(f"✅ Found {style} in components.css")
            else:
                print(f"⚠️  {style} not found in components.css")
    else:
        print("❌ components.css not found")
        return False
    
    return True

def suggest_fixes():
    """Suggest potential fixes if issues are found"""
    
    print("\n💡 Potential Fixes:")
    print("=" * 30)
    print("1. If hamburger menu shows on desktop:")
    print("   - Check browser developer tools (F12)")
    print("   - Look for CSS that might override 'md:hidden'")
    print("   - Ensure Tailwind CSS is loading properly")
    print("   - Check for conflicting CSS rules")
    
    print("\n2. To force hide on desktop, you could add:")
    print("   - !important to the md:hidden class")
    print("   - Additional CSS: @media (min-width: 768px) { #mobile-menu-button { display: none !important; } }")
    
    print("\n3. To test if it's a CSS issue:")
    print("   - Open browser dev tools")
    print("   - Inspect the hamburger button")
    print("   - Check if 'display: none' is applied at 768px+")
    print("   - Look for any CSS rules that override this")

def main():
    """Main test function"""
    print("🚀 Desktop Hamburger Menu Test")
    print("=" * 35)
    
    # Run all checks
    button_ok = check_hamburger_visibility()
    tailwind_ok = check_tailwind_loading()
    css_ok = check_css_conflicts()
    
    print("\n📊 Results Summary:")
    print("=" * 20)
    print(f"Button classes: {'✅' if button_ok else '❌'}")
    print(f"Tailwind loading: {'✅' if tailwind_ok else '❌'}")
    print(f"CSS conflicts: {'✅' if css_ok else '❌'}")
    
    if button_ok and tailwind_ok and css_ok:
        print("\n✅ All checks passed! The hamburger menu should be hidden on desktop.")
        print("💡 If you still see it on desktop, check browser dev tools for CSS conflicts.")
    else:
        print("\n❌ Some issues found. Check the details above.")
    
    suggest_fixes()
    
    return button_ok and tailwind_ok and css_ok

if __name__ == "__main__":
    main() 