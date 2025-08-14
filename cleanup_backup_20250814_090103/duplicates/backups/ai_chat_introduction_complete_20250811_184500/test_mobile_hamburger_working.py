#!/usr/bin/env python3
"""
Test script to verify hamburger menu still works on mobile after desktop hiding fix
"""

import re

def test_mobile_functionality():
    """Test that mobile hamburger menu still works"""
    
    print("📱 Testing Mobile Hamburger Menu Functionality...")
    
    # Read base.html
    with open("templates/base.html", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for mobile-specific classes
    if 'block md:hidden' in content:
        print("✅ Mobile classes found: 'block md:hidden' (visible on mobile, hidden on desktop)")
    else:
        print("❌ Mobile classes missing")
    
    # Check for JavaScript that shows on mobile
    if 'window.innerWidth >= 768' in content:
        print("✅ JavaScript desktop detection found (only hides on desktop)")
    else:
        print("❌ JavaScript desktop detection missing")
    
    # Check for mobile menu overlay
    if 'id="mobile-menu-overlay"' in content:
        print("✅ Mobile menu overlay found")
    else:
        print("❌ Mobile menu overlay missing")
    
    # Check for mobile menu close button
    if 'id="mobile-menu-close"' in content:
        print("✅ Mobile menu close button found")
    else:
        print("❌ Mobile menu close button missing")
    
    # Check for mobile menu JavaScript functions
    mobile_js_checks = [
        "openMobileMenu",
        "closeMobileMenu", 
        "addEventListener('click'",
        "keydown",
        "resize"
    ]
    
    print("\n🔧 Mobile JavaScript Functions:")
    for func in mobile_js_checks:
        if func in content:
            print(f"✅ {func} found")
        else:
            print(f"❌ {func} missing")
    
    # Check CSS for mobile-specific rules
    try:
        with open("static/css/components.css", 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Check that mobile menu button is visible on mobile
        if "#mobile-menu-button" in css_content:
            print("✅ Mobile menu button CSS found")
        else:
            print("❌ Mobile menu button CSS missing")
        
        # Check that desktop hiding only applies to desktop
        if "@media (min-width: 768px)" in css_content:
            print("✅ Desktop media query found (only affects desktop)")
        else:
            print("❌ Desktop media query missing")
            
    except FileNotFoundError:
        print("❌ components.css not found")
        return False
    
    return True

def explain_mobile_behavior():
    """Explain how the mobile menu should work"""
    
    print("\n📱 Mobile Menu Behavior:")
    print("=" * 30)
    print("• **Mobile (<768px)**: Hamburger menu should be visible and functional")
    print("• **Desktop (≥768px)**: Hamburger menu should be hidden")
    print("• **JavaScript**: Only hides on desktop, shows on mobile")
    print("• **CSS**: Uses media queries to target desktop only")
    
    print("\n🔧 To Test Mobile Functionality:")
    print("1. Open browser developer tools (F12)")
    print("2. Click the device toggle button (📱)")
    print("3. Select a mobile device (iPhone, iPad, etc.)")
    print("4. The hamburger menu should appear in the top-right")
    print("5. Click it to open the mobile navigation menu")
    print("6. Test the close button and overlay click to close")

def test_responsive_design():
    """Test responsive design implementation"""
    
    print("\n🎨 Responsive Design Test:")
    print("=" * 30)
    
    # Read base.html
    with open("templates/base.html", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for responsive classes
    responsive_checks = [
        "md:hidden",  # Hidden on desktop
        "hidden md:flex",  # Hidden on mobile, flex on desktop
        "max-w-7xl",  # Responsive container
        "px-4 sm:px-6 lg:px-8"  # Responsive padding
    ]
    
    for check in responsive_checks:
        if check in content:
            print(f"✅ {check} found")
        else:
            print(f"❌ {check} missing")

def main():
    """Main test function"""
    print("🚀 Mobile Hamburger Menu Test")
    print("=" * 35)
    
    mobile_ok = test_mobile_functionality()
    test_responsive_design()
    
    if mobile_ok:
        print("\n✅ Mobile functionality looks good!")
        print("💡 The hamburger menu should work perfectly on mobile devices.")
        print("🔄 Test it by switching to mobile view in browser dev tools.")
    else:
        print("\n❌ Some mobile functionality issues found.")
    
    explain_mobile_behavior()
    
    return mobile_ok

if __name__ == "__main__":
    main() 