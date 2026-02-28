"""
Tutorial API - Onboarding walkthrough completion tracking.
"""

from datetime import datetime, timezone
from functools import wraps
from flask import Blueprint, jsonify, session, request
from src.app.access_control import get_current_user
from src.app import db

tutorial_bp = Blueprint("tutorial", __name__, url_prefix="/api/tutorial")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function


@tutorial_bp.route("/status", methods=["GET"])
@login_required
def status():
    """Return tutorial completion status for current user."""
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 401

    completed = getattr(user, "tutorial_completed_at", None) is not None
    completed_at = getattr(user, "tutorial_completed_at", None)
    return jsonify({
        "completed": completed,
        "completed_at": completed_at.isoformat() if completed_at else None,
    })


@tutorial_bp.route("/complete", methods=["POST"])
@login_required
def complete():
    """Mark tutorial as completed for current user."""
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 401

    try:
        user.tutorial_completed_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
