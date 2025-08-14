"""
API Clients for AI Services.

This module provides a unified interface for interacting with different AI APIs
(OpenAI, Anthropic, Ollama) with consistent error handling and configuration.
"""

import os
import requests
import time
import json
from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, Any, Optional
from flask import current_app

from .config import AIConfig
from .exceptions import (
    AIAPIError,
    ConfigurationError,
    RateLimitError,
    AuthenticationError
)


class BaseAPIClient(ABC):
    """Abstract base class for AI API clients."""
    
    def __init__(self, client_type: str):
        self.client_type = client_type
        self.config = AIConfig()
    
    @abstractmethod
    def call_api(self, messages: List[Dict], system_prompt: str = None, 
                 max_tokens: int = None) -> Tuple[str, bool]:
        """
        Call the AI API with the given messages.
        
        Args:
            messages: List of message dictionaries
            system_prompt: Optional system prompt
            max_tokens: Optional max tokens limit
            
        Returns:
            Tuple of (response_text, success_boolean)
        """
        pass
    
    def _handle_error(self, error: Exception, status_code: int = None) -> Tuple[str, bool]:
        """Handle API errors consistently."""
        error_msg = str(error)
        
        # Log the error
        if current_app:
            current_app.logger.error(f"{self.client_type} API Error: {error_msg}")
        
        # Raise appropriate exception
        if status_code == 429:
            raise RateLimitError(f"Rate limit exceeded for {self.client_type}", self.client_type)
        elif status_code == 401:
            raise AuthenticationError(f"Authentication failed for {self.client_type}", self.client_type)
        else:
            raise AIAPIError(f"{self.client_type} API error: {error_msg}", self.client_type, status_code)
    
    def _validate_messages(self, messages: List[Dict]) -> None:
        """Validate message format."""
        if not messages:
            raise ValueError("Messages list cannot be empty")
        
        for msg in messages:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                raise ValueError("Each message must be a dict with 'role' and 'content' keys")


class AnthropicClient(BaseAPIClient):
    """Client for Anthropic Claude API."""
    
    def __init__(self):
        super().__init__("anthropic")
        self.api_key = self.config.get_anthropic_api_key()
        if not self.api_key:
            raise ConfigurationError("ANTHROPIC_API_KEY not found in environment")
        
        self.model = self.config.get_model_for_client("anthropic")
        self.base_url = "https://api.anthropic.com/v1/messages"
    
    def call_api(self, messages: List[Dict], system_prompt: str = None, 
                 max_tokens: int = None) -> Tuple[str, bool]:
        """Call Anthropic Claude API."""
        try:
            self._validate_messages(messages)
            
            # Convert messages to Anthropic format
            anthropic_messages = []
            for msg in messages:
                if msg['role'] == 'user':
                    anthropic_messages.append({"role": "user", "content": msg['content']})
                elif msg['role'] == 'assistant':
                    anthropic_messages.append({"role": "assistant", "content": msg['content']})
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": anthropic_messages,
                "max_tokens": self.config.get_max_tokens(max_tokens),
                "temperature": self.config.get_temperature()
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            # Make API request
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=self.config.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['content'][0]['text'], True
            else:
                return self._handle_error(
                    Exception(f"API returned status {response.status_code}: {response.text}"),
                    response.status_code
                )
                
        except Exception as e:
            return self._handle_error(e)


class OpenAIClient(BaseAPIClient):
    """Client for OpenAI API."""
    
    def __init__(self):
        super().__init__("openai")
        self.api_key = self.config.get_openai_api_key()
        if not self.api_key:
            raise ConfigurationError("OPENAI_API_KEY not found in environment")
        
        self.model = self.config.get_model_for_client("openai")
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    def call_api(self, messages: List[Dict], system_prompt: str = None, 
                 max_tokens: int = None) -> Tuple[str, bool]:
        """Call OpenAI API."""
        try:
            self._validate_messages(messages)
            
            # Prepare messages for OpenAI
            openai_messages = []
            if system_prompt:
                openai_messages.append({"role": "system", "content": system_prompt})
            
            for msg in messages:
                openai_messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": openai_messages,
                "max_tokens": self.config.get_max_tokens(max_tokens),
                "temperature": self.config.get_temperature()
            }
            
            # Make API request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=self.config.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'], True
            else:
                return self._handle_error(
                    Exception(f"API returned status {response.status_code}: {response.text}"),
                    response.status_code
                )
                
        except Exception as e:
            return self._handle_error(e)


