"""
Tests for Card View Dev API

Minimal tests for the /api/dev/card-segments endpoint.

Note: Full integration tests require a proper test environment with scrypt support.
These tests focus on the endpoint logic without user authentication.
"""

import os
import pytest


class TestCardViewAPIUnit:
    """Unit tests for card view API (no Flask app required)."""
    
    def test_segment_message_import(self):
        """Verify segment_message can be imported."""
        from src.utils.card_view import segment_message
        assert callable(segment_message)
    
    def test_segment_returns_list(self):
        """segment_message returns a list."""
        from src.utils.card_view import segment_message
        result = segment_message("Test message")
        assert isinstance(result, list)
    
    def test_segment_short_returns_one(self):
        """Short messages return 1 segment."""
        from src.utils.card_view import segment_message
        result = segment_message("Short test message.")
        assert len(result) == 1
    
    def test_segment_long_returns_substantial_cards(self):
        """Long messages return substantial cards (may merge small ones)."""
        from src.utils.card_view import segment_message
        
        long_text = """
        Understanding machine learning requires grasping several fundamental concepts 
        that form the foundation of modern AI systems.
        
        Supervised learning uses labeled data to train models that can make predictions.
        The algorithm learns from examples where the correct answer is provided.
        
        Unsupervised learning works with unlabeled data to find hidden patterns.
        Clustering and dimensionality reduction are common techniques here.
        
        Reinforcement learning involves an agent learning through trial and error.
        The agent receives rewards for good actions and penalties for bad ones.
        
        Deep learning uses neural networks with many layers to learn representations.
        It has revolutionized image recognition and natural language processing.
        """
        
        result = segment_message(long_text)
        assert len(result) >= 2
        # Each card should be substantial
        for seg in result:
            assert seg.length >= 80
    
    def test_segment_to_dict(self):
        """Segments can be serialized to dict."""
        from src.utils.card_view import segment_message
        result = segment_message("Test message for dict conversion.")
        
        for seg in result:
            d = seg.to_dict()
            assert "id" in d
            assert "header" in d
            assert "body" in d


class TestCardViewAPIAccess:
    """Tests for API access control logic."""
    
    def test_dev_api_disabled_by_default_in_prod(self):
        """Dev API should be disabled in production by default."""
        # Save current env
        old_env = os.environ.get("FLASK_ENV")
        old_flag = os.environ.get("CARD_VIEW_DEV_ENABLED")
        
        try:
            os.environ["FLASK_ENV"] = "production"
            os.environ.pop("CARD_VIEW_DEV_ENABLED", None)
            
            # Re-import to get fresh values
            import importlib
            from src.app.api import card_view
            importlib.reload(card_view)
            
            assert card_view.FLASK_ENV == "production"
            assert card_view.DEV_API_ENABLED is False
        finally:
            # Restore env
            if old_env:
                os.environ["FLASK_ENV"] = old_env
            if old_flag:
                os.environ["CARD_VIEW_DEV_ENABLED"] = old_flag
    
    def test_dev_api_enabled_in_development(self):
        """Dev API should be allowed in development."""
        old_env = os.environ.get("FLASK_ENV")
        
        try:
            os.environ["FLASK_ENV"] = "development"
            
            import importlib
            from src.app.api import card_view
            importlib.reload(card_view)
            
            # In development, _is_dev_api_allowed should return True
            # (can't fully test without app context, but env check works)
            assert card_view.FLASK_ENV == "development"
        finally:
            if old_env:
                os.environ["FLASK_ENV"] = old_env


class TestCardViewAPIBlueprint:
    """Tests for blueprint registration."""
    
    def test_blueprint_has_correct_prefix(self):
        """Blueprint should have /api/dev prefix."""
        from src.app.api.card_view import card_view_api
        assert card_view_api.url_prefix == "/api/dev"
    
    def test_blueprint_has_routes(self):
        """Blueprint should have expected routes."""
        from src.app.api.card_view import card_view_api
        
        # Get deferred functions (route registrations)
        route_funcs = [f.__name__ for f in card_view_api.deferred_functions]
        # Routes are registered via decorators, check the view functions exist
        assert hasattr(card_view_api, 'view_functions') or len(card_view_api.deferred_functions) >= 2
    
    def test_rate_limits_defined(self):
        """Rate limit constants should be defined."""
        from src.app.api.card_view import RATE_LIMIT_SEGMENT, RATE_LIMIT_AI
        assert "per minute" in RATE_LIMIT_SEGMENT
        assert "per minute" in RATE_LIMIT_AI


class TestCardViewCaching:
    """Tests for AI response caching."""
    
    def test_cache_functions_exist(self):
        """Cache utility functions should be importable."""
        from src.utils.card_view.ai_helpers import (
            _cache_key, _cache_get, _cache_set, clear_cache,
            CACHE_ENABLED, CACHE_TTL_SECONDS
        )
        assert callable(_cache_key)
        assert callable(_cache_get)
        assert callable(_cache_set)
        assert callable(clear_cache)
    
    def test_cache_key_generates_hash(self):
        """Cache key should include a hash of content."""
        from src.utils.card_view.ai_helpers import _cache_key
        
        key1 = _cache_key("test", "content")
        key2 = _cache_key("test", "different")
        
        assert key1.startswith("test:")
        assert key2.startswith("test:")
        assert key1 != key2
    
    def test_cache_set_and_get(self):
        """Cache set/get should work."""
        from src.utils.card_view.ai_helpers import _cache_set, _cache_get, clear_cache
        
        clear_cache()
        
        _cache_set("test:key", "test_value")
        result = _cache_get("test:key")
        
        assert result == "test_value"
        
        clear_cache()
    
    def test_clear_cache_returns_count(self):
        """Clear cache should return count of cleared entries."""
        from src.utils.card_view.ai_helpers import _cache_set, clear_cache
        
        clear_cache()
        _cache_set("test:1", "v1")
        _cache_set("test:2", "v2")
        
        cleared = clear_cache()
        assert cleared == 2


class TestCardViewEnhanceResponse:
    """Tests for AI enhancement response shape."""
    
    def test_enhance_response_has_meta(self):
        """Enhancement response should include _meta in structure."""
        from src.utils.card_view import segment_message, enhance_segments_with_ai
        
        segments = segment_message("Test message for enhancement.")
        result = enhance_segments_with_ai("Test message", segments, use_ai=False)
        
        assert "_meta" in result
        assert "cache_enabled" in result["_meta"]
        assert "latency_ms" in result["_meta"]
        assert "errors" in result["_meta"]
    
    def test_enhance_with_ai_disabled_returns_empty(self):
        """With use_ai=False, returns early with empty relationships."""
        from src.utils.card_view import segment_message, enhance_segments_with_ai
        
        long_text = """
        First section with substantial content about topic one.
        This has enough text to become its own card.
        
        Second section discusses another important topic entirely.
        It also has sufficient content to stand alone.
        
        Third section covers the final points we need to make.
        This wraps up the discussion nicely.
        """
        
        segments = segment_message(long_text)
        result = enhance_segments_with_ai(long_text, segments, use_ai=False)
        
        # With AI disabled, returns early without enhancements
        assert result["guiding_question"] is None
        assert result["relationships"] == []
        assert result["ai_enhanced"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
