from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, session, jsonify, current_app
from models import db, Room, RoomMember, Chat, User, Message, PromptRecord, CustomPrompt
from access_control import (
    get_current_user, 
    require_login, 
    require_room_access, 
    require_room_management,
    can_create_chats_in_room,
    can_invite_to_room,
    is_room_member
)
from openai_utils import get_ai_response, get_modes_for_room, BASE_MODES, generate_room_modes, get_client_type, call_anthropic_api, call_openai_api
from google_docs import validate_google_docs_url, get_document_content
from datetime import datetime, timedelta
import time

room = Blueprint('room', __name__)

@room.route("/")
def index():
    """Show all rooms the user has access to."""
    user = get_current_user()
    if user:
        # Show user's owned rooms and rooms they're a member of
        owned_rooms = Room.query.filter_by(owner_id=user.id, is_active=True).order_by(Room.created_at.desc()).all()
        member_rooms = Room.query.join(RoomMember).filter(
            RoomMember.user_id == user.id,
            Room.is_active == True
        ).order_by(Room.created_at.desc()).all()
        
        # Get recent unaccepted invitations (rooms they were added to in the last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_invitations = RoomMember.query.filter(
            RoomMember.user_id == user.id,
            RoomMember.joined_at >= recent_cutoff,
            RoomMember.accepted_at.is_(None)  # Only show unaccepted invitations
        ).join(Room).filter(Room.is_active == True).all()
        
    else:
        # Show only public rooms for anonymous users (if any)
        owned_rooms = []
        member_rooms = []
        recent_invitations = []
    
    return render_template("room/index.html", 
                         user=user, 
                         owned_rooms=owned_rooms, 
                         member_rooms=member_rooms,
                         recent_invitations=recent_invitations)

@room.route("/create", methods=["GET", "POST"])
@require_login
def create_room():
    """Create a new room."""
    user = get_current_user()
        
    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form.get("description", "").strip()
        goals = request.form.get("goals", "").strip()
        
        # Get refined modes from form data (if any)
        refined_modes_json = request.form.get("refined_modes", "")
        
        if not name:
            flash("Room name is required.")
            return redirect(url_for("room.create_room"))

        room_obj = Room(
            name=name, 
            description=description, 
            goals=goals,
            owner_id=user.id
        )
        db.session.add(room_obj)
        db.session.commit()
        
        # Handle refined modes if provided
        if refined_modes_json:
            try:
                import json
                refined_modes = json.loads(refined_modes_json)
                
                # Save refined modes as custom prompts
                for mode in refined_modes:
                    if 'key' in mode and 'label' in mode and 'prompt' in mode:
                        custom_prompt = CustomPrompt(
                            mode_key=mode['key'],
                            label=mode['label'],
                            prompt=mode['prompt'],
                            room_id=room_obj.id,
                            created_by=user.id
                        )
                        db.session.add(custom_prompt)
                
                db.session.commit()
                flash(f"Room '{name}' created successfully with {len(refined_modes)} refined modes!")
            except Exception as e:
                current_app.logger.error(f"Error saving refined modes: {e}")
                flash(f"Room '{name}' created successfully! (Mode saving failed: {str(e)})")
        # Fallback to original mode generation if no refined modes
        elif goals:
            try:
                contextual_modes = generate_room_modes(room_obj)
                
                # Save generated modes as custom prompts
                for mode_key, mode_info in contextual_modes.items():
                    custom_prompt = CustomPrompt(
                        mode_key=mode_key,
                        label=mode_info.label,
                        prompt=mode_info.prompt,
                        room_id=room_obj.id,
                        created_by=user.id
                    )
                    db.session.add(custom_prompt)
                
                db.session.commit()
                flash(f"Room '{name}' created successfully with {len(contextual_modes)} contextual modes!")
            except Exception as e:
                # If mode generation fails, still create the room but with base modes
                flash(f"Room '{name}' created successfully! (Mode generation failed: {str(e)})")
        else:
            flash(f"Room '{name}' created successfully!")
        
        return redirect(url_for("room.view_room", room_id=room_obj.id))
    
    return render_template("room/create.html")

