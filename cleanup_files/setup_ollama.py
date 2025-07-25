#!/usr/bin/env python3
"""
Ollama setup and testing script for AI_Collab_Online
"""

import requests
import json
import time
import os

def check_ollama_installation():
    """Check if Ollama is installed and running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running!")
            return True
        else:
            print("❌ Ollama is not responding properly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Ollama is not running or not installed")
        print("\n📥 To install Ollama on Windows:")
        print("1. Go to https://ollama.ai/download")
        print("2. Download the Windows installer")
        print("3. Run the installer")
        print("4. Start Ollama from the Start menu")
        return False

def list_available_models():
    """List available models in Ollama."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json()
            print("\n📋 Available models:")
            for model in models.get('models', []):
                print(f"  - {model['name']} ({model['size']})")
            return models.get('models', [])
        else:
            print("❌ Could not fetch models")
            return []
    except Exception as e:
        print(f"❌ Error fetching models: {e}")
        return []

def pull_model(model_name="llama3:8b"):
    """Pull a model from Ollama."""
    print(f"\n📥 Pulling {model_name}...")
    try:
        response = requests.post(
            "http://localhost:11434/api/pull",
            json={"name": model_name}
        )
        if response.status_code == 200:
            print(f"✅ {model_name} pulled successfully!")
            return True
        else:
            print(f"❌ Failed to pull {model_name}")
            return False
    except Exception as e:
        print(f"❌ Error pulling model: {e}")
        return False

