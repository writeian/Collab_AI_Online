#!/usr/bin/env python3
"""
Test script to verify environment variable loading from .env file
"""

import os

def test_env_loading():
    """Test if environment variables are loaded from .env file"""
    
    print("🧪 Testing Environment Variable Loading")
    print("=" * 50)
    
    # Try to load dotenv
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ python-dotenv loaded successfully")
    except ImportError:
        print("❌ python-dotenv not installed")
        return
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")
        return
    
    # Check for AI API keys
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
    
    print(f"\n📋 Environment Variables:")
    print(f"ANTHROPIC_API_KEY: {'✅ Set' if anthropic_key else '❌ Not set'}")
    print(f"OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Not set'}")
    print(f"USE_OLLAMA: {'✅ True' if use_ollama else '❌ False'}")
    
    # Test AI client type detection
    try:
        from openai_utils import get_client_type
        client_type = get_client_type()
        print(f"\n🤖 AI Client Type: {client_type}")
        
        if client_type:
            print("✅ AI service configured and ready")
        else:
            print("❌ No AI service configured")
            
    except Exception as e:
        print(f"❌ Error testing AI client: {e}")
    
    # Test Flask app environment loading
    try:
        from app import create_app
        app = create_app()
        print("\n✅ Flask app created successfully")
        
        # Test if the app can access environment variables
        with app.app_context():
            print("✅ Flask app context works")
            
    except Exception as e:
        print(f"❌ Error creating Flask app: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Environment Test Summary:")
    
    if anthropic_key or openai_key or use_ollama:
        print("✅ Environment variables are loaded")
        print("✅ AI service should be available")
        print("✅ The toggle feature should work with AI responses")
    else:
        print("❌ No AI API keys found")
        print("❌ AI responses will not work")
        print("❌ Check your .env file configuration")
    
    print("\nTo fix AI response issues:")
    print("1. Ensure your .env file contains ANTHROPIC_API_KEY or OPENAI_API_KEY")
    print("2. Restart the Flask application")
    print("3. Test the chat functionality again")

if __name__ == "__main__":
    test_env_loading() 