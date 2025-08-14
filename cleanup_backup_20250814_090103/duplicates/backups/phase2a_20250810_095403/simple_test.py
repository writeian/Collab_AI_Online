#!/usr/bin/env python3
"""
Simple test to check if the create room page loads correctly
"""

import requests

def simple_test():
    print("🔍 Simple Test: Checking if create room page loads...")
    
    try:
        response = requests.get('http://127.0.0.1:5000/room/create')
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            print(f"Content length: {len(content)} characters")
            
            # Check for basic elements
            checks = [
                ('Create New Room', 'Page title'),
                ('Generate Room Proposal', 'Generate button'),
                ('Assessment Rubric', 'Rubric section'),
                ('populateRubricTemplate', 'Template function'),
                ('toggleCriterionLevels', 'Accordion function'),
                ('criterion-accordion', 'CSS class')
            ]
            
            for text, description in checks:
                if text in content:
                    print(f"✅ Found: {description}")
                else:
                    print(f"❌ Missing: {description}")
            
            # Check for any obvious errors
            if 'error' in content.lower() or 'exception' in content.lower():
                print("⚠️  Possible error found in content")
            
            return True
        else:
            print(f"❌ Failed to load page: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    simple_test() 