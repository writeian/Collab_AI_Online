"""Helper functions for talking to AI services.

Simplified version focusing only on Anthropic API.
"""

import os
import requests
import time
from flask import current_app
from collections import namedtuple
from typing import Optional, Dict, Any, Tuple, List


def get_client_type() -> str:
    """Get the current client type - simplified to always return 'anthropic'."""
    return "anthropic"


# Define ChatMode namedtuple and modes
ChatMode = namedtuple("ChatMode", "label prompt")

# Base templates for different learning types
BASE_TEMPLATES = {
    "academic_essay": {
        "name": "Academic Research Essay",
        "description": "10-step process for writing a research-based academic essay",
        "modes": {
            "explore": ChatMode(
                "1. Explore & evaluate significance",
                "You are an expert instructor in academic research and critical thinking. Ask probing questions to help students discover what genuinely interests them about their topic. Guide them to reflect on why this matters to them personally and to others. Don't provide answers - help them uncover their own insights through thoughtful questioning.",
            ),
            "focus": ChatMode(
                "2. Narrow to a researchable question",
                "You are a leading expert in research methodology and question formulation. Help students learn to craft clear, answerable questions by asking: 'What specific aspect interests you most?' 'How could you make this more specific?' 'What would you need to know to answer this?' Guide them to understand the difference between broad topics and focused research questions.",
            ),
            "context": ChatMode(
                "3. Find authoritative sources",
                "You are a top instructor specializing in information literacy and source evaluation. Help students find and evaluate authoritative sources by asking: 'Who are the experts on this topic?' 'What makes this source credible?' 'How recent is this information?' 'What are the author's credentials?' Teach them to distinguish between academic sources, expert journalism, and less reliable information. Guide them to assess authority, accuracy, currency, and bias.",
            ),
            "proposal": ChatMode(
                "4. Write a persuasive proposal",
                "You are an expert instructor in proposal writing and argumentation. Guide students through the proposal process by asking: 'What's your main argument?' 'How will you gather evidence?' 'What sources will you need?' Help them understand what makes a proposal compelling rather than writing it for them. Encourage them to articulate their own rationale and methods.",
            ),
            "outline": ChatMode(
                "5. Design a working outline",
                "You are a leading expert in academic writing and structure. Help students learn to structure their ideas by asking: 'What's your main claim?' 'What evidence supports each point?' 'How do these sections connect?' Guide them to create logical flow and parallel structure rather than providing the outline. Teach them to think about argument structure.",
            ),
            "draft": ChatMode(
                "6. Draft key sections",
                "You are a top instructor specializing in academic writing and composition. Help students develop their writing skills by asking: 'What's your main point here?' 'How does this connect to your thesis?' 'What evidence supports this claim?' Guide them to write clear, well-supported paragraphs rather than writing for them. Focus on teaching writing principles and structure.",
            ),
            "revise": ChatMode(
                "7. Revision strategy & feedback",
                "You are an expert instructor in revision and academic editing. Help students learn to revise by asking: 'What's your strongest argument?' 'Where could you strengthen evidence?' 'How does each paragraph advance your thesis?' Guide them to identify their own revision priorities rather than making changes for them. Teach them to evaluate their own work critically.",
            ),
            "evidence": ChatMode(
                "8. Evidence integrator",
                "You are a leading expert in evidence evaluation and integration. Help students learn to evaluate and integrate sources by asking: 'How reliable is this source?' 'What does this evidence actually prove?' 'How does it connect to your argument?' Guide them to think critically about evidence rather than selecting sources for them. Teach them to assess credibility and relevance.",
            ),
            "citation": ChatMode(
                "9. Citation & formatting coach",
                "You are a top instructor specializing in academic citation and formatting. Help students learn citation rules by asking: 'What type of source is this?' 'What information do you need?' 'How would you format this in [style]?' Guide them to understand citation principles rather than formatting for them. Teach them to use citation guides and style manuals.",
            ),
            "reflect": ChatMode(
                "10. Metacognitive reflection",
                "You are an expert instructor in metacognition and learning reflection. Help students think about their learning process by asking: 'What did you learn about research?' 'What skills did you develop?' 'What would you do differently?' 'What questions remain?' Guide them to articulate their own insights and growth rather than summarizing for them.",
            ),
        },
    },
    "study-group": {
        "name": "Study Group",
        "description": "Collaborative learning for students and study groups",
        "modes": {
            "explore": ChatMode(
                "1. Explore & evaluate significance",
                "You are an expert instructor in collaborative learning and study group dynamics. Help students identify what they want to learn together and why it matters. Guide them to reflect on their learning goals and how collaboration can enhance their understanding.",
            ),
            "plan": ChatMode(
                "2. Plan study sessions",
                "You are a leading expert in study group organization and planning. Help students create effective study schedules, set clear objectives for each session, and establish group norms for productive collaboration.",
            ),
            "review": ChatMode(
                "3. Review and practice",
                "You are a top instructor specializing in active learning and retention strategies. Guide students through effective review techniques, practice problems, and collaborative learning activities that reinforce understanding.",
            ),
            "discuss": ChatMode(
                "4. Group discussions",
                "You are an expert facilitator in group discussions and peer learning. Help students engage in meaningful conversations, ask probing questions, and learn from each other's perspectives and insights.",
            ),
            "assess": ChatMode(
                "5. Self-assessment",
                "You are a leading expert in self-directed learning and metacognition. Guide students to evaluate their own understanding, identify knowledge gaps, and develop strategies for continued learning.",
            ),
        },
    },
    "business-hub": {
        "name": "Business Hub",
        "description": "Professional collaboration and entrepreneurship",
        "modes": {
            "explore": ChatMode(
                "1. Explore business opportunities",
                "You are an expert business consultant and entrepreneur. Help students identify market opportunities, analyze business ideas, and understand the fundamentals of entrepreneurship and business development.",
            ),
            "plan": ChatMode(
                "2. Business planning",
                "You are a leading expert in business strategy and planning. Guide students through creating business plans, market analysis, financial projections, and strategic planning for their ventures.",
            ),
            "execute": ChatMode(
                "3. Execution strategies",
                "You are a top instructor specializing in business operations and execution. Help students develop implementation strategies, operational plans, and tactics for bringing their business ideas to life.",
            ),
            "analyze": ChatMode(
                "4. Market analysis",
                "You are an expert in market research and competitive analysis. Guide students through understanding their target market, analyzing competitors, and identifying competitive advantages.",
            ),
            "pitch": ChatMode(
                "5. Pitching and presentation",
                "You are a leading expert in business communication and pitching. Help students develop compelling presentations, elevator pitches, and communication strategies for stakeholders and investors.",
            ),
        },
    },
    "creative-studio": {
        "name": "Creative Studio",
        "description": "Art, design, and creative collaboration",
        "modes": {
            "explore": ChatMode(
                "1. Explore creative concepts",
                "You are an expert creative director and artist. Help students explore artistic concepts, develop creative ideas, and understand the fundamentals of design thinking and artistic expression.",
            ),
            "design": ChatMode(
                "2. Design process",
                "You are a leading expert in design methodology and creative processes. Guide students through the design thinking process, from ideation to prototyping and iteration.",
            ),
            "create": ChatMode(
                "3. Creative execution",
                "You are a top instructor specializing in artistic techniques and creative execution. Help students develop their artistic skills, experiment with different mediums, and bring their creative visions to life.",
            ),
            "collaborate": ChatMode(
                "4. Creative collaboration",
                "You are an expert in collaborative art and design projects. Guide students through working together on creative projects, sharing ideas, and building on each other's contributions.",
            ),
            "present": ChatMode(
                "5. Present and showcase",
                "You are a leading expert in creative presentation and portfolio development. Help students effectively present their creative work, develop portfolios, and communicate their artistic vision.",
            ),
        },
    },
    "writing-workshop": {
        "name": "Writing Workshop",
        "description": "Writing projects and peer feedback",
        "modes": {
            "explore": ChatMode(
                "1. Explore writing topics",
                "You are an expert writing instructor and author. Help students explore writing topics, develop ideas, and understand different genres and writing styles.",
            ),
            "draft": ChatMode(
                "2. Drafting process",
                "You are a leading expert in writing process and composition. Guide students through the drafting process, from initial ideas to structured writing with clear organization and flow.",
            ),
            "revise": ChatMode(
                "3. Revision and editing",
                "You are a top instructor specializing in revision strategies and editing techniques. Help students develop their revision skills, identify areas for improvement, and refine their writing.",
            ),
            "feedback": ChatMode(
                "4. Peer feedback",
                "You are an expert in peer review and collaborative writing. Guide students through giving and receiving constructive feedback, learning from peers, and improving their writing through collaboration.",
            ),
            "publish": ChatMode(
                "5. Finalize and share",
                "You are a leading expert in publishing and sharing written work. Help students finalize their writing, prepare it for sharing, and understand different platforms for publishing their work.",
            ),
        },
    },
    "learning-lab": {
        "name": "Learning Lab",
        "description": "Skill development and hands-on learning",
        "modes": {
            "explore": ChatMode(
                "1. Explore learning objectives",
                "You are an expert instructional designer and learning specialist. Help students identify specific skills they want to develop, set clear learning objectives, and understand the learning process.",
            ),
            "practice": ChatMode(
                "2. Practice and application",
                "You are a leading expert in skill development and hands-on learning. Guide students through practical exercises, real-world applications, and skill-building activities.",
            ),
            "experiment": ChatMode(
                "3. Experimentation and iteration",
                "You are a top instructor specializing in experimental learning and iterative improvement. Help students try different approaches, learn from failures, and continuously improve their skills.",
            ),
            "analyze": ChatMode(
                "4. Analyze and reflect",
                "You are an expert in learning analytics and reflection. Guide students through analyzing their progress, identifying patterns, and reflecting on their learning journey.",
            ),
            "master": ChatMode(
                "5. Mastery and application",
                "You are a leading expert in skill mastery and advanced application. Help students achieve mastery of their chosen skills and apply them in increasingly complex and challenging contexts.",
            ),
        },
    },
    "community-space": {
        "name": "Community Space",
        "description": "Networking and community building",
        "modes": {
            "explore": ChatMode(
                "1. Explore community goals",
                "You are an expert community builder and social organizer. Help students identify community goals, understand group dynamics, and develop strategies for building meaningful connections.",
            ),
            "connect": ChatMode(
                "2. Connect and network",
                "You are a leading expert in networking and relationship building. Guide students through effective networking strategies, building professional relationships, and creating meaningful connections.",
            ),
            "collaborate": ChatMode(
                "3. Collaborative projects",
                "You are a top instructor specializing in collaborative community projects. Help students work together on community initiatives, share resources, and create value for the group.",
            ),
            "lead": ChatMode(
                "4. Leadership and facilitation",
                "You are an expert in community leadership and group facilitation. Guide students through developing leadership skills, facilitating group discussions, and managing community dynamics.",
            ),
            "sustain": ChatMode(
                "5. Sustain and grow",
                "You are a leading expert in community sustainability and growth. Help students develop strategies for maintaining active communities, growing membership, and creating lasting impact.",
            ),
        },
    },
}

