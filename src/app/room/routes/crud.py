"""
Room CRUD route handlers.
Handles HTTP requests for room operations.
"""

from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from typing import Any, Tuple, List
from src.app import db
from src.models import Room, User, Chat, RoomMember
from ..services.room_service import RoomService
from ..types import RoomCreationData, RoomUpdateData
from ..utils.room_utils import get_invitation_count
from src.app.access_control import get_current_user, require_login, require_room_access
from src.utils.title_generator import get_display_title
from src.utils.openai_utils import get_modes_for_room, get_available_templates
from src.app import csrf

crud_bp = Blueprint('room_crud', __name__)


@crud_bp.route("/test-route")
def test_route():
    return "CRUD BLUEPRINT WORKING"

@crud_bp.route("/generate-room-proposal-v2", methods=["POST"], endpoint="legacy_generate_room_proposal")
@require_login
@csrf.exempt
def legacy_generate_room_proposal() -> Any:
    """Compatibility endpoint for non-template room creation.
    Returns fields expected by the new UI (title/description/modes/conversation_id/ai_message),
    with safe fallbacks when AI mode generation is not used.
    """
    current_app.logger.info("🔥 ROUTE HIT: /generate-room-proposal-v2")
    
    try:
        from uuid import uuid4
        import json as _json
        from src.utils.openai_utils import generate_room_modes, BASE_TEMPLATES
        current_app.logger.info("🔥 IMPORTS SUCCESSFUL")
        
        # Parse goals from JSON body
        data = request.get_json(silent=True)
        current_app.logger.info(f"🔥 REQUEST DATA: {data}")
        if data is None:
            try:
                data = _json.loads(request.data or b"{}")
            except Exception:
                data = {}
        if not isinstance(data, dict):
            data = {}
        goals_text = (data.get("goals") or "").strip()

        # AI title generation with working fallback
        first_line = (goals_text.splitlines() or [""])[0].strip()
        
        # Try AI first using the exact same pattern as working learning modes
        try:
            from src.utils.openai_utils import call_anthropic_api
            
            prompt = f"Create ONE clear and concise title for this learning room. Respond with ONLY the title, nothing else. Maximum 5 words. Goals: {goals_text}"
            
            # Use exact same call pattern as working learning modes (line 300 in openai_utils.py)
            ai_response, _ = call_anthropic_api(
                [{"role": "user", "content": prompt}],
                max_tokens=50
            )
            
            if ai_response and ai_response.strip():
                suggested_title = ai_response.strip()
                # Auto-truncate if too long (prevent validation failures)
                if len(suggested_title) > 125:
                    suggested_title = suggested_title[:122].strip() + "..."
            else:
                raise Exception("AI returned empty response")
                
        except Exception:
            # Fallback to working string extraction
            if first_line:
                words = first_line.lower().replace("to learn about", "").replace("to study", "").replace("to learn", "").strip().split()
                key_words = [w.capitalize() for w in words[:4] if len(w) > 2]
                suggested_title = " ".join(key_words) if key_words else "New Learning Room"
            else:
                suggested_title = "New Learning Room"
        
        # Generate modes separately (keep existing working logic)
        modes_list = []

        # Use modes from the combined AI call, or fallback if needed
        if not modes_list:
            # Fallback to separate mode generation if combined call failed
            try:
                from src.utils.openai_utils import generate_room_modes, BASE_TEMPLATES
                temp_room = type('obj', (object,), {
                    'id': 0,
                    'name': suggested_title or 'New Room',
                    'goals': goals_text,
                    'description': ''
                })
                modes_obj = generate_room_modes(temp_room)
                if modes_obj:
                    modes_list = [
                        {"key": key, "label": mode.label, "prompt": mode.prompt}
                        for key, mode in modes_obj.items()
                    ]
                else:
                    modes_list = []
            except Exception:
                # Final fallback to base template
                from src.utils.openai_utils import BASE_TEMPLATES
                modes_list = [
                    {"key": key, "label": mode.label, "prompt": mode.prompt}
                    for key, mode in (BASE_TEMPLATES.get("academic_essay", {}).get("modes", {}).items())
                ]

        ai_message = (
            "I drafted a starter proposal based on your goals. You can refine the title, "
            "description, or add learning steps now."
        )

        return jsonify({
            "success": True,
            "room_title": suggested_title,
            "room_description": "",
            "modes": modes_list,
            "conversation_id": str(uuid4()),
            "ai_message": ai_message
        })
    except Exception as e:
        current_app.logger.error(f"[legacy_generate_room_proposal] error: {e}")
        return jsonify({
            "success": True,
            "room_title": "New Learning Room",
            "room_description": "",
            "modes": [],
            "conversation_id": str(uuid4()),
            "ai_message": "Let's refine your room details."
        })



