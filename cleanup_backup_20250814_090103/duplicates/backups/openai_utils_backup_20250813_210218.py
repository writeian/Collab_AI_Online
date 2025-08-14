"""
Compatibility Wrapper for OpenAI Utils.

This file provides backward compatibility for the old openai_utils.py
by redirecting all imports to the new modular structure.
"""

# Import all functions from the new modular structure
from openai_utils import *

# Log the migration
import logging
logger = logging.getLogger(__name__)
logger.info("Using new modular openai_utils structure")

# Re-export all symbols for backward compatibility
__all__ = [
    # Configuration and exceptions
    "AIConfig",
    "AIAPIError",
    "ConfigurationError", 
    "AssessmentError",
    "ModeGenerationError",
    "ConversationError",
    "RateLimitError",
    "AuthenticationError",
    
    # API Clients
    "BaseAPIClient",
    "AnthropicClient",
    "OpenAIClient",
    "OllamaClient",
    "APIClientFactory",
    "call_anthropic_api",
    "call_openai_api",
    "call_ollama_api",
    
    # Mode Manager
    "ChatMode",
    "ModeManager",
    "get_modes_for_room",
    "generate_room_modes",
    "get_mode_system_prompt",
    "get_client_type",
    "MODES",
    
    # Assessment
    "AssessmentResult",
    "LearningAssessment",
    "assess_learning_progression",
    "get_progression_recommendation",
    "get_next_learning_step",
    
    # Conversation
    "ConversationMessage",
    "ConversationManager",
    "format_conversation_for_ai",
    "get_ai_response",
    "generate_chat_introduction",
    "get_client_type",
    
    # Main Interface
    "OpenAIUtilsInterface",
    "get_client_type",
    "get_ai_response",
    "call_anthropic_api",
    "call_openai_api",
    "call_ollama_api",
    "get_modes_for_room",
    "generate_room_modes",
    "get_mode_system_prompt",
    "assess_learning_progression",
    "get_progression_recommendation",
    "get_next_learning_step",
    "generate_chat_introduction",
    "format_conversation_for_ai",
    "process_conversation_context",
    "get_config",
    "get_status"
]

# Print deprecation warning
import warnings
warnings.warn(
    "openai_utils.py is deprecated. Please use the new modular structure: from openai_utils import *",
    DeprecationWarning,
    stacklevel=2
)
