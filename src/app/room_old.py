#!/usr/bin/env python3
"""
room.py
Purpose: Collaborative room management blueprint
Status: [ACTIVE]
Created: 2025-01-27
Author: writeian

Handles room creation, membership, invitations, and room-based collaboration features
"""


from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    session,
    jsonify,
    current_app,
)
import json
import os
from datetime import datetime, timezone, timedelta
import time
from src.app import db
from typing import Any, Dict, List, Optional
from src.models import Room, RoomMember, Chat, User, Message, PromptRecord, CustomPrompt
from .access_control import (
    get_current_user,
    require_login,
    require_room_access,
    require_room_management,
    can_create_chats_in_room,
    can_invite_to_room,
    is_room_member,
)
from src.utils.openai_utils import (
    get_ai_response,
    get_modes_for_room,
    BASE_MODES,
    generate_room_modes,
    get_client_type,
    call_anthropic_api,
    call_openai_api,
    get_available_templates,
)
from .google_docs import validate_google_docs_url, get_document_content

room = Blueprint("room", __name__)


def get_invitation_count(user: Optional[User]) -> int:
    """Calculate invitation count for the navigation."""
    if not user:
        return 0

    recent_cutoff = datetime.utcnow() - timedelta(days=30)
    return (
        RoomMember.query.filter(
            RoomMember.user_id == user.id,
            RoomMember.joined_at >= recent_cutoff,
            RoomMember.accepted_at.is_(None),  # Only count unaccepted invitations
        )
        .join(Room)
        .filter(Room.is_active == True)
        .count()
    )


def infer_template_type_from_room(room: Room) -> Optional[str]:
    """
    Infer template type from room characteristics.
    
    Args:
        room: Room object to analyze
        
    Returns:
        Template type string or None if cannot be determined
    """
    if not room.goals:
        return None
    
    goals_lower = room.goals.lower()
    room_name_lower = room.name.lower()
    description_lower = (room.description or "").lower()
    
    # Template detection patterns
    template_patterns = {
        "academic-essay": [
            "research", "essay", "academic", "writing", "literature review",
            "thesis", "argument", "citation", "academic writing"
        ],
        "study-group": [
            "study", "collaborative", "peer", "group", "learning together",
            "shared", "collective", "team study"
        ],
        "business-hub": [
            "business", "entrepreneur", "startup", "market", "strategy",
            "commercial", "enterprise", "corporate", "business plan"
        ],
        "creative-studio": [
            "creative", "art", "design", "artistic", "visual", "portfolio",
            "creative project", "artistic expression", "design thinking"
        ],
        "writing-workshop": [
            "writing", "workshop", "creative writing", "storytelling",
            "narrative", "composition", "writing skills"
        ],
        "learning-lab": [
            "lab", "experiment", "hands-on", "practical", "skills",
            "experiential", "learning lab", "practical skills"
        ],
        "community-space": [
            "community", "network", "social", "connection", "collaboration",
            "community building", "networking", "social learning"
        ]
    }
    
    # Score each template based on pattern matches
    template_scores = {}
    for template, patterns in template_patterns.items():
        score = 0
        for pattern in patterns:
            if pattern in goals_lower:
                score += 2  # Goals are most important
            if pattern in room_name_lower:
                score += 1  # Room name is secondary
            if pattern in description_lower:
                score += 1  # Description is secondary
        template_scores[template] = score
    
    # Return the template with the highest score
    if template_scores:
        best_template = max(template_scores.items(), key=lambda x: x[1])
        if best_template[1] > 0:  # Only return if we have some confidence
            return best_template[0]
    
    return None


@room.route("/")
def index() -> Any:
    """Show all rooms the user has access to."""
    user = None  # Initialize user variable
    try:
        user = get_current_user()
        if user:
            # Show user's owned rooms and rooms they're a member of
            owned_rooms = (
                Room.query.filter_by(owner_id=user.id, is_active=True)
                .order_by(Room.created_at.desc())
                .all()
            )
            member_rooms = (
                Room.query.join(RoomMember)
                .filter(RoomMember.user_id == user.id, Room.is_active == True)
                .order_by(Room.created_at.desc())
                .all()
            )

            # Get recent unaccepted invitations (rooms they were added to in the last 24 hours)
            recent_cutoff = datetime.utcnow() - timedelta(hours=24)
            recent_invitations = (
                RoomMember.query.filter(
                    RoomMember.user_id == user.id,
                    RoomMember.joined_at >= recent_cutoff,
                    RoomMember.accepted_at.is_(
                        None
                    ),  # Only show unaccepted invitations
                )
                .join(Room)
                .filter(Room.is_active == True)
                .all()
            )

        else:
            # Show only public rooms for anonymous users (if any)
            owned_rooms = []
            member_rooms = []
            recent_invitations = []

        # Calculate invitation count for the navigation
        invitation_count = get_invitation_count(user)

        return render_template(
            "room/index.html",
            user=user,
            owned_rooms=owned_rooms,
            member_rooms=member_rooms,
            recent_invitations=recent_invitations,
            invitation_count=invitation_count,
        )
    except Exception as e:
        current_app.logger.error(f"Error loading room index: {str(e)}")
        flash("An error occurred while loading your rooms. Please try again.", "error")
        return render_template(
            "room/index.html",
            user=user,
            owned_rooms=[],
            member_rooms=[],
            recent_invitations=[],
            invitation_count=0,
        )


