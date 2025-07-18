"""Helper functions for talking to AI services.

Supports OpenAI, Anthropic Claude, and local Ollama APIs.
"""
import os
import requests
import time
from flask import current_app
from models import Message, Room
from collections import namedtuple

def get_client_type():
    """Get the current client type based on available API keys."""
    # Check API keys dynamically each time
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
    
    if use_ollama:
        return "ollama"
    elif anthropic_api_key:
        return "anthropic"
    elif openai_api_key:
        return "openai"
    else:
        return None

# Define ChatMode namedtuple and modes
ChatMode = namedtuple("ChatMode", "label prompt")

# Base modes for fallback
BASE_MODES = {
    "explore": ChatMode(
        "1. Explore & evaluate significance",
        "You are a Socratic tutor. Ask probing questions to help students discover \
what genuinely interests them about their topic. Guide them to reflect on why this \
matters to them personally and to others. Don't provide answers - help them \
uncover their own insights through thoughtful questioning."
    ),
    "focus": ChatMode(
        "2. Narrow to a researchable question",
        "You are a research question coach. Help students learn to craft clear, \
answerable questions by asking: 'What specific aspect interests you most?' \
'How could you make this more specific?' 'What would you need to know to \
answer this?' Guide them to understand the difference between broad topics \
and focused research questions."
    ),
    "context": ChatMode(
        "3. Find authoritative sources",
        "You are an information literacy coach. Help students find and evaluate \
authoritative sources by asking: 'Who are the experts on this topic?' \
'What makes this source credible?' 'How recent is this information?' \
'What are the author's credentials?' Teach them to distinguish between \
academic sources, expert journalism, and less reliable information. \
Guide them to assess authority, accuracy, currency, and bias."
    ),
    "proposal": ChatMode(
        "4. Write a persuasive proposal",
        "You are a proposal writing mentor. Guide students through the \
proposal process by asking: 'What's your main argument?' 'How will you \
gather evidence?' 'What sources will you need?' Help them understand \
what makes a proposal compelling rather than writing it for them. \
Encourage them to articulate their own rationale and methods."
    ),
    "outline": ChatMode(
        "5. Design a working outline",
        "You are an outline coach. Help students learn to structure their \
ideas by asking: 'What's your main claim?' 'What evidence supports each \
point?' 'How do these sections connect?' Guide them to create logical \
flow and parallel structure rather than providing the outline. \
Teach them to think about argument structure."
    ),
    "draft": ChatMode(
        "6. Draft key sections",
        "You are a writing coach. Help students develop their writing skills \
by asking: 'What's your main point here?' 'How does this connect to your \
thesis?' 'What evidence supports this claim?' Guide them to write \
clear, well-supported paragraphs rather than writing for them. \
Focus on teaching writing principles and structure."
    ),
    "revise": ChatMode(
        "7. Revision strategy & feedback",
        "You are a revision mentor. Help students learn to revise by asking: \
'What's your strongest argument?' 'Where could you strengthen evidence?' \
'How does each paragraph advance your thesis?' Guide them to identify \
their own revision priorities rather than making changes for them. \
Teach them to evaluate their own work critically."
    ),
    "evidence": ChatMode(
        "8. Evidence integrator",
        "You are an evidence coach. Help students learn to evaluate and \
integrate sources by asking: 'How reliable is this source?' 'What does \
this evidence actually prove?' 'How does it connect to your argument?' \
Guide them to think critically about evidence rather than selecting \
sources for them. Teach them to assess credibility and relevance."
    ),
    "citation": ChatMode(
        "9. Citation & formatting coach",
        "You are a citation mentor. Help students learn citation rules by \
asking: 'What type of source is this?' 'What information do you need?' \
'How would you format this in [style]?' Guide them to understand \
citation principles rather than formatting for them. Teach them \
to use citation guides and style manuals."
    ),
    "reflect": ChatMode(
        "10. Metacognitive reflection",
        "You are a reflection facilitator. Help students think about their \
learning process by asking: 'What did you learn about research?' \
'What skills did you develop?' 'What would you do differently?' \
'What questions remain?' Guide them to articulate their own \
insights and growth rather than summarizing for them."
    ),
}

# Global MODES variable that will be updated dynamically
MODES = BASE_MODES.copy()

def generate_room_modes(room):
    """Generate contextual writing modes based on room goals."""
    if not room.goals:
        return BASE_MODES
    
    client_type = get_client_type()
    if not client_type:
        return BASE_MODES
    
    # Create a prompt for generating contextual modes
    system_prompt = """You are an educational AI assistant. Based on the learning goals provided, generate 5-8 contextual writing modes that would help students achieve those goals.

For each mode, provide:
1. A short, descriptive label (2-4 words)
2. A detailed prompt explaining the AI's role and approach

Focus on modes that help students learn, not modes that do the work for them. Each mode should guide students through a specific aspect of their learning journey.

Return the response as a JSON object with mode keys and objects containing 'label' and 'prompt' fields."""

    user_prompt = f"""Learning Goals: {room.goals}

Generate contextual writing modes that would help students achieve these learning goals. Focus on modes that guide students through the learning process rather than doing the work for them."""

    try:
        if client_type == "anthropic":
            response = call_anthropic_api(
                [{"role": "user", "content": user_prompt}],
                system_prompt,
                max_tokens=800
            )
        else:
            response = call_openai_api(
                [{"role": "system", "content": system_prompt},
                 {"role": "user", "content": user_prompt}],
                max_tokens=800
            )
        
        # Try to parse JSON response
        import json
        try:
            modes_data = json.loads(response)
            contextual_modes = {}
            
            for mode_key, mode_info in modes_data.items():
                if isinstance(mode_info, dict) and 'label' in mode_info and 'prompt' in mode_info:
                    contextual_modes[mode_key] = ChatMode(mode_info['label'], mode_info['prompt'])
            
            if contextual_modes:
                return contextual_modes
        except json.JSONDecodeError:
            pass
        
        # Fallback to base modes if parsing fails
        return BASE_MODES
        
    except Exception as e:
        current_app.logger.error(f"Error generating room modes: {e}")
        return BASE_MODES

