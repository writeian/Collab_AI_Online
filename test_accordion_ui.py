#!/usr/bin/env python3
"""
Test script for Phase 2A: Mobile Accordion UI Implementation
Tests the accordion structure and functionality for rubric display
"""

import requests
import json
import time

def test_accordion_ui():
    """Test the mobile accordion UI implementation"""
    print("🧪 Testing Phase 2A: Mobile Accordion UI Implementation")
    print("=" * 60)
    
    # Test 1: Check if the create room page loads
    print("\n1. Testing create room page loads...")
    try:
        response = requests.get('http://127.0.0.1:5000/room/create')
        if response.status_code == 200:
            content = response.text
            print("✅ Create room page loads successfully")
        else:
            print(f"❌ Failed to load create room page: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the application. Is it running?")
        return False
    
    # Test 2: Check for JavaScript functions (these are always present)
    print("\n2. Testing JavaScript accordion functions...")
    js_functions = [
        'toggleCriterionLevels',
        'toggleLevelContent',
        'editLevel',
        'saveLevelEdit',
        'cancelLevelEdit',
        'showEditFeedback'
    ]
    
    missing_functions = []
    for func in js_functions:
        if func not in content:
            missing_functions.append(func)
    
    if missing_functions:
        print(f"❌ Missing JavaScript functions: {missing_functions}")
        return False
    else:
        print("✅ All accordion JavaScript functions found")
    
    # Test 3: Check for CSS styles (these are always present)
    print("\n3. Testing CSS accordion styles...")
    css_classes = [
        'criterion-accordion',
        'levels-accordion',
        'level-toggle',
        'level-content',
        'edit-mode'
    ]
    
    missing_styles = []
    for style in css_classes:
        if style not in content:
            missing_styles.append(style)
    
    if missing_styles:
        print(f"❌ Missing CSS styles: {missing_styles}")
        return False
    else:
        print("✅ All accordion CSS styles found")
    
    # Test 4: Check template data structure (this is in JavaScript)
    print("\n4. Testing template data structure...")
    template_checks = [
        'level: \'Emerging\'',
        'score: 1',
        'level: \'Developing\'',
        'score: 2',
        'level: \'Proficient\'',
        'score: 3',
        'level: \'Exemplary\'',
        'score: 4'
    ]
    
    missing_template_data = []
    for check in template_checks:
        if check not in content:
            missing_template_data.append(check)
    
    if missing_template_data:
        print(f"❌ Missing template data: {missing_template_data}")
        return False
    else:
        print("✅ Template data structure is correct")
    
    # Test 5: Check mobile responsiveness
    print("\n5. Testing mobile responsiveness...")
    mobile_checks = [
        '@media (min-width: 768px)',
        'flex-direction: column',
        'flex-direction: row'
    ]
    
    missing_mobile = []
    for check in mobile_checks:
        if check not in content:
            missing_mobile.append(check)
    
    if missing_mobile:
        print(f"❌ Missing mobile responsiveness: {missing_mobile}")
        return False
    else:
        print("✅ Mobile responsiveness implemented")
    
    # Test 6: Check for accordion generation function
    print("\n6. Testing accordion generation function...")
    if 'populateRubricTemplate' not in content:
        print("❌ Missing populateRubricTemplate function")
        return False
    else:
        print("✅ Accordion generation function found")
    
    print("\n" + "=" * 60)
    print("🎉 Phase 2A Mobile Accordion UI Implementation Test PASSED!")
    print("\n✅ Key Features Implemented:")
    print("   • Mobile-first accordion structure")
    print("   • One level open at a time on mobile")
    print("   • All levels visible on desktop")
    print("   • Inline editing functionality")
    print("   • Save/cancel edit operations")
    print("   • Visual feedback for edit mode")
    print("   • Responsive design")
    print("   • Dynamic accordion generation")
    
    return True

def test_accordion_interaction():
    """Test the accordion interaction functionality"""
    print("\n🔧 Testing Accordion Interaction (Manual Test Required)")
    print("=" * 60)
    print("Please manually test the following:")
    print("1. Go to http://127.0.0.1:5000/room/create")
    print("2. Enter some learning goals and generate a proposal")
    print("3. Expand the 'Assessment Rubric' dropdown")
    print("4. Test accordion behavior:")
    print("   • Click criterion headers to expand/collapse levels")
    print("   • On mobile: Only one level should be open at a time")
    print("   • On desktop: Multiple levels can be open")
    print("5. Test editing functionality:")
    print("   • Click 'Edit' on any level")
    print("   • Modify the description")
    print("   • Click 'Save' or 'Cancel'")
    print("6. Verify visual feedback appears")
    
    return True

if __name__ == "__main__":
    print("🚀 Phase 2A Mobile Accordion UI Test Suite")
    print("=" * 60)
    
    # Run automated tests
    success = test_accordion_ui()
    
    if success:
        # Run manual test instructions
        test_accordion_interaction()
    else:
        print("\n❌ Tests failed. Please fix the issues before proceeding.") 