@room.route("/create", methods=["GET", "POST"])
@require_login
def create_room() -> Any:
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
            name=name, description=description, goals=goals, owner_id=user.id
        )
        db.session.add(room_obj)
        db.session.commit()

        # Handle refined modes if provided
        if refined_modes_json:
            try:
                refined_modes = json.loads(refined_modes_json)

                # Save refined modes as custom prompts and create rubrics
                for mode in refined_modes:
                    if "key" in mode and "label" in mode and "prompt" in mode:
                        # Save custom prompt
                        custom_prompt = CustomPrompt(
                            mode_key=mode["key"],
                            label=mode["label"],
                            prompt=mode["prompt"],
                            room_id=room_obj.id,
                            created_by=user.id,
                        )
                        db.session.add(custom_prompt)

                        # Simplified mode creation without rubrics
                        pass

                db.session.commit()
                flash(
                    f"Room '{name}' created successfully with {len(refined_modes)} refined modes!"
                )
            except Exception as e:
                current_app.logger.error(f"Error saving refined modes and rubrics: {e}")
                flash(
                    f"Room '{name}' created successfully! (Mode and rubric saving failed: {str(e)})"
                )
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
                        created_by=user.id,
                    )
                    db.session.add(custom_prompt)

                    # Simplified mode creation without rubrics
                    pass

                db.session.commit()
                flash(
                    f"Room '{name}' created successfully with {len(contextual_modes)} contextual modes!"
                )
            except Exception as e:
                # If mode generation fails, still create the room but with base modes
                flash(
                    f"Room '{name}' created successfully! (Mode generation failed: {str(e)})"
                )
        else:
            flash(f"Room '{name}' created successfully!")

        return redirect(url_for("room.view_room", room_id=room_obj.id))

    # Calculate invitation count for the navigation
    invitation_count = get_invitation_count(user)

    # Get available templates for the template selector
    available_templates = get_available_templates()

    return render_template(
        "room/learning_steps.html",
        room=None,
        is_editing=False,
        user=user,
        invitation_count=invitation_count,
        available_templates=available_templates,
    )


@room.route("/<int:room_id>")
@require_room_access
def view_room(room_id: int) -> Any:
    """View a room and its chats."""
    room_obj = Room.query.get_or_404(room_id)
    user = get_current_user()

    # Mark invitation as accepted if user is a member and hasn't accepted yet
    if user and user.id != room_obj.owner_id:
        membership = RoomMember.query.filter_by(
            room_id=room_obj.id, user_id=user.id
        ).first()
        if membership and membership.accepted_at is None:
            membership.accepted_at = datetime.utcnow()
            db.session.commit()

    # Get all chats in this room
    chats = (
        Chat.query.filter_by(room_id=room_obj.id).order_by(Chat.created_at.desc()).all()
    )

    # Get room members
    members = RoomMember.query.filter_by(room_id=room_obj.id).all()
    member_users = [User.query.get(member.user_id) for member in members]

    # Add room owner to member list
    owner = User.query.get(room_obj.owner_id)
    if owner not in member_users:
        member_users.append(owner)

    # Calculate invitation count for the navigation
    invitation_count = get_invitation_count(user)

    return render_template(
        "room/view.html",
        room=room_obj,
        chats=chats,
        members=member_users,
        user=user,
        invitation_count=invitation_count,
    )


@room.route("/<int:room_id>/edit", methods=["GET", "POST"])
@require_room_management
def edit_room(room_id: int) -> Any:
    """Edit room details (owner only)."""
    room_obj = Room.query.get_or_404(room_id)

    if request.method == "POST":
        room_obj.name = request.form["name"].strip()
        room_obj.description = request.form.get("description", "").strip()
        room_obj.goals = request.form.get("goals", "").strip()
        db.session.commit()
        flash("Room updated successfully.")
        return redirect(url_for("room.view_room", room_id=room_obj.id))

    # Redirect to learning steps management page instead of showing basic edit form
    return redirect(url_for("room.learning_steps", room_id=room_obj.id))


