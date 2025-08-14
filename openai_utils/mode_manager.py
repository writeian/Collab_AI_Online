"""
Mode Manager for Learning Steps.

This module handles the management and generation of learning modes/steps
for different rooms and educational contexts.
"""

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from collections import namedtuple

from .config import AIConfig
from .exceptions import ModeGenerationError, ConfigurationError
from .api_clients import APIClientFactory


@dataclass
class ChatMode:
    """Data class for representing a chat mode."""
    label: str
    prompt: str


# Define ChatMode namedtuple for backward compatibility
ChatModeTuple = namedtuple("ChatMode", "label prompt")


class ModeManager:
    """Manages learning modes and their generation."""
    
    def __init__(self):
        self.config = AIConfig()
        self.base_modes = self._load_base_modes()
        self.api_factory = APIClientFactory()
    
    def _load_base_modes(self) -> Dict[str, ChatMode]:
        """Load the base modes for fallback."""
        return {
            "explore": ChatMode(
                "1. Explore & evaluate significance",
                "You are an expert instructor in academic research and critical thinking. Ask probing questions to help students discover what genuinely interests them about their topic. Guide them to reflect on why this matters to them personally and to others. Don't provide answers - help them uncover their own insights through thoughtful questioning."
            ),
            "focus": ChatMode(
                "2. Narrow to a researchable question",
                "You are a leading expert in research methodology and question formulation. Help students learn to craft clear, answerable questions by asking: 'What specific aspect interests you most?' 'How could you make this more specific?' 'What would you need to know to answer this?' Guide them to understand the difference between broad topics and focused research questions."
            ),
            "context": ChatMode(
                "3. Find authoritative sources",
                "You are a top instructor specializing in information literacy and source evaluation. Help students find and evaluate authoritative sources by asking: 'Who are the experts on this topic?' 'What makes this source credible?' 'How recent is this information?' 'What are the author's credentials?' Teach them to distinguish between academic sources, expert journalism, and less reliable information. Guide them to assess authority, accuracy, currency, and bias."
            ),
            "proposal": ChatMode(
                "4. Write a persuasive proposal",
                "You are an expert instructor in proposal writing and argumentation. Guide students through the proposal process by asking: 'What's your main argument?' 'How will you gather evidence?' 'What sources will you need?' Help them understand what makes a proposal compelling rather than writing it for them. Encourage them to articulate their own rationale and methods."
            ),
            "outline": ChatMode(
                "5. Design a working outline",
                "You are a leading expert in academic writing and structure. Help students learn to structure their ideas by asking: 'What's your main claim?' 'What evidence supports each point?' 'How do these sections connect?' Guide them to create logical flow and parallel structure rather than providing the outline. Teach them to think about argument structure."
            ),
            "draft": ChatMode(
                "6. Draft key sections",
                "You are a top instructor specializing in academic writing and composition. Help students develop their writing skills by asking: 'What's your main point here?' 'How does this connect to your thesis?' 'What evidence supports this claim?' Guide them to write clear, well-supported paragraphs rather than writing for them. Focus on teaching writing principles and structure."
            ),
            "revise": ChatMode(
                "7. Revision strategy & feedback",
                "You are an expert instructor in revision and academic editing. Help students learn to revise by asking: 'What's your strongest argument?' 'Where could you strengthen evidence?' 'How does each paragraph advance your thesis?' Guide them to identify their own revision priorities rather than making changes for them. Teach them to evaluate their own work critically."
            ),
            "evidence": ChatMode(
                "8. Evidence integrator",
                "You are a leading expert in evidence evaluation and integration. Help students learn to evaluate and integrate sources by asking: 'How reliable is this source?' 'What does this evidence actually prove?' 'How does it connect to your argument?' Guide them to think critically about evidence rather than selecting sources for them. Teach them to assess credibility and relevance."
            ),
            "citation": ChatMode(
                "9. Citation & formatting coach",
                "You are a top instructor specializing in academic citation and formatting. Help students learn citation rules by asking: 'What type of source is this?' 'What information do you need?' 'How would you format this in [style]?' Guide them to understand citation principles rather than formatting for them. Teach them to use citation guides and style manuals."
            ),
            "reflect": ChatMode(
                "10. Metacognitive reflection",
                "You are an expert instructor in metacognition and learning reflection. Help students think about their learning process by asking: 'What did you learn about research?' 'What skills did you develop?' 'What would you do differently?' 'What questions remain?' Guide them to articulate their own insights and growth rather than summarizing for them."
            ),
        }
    
    def get_modes_for_room(self, room) -> Dict[str, ChatMode]:
        """
        Get the appropriate modes for a room.
        
        Args:
            room: Room object with goals and custom modes
            
        Returns:
            Dictionary of mode keys to ChatMode objects
        """
        if not room:
            return self.base_modes
        
        # Check if room has custom modes
        if hasattr(room, 'custom_modes') and room.custom_modes:
            try:
                custom_modes = json.loads(room.custom_modes)
                return {k: ChatMode(v['label'], v['prompt']) for k, v in custom_modes.items()}
            except (json.JSONDecodeError, KeyError, TypeError):
                # Fall back to base modes if custom modes are invalid
                return self.base_modes
        
        # If room has goals, try to generate contextual modes
        if room.goals:
            try:
                return self.generate_room_modes(room)
            except Exception as e:
                # Log the error but don't fail - fall back to base modes
                if hasattr(self, 'logger'):
                    self.logger.warning(f"Failed to generate modes for room {room.id}: {e}")
                return self.base_modes
        
        return self.base_modes
    
    def generate_room_modes(self, room) -> Dict[str, ChatMode]:
        """
        Generate contextual writing modes based on room goals.
        
        Args:
            room: Room object with goals
            
        Returns:
            Dictionary of generated modes
            
        Raises:
            ModeGenerationError: If mode generation fails
        """
        if not room.goals:
            return self.base_modes
        
        try:
            client = self.api_factory.get_client()
        except ConfigurationError:
            return self.base_modes
        
        # Create a prompt for generating contextual modes
        system_prompt = """You are an educational AI assistant. Based on the learning goals provided, generate 5-8 contextual writing modes that would help students achieve those goals.

For each mode, provide:
1. A short, descriptive label (2-4 words)
2. A detailed prompt explaining the AI's role and approach

IMPORTANT: Every mode should start with the AI taking the role of an instructor who is a top expert in the learning goals. For example:
- "You are an expert instructor in [topic]..."
- "As a leading expert in [field]..."
- "I am a top instructor specializing in [subject]..."

Focus on modes that help students learn, not modes that do the work for them. Each mode should guide students through a specific aspect of their learning journey.

Return your response as a JSON object with mode keys and objects containing 'label' and 'prompt' fields."""

        user_message = f"Generate contextual writing modes for these learning goals: {room.goals}"
        
        try:
            response, success = client.call_api(
                messages=[{"role": "user", "content": user_message}],
                system_prompt=system_prompt,
                max_tokens=1000
            )
            
            if not success:
                raise ModeGenerationError("API call failed", room.id, room.goals)
            
            # Parse the response
            try:
                modes_data = json.loads(response)
                generated_modes = {}
                
                for key, mode_info in modes_data.items():
                    if isinstance(mode_info, dict) and 'label' in mode_info and 'prompt' in mode_info:
                        generated_modes[key] = ChatMode(
                            label=mode_info['label'],
                            prompt=mode_info['prompt']
                        )
                
                if generated_modes:
                    return generated_modes
                else:
                    raise ModeGenerationError("No valid modes generated", room.id, room.goals)
                    
            except json.JSONDecodeError:
                raise ModeGenerationError("Invalid JSON response from API", room.id, room.goals)
                
        except Exception as e:
            if isinstance(e, ModeGenerationError):
                raise
            raise ModeGenerationError(f"Mode generation failed: {str(e)}", room.id, room.goals)
    
    def get_mode_system_prompt(self, mode: str, room_id: Optional[int] = None) -> str:
        """
        Get the system prompt for a specific mode.
        
        Args:
            mode: Mode identifier
            room_id: Optional room ID for custom prompts
            
        Returns:
            System prompt string
        """
        # Check for custom system instructions first
        if room_id:
            from models import CustomPrompt
            custom_prompt = CustomPrompt.query.filter_by(
                room_id=room_id, 
                mode=mode
            ).first()
            
            if custom_prompt and custom_prompt.system_instructions:
                return custom_prompt.system_instructions
        
        # Fall back to default mode prompts
        modes = self.base_modes
        if mode in modes:
            return modes[mode].prompt
        
        # If mode not found, return a generic prompt
        return "You are an expert instructor helping students with their learning goals. Ask thoughtful questions and provide guidance without doing the work for them."
    
    def get_client_type(self) -> Optional[str]:
        """
        Get the current client type based on available API keys.
        
        Returns:
            Client type string or None if no service configured
        """
        if self.config.should_use_ollama():
            return "ollama"
        elif self.config.get_anthropic_api_key():
            return "anthropic"
        elif self.config.get_openai_api_key():
            return "openai"
        else:
            return None


# Global MODES variable for backward compatibility
MODES = ModeManager().base_modes

# Convenience functions for backward compatibility
def get_modes_for_room(room) -> Dict[str, ChatMode]:
    """Get modes for a room (backward compatibility)."""
    manager = ModeManager()
    return manager.get_modes_for_room(room)


def generate_room_modes(room) -> Dict[str, ChatMode]:
    """Generate room modes (backward compatibility)."""
    manager = ModeManager()
    return manager.generate_room_modes(room)


def get_mode_system_prompt(mode: str, room_id: Optional[int] = None) -> str:
    """Get mode system prompt (backward compatibility)."""
    manager = ModeManager()
    return manager.get_mode_system_prompt(mode, room_id)


def get_client_type() -> Optional[str]:
    """Get client type (backward compatibility)."""
    manager = ModeManager()
    return manager.get_client_type() 