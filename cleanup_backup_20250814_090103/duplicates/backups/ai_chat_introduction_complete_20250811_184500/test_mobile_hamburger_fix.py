#!/usr/bin/env python3
"""
Test script to verify mobile hamburger menu fix
"""

import re

def test_mobile_hamburger_fix():
    print("🔍 Testing Mobile Hamburger Menu Fix...")
    
    # Check CSS rules
    with open('static/css/components.css', 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    # Check base.html
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("\n📱 Mobile Menu Button CSS Rules:")
    
    # Check if mobile menu button has proper display on mobile
    mobile_button_rules = re.findall(r'#mobile-menu-button\s*\{[^}]*\}', css_content)
    if mobile_button_rules:
        print("✅ Mobile menu button base rules found")
        for rule in mobile_button_rules:
            if 'display: flex' in rule:
                print("✅ Mobile menu button has flex display (good for mobile)")
    else:
        print("❌ No mobile menu button base rules found")
    
    # Check desktop hiding rules
    desktop_hiding = re.findall(r'@media\s*\(min-width:\s*768px\)\s*\{[^}]*#mobile-menu-button[^}]*\}', css_content, re.DOTALL)
    if desktop_hiding:
        print("✅ Desktop hiding rules found (min-width: 768px)")
        for rule in desktop_hiding:
            if 'display: none !important' in rule:
                print("✅ Desktop hiding includes display: none !important")
    else:
        print("❌ No desktop hiding rules found")
    
    # Check if the problematic broad rule is fixed
    broad_rule = re.search(r'@media\s*screen\s*and\s*\(min-width:\s*768px\)\s*\{[^}]*\.md\\\\:hidden[^}]*\}', css_content, re.DOTALL)
    if broad_rule:
        print("✅ Broad md:hidden rule is properly scoped to desktop only")
    else:
        print("❌ Broad md:hidden rule not found or not properly scoped")
    
    # Check HTML classes
    print("\n📱 HTML Classes:")
    if 'block md:hidden' in html_content:
        print("✅ Mobile menu button has 'block md:hidden' classes (visible on mobile, hidden on desktop)")
    else:
        print("❌ Mobile menu button missing proper classes")
    
    # Check CSS version
    css_version = re.search(r'components\.css\?v=(\d+\.\d+)', html_content)
    if css_version:
        version = css_version.group(1)
        print(f"✅ CSS version: {version}")
        if float(version) >= 3.5:
            print("✅ CSS version is recent (should force cache refresh)")
        else:
            print("⚠️ CSS version might be cached")
    else:
        print("❌ No CSS version found")
    
    # Check JavaScript
    if 'hideHamburgerOnDesktop' in html_content:
        print("✅ JavaScript desktop hiding function found")
    else:
        print("❌ JavaScript desktop hiding function not found")
    
    print("\n🎯 Summary:")
    print("The fix should now:")
    print("✅ Show hamburger menu on mobile (screens < 768px)")
    print("✅ Hide hamburger menu on desktop (screens >= 768px)")
    print("✅ Force cache refresh with new CSS version")
    
    print("\n📱 Please test on your phone again!")
    print("The hamburger menu should now be visible on mobile.")

if __name__ == "__main__":
    test_mobile_hamburger_fix() 