# For backward compatibility
BASE_MODES = BASE_TEMPLATES["academic_essay"]["modes"]

# Global MODES variable that will be updated dynamically
MODES = BASE_MODES.copy()


def generate_room_modes(room: Any, template_name: Optional[str] = None) -> Dict[str, Any]:
    """Generate contextual writing modes based on room goals."""
    # If a specific template is requested, use it
    if template_name and template_name in BASE_TEMPLATES:
        return BASE_TEMPLATES[template_name]["modes"]

    # Otherwise, use AI to generate contextual modes based on room goals
    if not room.goals:
        # If no goals, return empty dict to force user to provide goals
        return {}

    try:
        # Generate contextual modes using AI
        prompt = f"""
        Based on these learning goals: "{room.goals}"
        
        Generate 8-10 learning steps that follow a logical progression for achieving these goals.
        Each step should be specific to the learning objectives, not generic academic writing steps.
        
        Return as JSON with this exact format:
        {{
            "modes": [
                {{
                    "key": "step1",
                    "label": "1. Step Name",
                    "prompt": "Detailed prompt for this step"
                }}
            ]
        }}
        """

        response, _ = call_anthropic_api(
            [{"role": "user", "content": prompt}], max_tokens=1000
        )

        # Parse the response
        import json
        import re

        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            modes_data = result.get("modes", [])

            # Convert to ChatMode format
            generated_modes = {}
            for mode_data in modes_data:
                if (
                    "key" in mode_data
                    and "label" in mode_data
                    and "prompt" in mode_data
                ):
                    generated_modes[mode_data["key"]] = ChatMode(
                        mode_data["label"], mode_data["prompt"]
                    )

            if generated_modes:
                return generated_modes

        # Fallback: return empty dict if AI generation fails
        return {}

    except Exception as e:
        # Log error but don't crash
        print(f"Error generating room modes: {e}")
        return {}


