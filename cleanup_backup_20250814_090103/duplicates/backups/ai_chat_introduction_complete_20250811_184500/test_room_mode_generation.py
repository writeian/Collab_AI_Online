#!/usr/bin/env python3
"""
Test script to debug room mode generation.
Checks if custom room goals are being used to generate contextual modes.
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Flask app correctly
from app import create_app
from models import db, Room, CustomPrompt
from openai_utils import generate_room_modes, get_modes_for_room, BASE_MODES

def test_room_mode_generation():
    """Test room mode generation with custom goals."""
    
    print("🔍 Testing room mode generation...")
    
    app = create_app()
    with app.app_context():
        # Find a room with custom goals
        room_with_goals = Room.query.filter(
            Room.goals.isnot(None),
            Room.goals != ""
        ).first()
        
        if not room_with_goals:
            print("❌ No rooms found with custom goals")
            return
        
        print(f"✅ Found room: {room_with_goals.name}")
        print(f"   Goals: {room_with_goals.goals}")
        print(f"   Created: {room_with_goals.created_at}")
        
        # Check if custom prompts exist for this room
        custom_prompts = CustomPrompt.query.filter_by(room_id=room_with_goals.id).all()
        print(f"   Custom prompts: {len(custom_prompts)}")
        
        for cp in custom_prompts:
            print(f"     - {cp.mode_key}: {cp.label}")
        
        # Test get_modes_for_room function
        print("\n📋 Testing get_modes_for_room...")
        modes = get_modes_for_room(room_with_goals)
        
        print(f"   Modes returned: {len(modes)}")
        for mode_key, mode_info in list(modes.items())[:3]:  # Show first 3
            print(f"     - {mode_key}: {mode_info.get('label', 'No label')}")
        
        # Test generate_room_modes function directly
        print("\n🤖 Testing generate_room_modes directly...")
        try:
            contextual_modes = generate_room_modes(room_with_goals)
            print(f"   Contextual modes generated: {len(contextual_modes)}")
            
            if contextual_modes:
                for mode_key, mode_info in list(contextual_modes.items())[:3]:
                    print(f"     - {mode_key}: {mode_info.label}")
                    print(f"       Prompt preview: {mode_info.prompt[:100]}...")
            else:
                print("   ❌ No contextual modes generated")
                
        except Exception as e:
            print(f"   ❌ Error generating modes: {e}")
        
        # Check if modes are different from BASE_MODES
        print("\n🔍 Comparing with BASE_MODES...")
        if contextual_modes:
            base_mode_keys = set(BASE_MODES.keys())
            contextual_mode_keys = set(contextual_modes.keys())
            
            if contextual_mode_keys == base_mode_keys:
                print("   ⚠️  Contextual modes are identical to BASE_MODES")
            else:
                print(f"   ✅ Contextual modes differ from BASE_MODES")
                print(f"   Base modes: {len(base_mode_keys)}")
                print(f"   Contextual modes: {len(contextual_mode_keys)}")
        
        # Test with a specific financial management goal
        print("\n💰 Testing with financial management goal...")
        test_room = Room(
            name="Test Financial Room",
            goals="teach financial management",
            owner_id=1
        )
        
        try:
            test_modes = generate_room_modes(test_room)
            print(f"   Test modes generated: {len(test_modes)}")
            
            if test_modes:
                for mode_key, mode_info in list(test_modes.items())[:3]:
                    print(f"     - {mode_key}: {mode_info.label}")
                    print(f"       Prompt preview: {mode_info.prompt[:100]}...")
            else:
                print("   ❌ No test modes generated")
                
        except Exception as e:
            print(f"   ❌ Error generating test modes: {e}")

def test_api_connection():
    """Test if the AI API is working."""
    print("\n🔌 Testing API connection...")
    
    from openai_utils import get_client_type
    
    client_type = get_client_type()
    print(f"   Client type: {client_type}")
    
    if client_type:
        print("   ✅ API client available")
    else:
        print("   ❌ No API client available")
        print("   Check your environment variables:")
        print("   - ANTHROPIC_API_KEY")
        print("   - OPENAI_API_KEY") 
        print("   - USE_OLLAMA")

if __name__ == "__main__":
    test_api_connection()
    test_room_mode_generation() 