@room.route("/<int:room_id>/learning-steps", methods=["GET", "POST"])
@require_room_management
def learning_steps(room_id: int) -> Any:
    """Manage learning steps, AI instructions, and rubrics for a room."""
    room_obj = Room.query.get_or_404(room_id)

    if request.method == "POST":
        # Handle form submission for updating room and learning steps
        room_obj.name = request.form["name"].strip()
        room_obj.description = request.form.get("description", "").strip()
        room_obj.goals = request.form.get("goals", "").strip()

        # Handle refined modes if provided
        refined_modes_json = request.form.get("refined_modes", "")

        if refined_modes_json:
            try:
                refined_modes = json.loads(refined_modes_json)

                # Save refined modes as custom prompts and create rubrics
                for mode in refined_modes:
                    if "key" in mode and "label" in mode and "prompt" in mode:
                        # Save custom prompt
                        custom_prompt = CustomPrompt(
                            mode_key=mode["key"],
                            label=mode["label"],
                            prompt=mode["prompt"],
                            room_id=room_obj.id,
                            created_by=get_current_user().id,
                        )
                        db.session.add(custom_prompt)

                        # Simplified mode creation without rubrics
                        pass

                db.session.commit()
                flash(
                    f"Room '{room_obj.name}' updated successfully with {len(refined_modes)} refined learning steps!"
                )
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error saving refined modes and rubrics: {e}")
                flash(
                    f"Room '{room_obj.name}' updated successfully! (Learning steps and rubric saving failed: {str(e)})"
                )
        else:
            db.session.commit()
            flash("Room updated successfully.")

        return redirect(url_for("room.view_room", room_id=room_obj.id))

    # Get existing learning steps for this room
    from src.utils.openai_utils import get_modes_for_room

    existing_modes_dict = get_modes_for_room(room_obj)

    # Convert dictionary to array format expected by JavaScript
    existing_modes = []
    for mode_key, mode_info in existing_modes_dict.items():
        existing_modes.append(
            {"key": mode_key, "label": mode_info.label, "prompt": mode_info.prompt}
        )

    # Get saved rubric data for each learning step
    from src.models import RubricCriterion, RubricLevel

    saved_rubrics = {}

    for mode in existing_modes:
        step_key = mode["key"]
        criteria = (
            RubricCriterion.query.filter_by(room_id=room_obj.id, step_key=step_key)
            .order_by(RubricCriterion.order)
            .all()
        )

        if criteria:  # If we have saved rubric data
            rubric_data = []
            for criterion in criteria:
                levels = (
                    RubricLevel.query.filter_by(criterion_id=criterion.id)
                    .order_by(RubricLevel.score)
                    .all()
                )
                criterion_data = {
                    "name": criterion.name,
                    "weight": criterion.weight,
                    "levels": [
                        {
                            "level": level.level,
                            "score": level.score,
                            "description": level.description,
                        }
                        for level in levels
                    ],
                }
                rubric_data.append(criterion_data)
            saved_rubrics[step_key] = rubric_data

    # Calculate invitation count for the navigation
    user = get_current_user()
    invitation_count = get_invitation_count(user)

    return render_template(
        "room/learning_steps.html",
        room=room_obj,
        is_editing=True,
        existing_modes=existing_modes,
        saved_rubrics=saved_rubrics,
        user=user,
        invitation_count=invitation_count,
    )


