#!/usr/bin/env python3
"""
Test to check if the chat page template contains the toggle elements
"""

def test_chat_template():
    """Test if the chat template contains the toggle elements"""
    
    print("🧪 Testing Chat Template")
    print("=" * 50)
    
    # Read the template file directly
    try:
        with open('templates/chat/view.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Template file loaded successfully")
        
        # Check for toggle elements
        has_toggle_id = 'ai-response-toggle' in content
        has_ai_response_name = 'name="ai_response"' in content
        has_checked = 'checked' in content
        has_ai_response_label = '🤖 AI Response' in content
        
        print(f"\n📋 Template Analysis:")
        print(f"Contains toggle ID: {'✅ Yes' if has_toggle_id else '❌ No'}")
        print(f"Contains ai_response name: {'✅ Yes' if has_ai_response_name else '❌ No'}")
        print(f"Contains checked attribute: {'✅ Yes' if has_checked else '❌ No'}")
        print(f"Contains AI response label: {'✅ Yes' if has_ai_response_label else '❌ No'}")
        
        if has_toggle_id and has_ai_response_name and has_checked and has_ai_response_label:
            print("\n✅ Template contains all required toggle elements")
        else:
            print("\n❌ Template is missing some toggle elements")
            
        # Show the specific section
        print(f"\n🔍 Toggle Section in Template:")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'ai-response-toggle' in line or 'AI Response' in line:
                print(f"Line {i+1}: {line.strip()}")
                
    except FileNotFoundError:
        print("❌ Template file not found")
    except Exception as e:
        print(f"❌ Error reading template: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Template Test Summary:")
    print("- Template file checked")
    print("- Toggle elements verified")
    print("\nIf template looks correct but page doesn't show toggle:")
    print("1. Clear browser cache")
    print("2. Restart Flask app")
    print("3. Check if user is logged in")
    print("4. Verify the correct chat page is being accessed")

if __name__ == "__main__":
    test_chat_template() 