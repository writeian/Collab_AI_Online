#!/usr/bin/env python3
"""
Debug script to check environment variables
"""

import os

def debug_env():
    """Debug environment variables"""
    
    print("🔍 Debugging Environment Variables")
    print("=" * 50)
    
    # Check if dotenv is available
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv is available")
        
        # Load .env file
        load_dotenv()
        print("✅ .env file loaded")
        
    except ImportError:
        print("❌ python-dotenv not available")
        return
    except Exception as e:
        print(f"❌ Error loading .env: {e}")
        return
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
    
    print(f"ANTHROPIC_API_KEY: {'✅ Set' if anthropic_key else '❌ Not set'}")
    if anthropic_key:
        print(f"  Length: {len(anthropic_key)} characters")
        print(f"  Starts with: {anthropic_key[:10]}...")
    
    print(f"OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Not set'}")
    if openai_key:
        print(f"  Length: {len(openai_key)} characters")
        print(f"  Starts with: {openai_key[:10]}...")
    
    print(f"USE_OLLAMA: {'✅ True' if use_ollama else '❌ False'}")
    
    # Test get_client_type function
    print("\n🤖 Testing get_client_type function...")
    try:
        from openai_utils import get_client_type
        client_type = get_client_type()
        print(f"get_client_type() returned: {client_type}")
        
        if client_type:
            print("✅ AI client type detected")
        else:
            print("❌ No AI client type detected")
            
    except Exception as e:
        print(f"❌ Error in get_client_type: {e}")
        import traceback
        traceback.print_exc()
    
    # Check if .env file exists
    print("\n📁 Checking for .env file...")
    env_files = [f for f in os.listdir('.') if f.endswith('.env')]
    print(f"Found .env files: {env_files}")
    
    if '.env' in env_files:
        try:
            with open('.env', 'r') as f:
                content = f.read()
                lines = content.split('\n')
                print(f"📄 .env file has {len(lines)} lines")
                
                # Check for API keys in .env content
                has_anthropic = any('ANTHROPIC_API_KEY' in line for line in lines)
                has_openai = any('OPENAI_API_KEY' in line for line in lines)
                
                print(f"Contains ANTHROPIC_API_KEY: {'✅ Yes' if has_anthropic else '❌ No'}")
                print(f"Contains OPENAI_API_KEY: {'✅ Yes' if has_openai else '❌ No'}")
                
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
    else:
        print("❌ No .env file found in current directory")

if __name__ == "__main__":
    debug_env() 