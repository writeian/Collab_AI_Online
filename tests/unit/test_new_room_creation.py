#!/usr/bin/env python3
"""
Test script to verify new room creation with custom goals.
Tests that contextual modes are generated and saved properly.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Room, CustomPrompt, User
from openai_utils import generate_room_modes, get_modes_for_room

def test_new_room_creation():
    """Test creating a new room with custom goals."""
    
    print("🔍 Testing new room creation with custom goals...")
    
    app = create_app()
    with app.app_context():
        # Find a test user
        test_user = User.query.first()
        if not test_user:
            print("❌ No users found in database")
            return
        
        print(f"✅ Using test user: {test_user.display_name}")
        
        # Create a test room with financial management goals
        test_room = Room(
            name="Financial Management Learning Room",
            description="A room for learning financial management concepts",
            goals="teach financial management, budgeting, and investment strategies",
            owner_id=test_user.id,
            created_at=datetime.utcnow()
        )
        
        print(f"   Creating room: {test_room.name}")
        print(f"   Goals: {test_room.goals}")
        
        # Test mode generation
        print("\n🤖 Testing mode generation...")
        try:
            contextual_modes = generate_room_modes(test_room)
            print(f"   Contextual modes generated: {len(contextual_modes)}")
            
            if contextual_modes:
                for mode_key, mode_info in list(contextual_modes.items())[:3]:
                    print(f"     - {mode_key}: {mode_info.label}")
                    print(f"       Prompt preview: {mode_info.prompt[:100]}...")
            else:
                print("   ❌ No contextual modes generated")
                
        except Exception as e:
            print(f"   ❌ Error generating modes: {e}")
            return
        
        # Test the full room creation process (without saving to DB)
        print("\n📋 Testing get_modes_for_room for new room...")
        try:
            modes = get_modes_for_room(test_room)
            print(f"   Modes returned: {len(modes)}")
            
            # Check if modes are contextual (not BASE_MODES)
            from openai_utils import BASE_MODES
            base_mode_keys = set(BASE_MODES.keys())
            mode_keys = set(modes.keys())
            
            if mode_keys == base_mode_keys:
                print("   ⚠️  Modes are identical to BASE_MODES")
            else:
                print("   ✅ Modes are contextual (different from BASE_MODES)")
                
        except Exception as e:
            print(f"   ❌ Error getting modes: {e}")
        
        # Test with a different goal
        print("\n🎨 Testing with creative writing goal...")
        creative_room = Room(
            name="Creative Writing Workshop",
            description="A room for learning creative writing techniques",
            goals="teach creative writing, storytelling, and narrative development",
            owner_id=test_user.id,
            created_at=datetime.utcnow()
        )
        
        try:
            creative_modes = generate_room_modes(creative_room)
            print(f"   Creative modes generated: {len(creative_modes)}")
            
            if creative_modes:
                for mode_key, mode_info in list(creative_modes.items())[:3]:
                    print(f"     - {mode_key}: {mode_info.label}")
                    print(f"       Prompt preview: {mode_info.prompt[:100]}...")
            else:
                print("   ❌ No creative modes generated")
                
        except Exception as e:
            print(f"   ❌ Error generating creative modes: {e}")

def test_existing_room_with_goals():
    """Test an existing room that should have contextual modes."""
    
    print("\n🔍 Testing existing room with goals...")
    
    app = create_app()
    with app.app_context():
        # Find a room with goals that doesn't have custom prompts saved
        room_with_goals = Room.query.filter(
            Room.goals.isnot(None),
            Room.goals != ""
        ).first()
        
        if not room_with_goals:
            print("❌ No rooms found with goals")
            return
        
        # Check if it has custom prompts
        custom_prompts = CustomPrompt.query.filter_by(room_id=room_with_goals.id).all()
        
        if custom_prompts:
            print(f"✅ Room '{room_with_goals.name}' has {len(custom_prompts)} saved custom prompts")
            print("   This room should use contextual modes when creating new chats")
        else:
            print(f"⚠️  Room '{room_with_goals.name}' has goals but no saved custom prompts")
            print("   This might indicate the mode generation failed during room creation")

if __name__ == "__main__":
    test_new_room_creation()
    test_existing_room_with_goals() 