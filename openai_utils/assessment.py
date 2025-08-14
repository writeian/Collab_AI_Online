"""
Learning Progression Assessment.

This module handles the assessment of student learning progression
and provides recommendations for next steps.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .config import AIConfig
from .exceptions import AssessmentError, ConfigurationError
from .api_clients import APIClientFactory
from .mode_manager import ModeManager


@dataclass
class AssessmentResult:
    """Data class for assessment results."""
    ready: bool
    confidence: float
    feedback: str
    recommendations: List[str]
    next_steps: List[str]


class LearningAssessment:
    """Handles learning progression assessment."""
    
    def __init__(self):
        self.config = AIConfig()
        self.api_factory = APIClientFactory()
        self.mode_manager = ModeManager()
    
    def assess_progression(self, chat, target_mode: str = None) -> AssessmentResult:
        """
        Assess learning progression for a chat.
        
        Args:
            chat: Chat object with messages
            target_mode: Optional target mode to assess against
            
        Returns:
            AssessmentResult with assessment details
            
        Raises:
            AssessmentError: If assessment fails
        """
        if not chat or not chat.messages:
            return AssessmentResult(
                ready=False,
                confidence=0.0,
                feedback="No messages to assess",
                recommendations=["Start a conversation to begin assessment"],
                next_steps=["Send your first message"]
            )
        
        # Check minimum message threshold
        if len(chat.messages) < self.config.MIN_MESSAGES_FOR_ASSESSMENT:
            return AssessmentResult(
                ready=False,
                confidence=0.0,
                feedback=f"Need at least {self.config.MIN_MESSAGES_FOR_ASSESSMENT} messages for assessment",
                recommendations=["Continue the conversation"],
                next_steps=["Send more messages"]
            )
        
        try:
            client = self.api_factory.get_client()
        except ConfigurationError:
            raise AssessmentError("No AI service configured for assessment", chat.id, target_mode)
        
        # Format conversation for assessment
        conversation_text = self._format_conversation_for_assessment(chat.messages)
        
        # Get target mode context
        target_context = ""
        if target_mode:
            target_context = f"\nTarget Learning Mode: {target_mode}"
        
        # Create assessment prompt
        system_prompt = f"""You are an expert educational assessor. Analyze the student's learning progression and provide a comprehensive assessment.

Assessment Criteria:
1. **Readiness**: Is the student ready to progress to the next learning step?
2. **Confidence**: How confident are you in this assessment (0.0-1.0)?
3. **Feedback**: Specific, constructive feedback on their current level
4. **Recommendations**: 2-3 specific actions they should take
5. **Next Steps**: 2-3 concrete next learning steps

{target_context}

