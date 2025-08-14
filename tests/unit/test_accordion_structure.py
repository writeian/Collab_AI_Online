#!/usr/bin/env python3
"""
Test script to verify accordion structure
"""

import re

def test_accordion_structure():
    print("🔍 Testing Accordion Structure...")
    
    with open('templates/room/create.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("\n📱 Accordion Structure Analysis:")
    
    # Check if levels-accordion is hidden by default
    if 'levels-accordion hidden' in html_content:
        print("❌ Levels accordion is hidden by default (this might be the issue)")
    elif 'levels-accordion' in html_content:
        print("✅ Levels accordion is visible by default")
    else:
        print("❌ No levels-accordion found")
    
    # Check for toggle functions
    if 'toggleCriterionLevels' in html_content:
        print("✅ toggleCriterionLevels function found")
    else:
        print("❌ toggleCriterionLevels function not found")
    
    if 'toggleLevelContent' in html_content:
        print("✅ toggleLevelContent function found")
    else:
        print("❌ toggleLevelContent function not found")
    
    # Check for onclick handlers
    criterion_buttons = re.findall(r'onclick="toggleCriterionLevels\([^"]*\)"', html_content)
    if criterion_buttons:
        print(f"✅ Found {len(criterion_buttons)} criterion toggle buttons")
    else:
        print("❌ No criterion toggle buttons found")
    
    level_buttons = re.findall(r'onclick="toggleLevelContent\([^"]*\)"', html_content)
    if level_buttons:
        print(f"✅ Found {len(level_buttons)} level toggle buttons")
    else:
        print("❌ No level toggle buttons found")
    
    # Check for data attributes
    if 'data-mode=' in html_content:
        print("✅ Data attributes added for debugging")
    else:
        print("❌ Data attributes not found")
    
    # Check CSS version
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        base_html = f.read()
    css_version = re.search(r'components\.css\?v=(\d+\.\d+)', base_html)
    if css_version:
        version = css_version.group(1)
        print(f"✅ CSS version: {version}")
    else:
        print("❌ No CSS version found")
    
    print("\n🎯 Summary:")
    print("The accordion should now:")
    print("✅ Show levels accordion by default (not hidden)")
    print("✅ Have proper toggle functions with event handling")
    print("✅ Include data attributes for debugging")
    print("✅ Force cache refresh with new CSS version")
    
    print("\n📱 Please test the accordion functionality again!")
    print("The main categories should be visible and the sub-categories should be toggleable.")

if __name__ == "__main__":
    test_accordion_structure() 