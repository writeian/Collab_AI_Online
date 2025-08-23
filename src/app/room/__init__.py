"""
Room blueprint initialization.
Registers all room-related routes and services.
"""

from flask import Blueprint
from src.app import csrf

# Create main blueprint
room = Blueprint("room", __name__)

# Import route blueprints to ensure they're registered
from .routes import crud, templates, invitations, api

# Register route blueprints
room.register_blueprint(crud.crud_bp, url_prefix="")
room.register_blueprint(templates.templates_bp, url_prefix="/template")
room.register_blueprint(invitations.invitations_bp, url_prefix="/<int:room_id>")
room.register_blueprint(api.api_bp, url_prefix="/api")

# Learning steps management routes (backward-compat)
@room.route('/<int:room_id>/update-learning-steps', methods=['POST'])
@csrf.exempt
def update_learning_steps(room_id: int):
    from flask import request, jsonify, current_app
    from src.models import CustomPrompt
    from src.app import db
    from src.app.access_control import get_current_user
    try:
        data = request.get_json(silent=True) or {}
        modes = data.get('modes') or data.get('refined_modes')
        if isinstance(modes, str):
            import json as _json
            try:
                modes = _json.loads(modes)
            except Exception:
                modes = []
        if not isinstance(modes, list):
            return jsonify({"success": False, "error": "Invalid modes payload"}), 400
        # Replace existing prompts for this room
        CustomPrompt.query.filter_by(room_id=room_id).delete()
        user = get_current_user()
        created_by = getattr(user, 'id', None) or 0
        for m in modes:
            key = m.get('key')
            label = m.get('label')
            prompt = m.get('prompt')
            if key and label and prompt:
                db.session.add(CustomPrompt(
                    mode_key=key,
                    label=label,
                    prompt=prompt,
                    room_id=room_id,
                    created_by=created_by
                ))
        db.session.commit()
        return jsonify({"success": True, "redirect_url": f"/room/{room_id}"})
    except Exception as e:
        current_app.logger.error(f"[learning-steps.update] error: {e}")
        return jsonify({"success": False, "error": "Failed to save changes"}), 500

# Import all routes to ensure they're registered
from .routes import crud, templates, invitations, api

# Export the main blueprint
__all__ = ['room']