@room.route("/<int:room_id>/update-learning-steps", methods=["POST"])
@require_room_management
def update_learning_steps(room_id: int) -> Any:
    """Update room learning steps via AJAX."""
    room_obj = Room.query.get_or_404(room_id)

    try:
        data = request.get_json()

        # Update basic room information
        room_obj.name = data.get("name", "").strip()
        room_obj.description = data.get("description", "").strip()
        room_obj.goals = data.get("goals", "").strip()

        # Handle learning steps updates
        modes = data.get("modes", [])

        if modes:
            # Clear existing custom prompts for this room
            CustomPrompt.query.filter_by(room_id=room_obj.id).delete()

            # Save new/updated modes as custom prompts
            for mode in modes:
                if "key" in mode and "label" in mode and "prompt" in mode:
                    custom_prompt = CustomPrompt(
                        mode_key=mode["key"],
                        label=mode["label"],
                        prompt=mode["prompt"],
                        room_id=room_obj.id,
                        created_by=get_current_user().id,
                    )
                    db.session.add(custom_prompt)

            # Note: Rubrics are handled separately via individual rubric save endpoints
            # This prevents accidental deletion of carefully crafted rubrics
            pass

        db.session.commit()

        return jsonify(
            {"success": True, "message": "Room learning steps updated successfully"}
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating learning steps: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@room.route("/<int:room_id>/regenerate-learning-steps", methods=["POST"])
@require_room_management
def regenerate_learning_steps(room_id: int) -> Any:
    """Regenerate learning steps based on current room goals."""
    room_obj = Room.query.get_or_404(room_id)

    try:
        # Generate new learning steps based on current goals
        from src.utils.openai_utils import generate_room_modes

        if not room_obj.goals:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Room must have learning goals to generate new learning steps",
                    }
                ),
                400,
            )

        # Generate new contextual modes
        new_modes = generate_room_modes(room_obj)

        # Convert to the format expected by frontend
        formatted_modes = []
        for mode_key, mode_info in new_modes.items():
            formatted_modes.append(
                {"key": mode_key, "label": mode_info.label, "prompt": mode_info.prompt}
            )

        return jsonify(
            {
                "success": True,
                "new_modes": formatted_modes,
                "message": f"Generated {len(formatted_modes)} new learning steps based on current goals",
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error regenerating learning steps: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@room.route("/<int:room_id>/apply-template", methods=["POST"])
@require_room_management
def apply_template(room_id: int) -> Any:
    """Apply a specific template to a room."""
    room_obj = Room.query.get_or_404(room_id)

    try:
        data = request.get_json()
        template_name = data.get("template_name")

        if not template_name:
            return (
                jsonify({"success": False, "error": "Template name is required"}),
                400,
            )

        # Generate modes using the specified template
        new_modes = generate_room_modes(room_obj, template_name)

        if not new_modes:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f'Template "{template_name}" not found or invalid',
                    }
                ),
                400,
            )

        # Convert to the format expected by frontend
        formatted_modes = []
        for mode_key, mode_info in new_modes.items():
            formatted_modes.append(
                {"key": mode_key, "label": mode_info.label, "prompt": mode_info.prompt}
            )

        return jsonify(
            {
                "success": True,
                "new_modes": formatted_modes,
                "message": f"Applied {template_name} template with {len(formatted_modes)} learning steps",
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error applying template: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@room.route("/<int:room_id>/delete", methods=["GET", "POST"])
@require_room_management
def delete_room(room_id: int) -> Any:
    """Delete a room (owner only)."""
    room_obj = Room.query.get_or_404(room_id)

    if request.method == "POST":
        # Delete the room (chats, members, and messages will be deleted due to cascade)
        db.session.delete(room_obj)
        db.session.commit()
        flash("Room deleted successfully.")
        return redirect(url_for("room.index"))

    # Calculate invitation count for the navigation
    user = get_current_user()
    invitation_count = get_invitation_count(user)

    return render_template(
        "room/delete.html", room=room_obj, user=user, invitation_count=invitation_count
    )


@room.route("/<int:room_id>/invite", methods=["GET", "POST"])
@require_login
def invite_member(room_id: int) -> Any:
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
        existing_member = RoomMember.query.filter_by(
            room_id=room_obj.id, user_id=target_user.id
        ).first()
        if existing_member:
            flash("User is already a member of this room.")
            return redirect(url_for("room.invite_member", room_id=room_obj.id))

        # Create membership
        member = RoomMember(
            room_id=room_obj.id,
            user_id=target_user.id,
            can_create_chats=can_create_chats,
            can_invite_members=can_invite_members,
        )
        db.session.add(member)
        db.session.commit()

        # Send notification to invited user
        notification_message = (
            f"You have been invited to join '{room_obj.name}' by {user.display_name}."
        )
        print(f"=== ROOM INVITATION NOTIFICATION ===")
        print(f"To: {target_user.display_name} ({target_user.email})")
        print(f"From: {user.display_name}")
        print(f"Room: {room_obj.name}")
        print(f"Message: {notification_message}")
        print(
            f"Room URL: {url_for('room.view_room', room_id=room_obj.id, _external=True)}"
        )
        print("=== END ROOM INVITATION NOTIFICATION ===")

        flash(f"User {target_user.display_name} invited to room successfully.")
        flash(
            f"Notification sent to {target_user.display_name} ({target_user.email})",
            "info",
        )
        return redirect(url_for("room.view_room", room_id=room_obj.id))

    # Calculate invitation count for the navigation
    user = get_current_user()
    invitation_count = get_invitation_count(user)

    return render_template(
        "room/invite.html", room=room_obj, user=user, invitation_count=invitation_count
    )


@room.route("/<int:room_id>/members")
@require_room_access
def view_members(room_id: int) -> Any:
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

    # Calculate invitation count for the navigation
    invitation_count = get_invitation_count(user)

    return render_template(
        "room/members.html",
        room=room_obj,
        members=member_users,
        user=user,
        invitation_count=invitation_count,
    )


@room.route("/<int:room_id>/members/<int:user_id>/remove", methods=["POST"])
@require_room_management
def remove_member(room_id: int, user_id: int) -> Any:
    """Remove a member from the room (owner only)."""
    room_obj = Room.query.get_or_404(room_id)
    target_user = User.query.get_or_404(user_id)

    if target_user.id == room_obj.owner_id:
        flash("Cannot remove the room owner.")
        return redirect(url_for("room.view_members", room_id=room_obj.id))

    # Remove membership
    membership = RoomMember.query.filter_by(
        room_id=room_obj.id, user_id=user_id
    ).first()
    if membership:
        db.session.delete(membership)
        db.session.commit()
        flash(f"User {target_user.display_name} removed from room.")
    else:
        flash("User is not a member of this room.")

    return redirect(url_for("room.view_members", room_id=room_obj.id))


@room.route("/<int:room_id>/chat/create", methods=["GET", "POST"])
@require_login
def create_chat(room_id: int) -> Any:
    """Create a new chat within a room."""
    # CRITICAL DEBUG: Log that OLD route is being hit
    try:
        from flask import current_app
        current_app.logger.error(f"🚨 OLD ROUTE HIT: room_old.create_chat room_id={room_id}, method={request.method}")
    except Exception:
        print(f"OLD ROUTE HIT: room_old.create_chat room_id={room_id}")
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

        chat_obj = Chat(title=title, room_id=room_obj.id, created_by=user.id, mode=mode)
        db.session.add(chat_obj)
        db.session.commit()

        # Generate and add AI introduction message
        try:
            from src.utils.openai_utils import generate_chat_introduction
            
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
    modes = get_modes_for_room(room_obj)

    # Calculate invitation count for the navigation
    user = get_current_user()
    invitation_count = get_invitation_count(user)

    return render_template(
        "room/create_chat.html",
        room=room_obj,
        modes=modes,
        user=user,
        invitation_count=invitation_count,
    )


@room.route("/generate-room-proposal", methods=["POST"])
@require_login
def generate_room_proposal():
    """Generate a complete room proposal including title, description, and modes."""
    try:
        data = request.get_json()
        goals = data.get("goals", "").strip()
        template_name = data.get("template", "").strip()

        if not goals:
            return jsonify({"error": "Goals are required for proposal generation"}), 400

        # Create a temporary room object for mode generation
        temp_room = Room(
            name="Temporary",
            description="",
            goals=goals,
            owner_id=get_current_user().id,
        )

        # Generate contextual modes (with template if specified)
        from src.utils.openai_utils import generate_room_modes, BASE_TEMPLATES

        contextual_modes = generate_room_modes(temp_room, template_name)

        # If a template is selected, use its name and description directly
        if template_name and template_name in BASE_TEMPLATES:
            template_data = BASE_TEMPLATES[template_name]
            room_title = template_data["name"]
            room_description = template_data["description"]
        else:
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
                            max_tokens=200,
                        )
                    else:
                        response = call_openai_api(
                            [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt},
                            ],
                            max_tokens=200,
                        )

                        # Parse the response to extract title and description
                    if isinstance(response, tuple):
                        response_text = response[0]
                    else:
                        response_text = response

                    # Parse the response to extract title and description
                    lines = response_text.strip().split("\n")
                    room_title = "Learning Room"  # Default
                    room_description = ""

                    for line in lines:
                        line = line.strip()
                        # Look for title patterns
                        if line.lower().startswith("title:"):
                            room_title = line.split(":", 1)[1].strip()
                            # Clean up any quotes or extra formatting
                            room_title = room_title.strip('"').strip("'").strip()
                        # Look for description patterns
                        elif line.lower().startswith("description:"):
                            room_description = line.split(":", 1)[1].strip()
                            # Clean up any quotes or extra formatting
                            room_description = (
                                room_description.strip('"').strip("'").strip()
                            )

                    # If no description was found, create a default one based on the title
                    if not room_description and room_title != "Learning Room":
                        room_description = f"A collaborative learning space focused on {room_title.lower()} where students can work together to achieve their learning goals."

                except Exception as e:
                    current_app.logger.error(
                        f"Error generating room title/description: {e}"
                    )
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
            if not label[0].isdigit() or not "." in label.split()[0]:
                label = f"{i}. {label}"

            modes_list.append(
                {"key": mode_key, "label": label, "prompt": mode_info.prompt}
            )

        # Generate AI welcome message
        ai_message = f"I've created a room proposal based on your goals! The room '{room_title}' includes {len(modes_list)} learning steps designed to help achieve your objectives. You can refine any aspect of this proposal by chatting with me below."

        return jsonify(
            {
                "success": True,
                "room_title": room_title,
                "room_description": room_description,
                "modes": modes_list,
                "conversation_id": f"proposal_{int(time.time())}",
                "ai_message": ai_message,
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error generating room proposal: {e}")
        return jsonify({"error": "Failed to generate proposal"}), 500


@room.route("/refine-room-proposal", methods=["POST"])
@require_login
def refine_room_proposal():
    """Refine room proposal for new room creation."""
    return _refine_room_proposal(None)


@room.route("/<int:room_id>/refine-room-proposal", methods=["POST"])
@require_room_management
def refine_existing_room_proposal(room_id):
    """Refine room proposal for existing room editing."""
    return _refine_room_proposal(room_id)


def _refine_room_proposal(room_id=None):
    """Internal function to handle room proposal refinement."""
    user = get_current_user()

    try:
        data = request.get_json()
        message = data.get("message", "").strip()
        conversation_id = data.get("conversation_id")
        current_modes = data.get("current_modes", [])
        current_room_title = data.get("current_room_title", "")
        current_room_description = data.get("current_room_description", "")

        if not message:
            return jsonify({"success": False, "error": "Message is required"})

        # Get room object if editing existing room
        room_obj = None
        if room_id:
            room_obj = Room.query.get_or_404(room_id)
            if room_obj.owner_id != user.id:
                return jsonify({"success": False, "error": "Permission denied"})

        # Use the existing refinement logic
        client_type = get_client_type()
        if not client_type:
            return jsonify({"success": False, "error": "No AI service available"})

        # Create refinement prompt that asks for structured JSON response
        system_prompt = """You are an AI assistant helping to refine room proposals for collaborative learning spaces. 

The user wants to improve their room proposal. Your job is to:
1. Understand their feedback about the room title, description, or modes
2. Suggest specific improvements
3. Provide updated data in JSON format

You can update:
- Room title (provide as 'room_title' field)
- Room description (provide as 'room_description' field) 
- Modes (provide as 'modes' array with objects containing 'key', 'label', 'prompt')

IMPORTANT: Return ONLY valid JSON with the fields you're updating. Do not include any other text.

Example response format:
{
  "room_title": "New Title",
  "room_description": "New description",
  "modes": [
    {
      "key": "explore",
      "label": "1. Topic Exploration",
      "prompt": "New prompt text"
    }
  ]
}"""

        # Build context from current proposal
        current_modes_text = "\n".join(
            [f"- {mode['label']}: {mode['prompt'][:100]}..." for mode in current_modes]
        )

        user_prompt = f"""Current Room Proposal:
Title: {current_room_title}
Description: {current_room_description}
Modes:
{current_modes_text}

User Feedback: {message}

Please refine this proposal based on the user's feedback. Return ONLY the JSON with the fields you're updating."""

        # Call AI for refinement
        if client_type == "anthropic":
            response, is_truncated = call_anthropic_api(
                [{"role": "user", "content": user_prompt}],
                system_prompt,
                max_tokens=1000,
            )
        else:
            response, is_truncated = call_openai_api(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=1000,
            )

        # Parse response - try to extract JSON from the response
        import json
        import re

        # Try to find JSON in the response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            try:
                refined_data = json.loads(json_match.group())
            except json.JSONDecodeError:
                # If JSON parsing fails, return conversational response
                return jsonify(
                    {
                        "success": True,
                        "ai_message": response,
                        "modes": current_modes,
                        "room_title": current_room_title,
                        "room_description": current_room_description,
                        "conversation_id": conversation_id or str(time.time()),
                        "changes_applied": False,
                    }
                )
        else:
            # No JSON found, return conversational response
            return jsonify(
                {
                    "success": True,
                    "ai_message": response,
                    "modes": current_modes,
                    "room_title": current_room_title,
                    "room_description": current_room_description,
                    "conversation_id": conversation_id or str(time.time()),
                    "changes_applied": False,
                }
            )

        # Process updates from JSON
        updated_room_title = refined_data.get("room_title", current_room_title)
        updated_room_description = refined_data.get(
            "room_description", current_room_description
        )
        updated_modes = current_modes.copy()

        if "modes" in refined_data:
            # Convert refined modes to proper format with numbering
            updated_modes = []
            for i, mode_info in enumerate(refined_data["modes"], 1):
                if (
                    isinstance(mode_info, dict)
                    and "label" in mode_info
                    and "prompt" in mode_info
                ):
                    # Add numbering to label if it doesn't already have it
                    label = mode_info["label"]
                    if not label[0].isdigit() or not "." in label.split()[0]:
                        label = f"{i}. {label}"

                    updated_modes.append(
                        {
                            "key": mode_info.get("key", f"mode_{i}"),
                            "label": label,
                            "prompt": mode_info["prompt"],
                        }
                    )

        # Generate AI response for the conversation
        changes_made = []
        if updated_room_title != current_room_title:
            changes_made.append(f"Updated room title to '{updated_room_title}'")
        if updated_room_description != current_room_description:
            changes_made.append("Updated room description")
        if updated_modes != current_modes:
            changes_made.append(f"Updated {len(updated_modes)} learning steps")

        if changes_made:
            ai_response = f"I've applied the following changes based on your feedback: {', '.join(changes_made)}. The updated proposal is now ready."
        else:
            ai_response = "I've reviewed your feedback but didn't make any changes. The current proposal remains as is."

        return jsonify(
            {
                "success": True,
                "ai_message": ai_response,
                "room_title": updated_room_title,
                "room_description": updated_room_description,
                "modes": updated_modes,
                "conversation_id": conversation_id or str(time.time()),
                "changes_applied": len(changes_made) > 0,
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error refining room proposal: {e}")
        return jsonify({"success": False, "error": str(e)})


@room.route("/<int:room_id>/rubric/<step_key>", methods=["GET"])
@require_room_access
def get_rubric(room_id, step_key):
    """Get rubric data for a specific learning step in a room."""
    try:
        from src.models import RubricCriterion, RubricLevel, RoomRubric

        # Get rubric criteria for this step
        criteria = (
            RubricCriterion.query.filter_by(room_id=room_id, step_key=step_key)
            .order_by(RubricCriterion.order)
            .all()
        )

        rubric_data = []
        for criterion in criteria:
            levels = (
                RubricLevel.query.filter_by(criterion_id=criterion.id)
                .order_by(RubricLevel.score)
                .all()
            )
            criterion_data = {
                "id": criterion.id,
                "name": criterion.name,
                "description": criterion.description,
                "weight": criterion.weight,
                "order": criterion.order,
                "levels": [
                    {
                        "id": level.id,
                        "level": level.level,
                        "score": level.score,
                        "description": level.description,
                        "examples": level.examples,
                    }
                    for level in levels
                ],
            }
            rubric_data.append(criterion_data)

        # Get room rubric configuration
        room_rubric = RoomRubric.query.filter_by(
            room_id=room_id, step_key=step_key
        ).first()
        progression_threshold = (
            room_rubric.progression_threshold if room_rubric else 2.5
        )

        return jsonify(
            {
                "success": True,
                "criteria": rubric_data,
                "progression_threshold": progression_threshold,
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error getting rubric: {e}")
        return jsonify({"error": "Failed to get rubric data"}), 500


@room.route("/<int:room_id>/rubric/<step_key>/update", methods=["POST"])
@require_room_management
def update_rubric(room_id, step_key):
    """Update rubric data for a specific learning step."""
    try:
        from src.models import RubricCriterion, RubricLevel, RoomRubric

        data = request.get_json()
        criteria_data = data.get("criteria", [])
        progression_threshold = data.get("progression_threshold", 2.5)

        # Update or create room rubric configuration
        room_rubric = RoomRubric.query.filter_by(
            room_id=room_id, step_key=step_key
        ).first()
        if not room_rubric:
            room_rubric = RoomRubric(
                room_id=room_id,
                step_key=step_key,
                progression_threshold=progression_threshold,
            )
            db.session.add(room_rubric)
        else:
            room_rubric.progression_threshold = progression_threshold
            room_rubric.updated_at = datetime.utcnow()

        # Clear existing criteria and levels for this step
        RubricCriterion.query.filter_by(room_id=room_id, step_key=step_key).delete(
            synchronize_session=False
        )

        # Create new criteria and levels
        for criterion_index, criterion_data in enumerate(criteria_data):
            criterion = RubricCriterion(
                room_id=room_id,
                step_key=step_key,
                name=criterion_data["name"],
                description=criterion_data.get("description", ""),
                weight=criterion_data.get("weight", 1.0),
                order=criterion_index,
            )
            db.session.add(criterion)
            db.session.flush()  # Get the ID

            # Create levels for new criterion
            for level_data in criterion_data.get("levels", []):
                level = RubricLevel(
                    criterion_id=criterion.id,
                    level=level_data["level"],
                    score=level_data["score"],
                    description=level_data["description"],
                    examples=level_data.get("examples", ""),
                )
                db.session.add(level)

        db.session.commit()

        return jsonify({"success": True, "message": "Rubric updated successfully"})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating rubric: {e}")
        return jsonify({"error": "Failed to update rubric"}), 500


# Template Wizard Routes
@room.route("/template/<template_type>")
@require_login
def template_wizard(template_type: str) -> Any:
    """Show template wizard for the specified template type."""
    valid_templates = [
        "study-group", "business-hub", "creative-studio", 
        "writing-workshop", "learning-lab", "community-space", "academic-essay"
    ]
    
    if template_type not in valid_templates:
        flash("Invalid template type.", "error")
        return redirect(url_for("room.index"))
    
    user = get_current_user()
    invitation_count = get_invitation_count(user)
    
    return render_template(
        f"room/templates/{template_type}.html",
        template_type=template_type,
        user=user,
        invitation_count=invitation_count
    )


@room.route("/template/<template_type>/generate-goals", methods=["POST"])
@require_login
def generate_template_goals(template_type: str) -> Any:
    """Generate learning goals based on template wizard answers."""
    try:
        # Validate request data
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        answers = data.get("answers", {})
        if not isinstance(answers, dict):
            return jsonify({"error": "Answers must be a dictionary"}), 400
        
        # Generate goals with proper error handling
        try:
            # Use new categorized goals for all supported templates
            supported_templates = ["study-group", "business-hub", "creative-studio", "writing-workshop", "learning-lab", "community-space", "academic-essay"]
            
            if template_type in supported_templates:
                from src.app.goals import generate_categorized_goals
                goals = generate_categorized_goals(template_type, answers)
                if not goals or not isinstance(goals, dict):
                    raise ValueError("Categorized goal generation returned invalid result")
            else:
                # For unsupported templates, return empty categorized goals
                current_app.logger.warning(f"Unsupported template type requested: {template_type}")
                goals = {
                    "core_goals": [],
                    "collaboration_goals": [],
                    "reflection_goals": []
                }
            
            return jsonify({
                "success": True, 
                "goals": goals,
                "template_type": template_type
            })
            
        except ValueError as ve:
            current_app.logger.error(f"Validation error in goal generation: {ve}")
            return jsonify({"error": "Invalid input data provided"}), 400
        except Exception as ge:
            current_app.logger.error(f"Goal generation error: {ge}")
            return jsonify({"error": "Failed to generate goals"}), 500
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error in generate_template_goals: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@room.route("/template/<template_type>/create-room", methods=["POST"])
@require_login
def create_template_room(template_type: str) -> Any:
    """Create a room from template wizard data."""
    try:
        # Validate request data
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract and validate required fields
        goals = data.get("goals", "").strip()
        room_name = data.get("room_name", "").strip()
        room_description = data.get("room_description", "").strip()
        group_size = data.get("group_size", "").strip()  # Extract group size
        
        # Validate required fields
        if not room_name:
            return jsonify({"error": "Room name is required"}), 400
        
        if len(room_name) > 100:
            return jsonify({"error": "Room name must be 100 characters or less"}), 400
        
        if len(room_description) > 500:
            return jsonify({"error": "Room description must be 500 characters or less"}), 400
        
        # Validate group size
        valid_group_sizes = ["small", "medium", "large", "individual"]
        if group_size and group_size not in valid_group_sizes:
            return jsonify({"error": "Invalid group size"}), 400
        
        user = get_current_user()
        
        # Generate unique room name to avoid conflicts
        from src.utils.room_descriptions import generate_unique_room_name, generate_room_short_description
        unique_room_name = generate_unique_room_name(room_name, user.id)
        
        # Generate short description for template rooms
        short_description = generate_room_short_description(
            template_type=template_type,
            room_name=room_name,
            group_size=group_size,
            goals=goals
        )
        
        # Create the room
        room = Room(
            name=unique_room_name,  # Use the unique name instead of original
            description=room_description,
            short_description=short_description,  # Add auto-generated short description
            goals=goals,
            group_size=group_size,  # Store group size
            owner_id=user.id,
            is_active=True
        )
        db.session.add(room)
        db.session.flush()  # Get the room ID
        
        # Generate modes based on goals
        try:
            modes = generate_room_modes(room, template_name=template_type)
            
            # Save generated modes as custom prompts
            if modes:
                for mode_key, mode_info in modes.items():
                    custom_prompt = CustomPrompt(
                        mode_key=mode_key,
                        label=mode_info.label,
                        prompt=mode_info.prompt,
                        room_id=room.id,
                        created_by=user.id,
                    )
                    db.session.add(custom_prompt)
            
        except Exception as mode_error:
            current_app.logger.warning(f"Mode generation failed for room {room.id}: {mode_error}")
            # Continue without modes - room will still be created
        
        db.session.commit()
        
        current_app.logger.info(f"Template room created successfully: {room.name} (ID: {room.id}) by user {user.id}")
        
        return jsonify({
            "success": True, 
            "room_id": room.id,
            "room_name": room.name,  # This will be the unique name
            "original_name": room_name,  # Include original name for reference
            "redirect_url": url_for("room.view_room", room_id=room.id)
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating template room: {e}")
        return jsonify({"error": "Failed to create room. Please try again."}), 500