def test_ollama_response(model_name="llama3:8b"):
    """Test Ollama with a simple prompt."""
    print(f"\n🧪 Testing {model_name} with a simple prompt...")
    
    test_prompt = {
        "model": model_name,
        "prompt": "Hello! Can you help me with writing?",
        "stream": False
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=test_prompt,
            timeout=60  # Longer timeout for local models
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response received in {end_time - start_time:.2f} seconds")
            print(f"📝 Response: {result.get('response', 'No response')[:200]}...")
            return True
        else:
            print(f"❌ Failed to get response: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Ollama: {e}")
        return False

def create_ollama_utils():
    """Create the Ollama utilities file."""
    ollama_utils_content = '''"""
Ollama API integration for AI_Collab_Online
Replaces OpenAI/Anthropic APIs with local Ollama models
"""

import requests
import json
import time
from flask import current_app
from models import Message, Room
from collections import namedtuple

def get_ollama_client():
    """Get Ollama client configuration."""
    base_url = current_app.config.get('OLLAMA_BASE_URL', 'http://localhost:11434')
    model = current_app.config.get('OLLAMA_MODEL', 'llama3:8b')
    return base_url, model

def call_ollama_api(messages, system_prompt=None, max_tokens=300):
    """Call Ollama API with messages and optional system prompt."""
    base_url, model = get_ollama_client()
    
    # Convert messages to Ollama format
    if system_prompt:
        # Add system prompt as first message
        prompt = f"System: {system_prompt}\\n\\n"
    else:
        prompt = ""
    
    # Add user messages
    for msg in messages:
        if msg.get('role') == 'user':
            prompt += f"User: {msg.get('content', '')}\\n"
        elif msg.get('role') == 'assistant':
            prompt += f"Assistant: {msg.get('content', '')}\\n"
    
    prompt += "Assistant: "
    
    # Prepare request
    request_data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": max_tokens
        }
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/generate",
            json=request_data,
            timeout=120  # Longer timeout for local models
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            current_app.logger.info(f"Ollama response time: {end_time - start_time:.2f}s")
            return result.get('response', '').strip()
        else:
            current_app.logger.error(f"Ollama API error: {response.status_code}")
            return "I'm sorry, I'm having trouble processing your request right now."
            
    except requests.exceptions.Timeout:
        current_app.logger.error("Ollama request timed out")
        return "I'm sorry, the request took too long to process. Please try again."
    except Exception as e:
        current_app.logger.error(f"Ollama API error: {e}")
        return "I'm sorry, I encountered an error processing your request."

def get_ollama_modes():
    """Get writing modes configured for Ollama."""
    # Use the same modes as the original system
    ChatMode = namedtuple("ChatMode", "label prompt")
    
    return {
        "explore": ChatMode(
            "1. Explore & evaluate significance",
            "You are a Socratic tutor. Ask probing questions to help students discover what genuinely interests them about their topic. Guide them to reflect on why this matters to them personally and to others. Don't provide answers - help them uncover their own insights through thoughtful questioning."
        ),
        "focus": ChatMode(
            "2. Narrow to a researchable question",
            "You are a research question coach. Help students learn to craft clear, answerable questions by asking: 'What specific aspect interests you most?' 'How could you make this more specific?' 'What would you need to know to answer this?' Guide them to understand the difference between broad topics and focused research questions."
        ),
        "context": ChatMode(
            "3. Find authoritative sources",
            "You are an information literacy coach. Help students find and evaluate authoritative sources by asking: 'Who are the experts on this topic?' 'What makes this source credible?' 'How recent is this information?' 'What are the author's credentials?' Teach them to distinguish between academic sources, expert journalism, and less reliable information."
        ),
        "proposal": ChatMode(
            "4. Write a persuasive proposal",
            "You are a proposal writing mentor. Guide students through the proposal process by asking: 'What's your main argument?' 'How will you gather evidence?' 'What sources will you need?' Help them understand what makes a proposal compelling rather than writing it for them."
        ),
        "outline": ChatMode(
            "5. Design a working outline",
            "You are an outline coach. Help students learn to structure their ideas by asking: 'What's your main claim?' 'What evidence supports each point?' 'How do these sections connect?' Guide them to create logical flow and parallel structure rather than providing the outline."
        ),
        "draft": ChatMode(
            "6. Draft key sections",
            "You are a writing coach. Help students develop their writing skills by asking: 'What's your main point here?' 'How does this connect to your thesis?' 'What evidence supports this claim?' Guide them to write clear, well-supported paragraphs rather than writing for them."
        ),
        "revise": ChatMode(
            "7. Revision strategy & feedback",
            "You are a revision mentor. Help students learn to revise by asking: 'What's your strongest argument?' 'Where could you strengthen evidence?' 'How does each paragraph advance your thesis?' Guide them to identify their own revision priorities rather than making changes for them."
        ),
        "evidence": ChatMode(
            "8. Evidence integrator",
            "You are an evidence coach. Help students learn to evaluate and integrate sources by asking: 'How reliable is this source?' 'What does this evidence actually prove?' 'How does it connect to your argument?' Guide them to think critically about evidence rather than selecting sources for them."
        ),
        "citation": ChatMode(
            "9. Citation & formatting coach",
            "You are a citation mentor. Help students learn citation rules by asking: 'What type of source is this?' 'What information do you need?' 'How would you format this in [style]?' Guide them to understand citation principles rather than formatting for them."
        ),
        "reflect": ChatMode(
            "10. Metacognitive reflection",
            "You are a reflection facilitator. Help students think about their learning process by asking: 'What did you learn about research?' 'What skills did you develop?' 'What would you do differently?' 'What questions remain?' Guide them to articulate their own insights and growth rather than summarizing for them."
        )
    }
'''
    
    with open('ollama_utils.py', 'w') as f:
        f.write(ollama_utils_content)
    
    print("✅ Created ollama_utils.py")

def main():
    """Main setup function."""
    print("🚀 Ollama Setup for AI_Collab_Online")
    print("=" * 50)
    
    # Check if Ollama is installed and running
    if not check_ollama_installation():
        return
    
    # List available models
    models = list_available_models()
    
    # If no models, suggest pulling one
    if not models:
        print("\n📥 No models found. Let's pull a model...")
        if pull_model("llama3:8b"):
            models = list_available_models()
    
    # Test with a model
    if models:
        model_name = models[0]['name']
        test_ollama_response(model_name)
    
    # Create Ollama utilities
    create_ollama_utils()
    
    print("\n✅ Ollama setup complete!")
    print("\n📝 Next steps:")
    print("1. Update openai_utils.py to use Ollama")
    print("2. Test the integration")
    print("3. Configure environment variables")

if __name__ == "__main__":
    main() 