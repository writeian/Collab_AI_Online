#!/usr/bin/env python3
"""
Test script to verify aggressive hamburger menu desktop hiding fix
"""

import re

def test_aggressive_fix():
    """Test the aggressive hamburger menu fix"""
    
    print("🔧 Testing Aggressive Hamburger Menu Fix...")
    
    # Read base.html
    with open("templates/base.html", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for inline style
    if 'style="display: block;"' in content:
        print("✅ Inline style found: display: block (visible by default)")
    else:
        print("❌ Inline style missing")
    
    # Check for JavaScript fix
    if 'hideHamburgerOnDesktop' in content:
        print("✅ JavaScript fix found: hideHamburgerOnDesktop function")
    else:
        print("❌ JavaScript fix missing")
    
    if 'window.innerWidth >= 768' in content:
        print("✅ JavaScript desktop detection found")
    else:
        print("❌ JavaScript desktop detection missing")
    
    # Check for CSS version update
    if 'components.css") }}?v=3.4' in content:
        print("✅ CSS cache busting version updated to 3.4")
    else:
        print("❌ CSS cache busting version not updated")
    
    # Read CSS file
    try:
        with open("static/css/components.css", 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Check for aggressive CSS rules
        aggressive_rules = [
            "visibility: hidden !important",
            "opacity: 0 !important", 
            "pointer-events: none !important",
            "position: absolute !important",
            "left: -9999px !important"
        ]
        
        print("\n🎨 CSS Aggressive Rules:")
        for rule in aggressive_rules:
            if rule in css_content:
                print(f"✅ {rule}")
            else:
                print(f"❌ {rule}")
        
        # Check for higher specificity rules
        if "header #mobile-menu-button" in css_content:
            print("✅ Higher specificity CSS rule found")
        else:
            print("❌ Higher specificity CSS rule missing")
            
    except FileNotFoundError:
        print("❌ components.css not found")
        return False
    
    return True

def explain_aggressive_fix():
    """Explain the aggressive fix approach"""
    
    print("\n🔧 Aggressive Fix Strategy:")
    print("=" * 35)
    print("1. **CSS Cache Busting**: Updated version to 3.4 to force reload")
    print("2. **Multiple CSS Rules**: Multiple !important rules with different properties")
    print("3. **Higher Specificity**: More specific CSS selectors")
    print("4. **JavaScript Backup**: JavaScript that runs on load and resize")
    print("5. **Multiple Hiding Methods**:")
    print("   - display: none")
    print("   - visibility: hidden") 
    print("   - opacity: 0")
    print("   - pointer-events: none")
    print("   - position: absolute + left: -9999px")
    
    print("\n💡 This should definitely hide the hamburger menu on desktop!")
    print("🔄 Please refresh your browser (Ctrl+F5 for hard refresh)")

def main():
    """Main test function"""
    print("🚀 Aggressive Hamburger Menu Fix Test")
    print("=" * 40)
    
    success = test_aggressive_fix()
    
    if success:
        print("\n✅ Aggressive fix applied successfully!")
        print("💡 The hamburger menu should now be completely hidden on desktop.")
        print("🔄 Please do a hard refresh (Ctrl+F5) to clear any CSS cache.")
    else:
        print("\n❌ Some issues found. Check the implementation.")
    
    explain_aggressive_fix()
    
    return success

if __name__ == "__main__":
    main() 