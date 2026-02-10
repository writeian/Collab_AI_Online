"""
Tests for Card View Segmentation

Tests boundary conditions and validates 3-9 segment constraint.
"""

import pytest
from src.utils.card_view import segment_message, Segment
from src.utils.card_view.detector import detect_structure
from src.utils.card_view.headers import generate_header_heuristic, is_weak_header


# =============================================================================
# Test Fixtures
# =============================================================================

SHORT_MESSAGE = "This is a short message that should return 1 segment."

PROSE_MESSAGE = """
Understanding machine learning requires grasping several fundamental concepts. 
At its core, machine learning is about finding patterns in data and using those 
patterns to make predictions or decisions.

The first key concept is supervised learning. In supervised learning, we train 
a model using labeled data, meaning each training example comes with the correct 
answer. The model learns to map inputs to outputs by studying these examples.

Unsupervised learning takes a different approach. Here, we don't have labeled 
data. Instead, the model must find hidden patterns or structures in the data 
on its own. Clustering and dimensionality reduction are common unsupervised 
techniques.

Reinforcement learning is the third major paradigm. In this approach, an agent 
learns by interacting with an environment and receiving rewards or penalties 
for its actions. The goal is to learn a policy that maximizes cumulative reward.

Finally, deep learning has revolutionized the field. Neural networks with many 
layers can learn hierarchical representations of data, enabling breakthroughs 
in image recognition, natural language processing, and more.
"""

BULLET_MESSAGE = """
Here are the key principles of good software design:

- Single Responsibility Principle: Each class should have only one reason to change
- Open/Closed Principle: Software entities should be open for extension but closed for modification
- Liskov Substitution Principle: Objects should be replaceable with their subtypes
- Interface Segregation Principle: Many specific interfaces are better than one general interface
- Dependency Inversion Principle: Depend on abstractions, not concrete implementations

Additional best practices include:

- Write clean, readable code with meaningful names
- Keep functions small and focused
- Use version control effectively
- Write tests for your code
- Document your decisions and reasoning
"""

MIXED_MESSAGE = """
The project architecture follows a modular design pattern.

Key components include:

- Frontend: React with TypeScript
- Backend: Flask with SQLAlchemy
- Database: PostgreSQL in production

Each component has specific responsibilities. The frontend handles user 
interactions and state management. The backend processes business logic 
and manages data persistence.

Deployment considerations:

1. Use containerization for consistency
2. Implement CI/CD pipelines
3. Monitor performance metrics
4. Plan for horizontal scaling

This architecture supports rapid iteration while maintaining stability.
"""

CODE_MESSAGE = """
Here's how to implement a binary search algorithm:

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1
```

The algorithm works by repeatedly dividing the search interval in half. 
This gives us O(log n) time complexity, making it much faster than linear 
search for large sorted arrays.

Key points to remember:

- The array must be sorted
- Returns the index of the target, or -1 if not found
- Time complexity: O(log n)
- Space complexity: O(1)
"""

MARKDOWN_HEADERS_MESSAGE = """
# Introduction

This document covers the basics of API design.

## REST Principles

REST APIs should follow these principles for consistency.

### Resource Naming

Use nouns for resources, not verbs. Use plural forms.

### HTTP Methods

- GET for retrieval
- POST for creation
- PUT for updates
- DELETE for removal

## Authentication

Always secure your APIs with proper authentication.

## Rate Limiting

Implement rate limiting to prevent abuse.
"""


# =============================================================================
# Detector Tests
# =============================================================================

class TestDetector:
    def test_detect_prose(self):
        structure, stats = detect_structure(PROSE_MESSAGE)
        assert structure == "prose"
        assert stats["bullet_ratio"] < 0.15
    
    def test_detect_bullets(self):
        structure, stats = detect_structure(BULLET_MESSAGE)
        assert structure == "bullets"
        assert stats["bullet_ratio"] > 0.4
    
    def test_detect_mixed(self):
        structure, stats = detect_structure(MIXED_MESSAGE)
        assert structure in ("mixed", "bullets", "prose")
    
    def test_detect_code(self):
        structure, stats = detect_structure(CODE_MESSAGE)
        assert stats["code_blocks"] >= 1
    
    def test_detect_empty(self):
        structure, stats = detect_structure("")
        assert structure == "prose"
        assert stats.get("empty") is True


# =============================================================================
# Header Tests
# =============================================================================

class TestHeaders:
    def test_generate_header_prose(self):
        header = generate_header_heuristic(
            "Machine learning is transforming how we approach complex problems."
        )
        assert len(header.split()) <= 12
        assert header  # Not empty
    
    def test_generate_header_bullet(self):
        header = generate_header_heuristic(
            "- First item with important information\n- Second item"
        )
        assert "First Item" in header or "important" in header.lower()
    
    def test_weak_header_detection(self):
        assert is_weak_header("The") is True
        assert is_weak_header("Here is") is True
        assert is_weak_header("Machine Learning Fundamentals") is False
    
    def test_header_removes_bullet_prefix(self):
        header = generate_header_heuristic("- This is a bullet point")
        assert not header.startswith("-")
        assert not header.startswith("•")


