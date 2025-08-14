"""
Custom exceptions for AI services.

This module provides specific exception types for different error scenarios
in the AI utilities, enabling better error handling and debugging.
"""


class AIAPIError(Exception):
    """Base exception for AI API errors."""
    
    def __init__(self, message: str, client_type: str = None, status_code: int = None):
        self.message = message
        self.client_type = client_type
        self.status_code = status_code
        super().__init__(self.message)
    
    def __str__(self):
        base_msg = f"AI API Error: {self.message}"
        if self.client_type:
            base_msg += f" (Client: {self.client_type})"
        if self.status_code:
            base_msg += f" (Status: {self.status_code})"
        return base_msg


class ConfigurationError(Exception):
    """Exception for configuration issues."""
    
    def __init__(self, message: str, missing_keys: list = None):
        self.message = message
        self.missing_keys = missing_keys or []
        super().__init__(self.message)
    
    def __str__(self):
        base_msg = f"Configuration Error: {self.message}"
        if self.missing_keys:
            base_msg += f" Missing keys: {', '.join(self.missing_keys)}"
        return base_msg


class AssessmentError(Exception):
    """Exception for assessment failures."""
    
    def __init__(self, message: str, chat_id: int = None, mode: str = None):
        self.message = message
        self.chat_id = chat_id
        self.mode = mode
        super().__init__(self.message)
    
    def __str__(self):
        base_msg = f"Assessment Error: {self.message}"
        if self.chat_id:
            base_msg += f" (Chat ID: {self.chat_id})"
        if self.mode:
            base_msg += f" (Mode: {self.mode})"
        return base_msg


class ModeGenerationError(Exception):
    """Exception for mode generation failures."""
    
    def __init__(self, message: str, room_id: int = None, goals: str = None):
        self.message = message
        self.room_id = room_id
        self.goals = goals
        super().__init__(self.message)
    
    def __str__(self):
        base_msg = f"Mode Generation Error: {self.message}"
        if self.room_id:
            base_msg += f" (Room ID: {self.room_id})"
        if self.goals:
            base_msg += f" (Goals: {self.goals[:50]}...)" if len(self.goals) > 50 else f" (Goals: {self.goals})"
        return base_msg


class ConversationError(Exception):
    """Exception for conversation formatting errors."""
    
    def __init__(self, message: str, chat_id: int = None):
        self.message = message
        self.chat_id = chat_id
        super().__init__(self.message)
    
    def __str__(self):
        base_msg = f"Conversation Error: {self.message}"
        if self.chat_id:
            base_msg += f" (Chat ID: {self.chat_id})"
        return base_msg


class RateLimitError(AIAPIError):
    """Exception for rate limiting errors."""
    
    def __init__(self, message: str = "Rate limit exceeded", client_type: str = None, retry_after: int = None):
        self.retry_after = retry_after
        super().__init__(message, client_type, 429)
    
    def __str__(self):
        base_msg = super().__str__()
        if self.retry_after:
            base_msg += f" (Retry after {self.retry_after} seconds)"
        return base_msg


class AuthenticationError(AIAPIError):
    """Exception for authentication errors."""
    
    def __init__(self, message: str = "Authentication failed", client_type: str = None):
        super().__init__(message, client_type, 401) 