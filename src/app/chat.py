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
    session,
)
from datetime import datetime
from src.app import db, markdown_filter, limiter
from typing import Any
from src.models import Chat, Message, User, PromptRecord, Room, Comment, RoomMember
from src.utils.openai_utils import get_ai_response, get_modes_for_room, BASE_MODES
from src.utils.progression import compute_suggestion, should_show_with_exponential_cooldown
from src.models.analytics import ProgressSuggestionState, ProgressSuggestionEvent
import os
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
            def coerce_bool(value, *, default=None):
                """Convert various truthy/falsey representations to bool."""
                if value is None:
                    return default
                if isinstance(value, bool):
                    return value
                if isinstance(value, (int, float)):
                    return value != 0
                value_str = str(value).strip().lower()
                if value_str in ("1", "true", "yes", "on"):
                    return True
                if value_str in ("0", "false", "no", "off"):
                    return False
                return default

            # CSRF-friendly: accept both form POST and fetch-based JSON
            if not user:
                flash("Please log in to send messages.")
                return redirect(url_for("auth.login"))

            # Try form first, then JSON fallback
            content = (request.form.get("content") or "").strip()
            ai_raw_values = request.form.getlist("ai_response")
            if ai_raw_values:
                ai_response_enabled = any(
                    coerce_bool(val, default=False) for val in ai_raw_values
                )
            else:
                # Default to enabled when the flag is omitted (legacy clients)
                ai_response_enabled = True
            if not content:
                # Try JSON then raw body parse
                if request.is_json:
                    data = request.get_json(silent=True) or {}
                    content = (data.get("content") or "").strip()
                    parsed_flag = coerce_bool(
                        data.get("ai_response"), default=ai_response_enabled
                    )
                    if parsed_flag is not None:
                        ai_response_enabled = parsed_flag
                else:
                    try:
                        import json
                        data = json.loads(request.data or b"{}")
                        if isinstance(data, dict):
                            content = (data.get("content") or "").strip()
                            parsed_flag = coerce_bool(
                                data.get("ai_response"), default=ai_response_enabled
                            )
                            if parsed_flag is not None:
                                ai_response_enabled = parsed_flag
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

                # Trigger automatic note generation if needed
                try:
                    from src.utils.learning.triggers import trigger_auto_note_generation
                    trigger_auto_note_generation(user_msg)
                except Exception as e:
                    current_app.logger.error(f"Auto note generation failed: {e}")

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
                        # Check for critique instructions (now available for all rooms)
                        critique_instructions = request.form.get("room81_critique_instructions", "")
                        
                        if critique_instructions:
                            ai_content, is_truncated = get_ai_response(
                                chat_obj, 
                                extra_system=critique_instructions
                            )
                        else:
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
                    
                    # Trigger automatic note generation if needed
                    try:
                        from src.utils.learning.triggers import trigger_auto_note_generation
                        trigger_auto_note_generation(ai_msg)
                    except Exception as e:
                        current_app.logger.error(f"Auto note generation failed: {e}")
                    # Conservative progression suggestion: feature-gated
                    try:
                        if os.getenv("MODE_SUGGEST_ENABLED", "true").lower() in ("1","true","yes"):
                            # Load or create per-chat, per-mode state
                            mode_key = chat_obj.mode or ""
                            state = (
                                ProgressSuggestionState.query.filter_by(chat_id=chat_obj.id, mode_key=mode_key).first()
                            )
                            if not state:
                                state = ProgressSuggestionState(chat_id=chat_obj.id, mode_key=mode_key)
                                db.session.add(state)
                                db.session.commit()

                            # Apply exponential cooldown gating based on assistant replies
                            state_dict = {
                                "mode": mode_key,
                                "shown_once": bool(state.shown_once),
                                "cooldown": int(state.cooldown or 1),
                                "since": int(state.since or 0),
                            }
                            should_show = should_show_with_exponential_cooldown(state_dict, chat_obj)
                            # Persist updated counters
                            state.shown_once = state_dict["shown_once"]
                            state.cooldown = state_dict["cooldown"]
                            state.since = state_dict["since"]
                            db.session.commit()

                            if should_show:
                                suggest = compute_suggestion(chat_obj)
                                if suggest:
                                    state.last_confidence = float(suggest.get("confidence", 0.0))
                                    state.last_shown_message_id = ai_msg.id
                                    db.session.commit()
                                    # Audit event
                                    try:
                                        ev = ProgressSuggestionEvent(
                                            chat_id=chat_obj.id,
                                            mode_key=mode_key,
                                            event_type="shown",
                                            user_id=(user.id if user else None),
                                            message_id=ai_msg.id,
                                        )
                                        db.session.add(ev)
                                        db.session.commit()
                                    except Exception:
                                        db.session.rollback()
                                    # Stash for next GET render
                                    payload = {
                                        "next_label": suggest.get("next_label") or "Next step",
                                        "link": suggest.get("link") or url_for("room.new_learning_steps", room_id=chat_obj.room_id),
                                        "confidence": suggest.get("confidence", 0.0),
                                    }
                                    session.setdefault("_mode_suggest", {})
                                    session["_mode_suggest"][str(chat_obj.id)] = payload
                                    session.modified = True
                    except Exception as _e:
                        current_app.logger.warning(f"[mode_suggest] skipped due to error: {_e}")
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
        # Get comments for this chat (with safe fallback if schema not yet migrated)
        try:
            comments = (
                Comment.query.options(joinedload(Comment.user))
                .filter_by(chat_id=chat_obj.id)
                .order_by(Comment.timestamp)
                .all()
            )
        except Exception as _e:
            current_app.logger.warning(
                f"Comments load failed (likely pending migration). Rendering without comments. err={_e}"
            )
            comments = []

        # Get room members for sidebar display
        room_members = (
            RoomMember.query.options(joinedload(RoomMember.user))
            .filter_by(room_id=chat_obj.room_id)
            .all()
        )
        member_users = [member.user for member in room_members]

        # Add room owner to member list if not already included
        owner = chat_obj.room.owner
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

        # Extract one-time suggestion payload from session (if present)
        suggestion = None
        try:
            ms = session.get('_mode_suggest', {}) or {}
            suggestion = ms.pop(str(chat_obj.id), None)
            if suggestion is not None:
                session['_mode_suggest'] = ms
                session.modified = True
        except Exception:
            suggestion = None

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
            suggestion=suggestion,
        )
    except Exception as e:
        current_app.logger.error(f"Error in chat view for chat_id {chat_id}: {str(e)}")
        flash("An error occurred while loading the chat. Please try again.", "error")
        return redirect(url_for("room.room_crud.index"))


