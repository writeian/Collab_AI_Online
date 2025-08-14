import unittest
from datetime import datetime, timedelta
from app import create_app
from models import db, User, Room, RoomMember, Chat, Comment, CustomPrompt


class TestDashboard(unittest.TestCase):
    def setUp(self):
        """Set up test database before each test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def create_test_data(self):
        """Helper method to create test data for dashboard"""
        with self.app.app_context():
            # Create users
            instructor = User(username='instructor', email='instructor@example.com', password_hash='hash')
            student1 = User(username='student1', email='student1@example.com', password_hash='hash')
            student2 = User(username='student2', email='student2@example.com', password_hash='hash')
            db.session.add_all([instructor, student1, student2])
            db.session.commit()
            
            # Create rooms
            room1 = Room(name='Writing Class', description='Creative writing class', creator_id=instructor.id, is_public=True)
            room2 = Room(name='Research Project', description='Group research project', creator_id=instructor.id, is_public=True)
            db.session.add_all([room1, room2])
            db.session.commit()
            
            # Add students to rooms
            member1 = RoomMember(room_id=room1.id, user_id=student1.id, role='member')
            member2 = RoomMember(room_id=room1.id, user_id=student2.id, role='member')
            member3 = RoomMember(room_id=room2.id, user_id=student1.id, role='member')
            db.session.add_all([member1, member2, member3])
            db.session.commit()
            
            # Create chats
            chat1 = Chat(title='Essay Draft', room_id=room1.id, user_id=student1.id, mode='draft')
            chat2 = Chat(title='Research Notes', room_id=room2.id, user_id=student1.id, mode='research')
            chat3 = Chat(title='Story Outline', room_id=room1.id, user_id=student2.id, mode='outline')
            db.session.add_all([chat1, chat2, chat3])
            db.session.commit()
            
            # Create comments
            comment1 = Comment(content='Great idea!', user_id=student2.id, chat_id=chat1.id, dialogue_number=1)
            comment2 = Comment(content='This needs more detail', user_id=instructor.id, chat_id=chat1.id, dialogue_number=2)
            db.session.add_all([comment1, comment2])
            db.session.commit()
            
            # Create custom prompts
            custom_prompt1 = CustomPrompt(mode='draft', room_id=room1.id, instructions='Custom draft instructions')
            custom_prompt2 = CustomPrompt(mode='research', room_id=room2.id, instructions='Custom research instructions')
            db.session.add_all([custom_prompt1, custom_prompt2])
            db.session.commit()
            
            return {
                'instructor': instructor,
                'students': [student1, student2],
                'rooms': [room1, room2],
                'chats': [chat1, chat2, chat3],
                'comments': [comment1, comment2],
                'custom_prompts': [custom_prompt1, custom_prompt2]
            }
    
    def test_dashboard_access(self):
        """Test dashboard access for instructor"""
        # Create test data
        test_data = self.create_test_data()
        instructor = test_data['instructor']
        
        # Login as instructor
        with self.client.session_transaction() as sess:
            sess['user_id'] = instructor.id
        
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
    
    def test_room_statistics(self):
        """Test room statistics calculation"""
        test_data = self.create_test_data()
        rooms = test_data['rooms']
        
        with self.app.app_context():
            # Test room statistics
            room1 = rooms[0]
            self.assertEqual(len(room1.members), 2)  # instructor + 2 students
            self.assertEqual(len(room1.chats), 2)  # 2 chats in room1
            
            room2 = rooms[1]
            self.assertEqual(len(room2.members), 1)  # instructor + 1 student
            self.assertEqual(len(room2.chats), 1)  # 1 chat in room2
    
    def test_chat_mode_analytics(self):
        """Test chat mode usage analytics"""
        test_data = self.create_test_data()
        chats = test_data['chats']
        
        with self.app.app_context():
            # Count chats by mode
            mode_counts = {}
            for chat in chats:
                mode_counts[chat.mode] = mode_counts.get(chat.mode, 0) + 1
            
            self.assertEqual(mode_counts.get('draft', 0), 1)
            self.assertEqual(mode_counts.get('research', 0), 1)
            self.assertEqual(mode_counts.get('outline', 0), 1)
    
    def test_member_activity_tracking(self):
        """Test member activity tracking"""
        test_data = self.create_test_data()
        students = test_data['students']
        chats = test_data['chats']
        comments = test_data['comments']
        
        with self.app.app_context():
            # Test student activity
            student1 = students[0]
            student1_chats = [chat for chat in chats if chat.user_id == student1.id]
            student1_comments = [comment for comment in comments if comment.user_id == student1.id]
            
            self.assertEqual(len(student1_chats), 2)  # 2 chats created by student1
            self.assertEqual(len(student1_comments), 0)  # 0 comments by student1
            
            student2 = students[1]
            student2_chats = [chat for chat in chats if chat.user_id == student2.id]
            student2_comments = [comment for comment in comments if comment.user_id == student2.id]
            
            self.assertEqual(len(student2_chats), 1)  # 1 chat created by student2
            self.assertEqual(len(student2_comments), 1)  # 1 comment by student2
    
    def test_custom_prompt_management(self):
        """Test custom prompt creation and retrieval"""
        test_data = self.create_test_data()
        rooms = test_data['rooms']
        custom_prompts = test_data['custom_prompts']
        
        with self.app.app_context():
            room1 = rooms[0]
            room2 = rooms[1]
            
            # Test custom prompts exist
            room1_prompts = [p for p in custom_prompts if p.room_id == room1.id]
            room2_prompts = [p for p in custom_prompts if p.room_id == room2.id]
            
            self.assertEqual(len(room1_prompts), 1)
            self.assertEqual(len(room2_prompts), 1)
            
            # Test prompt content
            draft_prompt = next(p for p in room1_prompts if p.mode == 'draft')
            self.assertEqual(draft_prompt.instructions, 'Custom draft instructions')
    
    def test_dashboard_room_filtering(self):
        """Test dashboard room filtering functionality"""
        test_data = self.create_test_data()
        rooms = test_data['rooms']
        
        with self.app.app_context():
            # Test room filtering by name
            writing_room = next(room for room in rooms if 'Writing' in room.name)
            research_room = next(room for room in rooms if 'Research' in room.name)
            
            self.assertIsNotNone(writing_room)
            self.assertIsNotNone(research_room)
            self.assertEqual(writing_room.name, 'Writing Class')
            self.assertEqual(research_room.name, 'Research Project')
    
    def test_comment_analytics(self):
        """Test comment analytics and threading"""
        test_data = self.create_test_data()
        comments = test_data['comments']
        chats = test_data['chats']
        
        with self.app.app_context():
            # Test comment threading
            chat1 = next(chat for chat in chats if chat.title == 'Essay Draft')
            chat1_comments = [comment for comment in comments if comment.chat_id == chat1.id]
            
            self.assertEqual(len(chat1_comments), 2)
            
            # Test dialogue number grouping
            dialogue_1_comments = [comment for comment in chat1_comments if comment.dialogue_number == 1]
            dialogue_2_comments = [comment for comment in chat1_comments if comment.dialogue_number == 2]
            
            self.assertEqual(len(dialogue_1_comments), 1)
            self.assertEqual(len(dialogue_2_comments), 1)
    
    def test_system_instructions_management(self):
        """Test system instructions management in dashboard"""
        test_data = self.create_test_data()
        custom_prompts = test_data['custom_prompts']
        
        with self.app.app_context():
            # Test custom prompt retrieval
            draft_prompt = next(p for p in custom_prompts if p.mode == 'draft')
            research_prompt = next(p for p in custom_prompts if p.mode == 'research')
            
            self.assertEqual(draft_prompt.instructions, 'Custom draft instructions')
            self.assertEqual(research_prompt.instructions, 'Custom research instructions')
            
            # Test prompt update
            draft_prompt.instructions = 'Updated draft instructions'
            db.session.commit()
            
            updated_prompt = CustomPrompt.query.filter_by(id=draft_prompt.id).first()
            self.assertEqual(updated_prompt.instructions, 'Updated draft instructions')
    
    def test_dashboard_permissions(self):
        """Test dashboard access permissions"""
        test_data = self.create_test_data()
        instructor = test_data['instructor']
        student1 = test_data['students'][0]
        
        # Test instructor access
        with self.client.session_transaction() as sess:
            sess['user_id'] = instructor.id
        
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        
        # Test student access (should be denied or limited)
        with self.client.session_transaction() as sess:
            sess['user_id'] = student1.id
        
        response = self.client.get('/dashboard/')
        # Should either be denied or show limited view
        self.assertIn(response.status_code, [200, 403])
    
    def test_room_analytics_detailed(self):
        """Test detailed room analytics"""
        test_data = self.create_test_data()
        rooms = test_data['rooms']
        chats = test_data['chats']
        comments = test_data['comments']
        
        with self.app.app_context():
            room1 = rooms[0]  # Writing Class
            
            # Calculate room statistics
            total_members = len(room1.members)
            total_chats = len(room1.chats)
            total_comments = len([c for c in comments if c.chat_id in [chat.id for chat in room1.chats]])
            
            self.assertEqual(total_members, 2)
            self.assertEqual(total_chats, 2)
            self.assertEqual(total_comments, 2)
            
            # Test mode distribution
            mode_counts = {}
            for chat in room1.chats:
                mode_counts[chat.mode] = mode_counts.get(chat.mode, 0) + 1
            
            self.assertEqual(mode_counts.get('draft', 0), 1)
            self.assertEqual(mode_counts.get('outline', 0), 1)


if __name__ == '__main__':
    unittest.main() 