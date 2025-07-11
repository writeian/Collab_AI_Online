import unittest
import json
from app import create_app
from models import db, User, Room, RoomMember, Chat, Comment


class TestRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test database and client before each test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def create_test_user(self, username='testuser', email='test@example.com', password='password'):
        """Helper method to create a test user"""
        with self.app.app_context():
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return user
    
    def login_user(self, username='testuser', password='password'):
        """Helper method to login a user"""
        return self.client.post('/auth/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)
    
    def test_home_route(self):
        """Test the home route redirects to rooms"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_about_route(self):
        """Test the about page loads correctly"""
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'About AI Collab Teams', response.data)
    
    def test_register_route(self):
        """Test user registration"""
        response = self.client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Check user was created
        with self.app.app_context():
            user = User.query.filter_by(username='newuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'newuser@example.com')
    
    def test_login_route(self):
        """Test user login"""
        # Create a test user
        self.create_test_user()
        
        # Test login
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
    
    def test_logout_route(self):
        """Test user logout"""
        # Create and login user
        self.create_test_user()
        self.login_user()
        
        # Test logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_room_index_route(self):
        """Test room listing page"""
        response = self.client.get('/room/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Rooms', response.data)
    
    def test_room_creation_route(self):
        """Test room creation"""
        # Create and login user
        self.create_test_user()
        self.login_user()
        
        response = self.client.post('/room/create', data={
            'name': 'Test Room',
            'description': 'A test room',
            'is_public': True
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Check room was created
        with self.app.app_context():
            room = Room.query.filter_by(name='Test Room').first()
            self.assertIsNotNone(room)
            self.assertEqual(room.description, 'A test room')
            self.assertTrue(room.is_public)
    
    def test_room_view_route(self):
        """Test room view page"""
        # Create user and room
        user = self.create_test_user()
        with self.app.app_context():
            room = Room(
                name='Test Room',
                description='A test room',
                creator_id=user.id,
                is_public=True
            )
            db.session.add(room)
            db.session.commit()
            
            response = self.client.get(f'/room/{room.id}')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test Room', response.data)
    
    def test_chat_creation_route(self):
        """Test chat creation"""
        # Create user and room
        user = self.create_test_user()
        self.login_user()
        
        with self.app.app_context():
            room = Room(
                name='Test Room',
                description='A test room',
                creator_id=user.id,
                is_public=True
            )
            db.session.add(room)
            db.session.commit()
            
            response = self.client.post(f'/chat/create', data={
                'title': 'Test Chat',
                'room_id': room.id,
                'mode': 'explore'
            }, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            
            # Check chat was created
            chat = Chat.query.filter_by(title='Test Chat').first()
            self.assertIsNotNone(chat)
            self.assertEqual(chat.mode, 'explore')
    
    def test_chat_view_route(self):
        """Test chat view page"""
        # Create user, room, and chat
        user = self.create_test_user()
        with self.app.app_context():
            room = Room(
                name='Test Room',
                description='A test room',
                creator_id=user.id,
                is_public=True
            )
            chat = Chat(
                title='Test Chat',
                room_id=room.id,
                user_id=user.id,
                mode='explore'
            )
            db.session.add_all([room, chat])
            db.session.commit()
            
            response = self.client.get(f'/chat/{chat.id}')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test Chat', response.data)
    
    def test_dashboard_route(self):
        """Test dashboard access"""
        # Create and login user
        self.create_test_user()
        self.login_user()
        
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
    
    def test_comment_creation_route(self):
        """Test comment creation"""
        # Create user, room, and chat
        user = self.create_test_user()
        self.login_user()
        
        with self.app.app_context():
            room = Room(
                name='Test Room',
                description='A test room',
                creator_id=user.id,
                is_public=True
            )
            chat = Chat(
                title='Test Chat',
                room_id=room.id,
                user_id=user.id,
                mode='explore'
            )
            db.session.add_all([room, chat])
            db.session.commit()
            
            response = self.client.post(f'/chat/{chat.id}/comment', data={
                'content': 'Test comment',
                'dialogue_number': 1
            }, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            
            # Check comment was created
            comment = Comment.query.filter_by(content='Test comment').first()
            self.assertIsNotNone(comment)
            self.assertEqual(comment.dialogue_number, 1)
    
    def test_unauthorized_access(self):
        """Test unauthorized access to protected routes"""
        # Test dashboard without login
        response = self.client.get('/dashboard/', follow_redirects=True)
        self.assertIn(b'Login', response.data)
        
        # Test room creation without login
        response = self.client.get('/room/create', follow_redirects=True)
        self.assertIn(b'Login', response.data)
    
    def test_room_member_management(self):
        """Test adding and removing room members"""
        # Create users
        creator = self.create_test_user('creator', 'creator@example.com')
        member = self.create_test_user('member', 'member@example.com')
        
        with self.app.app_context():
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
            
            # Test member is in room
            self.assertEqual(len(room.members), 1)
            self.assertEqual(room.members[0].user.username, 'member')
    
    def test_chat_mode_validation(self):
        """Test chat mode validation"""
        # Create user and room
        user = self.create_test_user()
        self.login_user()
        
        with self.app.app_context():
            room = Room(
                name='Test Room',
                description='A test room',
                creator_id=user.id,
                is_public=True
            )
            db.session.add(room)
            db.session.commit()
            
            # Test valid mode
            response = self.client.post(f'/chat/create', data={
                'title': 'Valid Chat',
                'room_id': room.id,
                'mode': 'explore'
            }, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            
            # Test invalid mode
            response = self.client.post(f'/chat/create', data={
                'title': 'Invalid Chat',
                'room_id': room.id,
                'mode': 'invalid_mode'
            }, follow_redirects=True)
            
            # Should still work but with default mode
            self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main() 