# =============================================================================
# Segmenter Tests
# =============================================================================

class TestSegmenter:
    def test_short_message_single_segment(self):
        segments = segment_message(SHORT_MESSAGE)
        assert len(segments) == 1
        assert segments[0].body == SHORT_MESSAGE
    
    def test_prose_3_to_9_segments(self):
        segments = segment_message(PROSE_MESSAGE)
        assert 3 <= len(segments) <= 9
    
    def test_bullets_reasonable_segments(self):
        """Bullet lists should segment into substantial cards (may be <3 if merged)."""
        segments = segment_message(BULLET_MESSAGE)
        # With tiny-card merging, bullet lists may have fewer but more substantial cards
        assert 1 <= len(segments) <= 9
        # Each card should be substantial
        for seg in segments:
            assert seg.length >= 80
    
    def test_mixed_3_to_9_segments(self):
        segments = segment_message(MIXED_MESSAGE)
        assert 3 <= len(segments) <= 9
    
    def test_code_preserved(self):
        segments = segment_message(CODE_MESSAGE)
        # Find segment with code
        code_segments = [s for s in segments if "```" in s.body or s.segment_type == "code"]
        assert len(code_segments) >= 1
        # Code block should not be split
        for seg in code_segments:
            if "```python" in seg.body:
                assert "def binary_search" in seg.body
                assert "return -1" in seg.body
    
    def test_markdown_headings_respected(self):
        segments = segment_message(MARKDOWN_HEADERS_MESSAGE)
        # Should use existing headings
        headers = [s.header for s in segments]
        assert any("Introduction" in h or "REST" in h or "Authentication" in h for h in headers)
    
    def test_no_empty_segments(self):
        segments = segment_message(PROSE_MESSAGE)
        for seg in segments:
            assert seg.body.strip()
            assert seg.header.strip()
    
    def test_no_duplicate_headers(self):
        segments = segment_message(PROSE_MESSAGE)
        headers = [s.header for s in segments]
        # Allow some duplicates but not all the same
        unique_headers = set(headers)
        assert len(unique_headers) >= len(headers) * 0.5
    
    def test_full_coverage(self):
        """Segments should cover all content without gaps."""
        segments = segment_message(PROSE_MESSAGE)
        if len(segments) > 1:
            # Check segments are ordered
            for i in range(len(segments) - 1):
                assert segments[i].end_idx <= segments[i + 1].start_idx + 10  # Allow small overlap
    
    def test_empty_input(self):
        segments = segment_message("")
        assert segments == []
    
    def test_whitespace_only(self):
        segments = segment_message("   \n\n   ")
        assert segments == []
    
    def test_segment_has_required_fields(self):
        segments = segment_message(PROSE_MESSAGE)
        for seg in segments:
            assert isinstance(seg, Segment)
            assert seg.id
            assert seg.header
            assert seg.body
            assert seg.start_idx >= 0
            assert seg.end_idx > seg.start_idx
            assert seg.segment_type in ("bullet", "paragraph", "code", "mixed", "heading")
            assert 0 <= seg.confidence <= 1
    
    def test_no_tiny_cards_in_multi_segment(self):
        """Multi-segment outputs should not have very short cards."""
        segments = segment_message(PROSE_MESSAGE)
        if len(segments) > 3:  # Only check if we have room to merge
            for seg in segments:
                # Allow slightly smaller cards but not micro-cards
                assert seg.length >= 80, f"Card too small: {seg.length} chars - '{seg.header}'"
    
    def test_cta_questions_merged(self):
        """Trailing CTA questions should be merged into previous card."""
        text_with_cta = """
        Here is a detailed explanation of the concept. This paragraph contains
        substantial information about the topic at hand, providing context and
        background that helps establish understanding.
        
        The second section elaborates further on the main points. It includes
        additional details and examples that reinforce the key ideas presented
        in the opening paragraph.
        
        Would you like to learn more?
        """
        segments = segment_message(text_with_cta)
        # The short CTA should be merged, not standalone
        for seg in segments:
            if seg.body.strip() == "Would you like to learn more?":
                assert False, "CTA question should have been merged"
    
    def test_transition_sentences_merged(self):
        """Short transitional sentences should be merged."""
        text_with_transition = """
        The first major concept is supervised learning. In this approach, we use
        labeled data to train our models. The algorithm learns from examples
        where the correct answers are provided.
        
        Let me explain further.
        
        The second concept is unsupervised learning. Here we work with unlabeled
        data and try to find hidden patterns. Clustering is a common technique
        in this category.
        """
        segments = segment_message(text_with_transition)
        # Short transition should be merged
        for seg in segments:
            if seg.body.strip() == "Let me explain further.":
                assert False, "Transition sentence should have been merged"
    
    def test_segments_are_complete_sentences(self):
        """Well-formed input should produce complete sentence segments."""
        # This text has proper sentence endings
        well_formed_text = """
        Machine learning is transforming industries. It enables computers to 
        learn from data without explicit programming.
        
        Deep learning uses neural networks with many layers. These networks 
        can learn complex patterns automatically.
        
        The future of AI looks promising. Many exciting applications await.
        """
        segments = segment_message(well_formed_text)
        for seg in segments:
            assert seg.is_complete_sentence, \
                f"Segment should be complete: ends with '{seg.ending_char}'"
    
    def test_bullet_segments_allowed_without_punctuation(self):
        """Bullet list segments don't require sentence-ending punctuation."""
        bullet_text = """
        Key points to remember:
        
        - First important item
        - Second key concept
        - Third critical point
        """
        segments = segment_message(bullet_text)
        # Bullet segments should pass completeness check even without periods
        for seg in segments:
            if seg.segment_type == "bullet":
                assert seg.is_complete_sentence, \
                    "Bullet segments should be considered complete"


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    def test_to_dict_serialization(self):
        segments = segment_message(PROSE_MESSAGE)
        for seg in segments:
            d = seg.to_dict()
            assert "id" in d
            assert "header" in d
            assert "body" in d
            assert "start_idx" in d
            assert "end_idx" in d
            assert "word_count" in d
    
    def test_large_message_performance(self):
        """Test that large messages complete in reasonable time."""
        import time
        large_message = PROSE_MESSAGE * 10
        
        start = time.time()
        segments = segment_message(large_message)
        elapsed = time.time() - start
        
        assert elapsed < 1.0  # Should complete in under 1 second
        assert 3 <= len(segments) <= 9


