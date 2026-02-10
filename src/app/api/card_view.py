"""
Card View Dev API

Dev-only endpoint for testing message segmentation.
Not for production use - no DB writes, just compute and return.

Guarded by CARD_VIEW_DEV_ENABLED env var (default: False in production).

Usage (curl):
    curl -X POST http://localhost:5001/api/dev/card-segments \
        -H "Content-Type: application/json" \
        -H "Cookie: session=YOUR_SESSION_COOKIE" \
        -d '{"text": "Your long message here...", "enhance": true}'

Usage (Python):
    import requests
    response = requests.post(
        "http://localhost:5001/api/dev/card-segments",
        json={"text": "...", "enhance": True},
        cookies={"session": "..."}
    )
    data = response.json()
    # data contains: segments, guiding_question, relationships
"""

import os
from flask import Blueprint, request, jsonify, current_app, render_template
from src.app.access_control import require_login, get_current_user
from src.app import limiter

card_view_api = Blueprint("card_view_api", __name__, url_prefix="/api/dev")

# Rate limits for card view API (more restrictive due to AI costs)
RATE_LIMIT_SEGMENT = "30 per minute"  # Segmentation is fast
RATE_LIMIT_AI = "10 per minute"       # AI calls are expensive

# Feature flag: only enable in dev or when explicitly enabled
DEV_API_ENABLED = os.getenv("CARD_VIEW_DEV_ENABLED", "false").lower() in ("true", "1", "yes")
FLASK_ENV = os.getenv("FLASK_ENV", "production")


def _is_dev_api_allowed() -> bool:
    """Check if dev API is allowed for current environment/user."""
    # Always allow in development
    if FLASK_ENV == "development":
        return True
    # Allow if explicitly enabled via env var
    if DEV_API_ENABLED:
        return True
    # In production without flag, check if user is admin
    user = get_current_user()
    if user and hasattr(user, 'email'):
        admin_emails = os.getenv("ADMIN_EMAILS", "").split(",")
        if user.email in admin_emails:
            return True
    return False


@card_view_api.route("/card-segments", methods=["POST"])
@require_login
@limiter.limit(RATE_LIMIT_AI, deduct_when=lambda response: (request.get_json(silent=True) or {}).get("enhance", False))
@limiter.limit(RATE_LIMIT_SEGMENT)
def segment_text():
    """
    Segment text into card-ready pieces with optional AI enhancements.
    
    Request JSON:
        {
            "text": "Long message to segment...",
            "enhance": true  // Optional: add guiding question + relationship hints
        }
    
    Response JSON:
        {
            "success": true,
            "segment_count": 5,
            "text_length": 1234,
            "segments": [...],
            "guiding_question": "What is...?" or null,
            "relationships": ["hint1", "hint2", ...] or [],
            "ai_enhanced": true/false
        }
    
    Errors:
        400: Missing or invalid text
        401: Not logged in
        403: Not authorized (production without admin access)
        500: Segmentation failed
    """
    # Check if dev API is allowed
    if not _is_dev_api_allowed():
        return jsonify({
            "success": False, 
            "error": "Dev API not enabled. Set CARD_VIEW_DEV_ENABLED=true or use admin account."
        }), 403
    
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    
    # Parse request
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "JSON body required"}), 400
    
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"success": False, "error": "text field required"}), 400
    
    # Optional: enable AI enhancements
    enhance = data.get("enhance", False)
    
    try:
        from src.utils.card_view import segment_message, enhance_segments_with_ai
        from src.models.card_comment import generate_card_key
        import time
        
        # Segment the text (Python-only, fast)
        segments = segment_message(text)
        
        # Generate stable card_key for preview mode (always return card_key)
        # Use mock message_id for preview: negative timestamp to avoid conflicts with real messages
        preview_message_id = -int(time.time() * 1000)
        
        # Convert to dicts for JSON, ensuring card_key is always present
        segment_dicts = []
        for i, seg in enumerate(segments):
            seg_dict = seg.to_dict()
            # Always include segment_index for frontend mapping
            seg_dict["segment_index"] = i
            # Generate card_key if not present (preview mode)
            if not seg_dict.get("card_key"):
                card_key = generate_card_key(preview_message_id, i, seg.body)
                seg_dict["card_key"] = card_key
                seg_dict["body_hash"] = seg.generate_body_hash()
            segment_dicts.append(seg_dict)
        
        # Build response
        response_data = {
            "success": True,
            "segment_count": len(segments),
            "text_length": len(text),
            "segments": segment_dicts,
            "guiding_question": None,
            "relationships": [],
            "ai_enhanced": False,
        }
        
        # Add AI enhancements if requested
        if enhance:
            try:
                ai_data = enhance_segments_with_ai(text, segments)
                response_data["guiding_question"] = ai_data.get("guiding_question")
                # Only include relationships if we have 2+ segments
                if len(segments) >= 2:
                    response_data["relationships"] = ai_data.get("relationships", [])
                response_data["ai_enhanced"] = ai_data.get("ai_enhanced", False)
                
                # Include debug meta in dev mode
                if FLASK_ENV == "development":
                    response_data["_ai_meta"] = ai_data.get("_meta", {})
            except Exception as e:
                # Log but don't fail - AI is optional
                current_app.logger.warning(f"AI enhancement failed (continuing): {e}")
        
        return jsonify(response_data)
        
    except Exception as e:
        current_app.logger.error(f"Card view segmentation failed: {e}")
        return jsonify({
            "success": False, 
            "error": f"Segmentation failed: {str(e)}"
        }), 500


