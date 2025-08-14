"""
Main Interface for OpenAI Utils.

This module provides the unified interface that ties together all other modules
and maintains backward compatibility with the original openai_utils.py functions.
"""

from typing import List, Dict, Any, Optional, Tuple
import logging

from .config import AIConfig
from .exceptions import AIAPIError, ConfigurationError
from .api_clients import APIClientFactory
from .mode_manager import ModeManager
from .assessment import LearningAssessment
from .conversation import ConversationManager


class OpenAIUtilsInterface:
    """
    Main interface class that provides unified access to all AI utilities.
    
    This class maintains backward compatibility while providing access to
    the new modular architecture.
    """
    
    def __init__(self):
        """Initialize the main interface with all sub-modules."""
        self.config = AIConfig()
        self.api_factory = APIClientFactory()
        self.mode_manager = ModeManager()
        self.assessment = LearningAssessment()
        self.conversation = ConversationManager()
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
    
    # ============================================================================
    # API CLIENT FUNCTIONS (Backward Compatibility)
    # ============================================================================
    
    def get_client_type(self) -> str:
        """Get the appropriate client type based on configuration."""
        try:
            return self.conversation._get_client_type()
        except Exception as e:
            self.logger.error(f"Failed to get client type: {e}")
            return self.config.DEFAULT_CLIENT_TYPE
    
    def call_anthropic_api(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call Anthropic API with messages."""
        try:
            return self.api_factory.get_response(
                client_type='anthropic',
                messages=messages,
                **kwargs
            )
        except Exception as e:
            raise AIAPIError(f"Anthropic API call failed: {str(e)}", client_type='anthropic')
    
    def call_openai_api(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call OpenAI API with messages."""
        try:
            return self.api_factory.get_response(
                client_type='openai',
                messages=messages,
                **kwargs
            )
        except Exception as e:
            raise AIAPIError(f"OpenAI API call failed: {str(e)}", client_type='openai')
    
    def call_ollama_api(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call Ollama API with messages."""
        try:
            return self.api_factory.get_response(
                client_type='ollama',
                messages=messages,
                **kwargs
            )
        except Exception as e:
            raise AIAPIError(f"Ollama API call failed: {str(e)}", client_type='ollama')
    
    # ============================================================================
    # CONVERSATION FUNCTIONS (Backward Compatibility)
    # ============================================================================
    
    def get_ai_response(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str = "",
        max_tokens: int = None,
        temperature: float = None,
        client_type: str = None
    ) -> str:
        """Get AI response for conversation."""
        try:
            return self.conversation.get_ai_response(
                messages, system_prompt, max_tokens, temperature, client_type
            )
        except Exception as e:
            raise AIAPIError(f"Failed to get AI response: {str(e)}")
    
    def generate_chat_introduction(
        self,
        room_name: str,
        room_description: str = "",
        client_type: str = None
    ) -> str:
        """Generate an AI introduction message for a new chat room."""
        try:
            return self.conversation.generate_chat_introduction(
                room_name, room_description, client_type
            )
        except Exception as e:
            raise AIAPIError(f"Failed to generate chat introduction: {str(e)}")
    
    # ============================================================================
    # MODE MANAGEMENT FUNCTIONS (Backward Compatibility)
    # ============================================================================
    
    def get_modes_for_room(self, room_id: int) -> List[Dict[str, str]]:
        """Get modes for a specific room."""
        try:
            return self.mode_manager.get_modes_for_room(room_id)
        except Exception as e:
            raise AIAPIError(f"Failed to get modes for room: {str(e)}")
    
    def generate_room_modes(self, room_id: int, room_name: str, room_description: str = "") -> List[Dict[str, str]]:
        """Generate custom modes for a room."""
        try:
            return self.mode_manager.generate_room_modes(room_id, room_name, room_description)
        except Exception as e:
            raise AIAPIError(f"Failed to generate room modes: {str(e)}")
    
    def get_mode_system_prompt(self, mode_label: str) -> str:
        """Get system prompt for a specific mode."""
        try:
            return self.mode_manager.get_mode_system_prompt(mode_label)
        except Exception as e:
            raise AIAPIError(f"Failed to get mode system prompt: {str(e)}")
    
    # ============================================================================
    # ASSESSMENT FUNCTIONS (Backward Compatibility)
    # ============================================================================
    
    def assess_learning_progression(
        self,
        messages: List[Dict[str, Any]],
        room_name: str = "",
        client_type: str = None
    ) -> Dict[str, Any]:
        """Assess learning progression based on conversation."""
        try:
            return self.assessment.assess_learning_progression(
                messages, room_name, client_type
            )
        except Exception as e:
            raise AIAPIError(f"Failed to assess learning progression: {str(e)}")
    
    def get_progression_recommendation(
        self,
        assessment_result: Dict[str, Any],
        room_name: str = "",
        client_type: str = None
    ) -> str:
        """Get recommendation based on assessment result."""
        try:
            return self.assessment.get_progression_recommendation(
                assessment_result, room_name, client_type
            )
        except Exception as e:
            raise AIAPIError(f"Failed to get progression recommendation: {str(e)}")
    
    def get_next_learning_step(
        self,
        current_level: str,
        room_name: str = "",
        client_type: str = None
    ) -> str:
        """Get next learning step based on current level."""
        try:
            return self.assessment.get_next_learning_step(
                current_level, room_name, client_type
            )
        except Exception as e:
            raise AIAPIError(f"Failed to get next learning step: {str(e)}")
    
    # ============================================================================
    # UTILITY FUNCTIONS
    # ============================================================================
    
    def format_conversation_for_ai(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str = "",
        max_tokens: int = None,
        temperature: float = None
    ) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
        """Format conversation messages for AI API calls."""
        try:
            return self.conversation.format_conversation_for_ai(
                messages, system_prompt, max_tokens, temperature
            )
        except Exception as e:
            raise AIAPIError(f"Failed to format conversation: {str(e)}")
    
    def process_conversation_context(
        self,
        messages: List[Dict[str, Any]],
        context_type: str = "general"
    ) -> Dict[str, Any]:
        """Process conversation context for analysis."""
        try:
            return self.conversation.process_conversation_context(messages, context_type)
        except Exception as e:
            raise AIAPIError(f"Failed to process conversation context: {str(e)}")
    
    # ============================================================================
    # CONFIGURATION AND STATUS
    # ============================================================================
    
    def get_config(self) -> AIConfig:
        """Get the current configuration."""
        return self.config
    
    def get_status(self) -> Dict[str, Any]:
        """Get the status of all modules."""
        try:
            return {
                "config": "loaded",
                "api_factory": "initialized",
                "mode_manager": "initialized",
                "assessment": "initialized",
                "conversation": "initialized",
                "default_client_type": self.config.DEFAULT_CLIENT_TYPE,
                "available_clients": ["anthropic", "openai", "ollama"]
            }
        except Exception as e:
            return {
                "error": f"Failed to get status: {str(e)}",
                "config": "error"
            }


# Global instance for backward compatibility
_interface = OpenAIUtilsInterface()


# ============================================================================
# BACKWARD COMPATIBILITY FUNCTIONS
# ============================================================================

def get_client_type() -> str:
    """Get the appropriate client type based on configuration."""
    return _interface.get_client_type()


def get_ai_response(messages, system_prompt="", max_tokens=None, temperature=None, client_type=None) -> str:
    """Get AI response for conversation."""
    return _interface.get_ai_response(messages, system_prompt, max_tokens, temperature, client_type)


def call_anthropic_api(messages, **kwargs) -> str:
    """Call Anthropic API with messages."""
    return _interface.call_anthropic_api(messages, **kwargs)


def call_openai_api(messages, **kwargs) -> str:
    """Call OpenAI API with messages."""
    return _interface.call_openai_api(messages, **kwargs)


def call_ollama_api(messages, **kwargs) -> str:
    """Call Ollama API with messages."""
    return _interface.call_ollama_api(messages, **kwargs)


def get_modes_for_room(room_id: int) -> List[Dict[str, str]]:
    """Get modes for a specific room."""
    return _interface.get_modes_for_room(room_id)


def generate_room_modes(room_id: int, room_name: str, room_description: str = "") -> List[Dict[str, str]]:
    """Generate custom modes for a room."""
    return _interface.generate_room_modes(room_id, room_name, room_description)


def get_mode_system_prompt(mode_label: str) -> str:
    """Get system prompt for a specific mode."""
    return _interface.get_mode_system_prompt(mode_label)


def assess_learning_progression(messages, room_name="", client_type=None) -> Dict[str, Any]:
    """Assess learning progression based on conversation."""
    return _interface.assess_learning_progression(messages, room_name, client_type)


def get_progression_recommendation(assessment_result, room_name="", client_type=None) -> str:
    """Get recommendation based on assessment result."""
    return _interface.get_progression_recommendation(assessment_result, room_name, client_type)


def get_next_learning_step(current_level, room_name="", client_type=None) -> str:
    """Get next learning step based on current level."""
    return _interface.get_next_learning_step(current_level, room_name, client_type)


def generate_chat_introduction(room_name, room_description="", client_type=None) -> str:
    """Generate an AI introduction message for a new chat room."""
    return _interface.generate_chat_introduction(room_name, room_description, client_type)


def format_conversation_for_ai(messages, system_prompt="", max_tokens=None, temperature=None):
    """Format conversation messages for AI API calls."""
    return _interface.format_conversation_for_ai(messages, system_prompt, max_tokens, temperature)


def process_conversation_context(messages, context_type="general") -> Dict[str, Any]:
    """Process conversation context for analysis."""
    return _interface.process_conversation_context(messages, context_type)


def get_config() -> AIConfig:
    """Get the current configuration."""
    return _interface.get_config()


def get_status() -> Dict[str, Any]:
    """Get the status of all modules."""
    return _interface.get_status() 