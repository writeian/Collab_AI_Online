import unittest
from unittest.mock import patch, MagicMock
from app import create_app
from models import db, User, Room, Chat, CustomPrompt
from openai_utils import get_ai_response, get_system_instructions, get_writing_modes


class TestAIIntegration(unittest.TestCase):
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
    
    def test_writing_modes_available(self):
        """Test that all writing modes are available"""
        modes = get_writing_modes()
        
        expected_modes = [
            'explore', 'focus', 'outline', 'draft', 'revise',
            'polish', 'proposal', 'research', 'context', 'feedback'
        ]
        
        for mode in expected_modes:
            self.assertIn(mode, modes)
            self.assertIsInstance(modes[mode], dict)
            self.assertIn('name', modes[mode])
            self.assertIn('description', modes[mode])
    
    def test_system_instructions_retrieval(self):
        """Test system instructions retrieval for different modes"""
        # Test default instructions
        instructions = get_system_instructions('explore')
        self.assertIsInstance(instructions, str)
        self.assertIn('explore', instructions.lower())
        
        instructions = get_system_instructions('draft')
        self.assertIsInstance(instructions, str)
        self.assertIn('draft', instructions.lower())
        
        # Test invalid mode returns default
        instructions = get_system_instructions('invalid_mode')
        self.assertIsInstance(instructions, str)
    
    def test_custom_prompt_override(self):
        """Test that custom prompts override default instructions"""
        with self.app.app_context():
            # Create user and room
            user = User(username='testuser', email='test@example.com', password_hash='hash')
            room = Room(name='Test Room', description='Test', creator_id=user.id)
            db.session.add_all([user, room])
            db.session.commit()
            
            # Create custom prompt
            custom_prompt = CustomPrompt(
                mode='explore',
                room_id=room.id,
                instructions='Custom explore instructions for this room'
            )
            db.session.add(custom_prompt)
            db.session.commit()
            
            # Test custom instructions are retrieved
            instructions = get_system_instructions('explore', room_id=room.id)
            self.assertEqual(instructions, 'Custom explore instructions for this room')
    
    @patch('openai_utils.openai.ChatCompletion.create')
    def test_ai_response_generation(self, mock_openai):
        """Test AI response generation with mocked OpenAI"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is a test AI response"
        mock_openai.return_value = mock_response
        
        # Test AI response generation
        response = get_ai_response(
            messages=[{"role": "user", "content": "Hello AI"}],
            mode='explore'
        )
        
        self.assertEqual(response, "This is a test AI response")
        mock_openai.assert_called_once()
    
    @patch('openai_utils.anthropic.Anthropic')
    def test_anthropic_fallback(self, mock_anthropic):
        """Test Anthropic fallback when OpenAI fails"""
        # Mock OpenAI to fail
        with patch('openai_utils.openai.ChatCompletion.create') as mock_openai:
            mock_openai.side_effect = Exception("OpenAI error")
            
            # Mock Anthropic response
            mock_anthropic_instance = MagicMock()
            mock_anthropic_instance.messages.create.return_value.content = [
                MagicMock(text="Anthropic fallback response")
            ]
            mock_anthropic.return_value = mock_anthropic_instance
            
            # Test fallback to Anthropic
            response = get_ai_response(
                messages=[{"role": "user", "content": "Hello AI"}],
                mode='explore'
            )
            
            self.assertEqual(response, "Anthropic fallback response")
            mock_anthropic_instance.messages.create.assert_called_once()
    
    def test_chat_mode_validation(self):
        """Test chat mode validation in database"""
        with self.app.app_context():
            # Create user and room
            user = User(username='testuser', email='test@example.com', password_hash='hash')
            room = Room(name='Test Room', description='Test', creator_id=user.id)
            db.session.add_all([user, room])
            db.session.commit()
            
            # Test valid mode
            chat = Chat(
                title='Test Chat',
                room_id=room.id,
                user_id=user.id,
                mode='explore'
            )
            db.session.add(chat)
            db.session.commit()
            
            self.assertEqual(chat.mode, 'explore')
            
            # Test invalid mode (should still work with default)
            chat2 = Chat(
                title='Test Chat 2',
                room_id=room.id,
                user_id=user.id,
                mode='invalid_mode'
            )
            db.session.add(chat2)
            db.session.commit()
            
            # Should still be saved
            self.assertEqual(chat2.mode, 'invalid_mode')
    
    def test_custom_prompt_creation_and_retrieval(self):
        """Test custom prompt creation and retrieval"""
        with self.app.app_context():
            # Create user and room
            user = User(username='testuser', email='test@example.com', password_hash='hash')
            room = Room(name='Test Room', description='Test', creator_id=user.id)
            db.session.add_all([user, room])
            db.session.commit()
            
            # Create custom prompts for different modes
            custom_prompts = [
                CustomPrompt(mode='explore', room_id=room.id, instructions='Custom explore'),
                CustomPrompt(mode='draft', room_id=room.id, instructions='Custom draft'),
                CustomPrompt(mode='revise', room_id=room.id, instructions='Custom revise')
            ]
            
            for prompt in custom_prompts:
                db.session.add(prompt)
            db.session.commit()
            
            # Test retrieval
            explore_instructions = get_system_instructions('explore', room_id=room.id)
            draft_instructions = get_system_instructions('draft', room_id=room.id)
            revise_instructions = get_system_instructions('revise', room_id=room.id)
            
            self.assertEqual(explore_instructions, 'Custom explore')
            self.assertEqual(draft_instructions, 'Custom draft')
            self.assertEqual(revise_instructions, 'Custom revise')
    
    def test_ai_response_with_context(self):
        """Test AI response with chat context"""
        with self.app.app_context():
            # Create user, room, and chat
            user = User(username='testuser', email='test@example.com', password_hash='hash')
            room = Room(name='Test Room', description='Test', creator_id=user.id)
            chat = Chat(title='Test Chat', room_id=room.id, user_id=user.id, mode='explore')
            db.session.add_all([user, room, chat])
            db.session.commit()
            
            # Test that system instructions include room context
            instructions = get_system_instructions('explore', room_id=room.id)
            self.assertIsInstance(instructions, str)
            self.assertGreater(len(instructions), 0)
    
    def test_writing_mode_descriptions(self):
        """Test that writing modes have proper descriptions"""
        modes = get_writing_modes()
        
        for mode_name, mode_data in modes.items():
            self.assertIn('name', mode_data)
            self.assertIn('description', mode_data)
            self.assertIsInstance(mode_data['name'], str)
            self.assertIsInstance(mode_data['description'], str)
            self.assertGreater(len(mode_data['name']), 0)
            self.assertGreater(len(mode_data['description']), 0)
    
    def test_default_system_instructions(self):
        """Test default system instructions for all modes"""
        modes = get_writing_modes()
        
        for mode in modes.keys():
            instructions = get_system_instructions(mode)
            self.assertIsInstance(instructions, str)
            self.assertGreater(len(instructions), 0)
            # Should contain mode-specific content
            self.assertIn(mode.lower(), instructions.lower())


if __name__ == '__main__':
    unittest.main() 