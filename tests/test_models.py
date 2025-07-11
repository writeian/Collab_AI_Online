import unittest
from datetime import datetime
from app import create_app
from models import db, User, Room, RoomMember, Chat, Comment, CustomPrompt


class TestModels(unittest.TestCase):
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
    
    def test_user_creation(self):
        """Test user creation and basic properties"""
        with self.app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                display_name='Test User'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            self.assertEqual(user.username, 'testuser')
            self.assertEqual(user.email, 'test@example.com')
            self.assertEqual(user.display_name, 'Test User')
            self.assertTrue(user.id is not None)
    
    def test_room_creation(self):
        """Test room creation and properties"""
        with self.app.app_context():
            # Create user first
            user = User(username='creator', email='creator@example.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            room = Room(
                name='Test Room',
                description='A test room',
                owner_id=user.id
            )
            db.session.add(room)
            db.session.commit()
            
            self.assertEqual(room.name, 'Test Room')
            self.assertEqual(room.description, 'A test room')
            self.assertEqual(room.owner_id, user.id)
            self.assertTrue(room.id is not None)
    
    def test_room_member_relationship(self):
        """Test room member relationships"""
        with self.app.app_context():
            # Create users
            creator = User(username='creator', email='creator@example.com', password_hash='hash')
            member = User(username='member', email='member@example.com', password_hash='hash')
            db.session.add_all([creator, member])
            db.session.commit()
            
            # Create room
            room = Room(
                name='Test Room',
                description='A test room',
                creator_id=creator.id,
                is_public=True
            )
            db.session.add(room)
            db.session.commit()
            
            # Add member to room
            room_member = RoomMember(
                room_id=room.id,
                user_id=member.id,
                role='member'
            )
            db.session.add(room_member)
            db.session.commit()
            
            # Test relationships
            self.assertEqual(len(room.members), 1)
            self.assertEqual(room.members[0].user.username, 'member')
            self.assertEqual(member.rooms[0].room.name, 'Test Room')
    
    def test_chat_creation(self):
        """Test chat creation and properties"""
        with self.app.app_context():
            # Create user and room
            user = User(username='user', email='user@example.com', password_hash='hash')
            room = Room(name='Test Room', description='Test', creator_id=user.id)
            db.session.add_all([user, room])
            db.session.commit()
            
            chat = Chat(
                title='Test Chat',
                room_id=room.id,
                user_id=user.id,
                mode='explore'
            )
            db.session.add(chat)
            db.session.commit()
            
            self.assertEqual(chat.title, 'Test Chat')
            self.assertEqual(chat.room_id, room.id)
            self.assertEqual(chat.user_id, user.id)
            self.assertEqual(chat.mode, 'explore')
            self.assertTrue(chat.id is not None)
    
    def test_comment_creation(self):
        """Test comment creation and properties"""
        with self.app.app_context():
            # Create user, room, and chat
            user = User(username='user', email='user@example.com', password_hash='hash')
            room = Room(name='Test Room', description='Test', creator_id=user.id)
            chat = Chat(title='Test Chat', room_id=room.id, user_id=user.id, mode='explore')
            db.session.add_all([user, room, chat])
            db.session.commit()
            
            comment = Comment(
                content='Test comment',
                user_id=user.id,
                chat_id=chat.id,
                dialogue_number=1
            )
            db.session.add(comment)
            db.session.commit()
            
            self.assertEqual(comment.content, 'Test comment')
            self.assertEqual(comment.user_id, user.id)
            self.assertEqual(comment.chat_id, chat.id)
            self.assertEqual(comment.dialogue_number, 1)
            self.assertTrue(comment.id is not None)
    
    def test_custom_prompt_creation(self):
        """Test custom prompt creation and properties"""
        with self.app.app_context():
            # Create user and room
            user = User(username='user', email='user@example.com', password_hash='hash')
            room = Room(name='Test Room', description='Test', creator_id=user.id)
            db.session.add_all([user, room])
            db.session.commit()
            
            custom_prompt = CustomPrompt(
                mode='explore',
                room_id=room.id,
                instructions='Custom instructions for explore mode'
            )
            db.session.add(custom_prompt)
            db.session.commit()
            
            self.assertEqual(custom_prompt.mode, 'explore')
            self.assertEqual(custom_prompt.room_id, room.id)
            self.assertEqual(custom_prompt.instructions, 'Custom instructions for explore mode')
            self.assertTrue(custom_prompt.id is not None)
    
    def test_user_password_hashing(self):
        """Test password hashing functionality"""
        with self.app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()
            
            self.assertTrue(user.check_password('testpassword'))
            self.assertFalse(user.check_password('wrongpassword'))
    
    def test_room_creator_relationship(self):
        """Test room creator relationship"""
        with self.app.app_context():
            creator = User(username='creator', email='creator@example.com', password_hash='hash')
            db.session.add(creator)
            db.session.commit()
            
            room = Room(
                name='Test Room',
                description='A test room',
                creator_id=creator.id,
                is_public=True
            )
            db.session.add(room)
            db.session.commit()
            
            self.assertEqual(room.creator.username, 'creator')
            self.assertEqual(creator.created_rooms[0].name, 'Test Room')
    
    def test_chat_room_relationship(self):
        """Test chat and room relationship"""
        with self.app.app_context():
            user = User(username='user', email='user@example.com', password_hash='hash')
            room = Room(name='Test Room', description='Test', creator_id=user.id)
            db.session.add_all([user, room])
            db.session.commit()
            
            chat1 = Chat(title='Chat 1', room_id=room.id, user_id=user.id, mode='explore')
            chat2 = Chat(title='Chat 2', room_id=room.id, user_id=user.id, mode='draft')
            db.session.add_all([chat1, chat2])
            db.session.commit()
            
            self.assertEqual(len(room.chats), 2)
            self.assertEqual(room.chats[0].title, 'Chat 1')
            self.assertEqual(room.chats[1].title, 'Chat 2')


if __name__ == '__main__':
    unittest.main() 