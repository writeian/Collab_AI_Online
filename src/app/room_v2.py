"""
Room V2 - Clean Enhanced Dashboard Implementation
Step 1: Basic route with room links and activity sorting
"""

from flask import Blueprint, render_template, current_app
from datetime import datetime, timedelta
from typing import List, Dict, Any
from src.app import db
from src.models import Room, Chat, Message
from src.app.access_control import get_current_user, require_login
from src.app.room.services.room_service import RoomService

# Create independent blueprint
room_v2 = Blueprint("room_v2", __name__)


def calculate_activity_score(room: Room) -> int:
    """
    Step 1: Simple activity scoring for room sorting.
    Counts recent chats and messages to determine activity level.
    """
    try:
        # Look at last 7 days
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        # Count recent activity
        recent_chats = Chat.query.filter(
            Chat.room_id == room.id,
            Chat.created_at >= cutoff_date
        ).count()
        
        recent_messages = Message.query.join(Chat).filter(
            Chat.room_id == room.id,
            Message.timestamp >= cutoff_date
        ).count()
        
        # Simple scoring: chats = 10 points, messages = 1 point
        score = (recent_chats * 10) + recent_messages
        
        return score
        
    except Exception as e:
        current_app.logger.warning(f"Activity score error for room {room.id}: {e}")
        return 0


@room_v2.route("/")
@require_login
def index() -> Any:
    """Step 1: Basic activity-sorted room dashboard."""
    current_app.logger.info("🚀 ROOM V2 STEP 1: Basic activity sorting")
    
    try:
        user = get_current_user()
        current_app.logger.info(f"🚀 V2 User: {user.username}")
        
        # Get rooms using proven RoomService
        rooms_data = RoomService.get_user_rooms(user)
        owned_rooms = rooms_data["owned"]
        member_rooms = rooms_data["member"]
        
        # Combine and score all rooms
        all_rooms = []
        
        # Process owned rooms
        for room in owned_rooms:
            score = calculate_activity_score(room)
            all_rooms.append({
                "room": room,
                "is_owner": True,
                "activity_score": score
            })
        
        # Process member rooms
        for room in member_rooms:
            score = calculate_activity_score(room)
            all_rooms.append({
                "room": room,
                "is_owner": False,
                "activity_score": score
            })
        
        # Sort by activity (highest first)
        all_rooms.sort(key=lambda x: -x["activity_score"])
        
        current_app.logger.info(f"🚀 V2: Sorted {len(all_rooms)} rooms by activity")
        
        # Log top 3 for verification
        for i, room_data in enumerate(all_rooms[:3]):
            room = room_data["room"]
            score = room_data["activity_score"]
            current_app.logger.info(f"🚀 V2 #{i+1}: {room.name[:40]} (Score: {score})")
        
        return render_template(
            "room_v2_step1.html",
            sorted_rooms=all_rooms,
            user=user,
            total_rooms=len(all_rooms)
        )
        
    except Exception as e:
        current_app.logger.error(f"V2 Step 1 error: {e}")
        import traceback
        current_app.logger.error(f"V2 Traceback: {traceback.format_exc()}")
        from flask import flash, redirect, url_for
        flash("V2 dashboard failed. Please try the original.", "error")
        return redirect(url_for('room.room_crud.index'))
