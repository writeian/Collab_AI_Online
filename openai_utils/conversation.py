"""
Conversation Management and Formatting.

This module handles conversation formatting, message processing,
and conversation state management for AI interactions.
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from .config import AIConfig
from .exceptions import ConversationError, ConfigurationError
from .api_clients import APIClientFactory


@dataclass
class ConversationMessage:
    """Data class for conversation messages."""
    role: str
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class ConversationManager:
    """Manages conversation formatting and processing."""
    
    def __init__(self):
        self.config = AIConfig()
        self.api_factory = APIClientFactory()
    
    def format_conversation_for_ai(
        self, 
        messages: List[Dict[str, Any]], 
        system_prompt: str = "",
        max_tokens: int = None,
        temperature: float = None
    ) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
        """
        Format conversation messages for AI API calls.
        
        Args:
            messages: List of message dictionaries
            system_prompt: System prompt to prepend
            max_tokens: Maximum tokens for response
            temperature: Temperature for response generation
            
        Returns:
            Tuple of (formatted_messages, parameters)
        """
        try:
            # Set default parameters
            max_tokens = max_tokens or self.config.DEFAULT_MAX_TOKENS
            temperature = temperature or self.config.DEFAULT_TEMPERATURE
            
            # Format messages for AI
            formatted_messages = []
            
            # Add system prompt if provided
            if system_prompt:
                formatted_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # Process user messages
            for msg in messages:
                if msg.get('is_ai'):
                    role = "assistant"
                else:
                    role = "user"
                
                content = msg.get('content', '').strip()
                if content:  # Only add non-empty messages
                    formatted_messages.append({
                        "role": role,
                        "content": content
                    })
            
            # Prepare parameters
            parameters = {
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            return formatted_messages, parameters
            
        except Exception as e:
            raise ConversationError(f"Failed to format conversation: {str(e)}")
    
    def get_ai_response(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str = "",
        max_tokens: int = None,
        temperature: float = None,
        client_type: str = None
    ) -> str:
        """
        Get AI response for conversation.
        
        Args:
            messages: List of message dictionaries
            system_prompt: System prompt to prepend
            max_tokens: Maximum tokens for response
            temperature: Temperature for response generation
            client_type: Specific AI client to use
            
        Returns:
            AI response string
        """
        try:
            # Format conversation
            formatted_messages, parameters = self.format_conversation_for_ai(
                messages, system_prompt, max_tokens, temperature
            )
            
            # Get client type if not specified
            if not client_type:
                client_type = self._get_client_type()
            
            # Get AI response
            response = self.api_factory.get_response(
                client_type=client_type,
                messages=formatted_messages,
                **parameters
            )
            
            return response
            
        except Exception as e:
            raise ConversationError(f"Failed to get AI response: {str(e)}")
    
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
    
    def generate_chat_introduction(
        self,
        room_name: str,
        room_description: str = "",
        client_type: str = None
    ) -> str:
        """
        Generate an AI introduction message for a new chat room.
        
        Args:
            room_name: Name of the chat room
            room_description: Description of the room
            client_type: Specific AI client to use
            
        Returns:
            Introduction message string
        """
        try:
            # Create introduction prompt
            intro_prompt = f"""You are an AI assistant in a collaborative learning environment. 
            The room is called "{room_name}"."""
            
            if room_description:
                intro_prompt += f"\n\nRoom description: {room_description}"
            
            intro_prompt += """

            Please provide a warm, welcoming introduction that:
            1. Greets the participants
            2. Explains that you're here to help with their learning
            3. Encourages collaboration and discussion
            4. Mentions that you can help with questions, explanations, and guidance
            5. Keeps it friendly and engaging but professional
            
            Keep your response under 150 words and make it feel natural and conversational."""
            
            # Get AI response
            response = self.get_ai_response(
                messages=[],  # Empty conversation for introduction
                system_prompt=intro_prompt,
                max_tokens=200,
                temperature=0.8,
                client_type=client_type
            )
            
            return response.strip()
            
        except Exception as e:
            raise ConversationError(f"Failed to generate chat introduction: {str(e)}")
    
    def process_conversation_context(
        self,
        messages: List[Dict[str, Any]],
        context_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Process conversation context for analysis.
        
        Args:
            messages: List of message dictionaries
            context_type: Type of context analysis
            
        Returns:
            Processed context dictionary
        """
        try:
            context = {
                "message_count": len(messages),
                "user_messages": 0,
                "ai_messages": 0,
                "total_content_length": 0,
                "context_type": context_type
            }
            
            for msg in messages:
                content = msg.get('content', '')
                context["total_content_length"] += len(content)
                
                if msg.get('is_ai'):
                    context["ai_messages"] += 1
                else:
                    context["user_messages"] += 1
            
            return context
            
        except Exception as e:
            raise ConversationError(f"Failed to process conversation context: {str(e)}")


# Convenience functions for backward compatibility
def format_conversation_for_ai(messages, system_prompt="", max_tokens=None, temperature=None):
    """Format conversation messages for AI API calls."""
    manager = ConversationManager()
    return manager.format_conversation_for_ai(messages, system_prompt, max_tokens, temperature)


def get_ai_response(messages, system_prompt="", max_tokens=None, temperature=None, client_type=None):
    """Get AI response for conversation."""
    manager = ConversationManager()
    return manager.get_ai_response(messages, system_prompt, max_tokens, temperature, client_type)


def generate_chat_introduction(room_name, room_description="", client_type=None):
    """Generate an AI introduction message for a new chat room."""
    manager = ConversationManager()
    return manager.generate_chat_introduction(room_name, room_description, client_type)


def get_client_type():
    """Get the appropriate client type based on configuration."""
    manager = ConversationManager()
    return manager._get_client_type() 