@crud_bp.route("/")
@require_login
def index() -> Any:
    """Redirect to enhanced V2 dashboard."""
    current_app.logger.info("🔄 HOME REDIRECT: Redirecting /room/ to /room/v2/")
    from flask import redirect, url_for
    return redirect(url_for('room_v2.index'))

@crud_bp.route("/create", methods=["GET", "POST"])
@require_login
@csrf.exempt
def create_room() -> Any:
    """Create a new room."""
    try:
        user = get_current_user()
        
        if request.method == "POST":
            # Extract and validate data
            data = RoomCreationData.from_request(request)
            
            # Use service layer
            result = RoomService.create_room(data, user)
            
            if result.success:
                # Redirect directly to learning steps management for newly created room
                return redirect(url_for('room.room_crud.view_room', room_id=result.room_id))
            else:
                flash(f"Error: {result.error}", "error")
                return redirect(url_for("room.room_crud.create_room"))
        
        # GET request - redirect to the unified learning steps editor (creation mode)
        return redirect(url_for('room.new_learning_steps'))
        
    except Exception as e:
        current_app.logger.error(f"Error in create room: {e}")
        flash("An unexpected error occurred. Please try again.", "error")
        return redirect(url_for("room.room_crud.create_room"))

@crud_bp.route("/<int:room_id>/mountain")
@require_room_access
def view_room_mountain(room_id: int) -> Any:
    """Mountain learning journey view (parallel implementation)."""
    try:
        user = get_current_user()
        room = RoomService.get_room_by_id(room_id, user)
        if not room:
            flash("Room not found or you don't have access to it.", "error")
            return redirect(url_for('room.room_crud.index'))

        # Get room data
        room_data = RoomService.get_room_display_data(room, user)
        
        # Get chats for this room
        chats = Chat.query.filter_by(room_id=room_id).order_by(Chat.created_at.desc()).all()
        
        # Get members
        members = [room.owner]  # Start with owner
        room_members = RoomMember.query.filter_by(room_id=room_id).all()
        for rm in room_members:
            if rm.user not in members:
                members.append(rm.user)
        
        # Get learning modes
        from src.utils.openai_utils import get_modes_for_room
        try:
            modes_obj = get_modes_for_room(room)
            modes = {}
            if hasattr(modes_obj, 'items'):
                for k, v in modes_obj.items():
                    modes[k] = v
        except Exception:
            modes = {}

        return render_template(
            "room/view_mountain_simple.html",
            room=room,
            room_data=room_data,
            chats=chats,
            members=members,
            modes=modes,
            user=user
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in mountain room view {room_id}: {e}")
        flash("Failed to load mountain view. Please try again.", "error")
        return redirect(url_for('room.room_crud.view_room', room_id=room_id))

@crud_bp.route("/<int:room_id>")
@require_room_access
def view_room(room_id: int) -> Any:
    """View a specific room (overview)."""
    try:
        user = get_current_user()
        room = RoomService.get_room_by_id(room_id, user)
        
        if not room:
            flash("Room not found or you don't have access to it.", "error")
            return redirect(url_for('room.room_crud.index'))
        
        # Get room data
        chats = RoomService.get_room_chats(room, user)
        members = RoomService.get_room_members(room, user)
        room_data = RoomService.get_room_display_data(room, user)
        
        # Get learning modes for mountain view
        modes = {}
        try:
            modes_obj = get_modes_for_room(room)
            if hasattr(modes_obj, 'items'):
                for k, v in modes_obj.items():
                    modes[k] = v
        except Exception:
            modes = {}

        return render_template(
            "room/view_mountain_simple.html",  # MOUNTAIN VIEW IS NOW DEFAULT
            room=room,
            room_data=room_data,
            chats=chats,
            members=members,
            modes=modes,
            user=user,
            invitation_count=get_invitation_count(user),
            get_display_title=get_display_title
        )
    except Exception as e:
        current_app.logger.error(f"Error viewing room {room_id}: {e}")
        flash("Failed to load room. Please try again.", "error")
        return redirect(url_for('room.room_crud.index'))

@crud_bp.route("/<int:room_id>/edit", methods=["GET", "POST"])
@require_room_access
def edit_room(room_id: int) -> Any:
    """Redirect legacy edit route to the unified learning steps editor."""
    try:
        # Preserve authorization check and then redirect
        user = get_current_user()
        room = RoomService.get_room_by_id(room_id, user)
        if not room:
            flash("Room not found or you don't have access to it.", "error")
            return redirect(url_for('room.room_crud.index'))

        permissions = RoomService.get_room_permissions(room, user)
        if not permissions.get("can_manage"):
            flash("You don't have permission to edit this room.", "error")
            return redirect(url_for('room.room_crud.view_room', room_id=room_id))

        # Redirect to unified editor with rubrics
        return redirect(url_for('room.new_learning_steps', room_id=room_id))
    except Exception as e:
        current_app.logger.error(f"Error redirecting edit room {room_id}: {e}")
        return redirect(url_for('room.room_crud.view_room', room_id=room_id))

@crud_bp.route("/<int:room_id>/delete", methods=["GET", "POST"])
@require_room_access
def delete_room(room_id: int) -> Any:
    """Delete a room."""
    try:
        user = get_current_user()
        room = RoomService.get_room_by_id(room_id, user)
        
        if not room:
            flash("Room not found or you don't have access to it.", "error")
            return redirect(url_for('room.room_crud.index'))
        
        # Check if user can manage the room
        permissions = RoomService.get_room_permissions(room, user)
        if not permissions["can_manage"]:
            flash("You don't have permission to delete this room.", "error")
            return redirect(url_for('room.room_crud.view_room', room_id=room_id))
        
        if request.method == "POST":
            # Use service layer to delete
            result = RoomService.delete_room(room_id, user)
            
            if result.success:
                flash("Room deleted successfully!", "success")
                return redirect(url_for('room.room_crud.index'))
            else:
                flash(f"Error: {result.error}", "error")
                return redirect(url_for('room.room_crud.view_room', room_id=room_id))
        else:
            # GET request - show confirmation page
            return render_template(
                "room/delete.html",
                room=room,
                user=user,
                invitation_count=get_invitation_count(user)
            )
            
    except Exception as e:
        current_app.logger.error(f"Error deleting room {room_id}: {e}")
        flash("An unexpected error occurred. Please try again.", "error")
        return redirect(url_for('room.room_crud.view_room', room_id=room_id))

@crud_bp.route("/search")
@require_login
def search_rooms() -> Any:
    """Search rooms."""
    try:
        user = get_current_user()
        query = request.args.get('q', '').strip()
        
        if not query:
            return redirect(url_for('room.room_crud.index'))
        
        # Use service layer
        rooms = RoomService.search_user_rooms(query, user)
        
        return render_template(
            "room/search.html",
            rooms=rooms,
            query=query,
            user=user,
            invitation_count=get_invitation_count(user)
        )
        
    except Exception as e:
        current_app.logger.error(f"Error searching rooms: {e}")
        flash("Failed to search rooms. Please try again.", "error")
        return redirect(url_for('room.room_crud.index'))

@crud_bp.route("/<int:room_id>/stats")
@require_room_access
def room_stats(room_id: int) -> Any:
    """Get room statistics."""
    try:
        user = get_current_user()
        room = RoomService.get_room_by_id(room_id, user)
        
        if not room:
            return jsonify({"error": "Room not found"}), 404
        
        # Get statistics
        stats = RoomService.get_room_statistics(room)
        activity = RoomService.get_room_activity(room)
        
        return jsonify({
            "success": True,
            "stats": stats,
            "activity": activity
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting room stats {room_id}: {e}")
        return jsonify({"error": "Failed to get room statistics"}), 500

@crud_bp.route("/<int:room_id>/activity")
@require_room_access
def room_activity(room_id: int) -> Any:
    """Get room activity."""
    try:
        user = get_current_user()
        room = RoomService.get_room_by_id(room_id, user)
        
        if not room:
            return jsonify({"error": "Room not found"}), 404
        
        # Get activity data
        days = request.args.get('days', 7, type=int)
        activity = RoomService.get_room_activity(room, days)
        
        return jsonify({
            "success": True,
            "activity": activity
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting room activity {room_id}: {e}")
        return jsonify({"error": "Failed to get room activity"}), 500

@crud_bp.route("/<int:room_id>/members")
@require_room_access
def room_members(room_id: int) -> Any:
    """Get room members."""
    try:
        user = get_current_user()
        room = RoomService.get_room_by_id(room_id, user)
        
        if not room:
            return jsonify({"error": "Room not found"}), 404
        
        # Get members
        members = RoomService.get_room_members(room, user)
        
        return jsonify({
            "success": True,
            "members": [
                {
                    "id": member.id,
                    "user_id": member.id,
                    "display_name": member.display_name,
                    "email": member.email,
                    "joined_at": None,  # User objects don't have joined_at
                    "accepted_at": None,  # User objects don't have accepted_at
                    "can_create_chats": False,  # These would need to be fetched separately
                    "can_invite_members": False
                }
                for member in members
            ]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting room members {room_id}: {e}")
        return jsonify({"error": "Failed to get room members"}), 500

@crud_bp.route("/<int:room_id>/chats")
@require_room_access
def room_chats(room_id: int) -> Any:
    """Get room chats."""
    try:
        user = get_current_user()
        room = RoomService.get_room_by_id(room_id, user)
        
        if not room:
            return jsonify({"error": "Room not found"}), 404
        
        # Get chats
        limit = request.args.get('limit', 50, type=int)
        chats = RoomService.get_room_chats(room, user, limit)
        
        return jsonify({
            "success": True,
            "chats": [
                {
                    "id": chat.id,
                    "title": chat.title,
                    "created_at": chat.created_at.isoformat() if chat.created_at else None,
                    "created_by": chat.created_by,
                    "is_active": chat.is_active
                }
                for chat in chats
            ]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting room chats {room_id}: {e}")
        return jsonify({"error": "Failed to get room chats"}), 500

@crud_bp.route("/<int:room_id>/chat/create", methods=["GET", "POST"])
@require_login
@csrf.exempt
def create_chat(room_id: int) -> Any:
    """Create a new chat within a room."""
    # ABSOLUTE FIRST LINE DEBUG - before ANY imports or logic
    print(f"\n\n=== CRUD ROUTE DEFINITELY HIT: room_id={room_id} ===")
    
    # CRITICAL DEBUG: Log that this route is being hit
    try:
        from flask import current_app
        current_app.logger.error(f"🚨 CRUD ROUTE HIT: create_chat room_id={room_id}, method={request.method}")
    except Exception as e:
        print(f"CRUD ROUTE HIT: create_chat room_id={room_id}, logger error: {e}")
    
    from src.models import Chat, Message
    from src.app.access_control import can_create_chats_in_room
    from src.utils.openai_utils import get_modes_for_room
    from src.app.google_docs import validate_google_docs_url, get_document_content
    from src.utils.openai_utils import get_ai_response, generate_chat_introduction
    from ..utils.room_utils import infer_template_type_from_room
    
    room = Room.query.get_or_404(room_id)
    user = get_current_user()

    if not can_create_chats_in_room(user, room):
        flash("You don't have permission to create chats in this room.")
        return redirect(url_for("room.room_crud.view_room", room_id=room.id))

    # Enforce per-room chat cap
    try:
        from flask import current_app as _ca
        max_chats = int((_ca.config.get('ROOM_MAX_CHATS') or 25))
    except Exception:
        max_chats = 25
    from src.models import Chat as _Chat
    existing_count = _Chat.query.filter_by(room_id=room.id).count()
    if existing_count >= max_chats:
        flash(f"Chat limit reached for this room (max {max_chats}). Please create a new room to continue.", "error")
        return redirect(url_for("room.room_crud.view_room", room_id=room.id))

    if request.method == "POST":
        title = request.form["title"].strip()
        mode = request.form.get("mode", "explore")
        google_doc_url = request.form.get("google_doc_url", "").strip()

        if not title:
            flash("Chat title is required.")
            return redirect(url_for("room.room_crud.create_chat", room_id=room.id))

        # Validate Google Doc URL if provided
        if google_doc_url:
            is_valid, doc_id_or_error = validate_google_docs_url(google_doc_url)
            if not is_valid:
                flash(f"Google Doc URL error: {doc_id_or_error}")
                return redirect(url_for("room.room_crud.create_chat", room_id=room.id))

        chat_obj = Chat(title=title, room_id=room.id, created_by=user.id, mode=mode)
        db.session.add(chat_obj)
        db.session.commit()

        print(f"\n=== STEP 1: About to generate notes for room {room_id} ===")
        
        # FIRST: Generate notes for any previous completed chats in this room
        # This must happen BEFORE the AI introduction so context is available
        try:
            from src.utils.learning.triggers import trigger_context_refresh_for_room
            print(f"=== STEP 2: Imported trigger_context_refresh_for_room ===")
            trigger_context_refresh_for_room(room_id)
            print(f"=== STEP 3: Completed trigger_context_refresh_for_room ===")
            current_app.logger.info(f"✅ Generated/updated notes for existing chats in room {room_id}")
        except Exception as e:
            print(f"=== ERROR in note generation: {e} ===")
            current_app.logger.error(f"Error generating context for new chat: {e}")

        # THEN: Generate and add AI introduction message with learning context
        try:
            # Infer template type from room characteristics
            template_type = infer_template_type_from_room(chat_obj.room)
            learning_step = "step1"  # Default to step 1 for new chats
            
            current_app.logger.info(f"🔍 Chat introduction params: template_type={template_type}, learning_step={learning_step}, room_id={chat_obj.room.id}, chat_id={chat_obj.id}")
            current_app.logger.info(f"🔍 Room goals: {chat_obj.room.goals[:100]}...")
            
            introduction = generate_chat_introduction(
                chat_obj.room.goals, 
                template_type=template_type, 
                learning_step=learning_step, 
                room_id=chat_obj.room.id,
                chat_id=chat_obj.id  # Pass chat_id for context loading
            )
            
            current_app.logger.info(f"✅ Introduction generated successfully, length: {len(introduction)} chars")

            # Add the AI introduction as the first message
            intro_message = Message(
                chat_id=chat_obj.id,
                role="assistant",
                content=introduction,
                is_truncated=False,
            )
            db.session.add(intro_message)
            db.session.commit()
        except Exception as e:
            # If introduction generation fails, add a simple fallback
            current_app.logger.error(f"Failed to generate chat introduction: {e}")
            fallback_intro = Message(
                chat_id=chat_obj.id,
                role="assistant",
                content="Hello! I'm here to help you with your learning. What would you like to work on today?",
                is_truncated=False,
            )
            db.session.add(fallback_intro)
            db.session.commit()

        # If Google Doc URL provided, import the content
        if google_doc_url:
            doc_id = doc_id_or_error  # This is the doc_id from validation
            content, error = get_document_content(doc_id)

            if error:
                flash(f"Could not access Google Doc: {error}")
                return redirect(url_for("chat.view_chat", chat_id=chat_obj.id))

            if content:
                # Add the Google Doc content as the first user message
                doc_message = Message(
                    chat_id=chat_obj.id,
                    user_id=user.id,
                    role="user",
                    content=f"[Google Doc Content]\n\n{content}",
                )
                db.session.add(doc_message)

                # Get AI response to the imported content
                ai_content = get_ai_response(chat_obj)
                ai_msg = Message(
                    chat_id=chat_obj.id, role="assistant", content=ai_content
                )
                db.session.add(ai_msg)
                db.session.commit()

                flash("Google Doc content imported successfully!")

        return redirect(url_for("chat.view_chat", chat_id=chat_obj.id))

    # Get dynamic modes for this room
    modes = get_modes_for_room(room)

    return render_template(
        "room/create_chat.html",
        room=room,
        modes=modes,
        user=user,
        invitation_count=get_invitation_count(user)
    )


def _generate_title_and_modes(goals_text: str) -> Tuple[str, List]:
    """
    Generate both room title and learning modes in single AI call.
    Uses simplified prompt approach as requested.
    """
    current_app.logger.info(f"🤖 AI Title Generation: Starting with goals: '{goals_text}'")
    
    try:
        from src.utils.openai_utils import call_anthropic_api
        
        prompt = f"""Based on these learning goals: "{goals_text}"

Please provide:
1. A clear and concise title for this learning room. It should be no longer than five words.
2. 8-10 learning steps that follow a logical progression for achieving these goals.

Return as JSON with this exact format:
{{
    "title": "Short Room Title",
    "modes": [
        {{
            "key": "step1",
            "label": "1. Step Name", 
            "prompt": "Detailed prompt for this step"
        }}
    ]
}}"""

        current_app.logger.info(f"🤖 AI Title: Calling Anthropic API...")
        
        response = call_anthropic_api(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.3
        )
        
        current_app.logger.info(f"🤖 AI Title: Response received: {len(response) if response else 0} chars")
        
        if response and response.strip():
            import json
            try:
                current_app.logger.info(f"🤖 AI Title: Parsing JSON response...")
                data = json.loads(response.strip())
                title = data.get("title", "").strip()
                modes = data.get("modes", [])
                
                current_app.logger.info(f"✅ AI SUCCESS: Generated title: '{title}' and {len(modes)} modes")
                return title, modes
                
            except json.JSONDecodeError as e:
                current_app.logger.error(f"❌ AI JSON Parse Error: {e}")
                current_app.logger.error(f"❌ Raw AI Response: {response[:500]}")
                
    except Exception as e:
        current_app.logger.error(f"❌ AI Call Exception: {e}")
        import traceback
        current_app.logger.error(f"❌ Traceback: {traceback.format_exc()}")
    
    # Fallback
    current_app.logger.warning("⚠️ AI FAILED: Using fallback title 'New Learning Room'")
    return "", []