Return your response as a JSON object with these fields:
- "ready": boolean
- "confidence": float (0.0-1.0)
- "feedback": string
- "recommendations": array of strings
- "next_steps": array of strings"""

        user_message = f"Assess this learning conversation:\n\n{conversation_text}"
        
        try:
            response, success = client.call_api(
                messages=[{"role": "user", "content": user_message}],
                system_prompt=system_prompt,
                max_tokens=800
            )
            
            if not success:
                raise AssessmentError("API call failed", chat.id, target_mode)
            
            # Parse the response
            try:
                assessment_data = json.loads(response)
                
                return AssessmentResult(
                    ready=assessment_data.get('ready', False),
                    confidence=float(assessment_data.get('confidence', 0.0)),
                    feedback=assessment_data.get('feedback', 'Assessment incomplete'),
                    recommendations=assessment_data.get('recommendations', []),
                    next_steps=assessment_data.get('next_steps', [])
                )
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                raise AssessmentError(f"Invalid assessment response: {str(e)}", chat.id, target_mode)
                
        except Exception as e:
            if isinstance(e, AssessmentError):
                raise
            raise AssessmentError(f"Assessment failed: {str(e)}", chat.id, target_mode)
    
    def get_progression_recommendation(self, chat) -> Dict[str, Any]:
        """
        Get progression recommendation for a chat.
        
        Args:
            chat: Chat object with messages
            
        Returns:
            Dictionary with recommendation data
        """
        try:
            assessment = self.assess_progression(chat)
            
            # Check confidence threshold
            if assessment.confidence < self.config.ASSESSMENT_CONFIDENCE_THRESHOLD:
                return {
                    "ready": False,
                    "message": "More conversation needed for confident assessment",
                    "confidence": assessment.confidence,
                    "recommendations": assessment.recommendations
                }
            
            return {
                "ready": assessment.ready,
                "message": assessment.feedback,
                "confidence": assessment.confidence,
                "recommendations": assessment.recommendations,
                "next_steps": assessment.next_steps
            }
            
        except AssessmentError as e:
            return {
                "ready": False,
                "message": f"Assessment error: {str(e)}",
                "confidence": 0.0,
                "recommendations": ["Try again later"]
            }
    
    def get_next_learning_step(self, chat) -> Optional[Dict[str, Any]]:
        """
        Get the next recommended learning step.
        
        Args:
            chat: Chat object with messages
            
        Returns:
            Dictionary with next step information or None
        """
        try:
            assessment = self.assess_progression(chat)
            
            if not assessment.ready or assessment.confidence < self.config.ASSESSMENT_CONFIDENCE_THRESHOLD:
                return None
            
            # Get available modes for the room
            if hasattr(chat, 'room') and chat.room:
                modes = self.mode_manager.get_modes_for_room(chat.room)
                
                # Find the next logical step based on current progress
                current_mode = getattr(chat, 'current_mode', None)
                next_mode = self._determine_next_mode(modes, current_mode, assessment)
                
                if next_mode:
                    return {
                        "mode": next_mode,
                        "label": modes[next_mode].label,
                        "prompt": modes[next_mode].prompt,
                        "reasoning": assessment.feedback
                    }
            
            return None
            
        except Exception as e:
            return None
    
    def _format_conversation_for_assessment(self, messages: List) -> str:
        """
        Format conversation messages for assessment.
        
        Args:
            messages: List of message objects
            
        Returns:
            Formatted conversation string
        """
        formatted_messages = []
        
        for msg in messages:
            role = "Student" if msg.user_id else "AI Assistant"
            content = msg.content.strip()
            
            if content:
                formatted_messages.append(f"{role}: {content}")
        
        return "\n\n".join(formatted_messages)
    
    def _determine_next_mode(self, modes: Dict, current_mode: str, assessment: AssessmentResult) -> Optional[str]:
        """
        Determine the next logical learning mode.
        
        Args:
            modes: Available modes dictionary
            current_mode: Current mode identifier
            assessment: Assessment result
            
        Returns:
            Next mode identifier or None
        """
        # Define learning progression order
        progression_order = [
            "explore", "focus", "context", "proposal", "outline",
            "draft", "revise", "evidence", "citation", "reflect"
        ]
        
        if current_mode in progression_order:
            current_index = progression_order.index(current_mode)
            next_index = current_index + 1
            
            if next_index < len(progression_order):
                next_mode = progression_order[next_index]
                if next_mode in modes:
                    return next_mode
        
        # Fallback: return first available mode
        if modes:
            return list(modes.keys())[0]
        
        return None
    
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
            raise AssessmentError(f"Failed to process conversation context: {str(e)}")


# Convenience functions for backward compatibility
def assess_learning_progression(chat, target_mode: str = None) -> AssessmentResult:
    """Assess learning progression (backward compatibility)."""
    assessor = LearningAssessment()
    return assessor.assess_progression(chat, target_mode)


def get_progression_recommendation(chat) -> Dict[str, Any]:
    """Get progression recommendation (backward compatibility)."""
    assessor = LearningAssessment()
    return assessor.get_progression_recommendation(chat)


def get_next_learning_step(chat) -> Optional[Dict[str, Any]]:
    """Get next learning step (backward compatibility)."""
    assessor = LearningAssessment()
    return assessor.get_next_learning_step(chat) 