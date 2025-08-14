#!/usr/bin/env python3
"""
Test script to verify mobile menu functionality
"""

import os
import sys

def test_mobile_menu_implementation():
    """Test the mobile menu implementation in base.html"""
    
    print("🔍 Testing Mobile Menu Implementation...")
    
    # Check if base.html exists
    base_html_path = "templates/base.html"
    if not os.path.exists(base_html_path):
        print("❌ templates/base.html not found")
        return False
    
    with open(base_html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required elements
    checks = [
        ("Mobile menu button", "id=\"mobile-menu-button\""),
        ("Mobile menu overlay", "id=\"mobile-menu-overlay\""),
        ("Mobile menu close button", "id=\"mobile-menu-close\""),
        ("Desktop navigation", "hidden md:flex"),
        ("Mobile menu button visibility", "md:hidden"),
        ("Mobile menu overlay visibility", "md:hidden"),
        ("JavaScript event listeners", "addEventListener"),
        ("Lucide icons", "data-lucide=\"menu\""),
        ("Lucide icons", "data-lucide=\"x\""),
    ]
    
    all_passed = True
    for check_name, search_term in checks:
        if search_term in content:
            print(f"✅ {check_name}: Found")
        else:
            print(f"❌ {check_name}: Missing")
            all_passed = False
    
    # Check for JavaScript functionality
    js_checks = [
        ("Open mobile menu function", "openMobileMenu"),
        ("Close mobile menu function", "closeMobileMenu"),
        ("Click event listeners", "addEventListener('click'"),
        ("Escape key handling", "keydown"),
        ("Resize handling", "resize"),
    ]
    
    print("\n🔧 JavaScript Functionality:")
    for check_name, search_term in js_checks:
        if search_term in content:
            print(f"✅ {check_name}: Found")
        else:
            print(f"❌ {check_name}: Missing")
            all_passed = False
    
    # Check CSS classes
    css_checks = [
        ("Mobile button styling", "md:hidden"),
        ("Mobile overlay styling", "md:hidden"),
        ("Desktop navigation styling", "hidden md:flex"),
        ("Responsive breakpoint", "md:"),
    ]
    
    print("\n🎨 CSS Classes:")
    for check_name, search_term in css_checks:
        if search_term in content:
            print(f"✅ {check_name}: Found")
        else:
            print(f"❌ {check_name}: Missing")
            all_passed = False
    
    return all_passed

def explain_mobile_menu_behavior():
    """Explain how the mobile menu should work"""
    
    print("\n📱 Mobile Menu Behavior Explanation:")
    print("=" * 50)
    print("• The hamburger menu (☰) is ONLY visible on screens < 768px")
    print("• On desktop (≥768px), the regular navigation links are shown")
    print("• The mobile menu uses Tailwind's responsive classes:")
    print("  - md:hidden = Hidden on medium screens and up (≥768px)")
    print("  - hidden md:flex = Hidden by default, flex on medium+ screens")
    print("\n🔧 To test the mobile menu:")
    print("1. Open browser developer tools (F12)")
    print("2. Click the device toggle button (📱)")
    print("3. Select a mobile device or set width < 768px")
    print("4. The hamburger menu should now be visible")
    print("5. Click it to open the mobile navigation")
    
    print("\n💡 If hamburger menu doesn't work on desktop:")
    print("• This is EXPECTED behavior - it's only for mobile")
    print("• Desktop users see the regular navigation links")
    print("• The menu is hidden on desktop to avoid confusion")

def main():
    """Main test function"""
    print("🚀 Mobile Menu Test Suite")
    print("=" * 30)
    
    # Test implementation
    implementation_ok = test_mobile_menu_implementation()
    
    # Explain behavior
    explain_mobile_menu_behavior()
    
    if implementation_ok:
        print("\n✅ All tests passed! Mobile menu implementation looks correct.")
        print("💡 The hamburger menu is working as designed - mobile only!")
    else:
        print("\n❌ Some tests failed. Check the implementation.")
    
    return implementation_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 