class OllamaClient(BaseAPIClient):
    """Client for local Ollama API."""
    
    def __init__(self):
        super().__init__("ollama")
        self.model = self.config.get_model_for_client("ollama")
        self.base_url = self.config.OLLAMA_BASE_URL
    
    def call_api(self, messages: List[Dict], system_prompt: str = None, 
                 max_tokens: int = None) -> Tuple[str, bool]:
        """Call local Ollama API."""
        try:
            self._validate_messages(messages)
            
            # Prepare messages for Ollama
            ollama_messages = []
            if system_prompt:
                ollama_messages.append({"role": "system", "content": system_prompt})
            
            for msg in messages:
                ollama_messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": ollama_messages,
                "stream": False
            }
            
            if max_tokens:
                payload["options"] = {"num_predict": max_tokens}
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.config.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['message']['content'], True
            else:
                return self._handle_error(
                    Exception(f"API returned status {response.status_code}: {response.text}"),
                    response.status_code
                )
                
        except Exception as e:
            return self._handle_error(e)


class APIClientFactory:
    """Factory for creating API clients based on configuration."""
    
    def __init__(self):
        self.config = AIConfig()
    
    def get_client(self) -> BaseAPIClient:
        """Get the appropriate API client based on configuration."""
        if self.config.should_use_ollama():
            return OllamaClient()
        elif self.config.get_anthropic_api_key():
            return AnthropicClient()
        elif self.config.get_openai_api_key():
            return OpenAIClient()
        else:
            raise ConfigurationError("No AI service configured. Please set API keys or enable Ollama.")
    
    def get_response(self, client_type: str, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Get response from the specified AI client.
        
        Args:
            client_type: Type of client to use ('anthropic', 'openai', 'ollama')
            messages: List of message dictionaries
            **kwargs: Additional parameters for the API call
            
        Returns:
            AI response string
        """
        try:
            if client_type == 'anthropic':
                client = AnthropicClient()
            elif client_type == 'openai':
                client = OpenAIClient()
            elif client_type == 'ollama':
                client = OllamaClient()
            else:
                raise ConfigurationError(f"Unknown client type: {client_type}")
            
            response, success = client.call_api(messages, **kwargs)
            if success:
                return response
            else:
                raise AIAPIError(f"API call failed: {response}", client_type=client_type)
        except Exception as e:
            raise AIAPIError(f"Failed to get response from {client_type}: {str(e)}", client_type=client_type)
    
    def _get_client_type(self) -> str:
        """Get the appropriate client type based on configuration."""
        try:
            # Check environment variables for client preference
            import os
            
            # Priority order: environment variable > config default
            if os.getenv('ANTHROPIC_API_KEY'):
                return 'anthropic'
            elif os.getenv('OPENAI_API_KEY'):
                return 'openai'
            elif os.getenv('OLLAMA_BASE_URL'):
                return 'ollama'
            else:
                # Fallback to config default
                return self.config.DEFAULT_CLIENT_TYPE
                
        except Exception as e:
            raise ConfigurationError(f"Failed to determine client type: {str(e)}")


# Convenience functions for backward compatibility
def call_anthropic_api(messages: List[Dict], system_prompt: str = None, 
                      max_tokens: int = None) -> Tuple[str, bool]:
    """Call Anthropic API (backward compatibility)."""
    client = AnthropicClient()
    return client.call_api(messages, system_prompt, max_tokens)


def call_openai_api(messages: List[Dict], system_prompt: str = None, 
                   max_tokens: int = None) -> Tuple[str, bool]:
    """Call OpenAI API (backward compatibility)."""
    client = OpenAIClient()
    return client.call_api(messages, system_prompt, max_tokens)


def call_ollama_api(messages: List[Dict], system_prompt: str = None, 
                   max_tokens: int = None) -> Tuple[str, bool]:
    """Call Ollama API (backward compatibility)."""
    client = OllamaClient()
    return client.call_api(messages, system_prompt, max_tokens) 