@chat.route("/<int:chat_id>/export")
@require_chat_access
def export_chat(chat_id: int) -> Any:
    """Show export options for a chat."""
    try:
        chat_obj = Chat.query.get_or_404(chat_id)
        user = get_current_user()
        
        # Get all messages for this chat
        messages = Message.query.filter_by(chat_id=chat_obj.id).order_by(Message.timestamp).all()
        
        return render_template(
            "chat/export.html",
            chat=chat_obj,
            room=chat_obj.room,
            messages=messages,
            user=user
        )
        
    except Exception as e:
        current_app.logger.error(f"Error showing export page for chat {chat_id}: {e}")
        flash("Failed to load export page. Please try again.", "error")
        return redirect(url_for("chat.view_chat", chat_id=chat_id))


        messages = (
            Message.query.options(joinedload(Message.user))
            .filter_by(chat_id=chat_obj.id)
            .order_by(Message.timestamp)
            .all()
        )
        # Get comments for this chat (with safe fallback if schema not yet migrated)
        try:
            comments = (
                Comment.query.options(joinedload(Comment.user))
                .filter_by(chat_id=chat_obj.id)
                .order_by(Comment.timestamp)
                .all()
            )
        except Exception as _e:
            current_app.logger.warning(
                f"Comments load failed (likely pending migration). Rendering without comments. err={_e}"
            )
            comments = []

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

        # Extract one-time suggestion payload from session (if present)
        suggestion = None
        try:
            ms = session.get('_mode_suggest', {}) or {}
            suggestion = ms.pop(str(chat_obj.id), None)
            if suggestion is not None:
                session['_mode_suggest'] = ms
                session.modified = True
        except Exception:
            suggestion = None

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
            suggestion=suggestion,
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
    parent_comment_id = None  # replies temporarily disabled during rollback
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
    # Optional reply-to parent
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


@chat.route("/<int:chat_id>/messages", methods=["GET"])
@limiter.limit("1000 per hour")  # High limit for polling - active users poll every 5s
@require_chat_access
def get_new_messages(chat_id: int) -> Any:
    """Return messages newer than a given message id for incremental polling.
    
    Adaptive polling intervals (chat-view.js):
    - Active: 5s (720/hour) when user interacting
    - Idle: 30-90s (40-120/hour) after 2 minutes inactive
    Rate limit set high to accommodate active polling while preventing abuse.
    """
    try:
        chat_obj = Chat.query.get(chat_id)
        if not chat_obj:
            current_app.logger.warning(f"Chat {chat_id} not found for message polling (may be deleted)")
            return jsonify({"success": False, "error": "Chat not found"}), 404
            
        after_id = request.args.get("after_id", type=int)

        q = Message.query.options(joinedload(Message.user)).filter_by(chat_id=chat_obj.id)
        if after_id:
            q = q.filter(Message.id > after_id)
        q = q.order_by(Message.id.asc()).limit(50)

        new_messages = q.all()

        def to_payload(m: Message) -> dict:
            return {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp.isoformat(),
                "rendered_html": markdown_filter(m.content or ""),
                "user": {
                    "id": m.user.id if m.user else None,
                    "display_name": m.user.display_name if m.user else None,
                },
            }

        payload = [to_payload(m) for m in new_messages]
        last_id = payload[-1]["id"] if payload else (after_id or 0)
        return jsonify({"success": True, "messages": payload, "last_id": last_id})
    except Exception as e:
        current_app.logger.error(f"Error fetching new messages for chat {chat_id}: {e}")
        return jsonify({"success": False, "error": "Failed to load new messages"}), 500


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
