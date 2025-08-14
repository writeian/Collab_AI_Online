#!/usr/bin/env python3
"""
Test script for Ollama integration with AI_Collab_Online
"""

import os
import requests
import time

def test_ollama_connection():
    """Test basic Ollama connection."""
    print("🧪 Testing Ollama connection...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Ollama is running! Found {len(models.get('models', []))} models")
            return True
        else:
            print("❌ Ollama is not responding properly")
            return False
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False

def test_ollama_generation():
    """Test Ollama text generation."""
    print("\n🧪 Testing Ollama text generation...")
    
    # Simple test prompt
    test_data = {
        "model": "gemma3",
        "prompt": "Hello! Can you help me with writing?",
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": 100
        }
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=test_data,
            timeout=60
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generation successful! Time: {end_time - start_time:.2f}s")
            print(f"📝 Response: {result.get('response', 'No response')[:200]}...")
            return True
        else:
            print(f"❌ Generation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Generation error: {e}")
        return False

def test_flask_integration():
    """Test Flask app with Ollama integration."""
    print("\n🧪 Testing Flask app with Ollama...")
    
    try:
        # Set environment variable to use Ollama
        os.environ['USE_OLLAMA'] = 'true'
        os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
        os.environ['OLLAMA_MODEL'] = 'gemma3'
        
        # Import and create app
        from app import create_app
        app = create_app('development')
        
        with app.app_context():
            from openai_utils import get_client_type, call_ollama_api
            
            # Test client type detection
            client_type = get_client_type()
            print(f"✅ Client type detected: {client_type}")
            
            # Test Ollama API call
            test_messages = [{"role": "user", "content": "Hello! Can you help me with writing?"}]
            response = call_ollama_api(test_messages, "You are a helpful writing assistant.", 100)
            print(f"✅ Flask integration test successful!")
            print(f"📝 Response: {response[:200]}...")
            
        return True
    except Exception as e:
        print(f"❌ Flask integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Ollama Integration Test for AI_Collab_Online")
    print("=" * 50)
    
    # Test 1: Basic connection
    if not test_ollama_connection():
        print("\n❌ Ollama connection failed. Please make sure Ollama is running.")
        return
    
    # Test 2: Text generation
    if not test_ollama_generation():
        print("\n❌ Ollama generation failed. The model might still be downloading.")
        print("💡 Wait a few minutes for the model to finish downloading, then try again.")
        return
    
    # Test 3: Flask integration
    if not test_flask_integration():
        print("\n❌ Flask integration failed.")
        return
    
    print("\n🎉 All tests passed! Ollama integration is working correctly.")
    print("\n📝 Next steps:")
    print("1. Start the Flask application: python app.py")
    print("2. Open http://localhost:5000 in your browser")
    print("3. Create a chat and test the AI responses")
    print("4. The AI will now use your local Ollama model instead of paid APIs!")

if __name__ == "__main__":
    main() 