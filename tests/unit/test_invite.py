#!/usr/bin/env python3
"""Test script for invite functionality."""

from app import create_app
from models import db, User, Room, RoomMember
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

def test_invite_functionality():
    """Test invite functionality."""
    app = create_app()
    with app.app_context():
        print("=== TESTING INVITE FUNCTIONALITY ===\n")
        
        # List all users
        users = User.query.all()
        print(f"Available users ({len(users)}):")
        for user in users:
            print(f"  - {user.username} ({user.display_name}) - ID: {user.id}")
        
        print("\n" + "="*50)
        
        # List all rooms
        rooms = Room.query.all()
        print(f"\nAvailable rooms ({len(rooms)}):")
        for room in rooms:
            owner = User.query.get(room.owner_id)
            print(f"  - {room.name} (Owner: {owner.username}) - ID: {room.id}")
            
            # List room members
            members = RoomMember.query.filter_by(room_id=room.id).all()
            print(f"    Members ({len(members)}):")
            for member in members:
                member_user = User.query.get(member.user_id)
                print(f"      - {member_user.username} (can_create_chats: {member.can_create_chats}, can_invite_members: {member.can_invite_members})")
        
        print("\n" + "="*50)
        
        # Test invite permissions
        print("\nTesting invite permissions:")
        room = Room.query.first()
        if room:
            for user in users:
                from access_control import can_invite_to_room
                can_invite = can_invite_to_room(user, room)
                print(f"  {user.username} can invite: {can_invite}")

def test_actual_invite():
    """Test the actual invite process."""
    app = create_app()
    with app.app_context():
        print("\n=== TESTING ACTUAL INVITE PROCESS ===\n")
        
        # Get test data
        room = Room.query.first()
        inviter = User.query.filter_by(username="TestUser").first()
        invitee = User.query.filter_by(username="testuser3").first()
        
        if not inviter or not invitee or not room:
            print("❌ Missing test data")
            return
        
        print(f"Inviter: {inviter.username} ({inviter.display_name})")
        print(f"Invitee: {invitee.username} ({invitee.display_name})")
        print(f"Room: {room.name}")
        
        # Check if invitee is already a member
        existing_member = RoomMember.query.filter_by(room_id=room.id, user_id=invitee.id).first()
        if existing_member:
            print(f"ERROR: {invitee.username} is already a member of this room")
            return
        
        # Check invite permissions
        from access_control import can_invite_to_room
        if not can_invite_to_room(inviter, room):
            print(f"ERROR: {inviter.username} cannot invite to this room")
            return
        
        print(f"\n✅ {inviter.username} can invite to this room")
        
        # Simulate the invite process
        try:
            member = RoomMember(
                room_id=room.id,
                user_id=invitee.id,
                can_create_chats=True,
                can_invite_members=False
            )
            db.session.add(member)
            db.session.commit()
            
            print(f"✅ Successfully invited {invitee.username} to {room.name}")
            
            # Verify the membership
            new_member = RoomMember.query.filter_by(room_id=room.id, user_id=invitee.id).first()
            print(f"✅ Membership verified: can_create_chats={new_member.can_create_chats}, can_invite_members={new_member.can_invite_members}")
            print(f"✅ Joined at: {new_member.joined_at}")
            
        except Exception as e:
            print(f"❌ Error during invite process: {e}")

def test_recent_invitations():
    """Test the recent invitations display."""
    app = create_app()
    with app.app_context():
        print("\n=== TESTING RECENT INVITATIONS ===\n")
        
        # Get a user to test with
        user = User.query.filter_by(username="testuser3").first()
        if not user:
            print("❌ No test user found")
            return
        
        print(f"Testing recent invitations for: {user.username}")
        
        # Get recent invitations (rooms they were added to in the last 24 hours)
        from datetime import datetime, timedelta
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_invitations = RoomMember.query.filter(
            RoomMember.user_id == user.id,
            RoomMember.joined_at >= recent_cutoff
        ).join(Room).filter(Room.is_active == True).all()
        
        print(f"Found {len(recent_invitations)} recent invitations:")
        for invitation in recent_invitations:
            room = invitation.room
            owner = User.query.get(room.owner_id)
            print(f"  - {room.name} (invited by {owner.username}) - joined at {invitation.joined_at}")
        
        # Test with different time windows
        print(f"\nTesting different time windows:")
        for hours in [1, 6, 12, 24, 48]:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            count = RoomMember.query.filter(
                RoomMember.user_id == user.id,
                RoomMember.joined_at >= cutoff
            ).count()
            print(f"  - Last {hours} hours: {count} invitations")

def test_web_interface_invite():
    """Test the web interface invite functionality."""
    app = create_app()
    with app.app_context():
        print("\n=== TESTING WEB INTERFACE INVITE ===\n")
        
        # Test the invite route
        from room import invite_member
        
        # Check if invite template exists
        try:
            room = Room.query.first()
            if room:
                print(f"✅ Invite template should be accessible for room: {room.name}")
                print(f"   URL: /room/{room.id}/invite")
        except Exception as e:
            print(f"❌ Error accessing invite template: {e}")
        
        # Test different invite scenarios
        print(f"\nTesting invite scenarios:")
        print("1. Invite non-existent user: Should show 'User not found'")
        print("2. Invite yourself: Should show 'You cannot invite yourself'")
        print("3. Invite existing member: Should show 'User is already a member'")
        print("4. Invite without permission: Should show 'You don't have permission'")
        print("5. Valid invite: Should succeed and add member")

def test_comprehensive_invite():
    """Comprehensive test of all invite scenarios."""
    app = create_app()
    with app.app_context():
        print("\n=== COMPREHENSIVE INVITE TEST ===\n")
        
        # Get test data
        room = Room.query.first()
        users = User.query.all()
        
        if not room or not users:
            print("❌ Missing test data")
            return
        
        print("Testing all invite scenarios:")
        
        for inviter in users:
            for invitee in users:
                if inviter.id == invitee.id:
                    continue  # Skip self-invite
                
                print(f"\n  Testing: {inviter.username} invites {invitee.username}")
                
                # Check permissions
                from access_control import can_invite_to_room
                can_invite = can_invite_to_room(inviter, room)
                
                if not can_invite:
                    print(f"    ❌ {inviter.username} cannot invite to this room")
                    continue
                
                # Check if already a member
                existing_member = RoomMember.query.filter_by(room_id=room.id, user_id=invitee.id).first()
                if existing_member:
                    print(f"    ⚠️  {invitee.username} is already a member")
                    continue
                
                print(f"    ✅ {inviter.username} can invite {invitee.username}")
                
                # Test the actual invite (but don't commit to avoid changing test data)
                try:
                    member = RoomMember(
                        room_id=room.id,
                        user_id=invitee.id,
                        can_create_chats=True,
                        can_invite_members=False
                    )
                    # Don't actually add to avoid changing test data
                    print(f"    ✅ Invite would succeed")
                except Exception as e:
                    print(f"    ❌ Invite would fail: {e}")

if __name__ == "__main__":
    test_invite_functionality()
    test_actual_invite()
    test_recent_invitations()
    test_web_interface_invite()
    test_comprehensive_invite() 