def get_modes_for_room(room):
    """Get writing modes for a specific room, prioritizing saved custom prompts."""
    from models import CustomPrompt
    
    # First, check for saved custom prompts for this room
    custom_prompts = CustomPrompt.query.filter_by(
        room_id=room.id, 
        is_active=True
    ).all()
    
    if custom_prompts:
        # Convert custom prompts to the same format as BASE_MODES
        room_modes = {}
        for cp in custom_prompts:
            room_modes[cp.mode_key] = {
                'label': cp.label,
                'prompt': cp.prompt
            }
        return room_modes
    
    # If no custom prompts exist, generate contextual modes if room has goals
    if room.goals:
        try:
            contextual_modes = generate_room_modes(room)
            # Convert to the same format as BASE_MODES
            room_modes = {}
            for mode_key, mode_info in contextual_modes.items():
                room_modes[mode_key] = {
                    'label': mode_info.label,
                    'prompt': mode_info.prompt
                }
            return room_modes
        except Exception as e:
            current_app.logger.error(f"Error generating room modes: {e}")
    
    # Fallback to base modes
    return BASE_MODES

def get_mode_system_prompt(mode, room_id=None):
    """Return a system prompt tailored to the writing stage."""
    # First check for custom prompts in the database
    from models import CustomPrompt
    from flask import current_app
    
    try:
        # Check for room-specific custom prompt first
        if room_id:
            custom_prompt = CustomPrompt.query.filter_by(
                mode_key=mode, 
                room_id=room_id,
                is_active=True
            ).first()
            
            if custom_prompt:
                return custom_prompt.prompt
        
        # Check for global custom prompt (room_id is null)
        custom_prompt = CustomPrompt.query.filter_by(
            mode_key=mode, 
            room_id=None,
            is_active=True
        ).first()
        
        if custom_prompt:
            return custom_prompt.prompt
    except Exception as e:
        current_app.logger.error(f"Error checking custom prompts: {e}")
    
    # Fallback to default modes
    if mode in BASE_MODES:
        return BASE_MODES[mode].prompt
    else:
        # Default to explore mode if mode is not found
        return BASE_MODES["explore"].prompt


def call_anthropic_api(messages, system_prompt, max_tokens=300):
    """Call Anthropic Claude API."""
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": anthropic_api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # Convert messages to Anthropic format
    anthropic_messages = []
    for msg in messages:
        if msg["role"] == "system":
            continue
        anthropic_messages.append({
            "role": msg["role"],
            "content": [{"type": "text", "text": msg["content"]}]
        })
    
    payload = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": max_tokens,
        "messages": anthropic_messages,
        "system": system_prompt
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["content"][0]["text"]
    except requests.exceptions.HTTPError as e:
        print("Anthropic API HTTPError:", e)
        print("Status code:", e.response.status_code)
        print("Response text:", e.response.text)
        current_app.logger.error("Anthropic API failure: %s", e)
        return f"⚠️ Anthropic API error: {e.response.text}"
    except Exception as e:
        print("Anthropic API Exception:", e)
        current_app.logger.error("Anthropic API failure: %s", e)
        return "⚠️ Sorry — I couldn't reach the AI service just now."


def call_openai_api(messages, max_tokens=300):
    """Call OpenAI API."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    from openai import OpenAI
    client = OpenAI(api_key=openai_api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content
        return content.strip() if content else ""
    except Exception as e:
        current_app.logger.error("OpenAI API failure: %s", e)
        return "⚠️ Sorry — I couldn't reach the AI service just now."


def call_ollama_api(messages, system_prompt, max_tokens=300):
    """Call local Ollama API."""
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "gemma3")
    
    # Convert messages to Ollama format with system prompt
    if system_prompt:
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
    
    payload = {
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
        response = requests.post(f"{ollama_url}/api/generate", json=payload, timeout=120)
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


def get_ai_response(
    chat,
    *,
    model=None,  # Ignored for now, using default based on available API
    temperature=0.7,  # Ignored for Anthropic
    max_tokens=300,
):
    """Return the assistant's reply text for a given Chat row."""
    client_type = get_client_type()
    if not client_type:
        return "⚠️ No AI API key configured. Please set ANTHROPIC_API_KEY, OPENAI_API_KEY, or USE_OLLAMA=true environment variable."
    
    # Get mode-specific system prompt
    system_prompt = get_mode_system_prompt(chat.mode, chat.room_id)
    
    messages_payload = [
        {"role": m.role, "content": m.content}
        for m in Message.query.filter_by(chat_id=chat.id)
        .order_by(Message.timestamp)
        .all()
    ]
    
    if client_type == "ollama":
        return call_ollama_api(messages_payload, system_prompt, max_tokens)
    elif client_type == "anthropic":
        return call_anthropic_api(messages_payload, system_prompt, max_tokens)
    else:  # openai
        return call_openai_api(messages_payload, max_tokens)
