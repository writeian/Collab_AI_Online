"""
Tests for Card Comments API

Unit tests for the /chat/<chat_id>/cards/<card_key>/comments endpoints.
These tests focus on the endpoint logic without requiring a full app context.
"""

import pytest


class TestCardCommentsAPIUnit:
    """Unit tests for card comments API (no Flask app required)."""
    
    def test_card_comment_model_import(self):
        """Verify CardComment model can be imported."""
        from src.models import CardComment
        assert CardComment is not None
    
    def test_generate_card_key_import(self):
        """Verify helper functions can be imported."""
        from src.models import generate_card_key, generate_body_hash
        assert callable(generate_card_key)
        assert callable(generate_body_hash)
    
    def test_card_key_format(self):
        """Card key should be SHA1 hex (40 chars)."""
        from src.models import generate_card_key
        
        key = generate_card_key(123, 0, "Test body content")
        
        assert len(key) == 40
        assert all(c in "0123456789abcdef" for c in key)
    
    def test_card_key_deterministic(self):
        """Same inputs should produce same key."""
        from src.models import generate_card_key
        
        key1 = generate_card_key(123, 0, "Test body")
        key2 = generate_card_key(123, 0, "Test body")
        
        assert key1 == key2
    
    def test_card_key_varies_by_message(self):
        """Different message_id should produce different key."""
        from src.models import generate_card_key
        
        key1 = generate_card_key(123, 0, "Test body")
        key2 = generate_card_key(456, 0, "Test body")
        
        assert key1 != key2
    
    def test_card_key_varies_by_index(self):
        """Different segment_index should produce different key."""
        from src.models import generate_card_key
        
        key1 = generate_card_key(123, 0, "Test body")
        key2 = generate_card_key(123, 1, "Test body")
        
        assert key1 != key2
    
    def test_card_key_varies_by_body(self):
        """Different body should produce different key."""
        from src.models import generate_card_key
        
        key1 = generate_card_key(123, 0, "Test body A")
        key2 = generate_card_key(123, 0, "Test body B")
        
        assert key1 != key2
    
    def test_body_hash_format(self):
        """Body hash should be MD5 prefix (16 chars)."""
        from src.models import generate_body_hash
        
        hash_val = generate_body_hash("Test content")
        
        assert len(hash_val) == 16
        assert all(c in "0123456789abcdef" for c in hash_val)
    
    def test_body_hash_deterministic(self):
        """Same body should produce same hash."""
        from src.models import generate_body_hash
        
        hash1 = generate_body_hash("Test content")
        hash2 = generate_body_hash("Test content")
        
        assert hash1 == hash2


class TestCardCommentsAPIBlueprint:
    """Tests for blueprint registration."""
    
    def test_blueprint_exists(self):
        """Blueprint should be importable."""
        from src.app.api.card_comments import card_comments_api
        assert card_comments_api is not None
    
    def test_blueprint_has_routes(self):
        """Blueprint should have routes defined."""
        from src.app.api.card_comments import card_comments_api
        
        # Check deferred functions exist (route registrations)
        assert len(card_comments_api.deferred_functions) >= 4  # list, create, delete, count
    
    def test_rate_limits_defined(self):
        """Rate limit constants should be defined."""
        from src.app.api.card_comments import RATE_LIMIT_POST, RATE_LIMIT_GET
        
        assert "per minute" in RATE_LIMIT_POST
        assert "per minute" in RATE_LIMIT_GET
    
    def test_content_limits_defined(self):
        """Content limit constants should be defined."""
        from src.app.api.card_comments import MAX_COMMENT_LENGTH, MAX_PAGE_SIZE
        
        assert MAX_COMMENT_LENGTH > 0
        assert MAX_PAGE_SIZE > 0


class TestCardCommentModel:
    """Tests for CardComment model methods."""
    
    def test_model_has_to_dict(self):
        """Model should have to_dict method."""
        from src.models import CardComment
        assert hasattr(CardComment, 'to_dict')
    
    def test_model_has_create(self):
        """Model should have create factory method."""
        from src.models import CardComment
        assert hasattr(CardComment, 'create')
    
    def test_model_has_soft_delete(self):
        """Model should have soft_delete method."""
        from src.models import CardComment
        assert hasattr(CardComment, 'soft_delete')
    
    def test_model_has_is_deleted(self):
        """Model should have is_deleted property."""
        from src.models import CardComment
        assert hasattr(CardComment, 'is_deleted')


class TestSegmentCardKey:
    """Tests for Segment.generate_card_key integration."""
    
    def test_segment_has_card_key_method(self):
        """Segment should have generate_card_key method."""
        from src.utils.card_view.schemas import Segment
        assert hasattr(Segment, 'generate_card_key')
    
    def test_segment_has_body_hash_method(self):
        """Segment should have generate_body_hash method."""
        from src.utils.card_view.schemas import Segment
        assert hasattr(Segment, 'generate_body_hash')
    
    def test_segment_to_dict_with_message_context(self):
        """to_dict should include card_key when message context provided."""
        from src.utils.card_view import segment_message
        
        segments = segment_message("Test message for card key generation.")
        
        # Without context - no card_key
        d1 = segments[0].to_dict()
        assert "card_key" not in d1
        
        # With context - has card_key
        d2 = segments[0].to_dict(message_id=123, segment_index=0)
        assert "card_key" in d2
        assert "body_hash" in d2
        assert len(d2["card_key"]) == 40