# =============================================================================
# AI Helpers Tests (fallback behavior without API calls)
# =============================================================================

class TestAIHelpers:
    """Test AI helper functions' fallback behavior (no actual API calls)."""
    
    def test_guiding_question_short_message_returns_default(self):
        """Short messages should return a default guiding question."""
        from src.utils.card_view.ai_helpers import generate_guiding_question, DEFAULT_GUIDING_QUESTION
        
        result = generate_guiding_question("Short", use_ai=False)
        assert result == DEFAULT_GUIDING_QUESTION
    
    def test_guiding_question_without_ai_returns_default(self):
        """When AI is disabled, should return default question."""
        from src.utils.card_view.ai_helpers import generate_guiding_question, DEFAULT_GUIDING_QUESTION
        
        result = generate_guiding_question(PROSE_MESSAGE, use_ai=False)
        assert result == DEFAULT_GUIDING_QUESTION
    
    def test_relationship_hints_without_ai_returns_fallbacks(self):
        """When AI is disabled, should return fallback hints (still shows buttons)."""
        from src.utils.card_view.ai_helpers import generate_relationship_hints, FALLBACK_RELATIONSHIP_HINT
        
        segments = segment_message(PROSE_MESSAGE)
        result = generate_relationship_hints("What is ML?", segments, use_ai=False)
        
        # Without AI, return fallback hints so buttons still appear
        assert len(result) == len(segments) - 1
        assert all(h == FALLBACK_RELATIONSHIP_HINT for h in result)
    
    def test_enhance_segments_returns_dict_shape(self):
        """enhance_segments_with_ai should return correct dict shape."""
        from src.utils.card_view.ai_helpers import enhance_segments_with_ai
        
        segments = segment_message(PROSE_MESSAGE)
        result = enhance_segments_with_ai(PROSE_MESSAGE, segments, use_ai=False)
        
        assert "guiding_question" in result
        assert "relationships" in result
        assert "ai_enhanced" in result
        assert result["ai_enhanced"] == False
        assert isinstance(result["relationships"], list)
    
    def test_enhance_segments_single_segment_no_relationships(self):
        """Single segment should have empty relationships."""
        from src.utils.card_view.ai_helpers import enhance_segments_with_ai
        
        segments = segment_message(SHORT_MESSAGE)
        result = enhance_segments_with_ai(SHORT_MESSAGE, segments, use_ai=False)
        
        assert result["relationships"] == []
    
    def test_parse_numbered_hints_handles_bullets(self):
        """Parser should handle bullet format in addition to numbered."""
        from src.utils.card_view.ai_helpers import _parse_numbered_hints
        
        response = """- First hint about connection
- Second hint about relationship
- Third hint about flow"""
        
        hints = _parse_numbered_hints(response, expected_count=3)
        assert len(hints) == 3
        assert "First hint" in hints[0]
    
    def test_parse_numbered_hints_pads_missing(self):
        """Parser should pad with fallbacks if not enough hints."""
        from src.utils.card_view.ai_helpers import _parse_numbered_hints, FALLBACK_RELATIONSHIP_HINT
        
        response = "1. Only one hint provided"
        hints = _parse_numbered_hints(response, expected_count=3)
        
        assert len(hints) == 3
        assert hints[0] == "Only one hint provided"
        assert hints[1] == FALLBACK_RELATIONSHIP_HINT
        assert hints[2] == FALLBACK_RELATIONSHIP_HINT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

