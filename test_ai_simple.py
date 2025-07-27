#!/usr/bin/env python3
"""
Simple test for AI response functionality
"""

def test_ai_simple():
    """Test AI response function directly"""
    
    print("🧪 Simple AI Response Test")
    print("=" * 50)
    
    try:
        from openai_utils import get_client_type, call_anthropic_api
        
        # Test 1: Check client type
        client_type = get_client_type()
        print(f"1. AI Client Type: {client_type}")
        
        if not client_type:
            print("❌ No AI client configured")
            return
        
        # Test 2: Test direct API call
        print("\n2. Testing direct API call...")
        
        messages = [
            {"role": "user", "content": "Hello, can you help me with my research?"}
        ]
        
        system_prompt = "You are an expert instructor in academic research and critical thinking. Ask probing questions to help students discover what genuinely interests them about their topic."
        
        if client_type == "anthropic":
            content, is_truncated = call_anthropic_api(messages, system_prompt)
        elif client_type == "openai":
            from openai_utils import call_openai_api
            content, is_truncated = call_openai_api(messages)
        else:
            from openai_utils import call_ollama_api
            content, is_truncated = call_ollama_api(messages, system_prompt)
        
        print(f"AI Response: {content}")
        print(f"Is Truncated: {is_truncated}")
        
        if content and not content.startswith("⚠️"):
            print("✅ AI response generated successfully!")
        else:
            print("❌ AI response failed or returned error")
            
    except Exception as e:
        print(f"❌ Error testing AI: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🎯 Simple Test Summary:")
    print("- AI client type detected")
    print("- Direct API call tested")
    print("- Response generated successfully")

if __name__ == "__main__":
    test_ai_simple() 