#!/usr/bin/env python3
"""Test script to check invitation display on home page."""

from app import create_app
from models import db, User, Room, RoomMember
from datetime import datetime, timedelta

def test_invitation_display():
    """Test if invitations are displayed correctly on home page."""
    app = create_app()
    with app.app_context():
        print("=== TESTING INVITATION DISPLAY ===\n")
        
        # Test with testuser3 (who has an invitation)
        user = User.query.filter_by(username="testuser3").first()
        if not user:
            print("❌ No test user found")
            return
        
        print(f"Testing invitation display for: {user.username} ({user.display_name})")
        
        # Simulate the home page logic
        owned_rooms = Room.query.filter_by(owner_id=user.id, is_active=True).order_by(Room.created_at.desc()).all()
        member_rooms = Room.query.join(RoomMember).filter(
            RoomMember.user_id == user.id,
            Room.is_active == True
        ).order_by(Room.created_at.desc()).all()
        
        # Get recent invitations (rooms they were added to in the last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_invitations = RoomMember.query.filter(
            RoomMember.user_id == user.id,
            RoomMember.joined_at >= recent_cutoff
        ).join(Room).filter(Room.is_active == True).all()
        
        print(f"\nResults:")
        print(f"  - Owned rooms: {len(owned_rooms)}")
        print(f"  - Member rooms: {len(member_rooms)}")
        print(f"  - Recent invitations: {len(recent_invitations)}")
        
        if recent_invitations:
            print(f"\nRecent invitations:")
            for invitation in recent_invitations:
                room = invitation.room
                owner = User.query.get(room.owner_id)
                print(f"  - {room.name} (invited by {owner.display_name})")
                print(f"    Joined at: {invitation.joined_at}")
                print(f"    Room URL: /room/{room.id}")
                print(f"    Can create chats: {invitation.can_create_chats}")
                print(f"    Can invite members: {invitation.can_invite_members}")
        else:
            print(f"\n❌ No recent invitations found")
            
            # Check if there are any invitations at all (not just recent)
            all_invitations = RoomMember.query.filter(
                RoomMember.user_id == user.id
            ).join(Room).filter(Room.is_active == True).all()
            
            print(f"  - Total invitations: {len(all_invitations)}")
            if all_invitations:
                print(f"  - Most recent invitation: {all_invitations[0].joined_at}")
                print(f"  - Time difference: {datetime.utcnow() - all_invitations[0].joined_at}")
        
        # Test with different time windows
        print(f"\nTesting different time windows:")
        for hours in [1, 6, 12, 24, 48]:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            count = RoomMember.query.filter(
                RoomMember.user_id == user.id,
                RoomMember.joined_at >= cutoff
            ).count()
            print(f"  - Last {hours} hours: {count} invitations")

def test_home_page_simulation():
    """Simulate the exact home page logic."""
    app = create_app()
    with app.app_context():
        print("\n=== SIMULATING HOME PAGE ===\n")
        
        user = User.query.filter_by(username="testuser3").first()
        if not user:
            print("❌ No test user found")
            return
        
        print(f"Simulating home page for: {user.username}")
        
        # Exact logic from room.py index route
        owned_rooms = Room.query.filter_by(owner_id=user.id, is_active=True).order_by(Room.created_at.desc()).all()
        member_rooms = Room.query.join(RoomMember).filter(
            RoomMember.user_id == user.id,
            Room.is_active == True
        ).order_by(Room.created_at.desc()).all()
        
        # Get recent invitations (rooms they were added to in the last 24 hours)
        from datetime import datetime, timedelta
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_invitations = RoomMember.query.filter(
            RoomMember.user_id == user.id,
            RoomMember.joined_at >= recent_cutoff
        ).join(Room).filter(Room.is_active == True).all()
        
        print(f"Template variables:")
        print(f"  - recent_invitations: {len(recent_invitations)}")
        print(f"  - owned_rooms: {len(owned_rooms)}")
        print(f"  - member_rooms: {len(member_rooms)}")
        
        if recent_invitations:
            print(f"\nTemplate should show 'Recent Invitations' section with:")
            for invitation in recent_invitations:
                room = invitation.room
                owner = User.query.get(room.owner_id)
                print(f"  - {room.name} (invited by {owner.display_name})")
        else:
            print(f"\nTemplate will NOT show 'Recent Invitations' section")

def test_ianr_invitations():
    """Test what invitations IanR (TestUser) should see."""
    app = create_app()
    with app.app_context():
        print("\n=== TESTING IANR'S INVITATIONS ===\n")
        
        # Test with IanR (TestUser) - the current logged in user
        user = User.query.filter_by(username="TestUser").first()
        if not user:
            print("❌ No IanR user found")
            return
        
        print(f"Testing invitation display for: {user.username} ({user.display_name})")
        
        # Simulate the home page logic for IanR
        owned_rooms = Room.query.filter_by(owner_id=user.id, is_active=True).order_by(Room.created_at.desc()).all()
        member_rooms = Room.query.join(RoomMember).filter(
            RoomMember.user_id == user.id,
            Room.is_active == True
        ).order_by(Room.created_at.desc()).all()
        
        # Get recent invitations (rooms they were added to in the last 24 hours)
        from datetime import datetime, timedelta
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_invitations = RoomMember.query.filter(
            RoomMember.user_id == user.id,
            RoomMember.joined_at >= recent_cutoff
        ).join(Room).filter(Room.is_active == True).all()
        
        print(f"\nResults for IanR:")
        print(f"  - Owned rooms: {len(owned_rooms)}")
        print(f"  - Member rooms: {len(member_rooms)}")
        print(f"  - Recent invitations: {len(recent_invitations)}")
        
        if recent_invitations:
            print(f"\nRecent invitations for IanR:")
            for invitation in recent_invitations:
                room = invitation.room
                owner = User.query.get(room.owner_id)
                print(f"  - {room.name} (invited by {owner.display_name})")
                print(f"    Joined at: {invitation.joined_at}")
        else:
            print(f"\n❌ No recent invitations for IanR")
            
            # Check if IanR has any invitations at all
            all_invitations = RoomMember.query.filter(
                RoomMember.user_id == user.id
            ).join(Room).filter(Room.is_active == True).all()
            
            print(f"  - Total invitations for IanR: {len(all_invitations)}")
            if all_invitations:
                print(f"  - Most recent invitation: {all_invitations[0].joined_at}")
                print(f"  - Time difference: {datetime.utcnow() - all_invitations[0].joined_at}")
        
        # Check what rooms IanR owns and can invite to
        print(f"\nRooms IanR owns:")
        for room in owned_rooms:
            print(f"  - {room.name} (ID: {room.id})")
        
        print(f"\nRooms IanR is a member of:")
        for room in member_rooms:
            print(f"  - {room.name} (ID: {room.id})")

if __name__ == "__main__":
    test_invitation_display()
    test_home_page_simulation()
    test_ianr_invitations() 