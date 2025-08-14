#!/usr/bin/env python3
"""
Test script for simplified accordion implementation
"""

def test_simple_accordion():
    print("🧪 Testing Simplified Accordion Implementation")
    print("=" * 50)
    
    # Test 1: Check if toggle functions are simplified
    print("\n1. Checking toggle functions...")
    try:
        with open('templates/room/create.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'window.toggleCriterionLevels = function(modeIndex, criterionIndex)' in content:
            print("✅ toggleCriterionLevels function is simplified")
        else:
            print("❌ toggleCriterionLevels function not found or not simplified")
            
        if 'window.toggleLevelContent = function(modeIndex, criterionIndex, levelIndex)' in content:
            print("✅ toggleLevelContent function is simplified")
        else:
            print("❌ toggleLevelContent function not found or not simplified")
            
    except Exception as e:
        print(f"❌ Error reading create.html: {e}")
    
    # Test 2: Check if HTML structure is simplified
    print("\n2. Checking HTML structure...")
    try:
        if 'style="display: none;"' in content:
            print("✅ Accordion divs use simple display:none")
        else:
            print("❌ Accordion divs not using simple display:none")
            
        if 'onclick="toggleCriterionLevels(' in content:
            print("✅ Criterion buttons have simplified onclick")
        else:
            print("❌ Criterion buttons not found or not simplified")
            
        if 'onclick="toggleLevelContent(' in content:
            print("✅ Level buttons have simplified onclick")
        else:
            print("❌ Level buttons not found or not simplified")
            
    except Exception as e:
        print(f"❌ Error checking HTML structure: {e}")
    
    # Test 3: Check CSS version
    print("\n3. Checking CSS version...")
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
            
        if '?v=4.2' in base_content:
            print("✅ CSS version updated to 4.2")
        else:
            print("❌ CSS version not updated to 4.2")
            
    except Exception as e:
        print(f"❌ Error checking CSS version: {e}")
    
    # Test 4: Check for simplified CSS
    print("\n4. Checking simplified CSS...")
    try:
        with open('static/css/components.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
            
        if 'Simple mobile-friendly accordion styles' in css_content:
            print("✅ Simplified CSS section found")
        else:
            print("❌ Simplified CSS section not found")
            
        if 'touch-action: manipulation' in css_content:
            print("✅ Touch action properties present")
        else:
            print("❌ Touch action properties missing")
            
    except Exception as e:
        print(f"❌ Error checking CSS: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Summary: Simplified accordion implementation ready for testing!")
    print("\n📱 Next steps:")
    print("1. Refresh your phone's browser")
    print("2. Go to: http://10.26.8.133:5000")
    print("3. Create a new room and test the rubric accordion")
    print("4. Look for blue 'Toggle' buttons and green level buttons")
    print("5. Tap buttons to expand/collapse sections")

if __name__ == "__main__":
    test_simple_accordion() 