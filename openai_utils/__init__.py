"""
OpenAI Utils Package

A modular, maintainable implementation of AI service utilities.
This package provides a clean interface for interacting with various AI APIs
while maintaining backward compatibility with the original openai_utils.py.
"""

# Import configuration and exceptions for easy access
from .config import AIConfig
from .exceptions import (
    AIAPIError,
    ConfigurationError,
    AssessmentError,
    ModeGenerationError,
    ConversationError,
    RateLimitError,
    AuthenticationError
)

# Import API clients
from .api_clients import (
    BaseAPIClient,
    AnthropicClient,
    OpenAIClient,
    OllamaClient,
    APIClientFactory,
    call_anthropic_api,
    call_openai_api,
    call_ollama_api
)

# Import mode manager
from .mode_manager import (
    ChatMode,
    ModeManager,
    get_modes_for_room,
    generate_room_modes,
    get_mode_system_prompt,
    get_client_type,
    MODES
)

# Import assessment module
from .assessment import (
    AssessmentResult,
    LearningAssessment,
    assess_learning_progression,
    get_progression_recommendation,
    get_next_learning_step
)

# Import conversation module
from .conversation import (
    ConversationMessage,
    ConversationManager,
    format_conversation_for_ai,
    get_ai_response,
    generate_chat_introduction,
    get_client_type
)

# Import main interface
from .main_interface import (
    OpenAIUtilsInterface,
    get_client_type,
    get_ai_response,
    call_anthropic_api,
    call_openai_api,
    call_ollama_api,
    get_modes_for_room,
    generate_room_modes,
    get_mode_system_prompt,
    assess_learning_progression,
    get_progression_recommendation,
    get_next_learning_step,
    generate_chat_introduction,
    format_conversation_for_ai,
    process_conversation_context,
    get_config,
    get_status
)

# Import the original functions for backward compatibility
# These will be gradually replaced as we implement the new modules
try:
    from openai_utils_legacy import (
        get_client_type,
        get_ai_response,
        get_modes_for_room,
        generate_room_modes,
        call_anthropic_api,
        call_openai_api,
        call_ollama_api,
        get_mode_system_prompt,
        assess_learning_progression,
        get_progression_recommendation,
        get_next_learning_step,
        generate_chat_introduction,
        BASE_MODES,
        MODES
    )
except ImportError:
    # If the legacy module doesn't exist yet, import from the original file
    from openai_utils_original import (
        get_client_type,
        get_ai_response,
        get_modes_for_room,
        generate_room_modes,
        call_anthropic_api,
        call_openai_api,
        call_ollama_api,
        get_mode_system_prompt,
        assess_learning_progression,
        get_progression_recommendation,
        get_next_learning_step,
        generate_chat_introduction,
        BASE_MODES,
        MODES
    )

__version__ = "2.0.0"
__author__ = "AI Collab Online Team"

# Export all the functions and classes for backward compatibility
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
    "get_status",
    
    # Legacy functions (for backward compatibility)
    "get_client_type",
    "get_ai_response", 
    "get_modes_for_room",
    "generate_room_modes",
    "call_anthropic_api",
    "call_openai_api",
    "call_ollama_api",
    "get_mode_system_prompt",
    "assess_learning_progression",
    "get_progression_recommendation",
    "get_next_learning_step",
    "generate_chat_introduction",
    "BASE_MODES",
    "MODES"
] 