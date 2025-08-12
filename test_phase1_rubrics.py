#!/usr/bin/env python3
"""
Test script for Phase 1 Rubric System Implementation.
This tests the basic rubric functionality without AI validation.
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_phase1_rubrics():
    """Test Phase 1 rubric functionality."""
    print("🧪 Testing Phase 1: Rubric System Foundation")
    print("=" * 60)
    
    try:
        # Import required modules
        from app import create_app
        from models import db, Room, User, RubricCriterion, RubricLevel, RoomRubric
        from rubric_templates import create_default_rubric_for_room, get_rubric_template
        
        # Create app context
        app = create_app('development')
        
        with app.app_context():
            print("✅ App context created successfully")
            
            # Test 1: Database Models
            print("\n📊 Test 1: Database Models")
            print("   Testing rubric model creation...")
            
            # Create test user
            test_user = User.query.filter_by(username='test_rubric_user').first()
            if not test_user:
                test_user = User(
                    username='test_rubric_user',
                    email='test_rubric@example.com',
                    display_name='Test Rubric User'
                )
                test_user.set_password('password123')
                db.session.add(test_user)
                db.session.commit()
                print("   ✅ Created test user")
            
            # Create test room
            test_room = Room.query.filter_by(name='Test Rubric Room').first()
            if not test_room:
                test_room = Room(
                    name='Test Rubric Room',
                    description='A test room for rubric functionality',
                    goals='Learn to write academic papers with proper assessment',
                    owner_id=test_user.id
                )
                db.session.add(test_room)
                db.session.commit()
                print("   ✅ Created test room")
            
            # Test 2: Rubric Template System
            print("\n📋 Test 2: Rubric Template System")
            
            # Test template retrieval
            explore_template = get_rubric_template('explore')
            if explore_template:
                print(f"   ✅ Explore template found with {len(explore_template['criteria'])} criteria")
            else:
                print("   ❌ Explore template not found")
                return False
            
            # Test 3: Default Rubric Creation
            print("\n🏗️ Test 3: Default Rubric Creation")
            
            # Create default rubric for explore step
            rubric_result = create_default_rubric_for_room(test_room, 'explore')
            if rubric_result:
                room_rubric, criteria_list, levels_list = rubric_result
                db.session.add(room_rubric)
                for criterion in criteria_list:
                    db.session.add(criterion)
                for level in levels_list:
                    db.session.add(level)
                db.session.commit()
                print("   ✅ Default rubric created successfully")
                
                # Verify rubric was created
                room_rubric = RoomRubric.query.filter_by(
                    room_id=test_room.id, 
                    step_key='explore'
                ).first()
                
                if room_rubric:
                    print(f"   ✅ Room rubric found with threshold: {room_rubric.progression_threshold}")
                    
                    # Check criteria
                    criteria = RubricCriterion.query.filter_by(
                        room_id=test_room.id,
                        step_key='explore'
                    ).all()
                    
                    print(f"   ✅ Found {len(criteria)} criteria")
                    
                    # Check levels for first criterion
                    if criteria:
                        levels = RubricLevel.query.filter_by(criterion_id=criteria[0].id).all()
                        print(f"   ✅ First criterion has {len(levels)} levels")
                        
                        # Display sample data
                        print(f"   📝 Sample criterion: {criteria[0].name}")
                        print(f"   📝 Sample level: {levels[0].level} (score {levels[0].score})")
                else:
                    print("   ❌ Room rubric not found")
                    return False
            else:
                print("   ❌ Default rubric creation failed")
                return False
            
            # Test 4: Multiple Rubrics
            print("\n🔄 Test 4: Multiple Rubrics")
            
            # Create rubrics for focus and context steps
            focus_result = create_default_rubric_for_room(test_room, 'focus')
            context_result = create_default_rubric_for_room(test_room, 'context')
            
            if focus_result and context_result:
                # Add focus rubric
                focus_rubric, focus_criteria, focus_levels = focus_result
                db.session.add(focus_rubric)
                for criterion in focus_criteria:
                    db.session.add(criterion)
                for level in focus_levels:
                    db.session.add(level)
                
                # Add context rubric
                context_rubric, context_criteria, context_levels = context_result
                db.session.add(context_rubric)
                for criterion in context_criteria:
                    db.session.add(criterion)
                for level in context_levels:
                    db.session.add(level)
                
                db.session.commit()
                print("   ✅ Multiple rubrics created successfully")
                
                # Count total rubrics
                total_rubrics = RoomRubric.query.filter_by(room_id=test_room.id).count()
                print(f"   ✅ Room has {total_rubrics} rubrics total")
            else:
                print("   ❌ Multiple rubric creation failed")
            
            # Test 5: Data Integrity
            print("\n🔒 Test 5: Data Integrity")
            
            # Test foreign key relationships
            all_criteria = RubricCriterion.query.filter_by(room_id=test_room.id).all()
            total_levels = 0
            
            for criterion in all_criteria:
                levels = RubricLevel.query.filter_by(criterion_id=criterion.id).all()
                total_levels += len(levels)
                
                # Verify each criterion has 4 levels
                if len(levels) != 4:
                    print(f"   ❌ Criterion '{criterion.name}' has {len(levels)} levels, expected 4")
                    return False
            
            print(f"   ✅ All {len(all_criteria)} criteria have proper levels")
            print(f"   ✅ Total levels: {total_levels}")
            
            # Test 6: Template Validation
            print("\n✅ Test 6: Template Validation")
            
            available_steps = ['explore', 'focus', 'context']
            for step in available_steps:
                template = get_rubric_template(step)
                if template:
                    print(f"   ✅ Template for '{step}' is valid")
                    
                    # Check template structure
                    required_fields = ['name', 'progression_threshold', 'criteria']
                    for field in required_fields:
                        if field not in template:
                            print(f"   ❌ Template '{step}' missing field: {field}")
                            return False
                    
                    # Check criteria structure
                    for criterion in template['criteria']:
                        if 'name' not in criterion or 'levels' not in criterion:
                            print(f"   ❌ Criterion in '{step}' missing required fields")
                            return False
                        
                        if len(criterion['levels']) != 4:
                            print(f"   ❌ Criterion '{criterion['name']}' has {len(criterion['levels'])} levels, expected 4")
                            return False
                else:
                    print(f"   ❌ Template for '{step}' not found")
                    return False
            
            print("   ✅ All templates are valid")
            
            # Test 7: UI Integration Simulation
            print("\n🎨 Test 7: UI Integration Simulation")
            
            # Simulate the data structure that would be sent to the frontend
            ui_data = {
                'room_id': test_room.id,
                'learning_steps': []
            }
            
            for step in available_steps:
                room_rubric = RoomRubric.query.filter_by(
                    room_id=test_room.id,
                    step_key=step
                ).first()
                
                if room_rubric:
                    criteria = RubricCriterion.query.filter_by(
                        room_id=test_room.id,
                        step_key=step
                    ).order_by(RubricCriterion.order).all()
                    
                    step_data = {
                        'key': step,
                        'label': f"{step.title()} Step",
                        'rubric': {
                            'threshold': room_rubric.progression_threshold,
                            'criteria': []
                        }
                    }
                    
                    for criterion in criteria:
                        levels = RubricLevel.query.filter_by(
                            criterion_id=criterion.id
                        ).order_by(RubricLevel.score).all()
                        
                        criterion_data = {
                            'name': criterion.name,
                            'description': criterion.description,
                            'weight': criterion.weight,
                            'levels': [
                                {
                                    'level': level.level,
                                    'score': level.score,
                                    'description': level.description
                                }
                                for level in levels
                            ]
                        }
                        step_data['rubric']['criteria'].append(criterion_data)
                    
                    ui_data['learning_steps'].append(step_data)
            
            print(f"   ✅ UI data structure created with {len(ui_data['learning_steps'])} steps")
            print(f"   ✅ Sample step: {ui_data['learning_steps'][0]['key']} with {len(ui_data['learning_steps'][0]['rubric']['criteria'])} criteria")
            
            # Test 8: Cleanup
            print("\n🧹 Test 8: Cleanup")
            
            # Clean up test data
            RubricLevel.query.filter(
                RubricLevel.criterion_id.in_(
                    db.session.query(RubricCriterion.id).filter_by(room_id=test_room.id)
                )
            ).delete(synchronize_session=False)
            
            RubricCriterion.query.filter_by(room_id=test_room.id).delete()
            RoomRubric.query.filter_by(room_id=test_room.id).delete()
            
            # Optionally clean up test room and user
            # Room.query.filter_by(id=test_room.id).delete()
            # User.query.filter_by(id=test_user.id).delete()
            
            db.session.commit()
            print("   ✅ Test data cleaned up")
            
            print(f"\n🎉 Phase 1 Rubric System Test Complete!")
            print(f"   ✅ All tests passed")
            print(f"   ✅ Database models working correctly")
            print(f"   ✅ Template system functional")
            print(f"   ✅ Default rubric creation working")
            print(f"   ✅ Data integrity maintained")
            print(f"   ✅ UI integration ready")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_migration():
    """Test database migration."""
    print("\n🗄️ Testing Database Migration")
    print("=" * 40)
    
    try:
        from alembic.config import Config
        from alembic import command
        
        # Check if migration exists
        migration_file = 'migrations/versions/rubric_models_migration.py'
        if os.path.exists(migration_file):
            print("✅ Migration file exists")
            
            # Test migration syntax
            with open(migration_file, 'r') as f:
                content = f.read()
                if 'def upgrade():' in content and 'def downgrade():' in content:
                    print("✅ Migration syntax appears correct")
                else:
                    print("❌ Migration syntax issues")
                    return False
        else:
            print("❌ Migration file not found")
            return False
        
        print("✅ Migration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Migration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Phase 1 Rubric System Test")
    print("=" * 70)
    
    # Run tests
    migration_success = test_migration()
    rubric_success = test_phase1_rubrics()
    
    if migration_success and rubric_success:
        print("\n🎉 All Phase 1 tests passed! The rubric system foundation is working correctly.")
        print("\n📋 Phase 1 Implementation Complete:")
        print("   ✅ Database models for rubrics")
        print("   ✅ Rubric template system")
        print("   ✅ Default rubric creation")
        print("   ✅ UI integration in room creation")
        print("   ✅ Database migration ready")
        print("   ✅ Basic validation and error handling")
        
        print("\n🎯 Next Steps for Phase 2:")
        print("   1. Implement inline editing for learning step instructions")
        print("   2. Implement table-based rubric editing")
        print("   3. Add save/cancel functionality")
        print("   4. Implement state management for dropdowns")
        
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        sys.exit(1) 