@room.route("/<int:room_id>")
@require_room_access
def view_room(room_id):
    """View a room and its chats."""
    room_obj = Room.query.get_or_404(room_id)
    user = get_current_user()
    
    # Mark invitation as accepted if user is a member and hasn't accepted yet
    if user and user.id != room_obj.owner_id:
        membership = RoomMember.query.filter_by(room_id=room_obj.id, user_id=user.id).first()
        if membership and membership.accepted_at is None:
            membership.accepted_at = datetime.utcnow()
            db.session.commit()
    
    # Get all chats in this room
    chats = Chat.query.filter_by(room_id=room_obj.id).order_by(Chat.created_at.desc()).all()
    
    # Get room members
    members = RoomMember.query.filter_by(room_id=room_obj.id).all()
    member_users = [User.query.get(member.user_id) for member in members]
    
    # Add room owner to member list
    owner = User.query.get(room_obj.owner_id)
    if owner not in member_users:
        member_users.append(owner)
    
    return render_template("room/view.html", 
                         room=room_obj, 
                         chats=chats, 
                         members=member_users,
                         user=user)

@room.route("/<int:room_id>/edit", methods=["GET", "POST"])
@require_room_management
def edit_room(room_id):
    """Edit room details (owner only)."""
    room_obj = Room.query.get_or_404(room_id)
    
    if request.method == "POST":
        room_obj.name = request.form["name"].strip()
        room_obj.description = request.form.get("description", "").strip()
        room_obj.goals = request.form.get("goals", "").strip()
        db.session.commit()
        flash("Room updated successfully.")
        return redirect(url_for("room.view_room", room_id=room_obj.id))
    
    return render_template("room/edit.html", room=room_obj)

@room.route("/<int:room_id>/delete", methods=["GET", "POST"])
@require_room_management
def delete_room(room_id):
    """Delete a room (owner only)."""
    room_obj = Room.query.get_or_404(room_id)
    
    if request.method == "POST":
        # Delete the room (chats, members, and messages will be deleted due to cascade)
        db.session.delete(room_obj)
        db.session.commit()
        flash("Room deleted successfully.")
        return redirect(url_for("room.index"))
    
    return render_template("room/delete.html", room=room_obj)

@room.route("/<int:room_id>/invite", methods=["GET", "POST"])
@require_login
def invite_member(room_id):
    """Invite a user to join the room."""
    room_obj = Room.query.get_or_404(room_id)
    user = get_current_user()
    
    if not can_invite_to_room(user, room_obj):
        flash("You don't have permission to invite members to this room.")
        return redirect(url_for("room.view_room", room_id=room_obj.id))

    if request.method == "POST":
        # Change: invite by display name instead of username
        display_name = request.form["display_name"].strip()
        can_create_chats = request.form.get("can_create_chats") == "on"
        can_invite_members = request.form.get("can_invite_members") == "on"
        
        # Look up user by display name
        target_user = User.query.filter_by(display_name=display_name).first()
        if not target_user:
            flash("User not found.")
            return redirect(url_for("room.invite_member", room_id=room_obj.id))
        
        if target_user.id == user.id:
            flash("You cannot invite yourself to a room.")
            return redirect(url_for("room.invite_member", room_id=room_obj.id))
        
        # Check if already a member
        existing_member = RoomMember.query.filter_by(room_id=room_obj.id, user_id=target_user.id).first()
        if existing_member:
            flash("User is already a member of this room.")
            return redirect(url_for("room.invite_member", room_id=room_obj.id))
        
        # Create membership
        member = RoomMember(
            room_id=room_obj.id, 
            user_id=target_user.id, 
            can_create_chats=can_create_chats,
            can_invite_members=can_invite_members
        )
        db.session.add(member)
        db.session.commit()
        
        # Send notification to invited user
        notification_message = f"You have been invited to join '{room_obj.name}' by {user.display_name}."
        print(f"=== ROOM INVITATION NOTIFICATION ===")
        print(f"To: {target_user.display_name} ({target_user.email})")
        print(f"From: {user.display_name}")
        print(f"Room: {room_obj.name}")
        print(f"Message: {notification_message}")
        print(f"Room URL: {url_for('room.view_room', room_id=room_obj.id, _external=True)}")
        print("=== END ROOM INVITATION NOTIFICATION ===")
        
        flash(f"User {target_user.display_name} invited to room successfully.")
        flash(f"Notification sent to {target_user.display_name} ({target_user.email})", "info")
        return redirect(url_for("room.view_room", room_id=room_obj.id))
    
    return render_template("room/invite.html", room=room_obj)