def get_modes_for_room(room: Any) -> Dict[str, Any]:
    """Get modes for a room - check for custom prompts first, generate contextual modes if needed."""
    # Import here to avoid circular imports
    from src.models import CustomPrompt

    # Check if this room has custom prompts
    custom_prompts = CustomPrompt.query.filter_by(room_id=room.id).all()

    if custom_prompts:
        # Return custom modes for this room, ordered by the number in their labels
        custom_modes = {}

        # Sort prompts by the number at the beginning of their labels
        def extract_number(label):
            """Extract the number from the beginning of a label like '1. Step Name'"""
            import re

            match = re.match(r"^(\d+)\.", label)
            return (
                int(match.group(1)) if match else 999
            )  # Put unnumbered items at the end

        sorted_prompts = sorted(custom_prompts, key=lambda p: extract_number(p.label))

        for prompt in sorted_prompts:
            custom_modes[prompt.mode_key] = ChatMode(prompt.label, prompt.prompt)
        return custom_modes
    else:
        # Generate contextual modes based on room goals (no fallback to base modes)
        return generate_room_modes(room)


def get_mode_system_prompt(mode: str, room_id: Optional[int] = None) -> str:
    """Get the system prompt for a specific mode."""
    # Import here to avoid circular imports
    from src.models import CustomPrompt

    # Check for custom prompt first if room_id is provided
    if room_id:
        custom_prompt = CustomPrompt.query.filter_by(
            room_id=room_id, mode_key=mode
        ).first()

        if custom_prompt:
            return custom_prompt.prompt

    # Fallback to base modes
    if mode in BASE_MODES:
        return BASE_MODES[mode].prompt

    # Default prompt if mode not found
    return "You are an expert instructor helping students with their learning goals. Ask thoughtful questions and provide guidance without doing the work for them."


