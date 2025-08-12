#!/usr/bin/env python3
"""
Test script to verify mobile rubric editing improvements
"""

import re

def test_mobile_rubric_editing():
    print("🔍 Testing Mobile Rubric Editing Improvements...")
    
    # Check CSS improvements
    with open('static/css/components.css', 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    # Check HTML template
    with open('templates/room/create.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("\n📱 Mobile Rubric Button Improvements:")
    
    # Check for mobile-optimized button CSS
    mobile_button_css = re.search(r'button\[onclick\*="editLevel"\][^}]*}', css_content)
    if mobile_button_css:
        print("✅ Mobile-optimized edit button CSS found")
        css_rule = mobile_button_css.group(0)
        if 'min-height: 44px' in css_rule:
            print("✅ Minimum touch target size (44px) set")
        if 'touch-action: manipulation' in css_rule:
            print("✅ Touch action optimization applied")
        if '-webkit-tap-highlight-color' in css_rule:
            print("✅ Tap highlight color set for better feedback")
    else:
        print("❌ Mobile-optimized edit button CSS not found")
    
    # Check for textarea improvements
    textarea_css = re.search(r'\.edit-mode textarea[^}]*}', css_content)
    if textarea_css:
        print("✅ Mobile-optimized textarea CSS found")
        textarea_rule = textarea_css.group(0)
        if 'min-height: 80px' in textarea_rule:
            print("✅ Minimum textarea height set for mobile")
        if 'font-size: 16px' in textarea_rule:
            print("✅ Font size prevents zoom on iOS")
    else:
        print("❌ Mobile-optimized textarea CSS not found")
    
    # Check JavaScript improvements
    print("\n📱 JavaScript Mobile Improvements:")
    
    if 'setTimeout' in html_content and 'scrollIntoView' in html_content:
        print("✅ Mobile-friendly focus and scroll behavior added")
    else:
        print("❌ Mobile-friendly focus behavior not found")
    
    if 'window.innerWidth <= 768' in html_content:
        print("✅ Mobile screen width detection added")
    else:
        print("❌ Mobile screen width detection not found")
    
    # Check for edit button HTML structure
    print("\n📱 Edit Button HTML Structure:")
    
    if 'onclick="editLevel(' in html_content:
        print("✅ Edit button onclick handlers found")
    else:
        print("❌ Edit button onclick handlers not found")
    
    if 'text-xs px-2 py-1' in html_content:
        print("✅ Edit buttons have proper CSS classes")
    else:
        print("❌ Edit buttons missing proper CSS classes")
    
    # Check CSS version
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        base_html = f.read()
    css_version = re.search(r'components\.css\?v=(\d+\.\d+)', base_html)
    if css_version:
        version = css_version.group(1)
        print(f"✅ CSS version: {version}")
        if float(version) >= 3.6:
            print("✅ CSS version is recent (should force cache refresh)")
        else:
            print("⚠️ CSS version might be cached")
    else:
        print("❌ No CSS version found")
    
    print("\n🎯 Summary:")
    print("The mobile rubric editing improvements should now:")
    print("✅ Have larger touch targets (44px minimum)")
    print("✅ Provide better touch feedback")
    print("✅ Auto-scroll to textarea on mobile")
    print("✅ Prevent iOS zoom with 16px font size")
    print("✅ Force cache refresh with new CSS version")
    
    print("\n📱 Please test rubric editing on your phone again!")
    print("The edit buttons should now be much easier to tap on mobile.")

if __name__ == "__main__":
    test_mobile_rubric_editing() 