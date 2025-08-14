"""
Configuration management for AI services.

This module centralizes all configuration values that were previously hardcoded
in openai_utils.py, making the system more maintainable and configurable.
"""

import os
from typing import Optional


class AIConfig:
    """Centralized configuration for AI services."""
    
    # API Configuration
    ANTHROPIC_MODEL = "claude-3-haiku-20240307"
    OPENAI_MODEL = "gpt-4o-mini"
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL = "gemma3"
    
    # Default Parameters
    DEFAULT_MAX_TOKENS = 300
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_CLIENT_TYPE = "anthropic"
    
    # Assessment Configuration
    ASSESSMENT_CONFIDENCE_THRESHOLD = 0.8
    MIN_MESSAGES_FOR_ASSESSMENT = 4
    
    # Timeout Configuration
    REQUEST_TIMEOUT = 30  # seconds
    
    # Rate Limiting
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    @classmethod
    def get_anthropic_api_key(cls) -> Optional[str]:
        """Get Anthropic API key from environment."""
        return os.getenv("ANTHROPIC_API_KEY")
    
    @classmethod
    def get_openai_api_key(cls) -> Optional[str]:
        """Get OpenAI API key from environment."""
        return os.getenv("OPENAI_API_KEY")
    
    @classmethod
    def should_use_ollama(cls) -> bool:
        """Check if Ollama should be used."""
        return os.getenv("USE_OLLAMA", "false").lower() == "true"
    
    @classmethod
    def get_max_tokens(cls, custom_max_tokens: Optional[int] = None) -> int:
        """Get max tokens value, with fallback to default."""
        return custom_max_tokens or cls.DEFAULT_MAX_TOKENS
    
    @classmethod
    def get_temperature(cls, custom_temperature: Optional[float] = None) -> float:
        """Get temperature value, with fallback to default."""
        return custom_temperature or cls.DEFAULT_TEMPERATURE
    
    @classmethod
    def get_model_for_client(cls, client_type: str) -> str:
        """Get the appropriate model for the given client type."""
        model_map = {
            "anthropic": cls.ANTHROPIC_MODEL,
            "openai": cls.OPENAI_MODEL,
            "ollama": cls.OLLAMA_MODEL
        }
        return model_map.get(client_type, cls.ANTHROPIC_MODEL)
    
    @classmethod
    def validate_configuration(cls) -> bool:
        """Validate that at least one AI service is configured."""
        return bool(
            cls.get_anthropic_api_key() or 
            cls.get_openai_api_key() or 
            cls.should_use_ollama()
        ) 