@card_view_api.route("/card-segments/health", methods=["GET"])
@require_login
def health():
    """Health check for the card view API (auth required)."""
    if not _is_dev_api_allowed():
        return jsonify({"status": "disabled", "reason": "Dev API not enabled"}), 403
    
    from src.utils.card_view.ai_helpers import CACHE_ENABLED, CACHE_TTL_SECONDS, _cache
    
    return jsonify({
        "status": "ok",
        "endpoint": "/api/dev/card-segments",
        "method": "POST",
        "env": FLASK_ENV,
        "dev_enabled": DEV_API_ENABLED,
        "cache": {
            "enabled": CACHE_ENABLED,
            "ttl_seconds": CACHE_TTL_SECONDS,
            "entries": len(_cache),
            "note": "In-memory, per-process only. Not shared across workers.",
        },
    })


@card_view_api.route("/card-segments/cache/clear", methods=["POST"])
@require_login
def clear_cache():
    """Clear the AI response cache (dev-only)."""
    if not _is_dev_api_allowed():
        return jsonify({"success": False, "error": "Dev API not enabled"}), 403
    
    from src.utils.card_view.ai_helpers import clear_cache as do_clear_cache
    
    cleared = do_clear_cache()
    return jsonify({
        "success": True,
        "cleared": cleared,
    })


@card_view_api.route("/card-preview", methods=["GET"])
@require_login
def card_preview():
    """
    Dev-only Card View preview page.
    
    Provides a UI to paste text and see how it would be segmented into cards.
    Uses the same access guard as the API endpoints.
    
    Query params:
        chat_id: Optional chat ID for real API integration (enables comments)
        room_id: Optional room ID (derived from chat if chat_id provided)
        message_id: Optional message ID (required for real API comments)
    
    WARNING: When chat_id/message_id are provided, comments will be saved to the database
    tied to the real chat/message, even though the previewed card content may be unrelated.
    Only use with test/development chats, never production data.
    """
    if not _is_dev_api_allowed():
        return render_template("errors/403.html"), 403
    
    # Get chat_id, room_id, and message_id from query params (optional, for real API integration)
    chat_id = request.args.get("chat_id", type=int)
    room_id = request.args.get("room_id", type=int)
    message_id = request.args.get("message_id", type=int)
    
    # If chat_id provided, validate and get room_id
    if chat_id:
        from src.models import Chat
        chat = Chat.query.get(chat_id)
        if chat:
            room_id = chat.room_id
            # If message_id not provided but chat_id is, try to get the latest message
            # NOTE: This creates a mismatch - preview content may be unrelated to this message
            if not message_id:
                from src.models import Message
                latest_message = Message.query.filter_by(chat_id=chat_id).order_by(Message.id.desc()).first()
                if latest_message:
                    message_id = latest_message.id
                    # Log warning about potential mismatch
                    current_app.logger.warning(
                        f"Card preview using latest message_id={message_id} for chat_id={chat_id}. "
                        "Preview content may be unrelated to this message."
                    )
        else:
            # Invalid chat_id, clear it
            chat_id = None
            room_id = None
            message_id = None
    
    return render_template("dev/card_preview.html", chat_id=chat_id, room_id=room_id, message_id=message_id)
