"""
Refinement and regeneration routes for learning steps.
"""

from flask import Blueprint, request, jsonify, current_app
from src.app import db, csrf
from src.models import Room, CustomPrompt
from src.app.access_control import get_current_user, require_login, require_room_access
from src.utils.openai_utils import generate_room_modes

refine_bp = Blueprint('room_refine', __name__)


@refine_bp.route("/refine-room-proposal", methods=["POST"]) 
@require_login
@csrf.exempt
def refine_room_proposal_new():
    """Refine proposal during new-room flow (no room_id yet).
    Regenerates modes based on current title/description hints; returns updates for UI.
    """
    try:
        from uuid import uuid4
        data = request.get_json(silent=True) or {}
        message = (data.get("message") or "").strip()
        current_modes = data.get("current_modes") or []
        title = (data.get("current_room_title") or "").strip()
        description = (data.get("current_room_description") or "").strip()

        # Create a temporary room-like object for mode generation
        tmp = type('obj', (object,), {
            'id': 0,
            'name': title or 'New Room',
            'goals': description or '',
            'description': description or ''
        })

        try:
            modes_obj = generate_room_modes(tmp)
            modes = [
                {"key": k, "label": v.label, "prompt": v.prompt}
                for k, v in (modes_obj.items() if hasattr(modes_obj, 'items') else [])
            ]
        except Exception:
            modes = current_modes if isinstance(current_modes, list) else []

        ai_message = "Updated your proposal. Adjust further or save when ready."

        return jsonify({
            "success": True,
            "room_title": title or 'New Room',
            "room_description": description or '',
            "modes": modes,
            "conversation_id": str(uuid4()),
            "ai_message": ai_message,
            "changes_applied": True
        })
    except Exception as e:
        current_app.logger.error(f"[refine.new] error: {e}")
        return jsonify({"success": False, "error": "Failed to refine"}), 500


@refine_bp.route("/<int:room_id>/refine-room-proposal", methods=["POST"]) 
@require_room_access
@csrf.exempt
def refine_room_proposal_edit(room_id: int):
    """Refine proposal for an existing room. Returns updated modes, not persisted."""
    try:
        room = Room.query.get_or_404(room_id)
        data = request.get_json(silent=True) or {}
        current_modes = data.get("current_modes") or []
        title = (data.get("current_room_title") or room.name or "").strip()
        description = (data.get("current_room_description") or room.description or "").strip()

        tmp = type('obj', (object,), {
            'id': room.id,
            'name': title or room.name,
            'goals': room.goals or description or '',
            'description': description or room.description or ''
        })

        try:
            modes_obj = generate_room_modes(tmp)
            modes = [
                {"key": k, "label": v.label, "prompt": v.prompt}
                for k, v in (modes_obj.items() if hasattr(modes_obj, 'items') else [])
            ]
        except Exception:
            modes = current_modes if isinstance(current_modes, list) else []

        ai_message = "Applied your feedback to the learning steps. Save changes to persist."

        return jsonify({
            "success": True,
            "room_title": title,
            "room_description": description,
            "modes": modes,
            "ai_message": ai_message,
            "changes_applied": True
        })
    except Exception as e:
        current_app.logger.error(f"[refine.edit] error: {e}")
        return jsonify({"success": False, "error": "Failed to refine"}), 500


@refine_bp.route("/<int:room_id>/regenerate-learning-steps", methods=["POST"]) 
@require_room_access
@csrf.exempt
def regenerate_learning_steps(room_id: int):
    """Generate a fresh set of modes for the room and replace existing CustomPrompt rows."""
    try:
        room = Room.query.get_or_404(room_id)
        modes_obj = generate_room_modes(room)
        new_modes = [
            {"key": k, "label": v.label, "prompt": v.prompt}
            for k, v in (modes_obj.items() if hasattr(modes_obj, 'items') else [])
        ]

        # Replace existing prompts transactionally
        CustomPrompt.query.filter_by(room_id=room_id).delete()
        user = get_current_user()
        created_by = getattr(user, 'id', None) or 0
        for m in new_modes:
            if m.get('key') and m.get('label') and m.get('prompt'):
                db.session.add(CustomPrompt(
                    mode_key=m['key'],
                    label=m['label'],
                    prompt=m['prompt'],
                    room_id=room_id,
                    created_by=created_by,
                ))
        db.session.commit()

        return jsonify({"success": True, "new_modes": new_modes})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[regenerate] error: {e}")
        return jsonify({"success": False, "error": "Failed to regenerate steps"}), 500


