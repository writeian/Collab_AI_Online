#!/usr/bin/env python3
"""
chat.py
Purpose: Chat functionality and AI integration blueprint
Status: [ACTIVE]
Created: 2025-01-27
Author: writeian

Manages chat conversations, AI responses, message handling, and prompt recording
"""


from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    current_app,
    jsonify,
)
from datetime import datetime
from src.app import db
from typing import Any
from src.models import Chat, Message, User, PromptRecord, Room, Comment, RoomMember
from src.utils.openai_utils import get_ai_response, get_modes_for_room, BASE_MODES
from src.app.access_control import (
    get_current_user,
    require_login,
    require_chat_access,
    require_chat_edit,
    require_chat_delete,
    can_access_chat,
    can_edit_chat,
)
from src.app.google_docs import validate_google_docs_url, get_document_content
from src.app.achievements import track_mode_usage
from sqlalchemy.orm import joinedload

chat = Blueprint("chat", __name__)

# Chat routes are now handled within room context
# See room.py for room-based chat creation and management


@chat.route("/<int:chat_id>", methods=["GET", "POST"])
@require_chat_access
def view_chat(chat_id: int) -> Any:
    """View and interact with a chat within a room."""
    try:
        chat_obj = Chat.query.get_or_404(chat_id)
        user = get_current_user()
        
        # Debug logging
        current_app.logger.info(f"Accessing chat {chat_id}, user: {user.username if user else 'None'}")
        current_app.logger.info(f"Chat room_id: {chat_obj.room_id}, created_by: {chat_obj.created_by}")

        if request.method == "POST":
            # CSRF-friendly: accept both form POST and fetch-based JSON
            if not user:
                flash("Please log in to send messages.")
                return redirect(url_for("auth.login"))

            # Try form first, then JSON fallback
            content = (request.form.get("content") or "").strip()
            ai_response_enabled = request.form.get("ai_response") == "1"
            if not content:
                # Try JSON then raw body parse
                if request.is_json:
                    data = request.get_json(silent=True) or {}
                    content = (data.get("content") or "").strip()
                    ai_response_enabled = bool(data.get("ai_response", ai_response_enabled))
                else:
                    try:
                        import json
                        data = json.loads(request.data or b"{}")
                        if isinstance(data, dict):
                            content = (data.get("content") or "").strip()
                            ai_response_enabled = bool(data.get("ai_response", ai_response_enabled))
                    except Exception:
                        pass

            # Debug logging
            current_app.logger.info(
                f"Received message content: '{content}' (length: {len(content)}), AI response enabled: {ai_response_enabled}"
            )

            if content:
                # Backend duplicate detection: Check for recent identical messages
                from datetime import datetime, timedelta

                recent_duplicate = Message.query.filter(
                    Message.chat_id == chat_obj.id,
                    Message.user_id == user.id,
                    Message.content == content,
                    Message.role == "user",
                    Message.timestamp >= datetime.utcnow() - timedelta(seconds=5),
                ).first()

                if recent_duplicate:
                    current_app.logger.info(
                        f"Duplicate message detected and ignored: '{content}'"
                    )
                    flash("Message sent successfully! (Duplicate prevented)")
                    return redirect(
                        url_for("chat.view_chat", chat_id=chat_obj.id), code=303
                    )

                # save user message
                user_msg = Message(
                    chat_id=chat_obj.id, user_id=user.id, role="user", content=content
                )
                db.session.add(user_msg)
                current_app.logger.info(
                    f"Adding user message: '{content}' to chat {chat_obj.id}"
                )

                # Track mode usage for achievements
                track_mode_usage(user.id, chat_obj.room_id, chat_obj.mode)

                # Record the prompt for dashboard analytics
                prompt_record = PromptRecord(
                    user_id=user.id,
                    chat_id=chat_obj.id,
                    room_id=chat_obj.room_id,
                    mode=chat_obj.mode,
                    prompt_content=content,
                )
                db.session.add(prompt_record)
                db.session.commit()

                # Ensure the user message is committed before getting AI response
                db.session.refresh(user_msg)
                current_app.logger.info(
                    f"User message committed with ID: {user_msg.id}"
                )

                # Double-check that the message is in the database
                db.session.flush()

                # Only get AI response if toggle is enabled
                if ai_response_enabled:
                    # ask GPT‑4o and store assistant reply
                    try:
                        ai_content, is_truncated = get_ai_response(chat_obj)
                    except Exception as e:
                        # If AI response fails, provide a helpful message
                        ai_content = "Hello! I'm here to help you with your research. What would you like to explore today?"
                        is_truncated = False
                        current_app.logger.error(f"AI response failed: {e}")

                    ai_msg = Message(
                        chat_id=chat_obj.id,
                        role="assistant",
                        content=ai_content,
                        is_truncated=is_truncated,
                        parent_message_id=None,
                    )
                    db.session.add(ai_msg)
                    db.session.commit()
                    current_app.logger.info(
                        f"AI message committed with ID: {ai_msg.id}"
                    )
                    flash("Message sent successfully!")
                else:
                    # No AI response requested
                    flash("Message sent successfully! (No AI response)")
                    current_app.logger.info(
                        f"User message sent without AI response: '{content}'"
                    )
            else:
                flash("Please enter a message to send.")
                current_app.logger.info(
                    f"Empty message rejected for user {user.id} in chat {chat_obj.id}"
                )

            return redirect(url_for("chat.view_chat", chat_id=chat_obj.id), code=303)

        messages = (
            Message.query.options(joinedload(Message.user))
            .filter_by(chat_id=chat_obj.id)
            .order_by(Message.timestamp)
            .all()
        )
        # Get comments for this chat
        comments = (
            Comment.query.options(joinedload(Comment.user))
            .filter_by(chat_id=chat_obj.id)
            .order_by(Comment.timestamp)
            .all()
        )

        # Get room members for sidebar display
        room_members = (
            RoomMember.query.options(joinedload(RoomMember.user))
            .filter_by(room_id=chat_obj.room_id)
            .all()
        )
        member_users = [member.user for member in room_members]

        # Add room owner to member list if not already included
        owner = User.query.get(chat_obj.room.owner_id)
        if owner and owner not in member_users:
            member_users.append(owner)

        # Get other chats in the same room (excluding current chat)
        other_chats = (
            Chat.query.filter_by(room_id=chat_obj.room_id)
            .filter(Chat.id != chat_obj.id)
            .order_by(Chat.created_at.desc())
            .all()
        )

        # Get dynamic modes for this chat's room
        modes = get_modes_for_room(chat_obj.room)

        # Get invitation count for navigation
        from src.app.room.utils.room_utils import get_invitation_count

        invitation_count = get_invitation_count(user)

        return render_template(
            "chat/view.html",
            chat=chat_obj,
            room=chat_obj.room,
            messages=messages,
            comments=comments,
            user=user,
            modes=modes,
            room_members=member_users,
            other_chats=other_chats,
            invitation_count=invitation_count,
        )
    except Exception as e:
        current_app.logger.error(f"Error in chat view for chat_id {chat_id}: {str(e)}")
        flash("An error occurred while loading the chat. Please try again.", "error")
        return redirect(url_for("room.room_crud.index"))