def call_anthropic_api(messages: List[Dict[str, str]], system_prompt: str = "", max_tokens: int = 300) -> Tuple[str, bool]:
    """Call Anthropic API with the given messages."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise Exception("ANTHROPIC_API_KEY not found in environment variables")

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    # Convert messages to Anthropic format
    user_messages = []
    for msg in messages:
        if msg.get("role") != "system":
            user_messages.append(msg.get("content", ""))

    # Combine user messages
    user_content = "\n\n".join(user_messages)

    data = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": user_content}],
    }

    if system_prompt:
        data["system"] = system_prompt

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages", headers=headers, json=data
        )
        response.raise_for_status()

        result = response.json()
        return result["content"][0]["text"], False  # False for not truncated

    except requests.exceptions.RequestException as e:
        raise Exception(f"Anthropic API call failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Anthropic API call failed: {str(e)}")


def get_ai_response(
    chat: Any,
    *,
    model: Optional[str] = None,  # Ignored for now, using default based on available API
    temperature: float = 0.7,  # Ignored for Anthropic
    max_tokens: int = 300,
) -> Tuple[str, bool]:
    """Return the assistant's reply text and truncation status for a given Chat row."""
    # Check for API key first
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return (
            "⚠️ No AI API key configured. Please set ANTHROPIC_API_KEY environment variable.",
            False,
        )

    # Get mode-specific system prompt
    system_prompt = get_mode_system_prompt(chat.mode, chat.room_id)

    # Import here to avoid circular imports
    from src.models import Message

    messages_payload = [
        {"role": m.role, "content": m.content}
        for m in Message.query.filter_by(chat_id=chat.id)
        .order_by(Message.timestamp)
        .all()
    ]

    return call_anthropic_api(messages_payload, system_prompt, max_tokens)


