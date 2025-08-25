"""
Refinement and regeneration routes for learning steps.
"""

from flask import Blueprint, request, jsonify, current_app
import re
from src.app import db, csrf
from src.models import Room, CustomPrompt
from src.app.access_control import get_current_user, require_login, require_room_access
from src.utils.openai_utils import generate_room_modes

refine_bp = Blueprint('room_refine', __name__)


def _normalize_modes(modes):
    """Ensure modes is a list of dicts with keys: key,label,prompt."""
    if not isinstance(modes, list):
        return []
    out = []
    for m in modes:
        if isinstance(m, dict):
            key = m.get('key')
            label = m.get('label')
            prompt = m.get('prompt')
            if key and label and prompt:
                out.append({'key': key, 'label': label, 'prompt': prompt})
    return out


def _reindex_modes(modes):
    """Reindex mode keys as step1.. and optionally renumber leading label indices."""
    reindexed = []
    for idx, m in enumerate(modes, start=1):
        new_key = f"step{idx}"
        label = m.get('label', '')
        # If label starts with a number. or number) or number:
        new_label = label
        m_num = re.match(r"^\s*(\d+)([\.)\:]?\s+)(.*)$", label)
        if m_num:
            new_label = f"{idx}{m_num.group(2)}{m_num.group(3)}".strip()
        reindexed.append({'key': new_key, 'label': new_label, 'prompt': m.get('prompt', '')})
    return reindexed


def _parse_target_count(text):
    """Extract target count like 'reduce to 6' or 'six steps'."""
    if not text:
        return None
    m = re.search(r"\b(?:to\s*)?(\d{1,2})\b", text)
    if m:
        try:
            n = int(m.group(1))
            if 1 <= n <= 30:
                return n
        except Exception:
            pass
    # word numbers simple mapping
    words = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
        'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
    }
    for w, n in words.items():
        if re.search(rf"\b{w}\b", text):
            return n
    return None


def _parse_remove_hint(text):
    """Return a removal hint: by step number or label substring.
    Examples: 'remove step 9', 'remove the 9 historical patterns step'
    """
    if not text:
        return {}
    # step number
    m = re.search(r"remove\s+step\s*(\d{1,2})", text, re.I)
    if m:
        try:
            return {'step_number': int(m.group(1))}
        except Exception:
            pass
    # label substring between remove and step
    m2 = re.search(r"remove\s+(.*?)\s+step", text, re.I)
    if m2:
        sub = m2.group(1).strip('"\' ).strip()
        if sub:
            return {'label_contains': sub.lower()}
    # generic remove <phrase>
    m3 = re.search(r"remove\s+(.+)$", text, re.I)
    if m3:
        sub = m3.group(1).strip()
        if sub:
            return {'label_contains': sub.lower()}
    return {}


def _apply_refinements(message: str, current_modes: list):
    """Apply simple deterministic refinements to the provided modes.
    Supports: reduce to N steps; remove step N; remove by label substring.
    Returns (new_modes, summary_message) or (None, None) if no change.
    """
    modes = _normalize_modes(current_modes)
    original_len = len(modes)
    if not modes:
        return None, None

    changed = False
    feedbacks = []
    text = (message or '').strip()

    # Reduce to N steps
    target = _parse_target_count(text)
    if target and target < len(modes):
        modes = modes[:target]
        changed = True
        feedbacks.append(f"reduced to {target} steps")

    # Remove specific step
    hint = _parse_remove_hint(text)
    if hint:
        before = len(modes)
        if 'step_number' in hint:
            num = hint['step_number']
            modes = [m for m in modes if not m.get('key', '').lower() == f'step{num}']
            if len(modes) != before:
                changed = True
                feedbacks.append(f"removed step {num}")
        elif 'label_contains' in hint:
            substr = hint['label_contains']
            modes = [m for m in modes if substr not in m.get('label', '').lower()]
            if len(modes) != before:
                changed = True
                feedbacks.append(f"removed step matching '{substr}'")

    if changed:
        modes = _reindex_modes(modes)
        msg = "; ".join(feedbacks) if feedbacks else "applied your changes"
        return modes, msg
    return None, None


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

        # If user provided modes and a refinement message, try to apply a deterministic transform first
        modes, summary = _apply_refinements(message, current_modes)
        if modes is None:
            try:
                modes_obj = generate_room_modes(tmp)
                modes = [
                    {"key": k, "label": v.label, "prompt": v.prompt}
                    for k, v in (modes_obj.items() if hasattr(modes_obj, 'items') else [])
                ]
                summary = None
            except Exception:
                modes = current_modes if isinstance(current_modes, list) else []
                summary = None

        ai_message = (
            f"I {summary}. Save changes to persist." if summary else
            "Updated your proposal. Adjust further or save when ready."
        )

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

        # Prefer deterministic transform on provided modes for edit flow
        modes, summary = _apply_refinements(data.get("message"), current_modes)
        if modes is None:
            try:
                modes_obj = generate_room_modes(tmp)
                modes = [
                    {"key": k, "label": v.label, "prompt": v.prompt}
                    for k, v in (modes_obj.items() if hasattr(modes_obj, 'items') else [])
                ]
                summary = None
            except Exception:
                modes = current_modes if isinstance(current_modes, list) else []
                summary = None

        ai_message = (
            f"I {summary}. Save changes to persist." if summary else
            "Applied your feedback to the learning steps. Save changes to persist."
        )

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


