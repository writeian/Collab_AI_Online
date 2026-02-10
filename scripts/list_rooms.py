#!/usr/bin/env python3
"""
List all rooms in the database

Usage:
    python scripts/list_rooms.py
"""

import sys
import os

# Ensure we can import from src by adding project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import create_app, db
from src.models import Room, User, RoomMember


def list_rooms():
    """List all rooms in the database."""
    
    app = create_app()
    
    with app.app_context():
        # Get all rooms
        rooms = Room.query.order_by(Room.created_at.desc()).all()
        
        if not rooms:
            print("="*60)
            print("No rooms found in the database.")
            print("="*60)
            return
        
        print("="*60)
        print(f"Found {len(rooms)} room(s):")
        print("="*60)
        
        for room in rooms:
            # Get owner
            owner = User.query.get(room.owner_id)
            owner_name = owner.username if owner else "Unknown"
            
            # Get member count
            member_count = RoomMember.query.filter_by(room_id=room.id).count()
            
            # Get chat count
            chat_count = len(room.chats) if room.chats else 0
            
            print(f"\n📁 Room ID: {room.id}")
            print(f"   Name: {room.name}")
            print(f"   Description: {room.description[:100] if room.description else 'None'}...")
            print(f"   Owner: {owner_name} (ID: {room.owner_id})")
            print(f"   Members: {member_count + 1}")  # +1 for owner
            print(f"   Chats: {chat_count}")
            print(f"   Active: {'✅ Yes' if room.is_active else '❌ No'}")
            print(f"   Created: {room.created_at}")
            print("-" * 60)
        
        print("\n" + "="*60)
        print("Summary:")
        print(f"  Total rooms: {len(rooms)}")
        print(f"  Active rooms: {sum(1 for r in rooms if r.is_active)}")
        print(f"  Inactive rooms: {sum(1 for r in rooms if not r.is_active)}")
        print("="*60)


if __name__ == "__main__":
    list_rooms()