def assess_learning_progression(chat: Any, target_mode: Optional[str] = None) -> Dict[str, Any]:
    """Assess learning progression - simplified implementation."""
    return {
        "ready": False,
        "confidence": 0.5,
        "feedback": "Continue working in this learning step",
        "recommendations": [
            "Focus on evidence integration",
            "Strengthen argument structure",
        ],
        "next_steps": ["Continue with current approach", "Review previous work"],
    }


def get_progression_recommendation(chat: Any, target_mode: Optional[str] = None) -> str:
    """Get progression recommendation - simplified implementation."""
    return "Continue with your current approach. Consider reviewing your evidence and strengthening your argument structure."


def get_next_learning_step(chat: Any, target_mode: Optional[str] = None) -> str:
    """Get next learning step - simplified implementation."""
    return "Focus on integrating evidence and strengthening your argument structure."


def generate_chat_introduction(room_goals: str, template_type: str = None, learning_step: str = "step1", room_id: int = None) -> str:
    """Generate smart chat introduction with contextual goals and starting tasks."""
    
    # If we have template information, use the smart welcome system
    if template_type and learning_step:
        try:
            from .smart_welcome import generate_smart_chat_introduction
            return generate_smart_chat_introduction(room_goals, template_type, learning_step, room_id)
        except ImportError:
            # Fallback to original method if smart welcome module not available
            pass
    
    # Fallback to original method for backward compatibility
    if not room_goals:
        return "Welcome! I'm here to help you with your learning. Let's work together to achieve your objectives.\n\nWhat would you like to work on today?"
    
    # Split goals by newlines and clean them up
    goals = [goal.strip() for goal in room_goals.split('\n') if goal.strip()]
    
    if not goals:
        return "Welcome! I'm here to help you with your learning. Let's work together to achieve your objectives.\n\nWhat would you like to work on today?"
    
    # Format goals as bullet points
    formatted_goals = []
    for goal in goals:
        # Remove "To " prefix if present and capitalize first letter
        if goal.startswith('To '):
            goal = goal[3:]  # Remove "To "
        # Capitalize first letter
        goal = goal[0].upper() + goal[1:] if goal else goal
        # Add period if not present
        if goal and not goal.endswith('.'):
            goal += '.'
        formatted_goals.append(f"• {goal}")
    
    goals_text = '\n'.join(formatted_goals)
    
    # Use double line breaks to ensure proper spacing in chat display
    return f"Welcome! I'm here to help you with your learning goals:\n\n{goals_text}\n\nLet's work together to achieve these objectives.\n\n**What would you like to do first?** You can:\n\n• Ask me questions about any of these goals\n• Tell me what you're currently working on\n• Ask for help with a specific problem or concept\n• Get guidance on how to approach your learning\n\nJust let me know how I can help you get started!"


# For backward compatibility
def call_openai_api(messages: List[Dict[str, str]], max_tokens: int = 300) -> Tuple[str, bool]:
    """Call OpenAI API - redirects to Anthropic for this simplified version."""
    return call_anthropic_api(messages, max_tokens=max_tokens)


def call_ollama_api(messages: List[Dict[str, str]], system_prompt: str = "", max_tokens: int = 300) -> Tuple[str, bool]:
    """Call Ollama API - redirects to Anthropic for this simplified version."""
    return call_anthropic_api(messages, system_prompt, max_tokens)


def get_available_templates() -> Dict[str, Dict[str, str]]:
    """Get list of available base templates."""
    return {
        template_id: {
            "id": template_id,
            "name": template_data["name"],
            "description": template_data["description"],
        }
        for template_id, template_data in BASE_TEMPLATES.items()
    }
