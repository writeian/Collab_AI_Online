#!/usr/bin/env python3
"""Comprehensive test script to verify all environment variables are loaded correctly."""

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_env_variable(name, required=True, show_value=False):
    """Test if an environment variable is set."""
    value = os.getenv(name)
    status = "✅ Set" if value else "❌ Not set"
    print(f"{name}: {status}")
    
    if value and show_value:
        if "KEY" in name or "SECRET" in name or "TOKEN" in name:
            print(f"  Value starts with: {value[:10]}...")
        else:
            print(f"  Value: {value}")
    
    if required and not value:
        print(f"  ⚠️  Required variable '{name}' is missing!")
        return False
    return True

def test_ai_services():
    """Test AI service configuration."""
    print("\n🤖 AI Services Configuration:")
    print("-" * 40)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_key and not anthropic_key:
        print("❌ No AI service configured!")
        print("   Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY")
        return False
    elif openai_key and anthropic_key:
        print("✅ Both OpenAI and Anthropic configured")
        print("   Will use Anthropic as default (cheaper)")
    elif anthropic_key:
        print("✅ Anthropic Claude configured")
    elif openai_key:
        print("✅ OpenAI configured")
    
    return True

def test_google_services():
    """Test Google services configuration."""
    print("\n📄 Google Services Configuration:")
    print("-" * 40)
    
    # Test service account file
    service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'service-account-key.json')
    test_env_variable("GOOGLE_SERVICE_ACCOUNT_FILE", required=False)
    
    # Check if service account file exists
    if os.path.exists(service_account_file):
        print(f"✅ Service account file found: {service_account_file}")
    else:
        print(f"⚠️  Service account file not found: {service_account_file}")
        print("   Google Docs import will not work without this file")
    
    # Test OAuth configuration
    print("\nOAuth Configuration (for user Google Docs access):")
    test_env_variable("GOOGLE_CLIENT_ID", required=False)
    test_env_variable("GOOGLE_CLIENT_SECRET", required=False)
    test_env_variable("GOOGLE_REDIRECT_URI", required=False)
    
    return True

def main():
    """Run all environment tests."""
    print("🔧 AI Collab Environment Configuration Test")
    print("=" * 50)
    
    # Test basic configuration
    print("\n🔑 Basic Configuration:")
    print("-" * 30)
    test_env_variable("SECRET_KEY", required=True, show_value=False)
    
    # Test AI services
    ai_configured = test_ai_services()
    
    # Test Google services
    google_configured = test_google_services()
    
    # Summary
    print("\n📋 Configuration Summary:")
    print("-" * 30)
    
    if ai_configured:
        print("✅ AI services are configured")
    else:
        print("❌ AI services need configuration")
    
    if google_configured:
        print("✅ Google services are configured")
    else:
        print("⚠️  Google services are optional")
    
    print("\n🚀 Ready to run the application!")
    print("   Run: python app.py")

if __name__ == "__main__":
    main() 