@room.route("/<int:room_id>/members")
@require_room_access
def view_members(room_id):
    """View room members and their permissions."""
    room_obj = Room.query.get_or_404(room_id)
    user = get_current_user()
    
    # Get room members
    members = RoomMember.query.filter_by(room_id=room_obj.id).all()
    member_users = [User.query.get(member.user_id) for member in members]
    
    # Add room owner to member list
    owner = User.query.get(room_obj.owner_id)
    if owner not in member_users:
        member_users.append(owner)
    
    return render_template("room/members.html", room=room_obj, members=member_users, user=user)

@room.route("/<int:room_id>/members/<int:user_id>/remove", methods=["POST"])
@require_room_management
def remove_member(room_id, user_id):
    """Remove a member from the room (owner only)."""
    room_obj = Room.query.get_or_404(room_id)
    target_user = User.query.get_or_404(user_id)
    
    if target_user.id == room_obj.owner_id:
        flash("Cannot remove the room owner.")
        return redirect(url_for("room.view_members", room_id=room_obj.id))
    
    # Remove membership
    membership = RoomMember.query.filter_by(room_id=room_obj.id, user_id=user_id).first()
    if membership:
        db.session.delete(membership)
        db.session.commit()
        flash(f"User {target_user.display_name} removed from room.")
    else:
        flash("User is not a member of this room.")
    
    return redirect(url_for("room.view_members", room_id=room_obj.id))

@room.route("/<int:room_id>/chat/create", methods=["GET", "POST"])
@require_login
def create_chat(room_id):
    """Create a new chat within a room."""
    room_obj = Room.query.get_or_404(room_id)
    user = get_current_user()
    
    if not can_create_chats_in_room(user, room_obj):
        flash("You don't have permission to create chats in this room.")
        return redirect(url_for("room.view_room", room_id=room_obj.id))
        
    if request.method == "POST":
        title = request.form["title"].strip()
        mode = request.form.get("mode", "explore")
        google_doc_url = request.form.get("google_doc_url", "").strip()
        
        if not title:
            flash("Chat title is required.")
            return redirect(url_for("room.create_chat", room_id=room_obj.id))

        # Validate Google Doc URL if provided
        if google_doc_url:
            is_valid, doc_id_or_error = validate_google_docs_url(google_doc_url)
            if not is_valid:
                flash(f"Google Doc URL error: {doc_id_or_error}")
                return redirect(url_for("room.create_chat", room_id=room_obj.id))

        chat_obj = Chat(
            title=title, 
            room_id=room_obj.id, 
            created_by=user.id,
            mode=mode
        )
        db.session.add(chat_obj)
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
                    content=f"[Google Doc Content]\n\n{content}"
                )
                db.session.add(doc_message)
                
                # Get AI response to the imported content
                ai_content = get_ai_response(chat_obj)
                ai_msg = Message(chat_id=chat_obj.id, role="assistant", content=ai_content)
                db.session.add(ai_msg)
                db.session.commit()
                
                flash("Google Doc content imported successfully!")
        
        return redirect(url_for("chat.view_chat", chat_id=chat_obj.id))
    
    # Get dynamic modes for this room
    modes = get_modes_for_room(room_obj)
    return render_template("room/create_chat.html", room=room_obj, modes=modes) 

