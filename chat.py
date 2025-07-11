from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from models import db, Chat, Message, User, PromptRecord, Room
from openai_utils import get_ai_response, get_modes_for_room, BASE_MODES
from access_control import (
    get_current_user, 
    require_login, 
    require_chat_access, 
    require_chat_edit, 
    require_chat_delete,
    can_access_chat,
    can_edit_chat
)
from google_docs import validate_google_docs_url, get_document_content

chat = Blueprint('chat', __name__)

# Chat routes are now handled within room context
# See room.py for room-based chat creation and management

@chat.route("/chat/<int:chat_id>", methods=["GET", "POST"])
@require_chat_access
def view_chat(chat_id):
    """View and interact with a chat within a room."""
    chat_obj = Chat.query.get_or_404(chat_id)
    user = get_current_user()
    
    if request.method == "POST":
        if not user:
            flash("Please log in to send messages.")
            return redirect(url_for("auth.login"))
        
        content = request.form["content"].strip()
        if content:
            # save user message
            user_msg = Message(chat_id=chat_obj.id, user_id=user.id, role="user", content=content)
            db.session.add(user_msg)
            
            # Record the prompt for dashboard analytics
            prompt_record = PromptRecord(
                user_id=user.id,
                chat_id=chat_obj.id,
                room_id=chat_obj.room_id,
                mode=chat_obj.mode,
                prompt_content=content
            )
            db.session.add(prompt_record)
            db.session.commit()

            # ask GPT‑4o and store assistant reply
            ai_content = get_ai_response(chat_obj)
            ai_msg = Message(chat_id=chat_obj.id, role="assistant", content=ai_content)
            db.session.add(ai_msg)
            db.session.commit()
        return redirect(url_for("chat.view_chat", chat_id=chat_obj.id))

    messages = Message.query.filter_by(chat_id=chat_obj.id).order_by(Message.timestamp).all()
    # Get dynamic modes for this chat's room
    modes = get_modes_for_room(chat_obj.room)
    return render_template("chat/view.html", chat=chat_obj, messages=messages, user=user, modes=modes)

@chat.route("/chat/<int:chat_id>/edit", methods=["GET", "POST"])
@require_chat_edit
def edit_chat(chat_id):
    """Edit chat details."""
    chat_obj = Chat.query.get_or_404(chat_id)
    
    if request.method == "POST":
        chat_obj.title = request.form["title"].strip()
        chat_obj.mode = request.form.get("mode", "explore")
        db.session.commit()
        flash("Chat updated successfully.")
        return redirect(url_for("chat.view_chat", chat_id=chat_obj.id))
    
    # Get dynamic modes for this chat's room
    modes = get_modes_for_room(chat_obj.room)
    return render_template("chat/edit.html", chat=chat_obj, modes=modes)

@chat.route("/chat/<int:chat_id>/delete", methods=["GET", "POST"])
@require_chat_delete
def delete_chat(chat_id):
    """Delete a chat."""
    chat_obj = Chat.query.get_or_404(chat_id)
    room_id = chat_obj.room_id
    
    if request.method == "POST":
        # Delete the chat (messages will be deleted due to cascade)
        db.session.delete(chat_obj)
        db.session.commit()
        flash("Chat deleted successfully.")
        return redirect(url_for("room.view_room", room_id=room_id))
    
    return render_template("chat/delete.html", chat=chat_obj) 