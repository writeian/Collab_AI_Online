"""
Beta Enhanced Room Dashboard Routes
Safe parallel implementation of activity-based room sorting
"""

from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from typing import Any, List, Dict
from datetime import datetime, timedelta
from src.app import db
from src.models import Room, User, Chat, Message, RoomMember
from src.app.access_control import get_current_user, require_login
from src.app.room.utils.room_utils import get_invitation_count

beta_bp = Blueprint("beta", __name__)


def get_unread_messages_count_beta(room: Room, user: User) -> int:
    """
    Beta version: Simple unread message detection based on room last visit.
    Returns count of messages newer than user's last room visit.
    """
    try:
        # Simple approach: messages from last 24 hours are considered "new"
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        unread_count = Message.query.join(Chat).filter(
            Chat.room_id == room.id,
            Message.timestamp > cutoff_time,
            Message.user_id != user.id  # Don't count user's own messages as unread
        ).count()
        
        return unread_count
        
    except Exception as e:
        current_app.logger.error(f"Beta: Error counting unread messages for room {room.id}: {e}")
        return 0


def get_room_activity_score(room: Room) -> int:
    """
    Calculate activity score for room sorting.
    Higher score = more recent activity.
    """
    try:
        # Get recent activity (last 7 days)
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        # Count recent messages (weighted more heavily)
        recent_messages = Message.query.join(Chat).filter(
            Chat.room_id == room.id,
            Message.timestamp >= cutoff_date
        ).count()
        
        # Count recent chats
        recent_chats = Chat.query.filter(
            Chat.room_id == room.id,
            Chat.created_at >= cutoff_date
        ).count()
        
        # Calculate activity score
        # Messages worth 1 point each, chats worth 5 points each
        activity_score = (recent_messages * 1) + (recent_chats * 5)
        
        return activity_score
        
    except Exception as e:
        current_app.logger.error(f"Beta: Error calculating activity score for room {room.id}: {e}")
        return 0


def get_rooms_with_activity_data_beta(user: User) -> List[Dict[str, Any]]:
    """
    Beta version: Get all user's rooms with comprehensive activity data, sorted by recent activity.
    Returns enhanced room data with activity sorting.
    """
    try:
        current_app.logger.info("🚀 Beta: Getting rooms with enhanced activity data")
        
        if not user or not user.id:
            current_app.logger.warning("Beta: Invalid user provided")
            return []
        
        # Get all rooms user has access to (owned + member)
        owned_rooms = Room.query.filter_by(owner_id=user.id, is_active=True).all() or []
        
        try:
            member_room_ids = db.session.query(RoomMember.room_id).filter_by(user_id=user.id).subquery()
            member_rooms = Room.query.filter(
                Room.id.in_(member_room_ids),
                Room.is_active == True,
                Room.owner_id != user.id  # Avoid duplicates with owned rooms
            ).all() or []
        except Exception:
            # If RoomMember table doesn't exist or query fails, continue with owned rooms only
            member_rooms = []
        
        all_rooms = owned_rooms + member_rooms
        
        if not all_rooms:
            current_app.logger.info(f"Beta: No rooms found for user {user.id}")
            return []
        
        # Get activity data for each room
        rooms_with_data = []
        for room in all_rooms:
            try:
                unread_count = get_unread_messages_count_beta(room, user)
                activity_score = get_room_activity_score(room)
                
                room_data = {
                    "room": room,
                    "unread_count": unread_count,
                    "has_unread": unread_count > 0,
                    "is_owner": room.owner_id == user.id,
                    "activity_score": activity_score
                }
                rooms_with_data.append(room_data)
            except Exception as room_error:
                current_app.logger.warning(f"Beta: Error processing room {room.id}: {room_error}")
                # Continue with other rooms
                continue
        
        # Sort by activity: unread messages first, then by activity score
        try:
            rooms_with_data.sort(key=lambda x: (
                -int(x.get("has_unread", False)),  # Unread rooms first (negative for desc)
                -x.get("activity_score", 0)        # Then by recent activity (negative for desc)
            ))
        except Exception as sort_error:
            current_app.logger.warning(f"Beta: Error sorting rooms: {sort_error}")
            # Return unsorted data rather than crash
        
        current_app.logger.info(f"Beta: Successfully processed {len(rooms_with_data)} rooms with activity data")
        return rooms_with_data
        
    except Exception as e:
        current_app.logger.error(f"Beta: Error getting rooms with activity data: {e}")
        import traceback
        current_app.logger.error(f"Beta: Traceback: {traceback.format_exc()}")
        return []


@beta_bp.route("/")
@require_login
def beta_index() -> Any:
    """Beta enhanced room dashboard with activity sorting."""
    current_app.logger.info("🚀 Beta route hit: Enhanced room dashboard")
    
    try:
        user = get_current_user()
        current_app.logger.info(f"🚀 Beta user: {user.username if user else 'None'}")
        
        # Get enhanced activity data
        rooms_with_activity = get_rooms_with_activity_data_beta(user)
        
        # Create compatibility data for existing template
        owned_rooms = [room_data['room'] for room_data in rooms_with_activity if room_data.get('is_owner', False)]
        member_rooms = [room_data['room'] for room_data in rooms_with_activity if not room_data.get('is_owner', False)]
        
        # Calculate summary stats
        total_rooms = len(rooms_with_activity)
        rooms_with_unread = sum(1 for r in rooms_with_activity if r.get("has_unread", False))
        
        # Get invitation count
        invitation_count = get_invitation_count(user)
        
        current_app.logger.info(f"🚀 Beta stats: {total_rooms} rooms, {rooms_with_unread} with unread, {invitation_count} invitations")
        
        return render_template(
            "room/beta_index.html",
            # Enhanced data
            rooms_with_activity=rooms_with_activity,
            total_rooms=total_rooms,
            rooms_with_unread=rooms_with_unread,
            # Compatibility data
            owned_rooms=owned_rooms,
            member_rooms=member_rooms,
            # Common data
            invitation_count=invitation_count,
            user=user
        )
        
    except Exception as e:
        current_app.logger.error(f"Beta: Error in beta index: {e}")
        flash("Failed to load enhanced room dashboard. Please try again.", "error")
        # Fallback to regular dashboard
        return redirect(url_for('room.room_crud.index'))
