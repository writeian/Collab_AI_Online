from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, PromptRecord, User, Chat, Room, RoomMember, Message
from access_control import get_current_user, require_login
from sqlalchemy import func
from collections import defaultdict

dashboard = Blueprint('dashboard', __name__)

@dashboard.route("/")
@require_login
def index():
    """Instructor/Team Leader Dashboard - Room Overview."""
    user = get_current_user()
    
    # Get rooms owned by the user
    owned_rooms = Room.query.filter_by(owner_id=user.id, is_active=True).order_by(Room.created_at.desc()).all()
    
    # Get rooms where user is a member (for team leaders who might not own all rooms)
    member_rooms = Room.query.join(RoomMember).filter(
        RoomMember.user_id == user.id,
        Room.is_active == True
    ).order_by(Room.created_at.desc()).all()
    
    # Combine and remove duplicates (rooms should never be None from queries)
    all_rooms = list({room.id: room for room in owned_rooms + member_rooms}.values())
    
    # Get room statistics
    room_stats = {}
    for room in all_rooms:
        # Count members (including owner)
        member_count = RoomMember.query.filter_by(room_id=room.id).count() + 1
        
        # Count chats
        chat_count = Chat.query.filter_by(room_id=room.id).count()
        
        # Count total messages
        message_count = db.session.query(func.count(Message.id)).join(Chat).filter(
            Chat.room_id == room.id
        ).scalar()
        
        # Get last activity (latest message timestamp)
        last_activity = db.session.query(func.max(Message.timestamp)).join(Chat).filter(
            Chat.room_id == room.id
        ).scalar()
        
        # Count prompts in this room
        prompt_count = PromptRecord.query.filter_by(room_id=room.id).count()
        
        room_stats[room.id] = {
            'member_count': member_count,
            'chat_count': chat_count,
            'message_count': message_count or 0,
            'last_activity': last_activity,
            'prompt_count': prompt_count
        }
    
    return render_template("dashboard/index.html", 
                         user=user,
                         rooms=all_rooms,
                         room_stats=room_stats)

@dashboard.route("/room/<int:room_id>")
@require_login
def room_detail(room_id):
    """Detailed view of a specific room with members and analytics."""
    user = get_current_user()
    room = Room.query.get_or_404(room_id)
    
    # Check if user has access to this room
    if room.owner_id != user.id and not RoomMember.query.filter_by(room_id=room.id, user_id=user.id).first():
        flash("You don't have access to this room.")
        return redirect(url_for("dashboard.index"))
    
    # Get room members
    members = RoomMember.query.filter_by(room_id=room.id).all()
    member_users = [User.query.get(member.user_id) for member in members]
    
    # Add room owner to member list
    owner = User.query.get(room.owner_id)
    if owner not in member_users:
        member_users.append(owner)
    
    # Get chats in this room
    chats = Chat.query.filter_by(room_id=room.id).order_by(Chat.created_at.desc()).all()
    
    # Get prompt analytics for this room
    prompts = PromptRecord.query.filter_by(room_id=room.id).order_by(PromptRecord.timestamp.desc()).all()
    
    # Mode usage statistics for this room
    mode_stats = db.session.query(
        PromptRecord.mode,
        func.count(PromptRecord.id).label('count')
    ).filter(PromptRecord.room_id == room.id).group_by(PromptRecord.mode).all()
    
    mode_counts = {mode: count for mode, count in mode_stats}
    
    # User activity in this room
    user_activity = db.session.query(
        PromptRecord.user_id,
        User.display_name,
        func.count(PromptRecord.id).label('prompt_count')
    ).join(User).filter(PromptRecord.room_id == room.id).group_by(
        PromptRecord.user_id, User.display_name
    ).all()
    
    return render_template("dashboard/room_detail.html",
                         user=user,
                         room=room,
                         members=member_users,
                         chats=chats,
                         prompts=prompts,
                         mode_counts=mode_counts,
                         user_activity=user_activity)

@dashboard.route("/prompts")
@require_login
def view_prompts():
    """View all prompts with room-based filtering."""
    user = get_current_user()
    
    # Get filter parameters
    room_filter = request.args.get('room', '')
    mode_filter = request.args.get('mode', '')
    user_filter = request.args.get('user', '')
    
    # Build query - only show prompts from rooms the user has access to
    user_room_ids = []
    
    # Rooms owned by user
    owned_rooms = Room.query.filter_by(owner_id=user.id).all()
    user_room_ids.extend([room.id for room in owned_rooms if room is not None])
    
    # Rooms where user is a member
    member_rooms = Room.query.join(RoomMember).filter(RoomMember.user_id == user.id).all()
    user_room_ids.extend([room.id for room in member_rooms if room is not None])
    
    query = PromptRecord.query.join(User).join(Chat).filter(
        PromptRecord.room_id.in_(user_room_ids)
    )
    
    if room_filter:
        query = query.filter(PromptRecord.room_id == room_filter)
    
    if mode_filter:
        query = query.filter(PromptRecord.mode == mode_filter)
    
    if user_filter:
        query = query.filter(User.username == user_filter)
    
    # Get unique rooms, modes, and users for filter dropdowns
    rooms = Room.query.filter(Room.id.in_(user_room_ids)).all()
    modes = db.session.query(PromptRecord.mode).filter(
        PromptRecord.room_id.in_(user_room_ids)
    ).distinct().all()
    users = db.session.query(User.username, User.display_name).join(PromptRecord).filter(
        PromptRecord.room_id.in_(user_room_ids)
    ).distinct().all()
    
    # Get filtered results
    prompts = query.order_by(PromptRecord.timestamp.desc()).all()
    
    return render_template("dashboard/prompts.html",
                         user=user,
                         prompts=prompts,
                         rooms=rooms,
                         modes=modes,
                         users=users,
                         current_room=room_filter,
                         current_mode=mode_filter,
                         current_user=user_filter) 