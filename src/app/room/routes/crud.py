"""
Room CRUD route handlers.
Handles HTTP requests for room operations.
"""

from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from typing import Any
from src.app import db
from src.models import Room, User, Chat, RoomMember
from ..services.room_service import RoomService
from ..types import RoomCreationData, RoomUpdateData
from ..utils.room_utils import get_invitation_count
from src.app.access_control import get_current_user, require_login, require_room_access
from src.app import csrf

crud_bp = Blueprint('room_crud', __name__)


@crud_bp.route("/generate-room-proposal", methods=["POST"])
@require_login
def legacy_generate_room_proposal() -> Any:
    """Compatibility endpoint used by older templates.
    Returns a minimal proposal structure so the UI can proceed.
    """
    try:
        return jsonify({
            "success": True,
            "proposal": {
                "goals": {
                    "core_goals": [],
                    "collaboration_goals": [],
                    "reflection_goals": []
                }
            }
        }), 200
    except Exception:
        return jsonify({"success": True, "proposal": {}}), 200



@crud_bp.route("/")
@require_login
def index() -> Any:
    """Display room index page."""
    try:
        user = get_current_user()
        rooms_data = RoomService.get_user_rooms(user)
        
        # Get invitation count
        invitation_count = get_invitation_count(user)
        
        return render_template(
            "room/index.html",
            owned_rooms=rooms_data["owned"],
            member_rooms=rooms_data["member"],
            invitation_count=invitation_count,
            user=user
        )
    except Exception as e:
        current_app.logger.error(f"Error in room index: {e}")
        flash("Failed to load rooms. Please try again.", "error")
        return render_template("error.html", error="Failed to load rooms"), 500

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
                flash(f"Room '{result.data['room_name']}' created successfully!", "success")
                return redirect(url_for('room.room_crud.view_room', room_id=result.room_id))
            else:
                flash(f"Error: {result.error}", "error")
                return redirect(url_for("room.room_crud.create_room"))
        
        # GET request - show create form
        return render_template(
            "room/create.html",
            user=user,
            invitation_count=get_invitation_count(user)
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in create room: {e}")
        flash("An unexpected error occurred. Please try again.", "error")
        return redirect(url_for("room.room_crud.create_room"))

@crud_bp.route("/<int:room_id>")
@require_room_access
def view_room(room_id: int) -> Any:
    """View a specific room."""
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
        
        return render_template(
            "room/view.html",
            room=room,
            room_data=room_data,
            chats=chats,
            members=members,
            user=user,
            invitation_count=get_invitation_count(user)
        )
    except Exception as e:
        current_app.logger.error(f"Error viewing room {room_id}: {e}")
        flash("Failed to load room. Please try again.", "error")
        return redirect(url_for('room.room_crud.index'))

@crud_bp.route("/<int:room_id>/edit", methods=["GET", "POST"])
@require_room_access
def edit_room(room_id: int) -> Any:
    """Edit a room."""
    try:
        user = get_current_user()
        room = RoomService.get_room_by_id(room_id, user)
        
        if not room:
            flash("Room not found or you don't have access to it.", "error")
            return redirect(url_for('room.room_crud.index'))
        
        # Check if user can manage the room
        permissions = RoomService.get_room_permissions(room, user)
        if not permissions["can_manage"]:
            flash("You don't have permission to edit this room.", "error")
            return redirect(url_for('room.room_crud.view_room', room_id=room_id))
        
        if request.method == "POST":
            # Extract update data
            update_data = RoomUpdateData(
                name=request.form.get('name'),
                description=request.form.get('description'),
                goals=request.form.get('goals'),
                group_size=request.form.get('group_size')
            )
            
            # Use service layer
            result = RoomService.update_room(room_id, update_data, user)
            
            if result.success:
                flash("Room updated successfully!", "success")
                return redirect(url_for('room.room_crud.view_room', room_id=room_id))
            else:
                flash(f"Error: {result.error}", "error")
        
        # GET request - show edit form
        return render_template(
            "room/edit.html",
            room=room,
            user=user,
            invitation_count=get_invitation_count(user)
        )
        
    except Exception as e:
        current_app.logger.error(f"Error editing room {room_id}: {e}")
        flash("An unexpected error occurred. Please try again.", "error")
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
def create_chat(room_id: int) -> Any:
    """Create a new chat within a room."""
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

        # Generate and add AI introduction message
        try:
            # Infer template type from room characteristics
            template_type = infer_template_type_from_room(chat_obj.room)
            learning_step = "step1"  # Default to step 1 for new chats
            
            introduction = generate_chat_introduction(
                chat_obj.room.goals, 
                template_type=template_type, 
                learning_step=learning_step, 
                room_id=chat_obj.room.id
            )

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
