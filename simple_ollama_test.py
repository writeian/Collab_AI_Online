#!/usr/bin/env python3
"""
Simple Ollama integration test
"""

import requests
import os

def test_ollama_basic():
    """Test basic Ollama functionality."""
    print("🧪 Testing Ollama basic functionality...")
    
    # Test 1: Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        print(f"✅ Ollama is running (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False
    
    # Test 2: Check available models
    try:
        response = requests.get("http://localhost:11434/api/tags")
        models = response.json()
        model_count = len(models.get('models', []))
        print(f"📋 Found {model_count} models")
        
        if model_count == 0:
            print("💡 No models available yet. This is normal for a fresh installation.")
            print("📥 You can download a model with: ollama pull gemma3")
            return True
        else:
            for model in models.get('models', []):
                print(f"  - {model['name']} ({model.get('size', 'unknown size')})")
            return True
            
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False

def test_flask_config():
    """Test Flask configuration with Ollama."""
    print("\n🧪 Testing Flask configuration...")
    
    try:
        # Set environment variables
        os.environ['USE_OLLAMA'] = 'true'
        os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
        os.environ['OLLAMA_MODEL'] = 'gemma3'
        
        # Import and test app creation
        from app import create_app
        app = create_app('development')
        
        with app.app_context():
            from openai_utils import get_client_type
            client_type = get_client_type()
            print(f"✅ Flask app created successfully")
            print(f"✅ Client type detected: {client_type}")
            
        return True
    except Exception as e:
        print(f"❌ Flask configuration test failed: {e}")
        return False

def main():
    """Run tests."""
    print("🚀 Simple Ollama Integration Test")
    print("=" * 40)
    
    # Test 1: Basic Ollama functionality
    if not test_ollama_basic():
        print("\n❌ Basic Ollama test failed")
        return
    
    # Test 2: Flask configuration
    if not test_flask_config():
        print("\n❌ Flask configuration test failed")
        return
    
    print("\n✅ All basic tests passed!")
    print("\n📝 Next steps:")
    print("1. Download a model: ollama pull gemma3")
    print("2. Start the Flask app: python app.py")
    print("3. Test the AI functionality in your browser")
    print("4. The app will use local Ollama instead of paid APIs!")

if __name__ == "__main__":
    main() 