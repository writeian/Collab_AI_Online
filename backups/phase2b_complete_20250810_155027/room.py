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
                
                # Save refined modes as custom prompts and create rubrics
                for mode in refined_modes:
                    if 'key' in mode and 'label' in mode and 'prompt' in mode:
                        # Save custom prompt
                        custom_prompt = CustomPrompt(
                            mode_key=mode['key'],
                            label=mode['label'],
                            prompt=mode['prompt'],
                            room_id=room_obj.id,
                            created_by=user.id
                        )
                        db.session.add(custom_prompt)
                        
                        # Create default rubric for this learning step
                        from rubric_templates import create_default_rubric_for_room
                        rubric_result = create_default_rubric_for_room(room_obj, mode['key'])
                        if rubric_result:
                            room_rubric, criteria_list, levels_list = rubric_result
                            db.session.add(room_rubric)
                            for criterion in criteria_list:
                                db.session.add(criterion)
                            for level in levels_list:
                                db.session.add(level)
                
                db.session.commit()
                flash(f"Room '{name}' created successfully with {len(refined_modes)} refined modes and assessment rubrics!")
            except Exception as e:
                current_app.logger.error(f"Error saving refined modes and rubrics: {e}")
                flash(f"Room '{name}' created successfully! (Mode and rubric saving failed: {str(e)})")
        # Fallback to original mode generation if no refined modes
        elif goals:
            try:
                contextual_modes = generate_room_modes(room_obj)
                
                # Save generated modes as custom prompts and create rubrics
                for mode_key, mode_info in contextual_modes.items():
                    # Save custom prompt
                    custom_prompt = CustomPrompt(
                        mode_key=mode_key,
                        label=mode_info.label,
                        prompt=mode_info.prompt,
                        room_id=room_obj.id,
                        created_by=user.id
                    )
                    db.session.add(custom_prompt)
                    
                    # Create default rubric for this learning step
                    from rubric_templates import create_default_rubric_for_room
                    rubric_result = create_default_rubric_for_room(room_obj, mode_key)
                    if rubric_result:
                        room_rubric, criteria_list, levels_list = rubric_result
                        db.session.add(room_rubric)
                        for criterion in criteria_list:
                            db.session.add(criterion)
                        for level in levels_list:
                            db.session.add(level)
                
                db.session.commit()
                flash(f"Room '{name}' created successfully with {len(contextual_modes)} contextual modes and assessment rubrics!")
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