@chat.route("/<int:chat_id>/comment", methods=["POST"])
@require_chat_access
def add_comment(chat_id: int) -> Any:
    """Add a comment on a specific dialogue item."""
    chat_obj = Chat.query.get_or_404(chat_id)
    user = get_current_user()

    if not user:
        flash("Please log in to add comments.")
        return redirect(url_for("auth.login"))

    dialogue_number = request.form.get("dialogue_number", type=int)
    content = request.form.get("comment_content", "").strip()

    if not dialogue_number or not content:
        flash("Please provide both dialogue number and comment content.")
        return redirect(url_for("chat.view_chat", chat_id=chat_obj.id))

    # Validate that the dialogue number exists (check if there are enough messages)
    messages = (
        Message.query.filter_by(chat_id=chat_obj.id).order_by(Message.timestamp).all()
    )
    if dialogue_number < 1 or dialogue_number > len(messages):
        flash("Invalid dialogue number.")
        return redirect(url_for("chat.view_chat", chat_id=chat_obj.id))

    # Create the comment
    comment = Comment(
        chat_id=chat_obj.id,
        user_id=user.id,
        dialogue_number=dialogue_number,
        content=content,
    )
    db.session.add(comment)
    db.session.commit()

    flash("Comment added successfully.")
    return redirect(url_for("chat.view_chat", chat_id=chat_obj.id))


