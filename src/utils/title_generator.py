"""
AI-powered short title generation for rooms
Creates concise 1-5 word titles from room names and goals
"""

from typing import Optional
from flask import current_app
import re


def generate_short_title(room_name: str, room_goals: Optional[str] = None) -> str:
    """
    Generate a concise 1-5 word title for a room using AI.
    Falls back to smart extraction if AI fails.
    """
    try:
        # First try AI generation
        ai_title = _generate_ai_title(room_name, room_goals)
        if ai_title and _is_valid_short_title(ai_title):
            current_app.logger.info(f"AI title generated: '{room_name}' → '{ai_title}'")
            return ai_title
            
    except Exception as e:
        current_app.logger.warning(f"AI title generation failed: {e}")
    
    # Fallback to smart extraction
    try:
        extracted_title = _extract_smart_title(room_name)
        if extracted_title and _is_valid_short_title(extracted_title):
            current_app.logger.info(f"Smart extraction: '{room_name}' → '{extracted_title}'")
            return extracted_title
            
    except Exception as e:
        current_app.logger.warning(f"Smart extraction failed: {e}")
    
    # Final fallback to truncated original
    fallback_title = _truncate_title(room_name)
    current_app.logger.info(f"Fallback title: '{room_name}' → '{fallback_title}'")
    return fallback_title


def _generate_ai_title(room_name: str, room_goals: Optional[str] = None) -> Optional[str]:
    """Use AI to generate a concise room title."""
    try:
        from src.utils.openai_utils import call_anthropic_api
        
        # Create focused prompt for title generation
        context = f"Room name: {room_name}"
        if room_goals:
            context += f"\nRoom goals: {room_goals[:200]}"
        
        prompt = f"""Create a concise, catchy title (1-5 words) for this learning room:

{context}

Requirements:
- 1-5 words maximum
- Clear and descriptive
- Suitable for a learning/educational context
- Remove unnecessary words like "To learn about"
- Make it engaging and memorable

Examples:
"To learn about succulent plants and how to grow them" → "Succulent Gardening"
"To learn about the history of Japan" → "Japanese History"
"Entrepreneurship Business Hub" → "Business Hub"
"Science Study Group" → "Science Study"

Respond with ONLY the short title, nothing else."""

        response = call_anthropic_api(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0.3
        )
        
        if response and response.strip():
            # Clean and validate the response
            title = response.strip().strip('"\'')
            return title if len(title.split()) <= 5 else None
            
    except Exception as e:
        current_app.logger.warning(f"AI title generation error: {e}")
        return None


def _extract_smart_title(room_name: str) -> str:
    """Extract key words from room name using smart rules."""
    # Remove common prefixes and suffixes
    title = room_name.lower()
    
    # Remove common learning prefixes
    prefixes_to_remove = [
        "to learn about",
        "to learn",
        "to study",
        "learning about",
        "studying"
    ]
    
    for prefix in prefixes_to_remove:
        if title.startswith(prefix):
            title = title[len(prefix):].strip()
            break
    
    # Remove common words
    words_to_remove = {"the", "and", "of", "in", "on", "at", "for", "with", "about"}
    
    words = title.split()
    filtered_words = [word for word in words if word not in words_to_remove]
    
    # Take first 3-4 meaningful words
    key_words = filtered_words[:4] if len(filtered_words) > 3 else filtered_words
    
    # Capitalize properly
    result = " ".join(word.capitalize() for word in key_words)
    
    return result if result else room_name


def _truncate_title(room_name: str) -> str:
    """Simple truncation fallback."""
    words = room_name.split()
    if len(words) <= 5:
        return room_name
    return " ".join(words[:4]) + "..."


def _is_valid_short_title(title: str) -> bool:
    """Validate that a title meets our criteria."""
    if not title or not title.strip():
        return False
    
    words = title.strip().split()
    return 1 <= len(words) <= 5 and len(title) <= 50


def get_display_title(room) -> str:
    """
    Get the best title for display - generates short title on-the-fly.
    No database changes needed - works with existing room structure.
    """
    # Generate short title on-the-fly using smart extraction
    return _extract_smart_title(room.name)
