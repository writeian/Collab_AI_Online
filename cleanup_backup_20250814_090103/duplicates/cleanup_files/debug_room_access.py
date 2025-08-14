#!/usr/bin/env python3
"""
Debug script to check room and chat access permissions
"""

from app import create_app
from models import db, Chat, Message, User, Room, RoomMember
from access_control import get_current_user, can_access_room, can_access_chat, is_room_member

def test_room_access():
    app = create_app()
    
    with app.app_context():
        print("=== Room Access Debug ===")
        
        # Get the test user
        user = User.query.filter_by(username="TestUser").first()
        if not user:
            print("❌ TestUser not found!")
            return
        print(f"✅ Found user: {user.username} (ID: {user.id})")
        
        # Get a chat and its room
        chat = Chat.query.first()
        if not chat:
            print("❌ No chats found!")
            return
        print(f"✅ Found chat: {chat.id}")
        
        room = chat.room
        print(f"✅ Chat is in room: {room.name} (ID: {room.id})")
        print(f"   Room owner: {room.owner_id}")
        
        # Check room membership
        print(f"\n🔍 Checking room membership...")
        is_member = is_room_member(user, room)
        print(f"   Is room member: {is_member}")
        
        # Check room access
        can_access = can_access_room(user, room)
        print(f"   Can access room: {can_access}")
        
        # Check chat access
        can_access_chat_result = can_access_chat(user, chat)
        print(f"   Can access chat: {can_access_chat_result}")
        
        # Check if user is room owner
        is_owner = (room.owner_id == user.id)
        print(f"   Is room owner: {is_owner}")
        
        # Check room memberships
        memberships = RoomMember.query.filter_by(room_id=room.id).all()
        print(f"\n📋 Room memberships: {len(memberships)}")
        for membership in memberships:
            member_user = User.query.get(membership.user_id)
            print(f"   - {member_user.username if member_user else 'Unknown'} (ID: {membership.user_id})")
        
        # If user is not a member, let's add them
        if not is_member:
            print(f"\n➕ Adding TestUser to room...")
            new_membership = RoomMember(
                room_id=room.id,
                user_id=user.id,
                can_create_chats=True,
                can_invite=True
            )
            db.session.add(new_membership)
            db.session.commit()
            print(f"✅ Added TestUser to room!")
            
            # Check again
            is_member = is_room_member(user, room)
            can_access = can_access_room(user, room)
            can_access_chat_result = can_access_chat(user, chat)
            print(f"   Is room member: {is_member}")
            print(f"   Can access room: {can_access}")
            print(f"   Can access chat: {can_access_chat_result}")

if __name__ == "__main__":
    test_room_access() 