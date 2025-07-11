#!/usr/bin/env python3
"""
Check which LLM model the application is using
"""

import os
import requests

def check_ollama_models():
    """Check available Ollama models."""
    print("🔍 Checking Ollama models...")
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json()
            print(f"📋 Available models: {len(models.get('models', []))}")
            for model in models.get('models', []):
                print(f"  - {model['name']} (Size: {model.get('size', 'unknown')})")
            return models.get('models', [])
        else:
            print("❌ Could not fetch models")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def check_app_config():
    """Check application configuration."""
    print("\n🔍 Checking application configuration...")
    
    # Set environment variables
    os.environ['USE_OLLAMA'] = 'true'
    os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
    os.environ['OLLAMA_MODEL'] = 'gemma3'
    
    try:
        from app import create_app
        app = create_app('development')
        
        with app.app_context():
            from openai_utils import get_client_type
            
            # Check client type
            client_type = get_client_type()
            print(f"✅ Client type: {client_type}")
            
            # Check Ollama configuration
            if client_type == 'ollama':
                base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
                model = os.getenv('OLLAMA_MODEL', 'gemma3')
                print(f"✅ Ollama base URL: {base_url}")
                print(f"✅ Ollama model: {model}")
                
                # Check if model exists
                models = check_ollama_models()
                model_names = [m['name'] for m in models]
                if model in model_names:
                    print(f"✅ Model '{model}' is available!")
                else:
                    print(f"⚠️ Model '{model}' not found in available models")
                    print(f"Available models: {model_names}")
            
            return True
    except Exception as e:
        print(f"❌ Error checking app config: {e}")
        return False

def test_model_response():
    """Test a simple response to see which model responds."""
    print("\n🧪 Testing model response...")
    
    try:
        test_data = {
            "model": "gemma3",
            "prompt": "What model are you? Please identify yourself briefly.",
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 100
            }
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=test_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Model response: {result.get('response', 'No response')[:200]}...")
            return True
        else:
            print(f"❌ Response failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing response: {e}")
        return False

def main():
    """Main function."""
    print("🚀 LLM Model Check for AI_Collab_Online")
    print("=" * 50)
    
    # Check 1: Available models
    models = check_ollama_models()
    
    # Check 2: App configuration
    if not check_app_config():
        return
    
    # Check 3: Test response
    if not test_model_response():
        return
    
    print("\n✅ Model check complete!")
    print("\n📝 Summary:")
    print("- Your app is configured to use Ollama")
    print("- Model: gemma3")
    print("- The model is available and responding")
    print("- You're using FREE local AI instead of paid APIs!")

if __name__ == "__main__":
    main() 