@room.route("/generate-draft-modes", methods=["POST"])
@require_login
def generate_draft_modes():
    """Generate draft modes for room creation without creating the room yet."""
    try:
        data = request.get_json()
        goals = data.get('goals', '').strip()
        
        if not goals:
            return jsonify({'error': 'Goals are required for mode generation'}), 400
        
        # Create a temporary room object for mode generation
        temp_room = Room(
            name="Temporary",
            description="",
            goals=goals,
            owner_id=get_current_user().id
        )
        
        # Generate contextual modes
        contextual_modes = generate_room_modes(temp_room)
        
        # Convert to JSON-serializable format
        modes_list = []
        for mode_key, mode_info in contextual_modes.items():
            modes_list.append({
                'key': mode_key,
                'label': mode_info.label,
                'prompt': mode_info.prompt
            })
        
        return jsonify({
            'success': True,
            'modes': modes_list,
            'conversation_id': f"refinement_{int(time.time())}"
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating draft modes: {e}")
        return jsonify({'error': 'Failed to generate modes'}), 500

@room.route("/refine-modes", methods=["POST"])
@require_login
def refine_modes():
    """Refine modes through AI conversation."""
    try:
        data = request.get_json()
        conversation_id = data.get('conversation_id')
        user_message = data.get('message', '').strip()
        current_modes = data.get('current_modes', [])
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Create refinement prompt
        system_prompt = """You are an AI assistant helping to refine writing modes for a collaborative learning room. 

The user has provided learning goals and wants to improve the generated modes. Your job is to:
1. Understand their feedback
2. Suggest specific improvements to the modes
3. Provide updated mode data in the same format

Each mode should have:
- A clear, descriptive label (2-4 words)
- A detailed prompt explaining the AI's role and approach

Return your response as a JSON object with mode keys and objects containing 'label' and 'prompt' fields."""

        # Build context from current modes
        current_modes_text = "\n".join([
            f"- {mode['label']}: {mode['prompt'][:100]}..." 
            for mode in current_modes
        ])
        
        user_prompt = f"""Current Modes:
{current_modes_text}

User Feedback: {user_message}

Please refine these modes based on the user's feedback. Return the updated modes as JSON."""

        # Call AI for refinement
        client_type = get_client_type()
        if client_type == "anthropic":
            response = call_anthropic_api(
                [{"role": "user", "content": user_prompt}],
                system_prompt,
                max_tokens=1000
            )
        else:
            response = call_openai_api(
                [{"role": "system", "content": system_prompt},
                 {"role": "user", "content": user_prompt}],
                max_tokens=1000
            )
        
        # Parse response
        import json
        if isinstance(response, tuple):
            response_text = response[0]
        else:
            response_text = response
            
        refined_modes_data = json.loads(response_text)
        
        # Convert to list format
        refined_modes = []
        for mode_key, mode_info in refined_modes_data.items():
            if isinstance(mode_info, dict) and 'label' in mode_info and 'prompt' in mode_info:
                refined_modes.append({
                    'key': mode_key,
                    'label': mode_info['label'],
                    'prompt': mode_info['prompt']
                })
        
        # Generate AI response for the conversation
        ai_response = f"I've refined the modes based on your feedback. The updated modes now better align with your learning goals."
        
        return jsonify({
            'success': True,
            'modes': refined_modes,
            'ai_response': ai_response
        })
        
    except Exception as e:
        current_app.logger.error(f"Error refining modes: {e}")
        return jsonify({'error': 'Failed to refine modes'}), 500 