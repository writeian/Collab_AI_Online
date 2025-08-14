import unittest
from app import create_app
from models import db


class TestBasicFunctionality(unittest.TestCase):
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
    
    def test_app_creation(self):
        """Test that the Flask app can be created"""
        self.assertIsNotNone(self.app)
        self.assertTrue(self.app.config['TESTING'])
    
    def test_database_creation(self):
        """Test that database tables can be created"""
        with self.app.app_context():
            # This should work without errors
            db.create_all()
            self.assertTrue(True)  # If we get here, it worked
    
    def test_home_route(self):
        """Test the home route redirects"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_about_route(self):
        """Test the about page loads"""
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'About AI Collab Teams', response.data)
    
    def test_room_index_route(self):
        """Test room listing page loads"""
        response = self.client.get('/room/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Rooms', response.data)
    
    def test_register_page_loads(self):
        """Test registration page loads"""
        response = self.client.get('/auth/register')
        self.assertEqual(response.status_code, 200)
    
    def test_login_page_loads(self):
        """Test login page loads"""
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main() 