@chat.route("/<int:chat_id>/comment/<int:comment_id>/delete", methods=["POST"])
@require_chat_edit
def delete_comment(chat_id: int, comment_id: int) -> Any:
    """Delete a comment (only comment author or chat owner can delete)."""
    comment = Comment.query.get_or_404(comment_id)
    user = get_current_user()

    # Check if user can delete this comment
    if comment.user_id != user.id and comment.chat.created_by != user.id:
        flash("You don't have permission to delete this comment.")
        return redirect(url_for("chat.view_chat", chat_id=chat_id))

    db.session.delete(comment)
    db.session.commit()
    flash("Comment deleted successfully.")
    return redirect(url_for("chat.view_chat", chat_id=chat_id))


@chat.route("/<int:chat_id>/edit", methods=["GET", "POST"])
@require_chat_edit
def edit_chat(chat_id: int) -> Any:
    """Edit chat details."""
    chat_obj = Chat.query.get_or_404(chat_id)
    user = get_current_user()

    if request.method == "POST":
        chat_obj.title = request.form["title"].strip()
        chat_obj.mode = request.form.get("mode", "explore")
        db.session.commit()
        flash("Chat updated successfully.")
        return redirect(url_for("chat.view_chat", chat_id=chat_obj.id))

    # Get dynamic modes for this chat's room
    modes = get_modes_for_room(chat_obj.room)

    # Get invitation count for navigation
    from src.app.room.utils.room_utils import get_invitation_count

    invitation_count = get_invitation_count(user)

    return render_template(
        "chat/edit.html", chat=chat_obj, modes=modes, invitation_count=invitation_count
    )


@chat.route("/<int:chat_id>/delete", methods=["GET", "POST"])
@require_chat_delete
def delete_chat(chat_id: int) -> Any:
    """Delete a chat."""
    chat_obj = Chat.query.get_or_404(chat_id)
    user = get_current_user()
    room_id = chat_obj.room_id

    if request.method == "POST":
        # Delete the chat (messages will be deleted due to cascade)
        db.session.delete(chat_obj)
        db.session.commit()
        flash("Chat deleted successfully.")
        return redirect(url_for("room.room_crud.view_room", room_id=room_id))

    # Get invitation count for navigation
    from src.app.room.utils.room_utils import get_invitation_count

    invitation_count = get_invitation_count(user)

    return render_template(
        "chat/delete.html", chat=chat_obj, invitation_count=invitation_count
    )


@require_chat_access
@chat.route("/<int:chat_id>/continue/<int:message_id>", methods=["POST"])
def continue_message(chat_id: int, message_id: int) -> Any:
    print(f"continue_message called with chat_id={chat_id}, message_id={message_id}")
    prev_msg = Message.query.get_or_404(message_id)
    chat_obj = Chat.query.get_or_404(chat_id)
    ai_content, is_truncated = get_ai_response(chat_obj)
    print(f"get_ai_response returned: {ai_content[:40]}, truncated: {is_truncated}")
    try:
        new_msg = Message(
            chat_id=chat_obj.id,
            role="assistant",
            content=ai_content,
            is_truncated=is_truncated,
            parent_message_id=prev_msg.id,
        )
        db.session.add(new_msg)
        db.session.commit()
        print(
            f"Created continued message: {new_msg.id}, parent: {new_msg.parent_message_id}, truncated: {new_msg.is_truncated}, content: {new_msg.content[:40]}"
        )
    except Exception as e:
        print(f"Exception while creating continued message: {e}")
    return redirect(url_for("chat.view_chat", chat_id=chat_obj.id))


@chat.route("/<int:chat_id>/assess-progression", methods=["POST"])
@require_chat_access
def assess_progression(chat_id: int) -> Any:
    """Assess whether the user is ready to progress to the next learning step."""
    chat_obj = Chat.query.get_or_404(chat_id)
    user = get_current_user()

    if not user:
        return jsonify({"error": "User not authenticated"}), 401

    try:
        from src.utils.openai_utils import get_progression_recommendation_with_rubric as get_progression_recommendation

        # Get progression recommendation
        recommendation = get_progression_recommendation(chat_obj)

        return jsonify({"success": True, "recommendation": recommendation})

    except Exception as e:
        current_app.logger.error(f"Progression assessment failed: {e}")
        return (
            jsonify(
                {"success": False, "error": "Assessment failed. Please try again."}
            ),
            500,
        )