@room.route("/generate-room-proposal", methods=["POST"])
@require_login
def generate_room_proposal():
    """Generate a complete room proposal including title, description, and modes."""
    try:
        data = request.get_json()
        goals = data.get('goals', '').strip()
        
        if not goals:
            return jsonify({'error': 'Goals are required for proposal generation'}), 400
        
        # Create a temporary room object for mode generation
        temp_room = Room(
            name="Temporary",
            description="",
            goals=goals,
            owner_id=get_current_user().id
        )
        
        # Generate contextual modes
        from openai_utils import generate_room_modes
        contextual_modes = generate_room_modes(temp_room)
        
        # Generate room title and description using AI
        client_type = get_client_type()
        if client_type:
            system_prompt = """You are an AI assistant helping to create collaborative learning rooms. Based on the learning goals provided, suggest:
1. A clear, descriptive room title (3-6 words)
2. A brief room description (1-2 sentences)

The title should be engaging and clearly indicate the room's purpose. The description should provide context about what students will learn.

IMPORTANT: Format your response exactly as follows:
Title: [Your suggested title]
Description: [Your suggested description]"""
            
            user_prompt = f"""Learning Goals: {goals}

Please suggest a room title and description for a collaborative learning space focused on these goals.

Format your response as:
Title: [suggested title]
Description: [suggested description]"""

            try:
                if client_type == "anthropic":
                    response = call_anthropic_api(
                        [{"role": "user", "content": user_prompt}],
                        system_prompt,
                        max_tokens=200
                    )
                else:
                    response = call_openai_api(
                        [{"role": "system", "content": system_prompt},
                         {"role": "user", "content": user_prompt}],
                        max_tokens=200
                    )
                
                # Parse the response to extract title and description
                if isinstance(response, tuple):
                    response_text = response[0]
                else:
                    response_text = response
                
                # Parse the response to extract title and description
                lines = response_text.strip().split('\n')
                room_title = "Learning Room"  # Default
                room_description = ""
                
                for line in lines:
                    line = line.strip()
                    # Look for title patterns
                    if line.lower().startswith('title:'):
                        room_title = line.split(':', 1)[1].strip()
                        # Clean up any quotes or extra formatting
                        room_title = room_title.strip('"').strip("'").strip()
                    # Look for description patterns
                    elif line.lower().startswith('description:'):
                        room_description = line.split(':', 1)[1].strip()
                        # Clean up any quotes or extra formatting
                        room_description = room_description.strip('"').strip("'").strip()
                
                # If no description was found, create a default one based on the title
                if not room_description and room_title != "Learning Room":
                    room_description = f"A collaborative learning space focused on {room_title.lower()} where students can work together to achieve their learning goals."
                
            except Exception as e:
                current_app.logger.error(f"Error generating room title/description: {e}")
                room_title = "Learning Room"
                room_description = ""
        else:
            room_title = "Learning Room"
            room_description = ""
        
        # Convert modes to JSON-serializable format with proper numbering
        modes_list = []
        for i, (mode_key, mode_info) in enumerate(contextual_modes.items(), 1):
            # Add numbering to label if it doesn't already have it
            label = mode_info.label
            if not label[0].isdigit() or not '.' in label.split()[0]:
                label = f"{i}. {label}"
            
            modes_list.append({
                'key': mode_key,
                'label': label,
                'prompt': mode_info.prompt
            })
        
        # Generate AI welcome message
        ai_message = f"I've created a room proposal based on your goals! The room '{room_title}' includes {len(modes_list)} learning steps designed to help achieve your objectives. You can refine any aspect of this proposal by chatting with me below."
        
        return jsonify({
            'success': True,
            'room_title': room_title,
            'room_description': room_description,
            'modes': modes_list,
            'conversation_id': f"proposal_{int(time.time())}",
            'ai_message': ai_message
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating room proposal: {e}")
        return jsonify({'error': 'Failed to generate proposal'}), 500

@room.route("/refine-room-proposal", methods=["POST"])
@require_login
def refine_room_proposal():
    """Refine room proposal through AI conversation."""
    try:
        data = request.get_json()
        conversation_id = data.get('conversation_id')
        user_message = data.get('message', '').strip()
        current_room_title = data.get('current_room_title', '')
        current_room_description = data.get('current_room_description', '')
        current_modes = data.get('current_modes', [])
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Create refinement prompt
        system_prompt = """You are an AI assistant helping to refine room proposals for collaborative learning spaces. 

The user wants to improve their room proposal. Your job is to:
1. Understand their feedback about the room title, description, or modes
2. Suggest specific improvements
3. Provide updated data in the requested format

You can update:
- Room title (provide as 'room_title' field)
- Room description (provide as 'room_description' field) 
- Modes (provide as 'modes' array with objects containing 'key', 'label', 'prompt')

Only update what the user specifically asks to change. Return your response as JSON with the fields you're updating."""

        # Build context from current proposal
        current_modes_text = "\n".join([
            f"- {mode['label']}: {mode['prompt'][:100]}..." 
            for mode in current_modes
        ])
        
        user_prompt = f"""Current Room Proposal:
Title: {current_room_title}
Description: {current_room_description}
Modes:
{current_modes_text}

User Feedback: {user_message}

Please refine this proposal based on the user's feedback. Return only the fields you're updating as JSON."""

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
            
        refined_data = json.loads(response_text)
        
        # Process updates
        updated_room_title = refined_data.get('room_title', current_room_title)
        updated_room_description = refined_data.get('room_description', current_room_description)
        updated_modes = current_modes
        
        if 'modes' in refined_data:
            # Convert refined modes to proper format with numbering
            updated_modes = []
            for i, mode_info in enumerate(refined_data['modes'], 1):
                if isinstance(mode_info, dict) and 'label' in mode_info and 'prompt' in mode_info:
                    # Add numbering to label if it doesn't already have it
                    label = mode_info['label']
                    if not label[0].isdigit() or not '.' in label.split()[0]:
                        label = f"{i}. {label}"
                    
                    updated_modes.append({
                        'key': mode_info.get('key', f'mode_{i}'),
                        'label': label,
                        'prompt': mode_info['prompt']
                    })
        
        # Generate AI response for the conversation
        ai_response = f"I've updated the proposal based on your feedback. The changes have been applied to the form above."
        
        return jsonify({
            'success': True,
            'room_title': updated_room_title,
            'room_description': updated_room_description,
            'modes': updated_modes,
            'ai_response': ai_response
        })
        
    except Exception as e:
        current_app.logger.error(f"Error refining room proposal: {e}")
        return jsonify({'error': 'Failed to refine proposal'}), 500 

@room.route("/<int:room_id>/rubric/<step_key>", methods=["GET"])
@require_room_access
def get_rubric(room_id, step_key):
    """Get rubric data for a specific learning step in a room."""
    try:
        from models import RubricCriterion, RubricLevel, RoomRubric
        
        # Get rubric criteria for this step
        criteria = RubricCriterion.query.filter_by(
            room_id=room_id, 
            step_key=step_key
        ).order_by(RubricCriterion.order).all()
        
        rubric_data = []
        for criterion in criteria:
            levels = RubricLevel.query.filter_by(criterion_id=criterion.id).order_by(RubricLevel.score).all()
            criterion_data = {
                'id': criterion.id,
                'name': criterion.name,
                'description': criterion.description,
                'weight': criterion.weight,
                'order': criterion.order,
                'levels': [{
                    'id': level.id,
                    'level': level.level,
                    'score': level.score,
                    'description': level.description,
                    'examples': level.examples
                } for level in levels]
            }
            rubric_data.append(criterion_data)
        
        # Get room rubric configuration
        room_rubric = RoomRubric.query.filter_by(room_id=room_id, step_key=step_key).first()
        progression_threshold = room_rubric.progression_threshold if room_rubric else 2.5
        
        return jsonify({
            'success': True,
            'criteria': rubric_data,
            'progression_threshold': progression_threshold
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting rubric: {e}")
        return jsonify({'error': 'Failed to get rubric data'}), 500

@room.route("/<int:room_id>/rubric/<step_key>/update", methods=["POST"])
@require_room_management
def update_rubric(room_id, step_key):
    """Update rubric data for a specific learning step."""
    try:
        from models import RubricCriterion, RubricLevel, RoomRubric
        
        data = request.get_json()
        criteria_data = data.get('criteria', [])
        progression_threshold = data.get('progression_threshold', 2.5)
        
        # Update or create room rubric configuration
        room_rubric = RoomRubric.query.filter_by(room_id=room_id, step_key=step_key).first()
        if not room_rubric:
            room_rubric = RoomRubric(
                room_id=room_id,
                step_key=step_key,
                progression_threshold=progression_threshold
            )
            db.session.add(room_rubric)
        else:
            room_rubric.progression_threshold = progression_threshold
            room_rubric.updated_at = datetime.utcnow()
        
        # Update criteria and levels
        for criterion_data in criteria_data:
            criterion_id = criterion_data.get('id')
            
            if criterion_id:
                # Update existing criterion
                criterion = RubricCriterion.query.get(criterion_id)
                if criterion and criterion.room_id == room_id:
                    criterion.name = criterion_data['name']
                    criterion.description = criterion_data.get('description', '')
                    criterion.weight = criterion_data.get('weight', 1.0)
                    criterion.order = criterion_data.get('order', 0)
                    
                    # Update levels
                    for level_data in criterion_data.get('levels', []):
                        level_id = level_data.get('id')
                        if level_id:
                            level = RubricLevel.query.get(level_id)
                            if level and level.criterion_id == criterion_id:
                                level.description = level_data['description']
                                level.examples = level_data.get('examples', '')
            else:
                # Create new criterion
                criterion = RubricCriterion(
                    room_id=room_id,
                    step_key=step_key,
                    name=criterion_data['name'],
                    description=criterion_data.get('description', ''),
                    weight=criterion_data.get('weight', 1.0),
                    order=criterion_data.get('order', 0)
                )
                db.session.add(criterion)
                db.session.flush()  # Get the ID
                
                # Create levels for new criterion
                for level_data in criterion_data.get('levels', []):
                    level = RubricLevel(
                        criterion_id=criterion.id,
                        level=level_data['level'],
                        score=level_data['score'],
                        description=level_data['description'],
                        examples=level_data.get('examples', '')
                    )
                    db.session.add(level)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rubric updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating rubric: {e}")
        return jsonify({'error': 'Failed to update rubric'}), 500

@room.route("/<int:room_id>/rubric/<step_key>/validate", methods=["POST"])
@require_room_management
def validate_rubric(room_id, step_key):
    """Validate rubric content using AI."""
    try:
        from models import RubricCriterion, RubricLevel
        
        data = request.get_json()
        criteria_data = data.get('criteria', [])
        
        # Build rubric text for AI validation
        rubric_text = f"Learning Step: {step_key}\n\n"
        
        for criterion in criteria_data:
            rubric_text += f"Criterion: {criterion['name']}\n"
            for level in criterion.get('levels', []):
                rubric_text += f"  {level['level']} ({level['score']}): {level['description']}\n"
            rubric_text += "\n"
        
        # AI validation prompt
        system_prompt = """You are an educational assessment expert. Review this rubric and provide feedback on:

1. **Clarity**: Are the descriptions clear and specific?
2. **Progression**: Do the levels show clear progression from basic to advanced?
3. **Educational Value**: Will this help students understand expectations?
4. **Balance**: Is the progression reasonable and achievable?

Provide specific suggestions for improvement. Be encouraging but honest about areas that need work."""

        user_prompt = f"Please review this rubric:\n\n{rubric_text}"
        
        # Call AI for validation
        client_type = get_client_type()
        if client_type == "anthropic":
            response = call_anthropic_api(
                [{"role": "user", "content": user_prompt}],
                system_prompt,
                max_tokens=800
            )
        else:
            response = call_openai_api(
                [{"role": "system", "content": system_prompt},
                 {"role": "user", "content": user_prompt}],
                max_tokens=800
            )
        
        if isinstance(response, tuple):
            validation_feedback = response[0]
        else:
            validation_feedback = response
        
        # Calculate average score for progression assessment
        total_score = 0
        total_levels = 0
        
        for criterion in criteria_data:
            for level in criterion.get('levels', []):
                total_score += level['score']
                total_levels += 1
        
        average_score = total_score / total_levels if total_levels > 0 else 0
        
        # Determine if progression threshold is appropriate
        threshold_warning = None
        if average_score < 2.0:
            threshold_warning = "The average score is quite low. Consider if students can realistically achieve higher levels."
        elif average_score > 3.5:
            threshold_warning = "The average score is quite high. Consider if the progression threshold is too lenient."
        
        return jsonify({
            'success': True,
            'validation_feedback': validation_feedback,
            'average_score': round(average_score, 2),
            'threshold_warning': threshold_warning,
            'recommendation': 'proceed' if average_score >= 2.0 else 'review'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error validating rubric: {e}")
        return jsonify({'error': 'Failed to validate rubric'}), 500 