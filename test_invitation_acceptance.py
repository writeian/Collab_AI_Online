#!/usr/bin/env python3
"""Test script to verify invitation acceptance functionality."""

from app import create_app
from models import db, User, Room, RoomMember
from datetime import datetime, timedelta

def test_invitation_acceptance():
    """Test the invitation acceptance functionality."""
    app = create_app()
    with app.app_context():
        print("=== TESTING INVITATION ACCEPTANCE ===\n")
        
        # Test with testuser3 (who has an invitation)
        user = User.query.filter_by(username="testuser3").first()
        if not user:
            print("❌ No test user found")
            return
        
        print(f"Testing invitation acceptance for: {user.username} ({user.display_name})")
        
        # Check current invitations before acceptance
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_invitations = RoomMember.query.filter(
            RoomMember.user_id == user.id,
            RoomMember.joined_at >= recent_cutoff,
            RoomMember.accepted_at.is_(None)
        ).join(Room).filter(Room.is_active == True).all()
        
        print(f"\nBefore acceptance:")
        print(f"  - Unaccepted invitations: {len(recent_invitations)}")
        for invitation in recent_invitations:
            room = invitation.room
            print(f"    - {room.name} (joined: {invitation.joined_at}, accepted: {invitation.accepted_at})")
        
        # Simulate accepting an invitation by setting accepted_at
        if recent_invitations:
            invitation = recent_invitations[0]
            room = invitation.room
            print(f"\nSimulating acceptance of invitation to: {room.name}")
            
            # Update the invitation to mark it as accepted
            invitation.accepted_at = datetime.utcnow()
            db.session.commit()
            
            print(f"✅ Marked invitation as accepted at: {invitation.accepted_at}")
        
        # Check invitations after acceptance
        recent_invitations_after = RoomMember.query.filter(
            RoomMember.user_id == user.id,
            RoomMember.joined_at >= recent_cutoff,
            RoomMember.accepted_at.is_(None)
        ).join(Room).filter(Room.is_active == True).all()
        
        print(f"\nAfter acceptance:")
        print(f"  - Unaccepted invitations: {len(recent_invitations_after)}")
        for invitation in recent_invitations_after:
            room = invitation.room
            print(f"    - {room.name} (joined: {invitation.joined_at}, accepted: {invitation.accepted_at})")
        
        # Verify the notification count would be correct
        invitation_count = len(recent_invitations_after)
        print(f"\nNotification count: {invitation_count}")
        
        if invitation_count == 0:
            print("✅ Invitation notification cleared successfully!")
        else:
            print(f"⚠️  Still showing {invitation_count} unaccepted invitations")

def test_home_page_logic():
    """Test the home page invitation logic."""
    app = create_app()
    with app.app_context():
        print("\n=== TESTING HOME PAGE LOGIC ===\n")
        
        user = User.query.filter_by(username="testuser3").first()
        if not user:
            print("❌ No test user found")
            return
        
        print(f"Testing home page logic for: {user.username}")
        
        # Simulate the exact home page logic
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_invitations = RoomMember.query.filter(
            RoomMember.user_id == user.id,
            RoomMember.joined_at >= recent_cutoff,
            RoomMember.accepted_at.is_(None)  # Only show unaccepted invitations
        ).join(Room).filter(Room.is_active == True).all()
        
        print(f"Template variables:")
        print(f"  - recent_invitations: {len(recent_invitations)}")
        
        if recent_invitations:
            print(f"\nTemplate should show 'Recent Invitations' section with:")
            for invitation in recent_invitations:
                room = invitation.room
                owner = User.query.get(room.owner_id)
                print(f"  - {room.name} (invited by {owner.display_name})")
        else:
            print(f"\nTemplate will NOT show 'Recent Invitations' section")

if __name__ == "__main__":
    test_invitation_acceptance()
    test_home_page_logic() 