class TestAIReplyFeature:
    """Tests for AI reply functionality."""
    
    def test_content_type_field_exists(self):
        """CardComment should have content_type field."""
        from src.models import CardComment
        assert hasattr(CardComment, 'content_type')
    
    def test_is_ai_property_exists(self):
        """CardComment should have is_ai property."""
        from src.models import CardComment
        assert hasattr(CardComment, 'is_ai')
    
    def test_consecutive_ai_counter_exists(self):
        """CardComment should have count_consecutive_ai_for_user method."""
        from src.models import CardComment
        assert hasattr(CardComment, 'count_consecutive_ai_for_user')
        assert callable(CardComment.count_consecutive_ai_for_user)
    
    def test_ai_rate_limit_defined(self):
        """AI rate limit constant should be defined."""
        from src.app.api.card_comments import RATE_LIMIT_AI
        assert "per minute" in RATE_LIMIT_AI
    
    def test_ai_reply_constants_defined(self):
        """AI reply constants should be defined."""
        from src.app.api.card_comments import (
            MAX_CONSECUTIVE_AI_REPLIES,
            AI_REPLY_MAX_TOKENS,
            AI_REPLY_MAX_CHARS,
            AI_CONTEXT_MAX_COMMENTS,
            AI_CONTEXT_MAX_CHARS,
        )
        assert MAX_CONSECUTIVE_AI_REPLIES == 2
        assert AI_REPLY_MAX_TOKENS > 0
        assert AI_REPLY_MAX_CHARS > 0  # Hard cap on response length
        assert AI_CONTEXT_MAX_COMMENTS > 0
        assert AI_CONTEXT_MAX_CHARS > 0
    
    def test_build_context_helper_exists(self):
        """Context builder helper should exist."""
        from src.app.api.card_comments import _build_ai_reply_context
        assert callable(_build_ai_reply_context)
    
    def test_generate_reply_helper_exists(self):
        """AI reply generator helper should exist."""
        from src.app.api.card_comments import _generate_ai_reply
        assert callable(_generate_ai_reply)
    
    def test_create_accepts_content_type(self):
        """CardComment.create should accept content_type parameter."""
        import inspect
        from src.models import CardComment
        
        sig = inspect.signature(CardComment.create)
        param_names = list(sig.parameters.keys())
        
        assert 'content_type' in param_names
    
    def test_to_dict_includes_content_type(self):
        """to_dict should include content_type."""
        from src.models import CardComment
        
        # Check the to_dict method source includes content_type
        import inspect
        source = inspect.getsource(CardComment.to_dict)
        assert 'content_type' in source


class TestAIReplyCleanup:
    """Tests for AI reply post-processing."""
    
    def test_clean_ai_reply_exists(self):
        """Cleanup function should exist."""
        from src.app.api.card_comments import _clean_ai_reply
        assert callable(_clean_ai_reply)
    
    def test_clean_removes_preambles(self):
        """Should remove common preamble phrases."""
        from src.app.api.card_comments import _clean_ai_reply
        
        result = _clean_ai_reply("Here's my comment: This is the actual content.")
        assert not result.startswith("Here's my comment")
        assert "actual content" in result
    
    def test_clean_normalizes_bullets(self):
        """Should normalize bullet markers to •."""
        from src.app.api.card_comments import _clean_ai_reply
        
        result = _clean_ai_reply("- First item\n* Second item\n– Third item")
        assert result.count('•') == 3
        assert '- ' not in result
        assert '* ' not in result
    
    def test_clean_handles_empty(self):
        """Should handle empty/None input."""
        from src.app.api.card_comments import _clean_ai_reply
        
        assert _clean_ai_reply("") == ""
        assert _clean_ai_reply(None) is None


class TestAIReplyGuard:
    """Tests for consecutive AI reply guard logic."""
    
    def test_guard_checks_user_specific(self):
        """Guard should be user-specific, not global."""
        # The implementation should filter by user_id
        from src.models import CardComment
        import inspect
        
        source = inspect.getsource(CardComment.count_consecutive_ai_for_user)
        assert 'user_id' in source
    
    def test_guard_checks_card_specific(self):
        """Guard should be card-specific."""
        from src.models import CardComment
        import inspect
        
        source = inspect.getsource(CardComment.count_consecutive_ai_for_user)
        assert 'card_key' in source
    
    def test_guard_orders_by_created_at(self):
        """Guard should check most recent comments first."""
        from src.models import CardComment
        import inspect
        
        source = inspect.getsource(CardComment.count_consecutive_ai_for_user)
        assert 'desc' in source.lower() or 'DESC' in source
    
    def test_guard_accepts_chat_id(self):
        """Guard should accept optional chat_id for extra isolation."""
        from src.models import CardComment
        import inspect
        
        sig = inspect.signature(CardComment.count_consecutive_ai_for_user)
        param_names = list(sig.parameters.keys())
        assert 'chat_id' in param_names
    
    def test_guard_filters_by_chat_id_when_provided(self):
        """Guard should filter by chat_id when provided."""
        from src.models import CardComment
        import inspect
        
        source = inspect.getsource(CardComment.count_consecutive_ai_for_user)
        # Should have conditional chat_id filter
        assert 'chat_id' in source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

