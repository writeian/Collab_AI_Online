"""
Test Suite for OpenAI Utils Modules.

This module provides comprehensive testing for all the new modular components
to ensure they work correctly before migration from the old openai_utils.py.
"""

import unittest
from unittest.mock import Mock, patch
from typing import List, Dict, Any

from .config import AIConfig
from .exceptions import AIAPIError, ConfigurationError
from .api_clients import APIClientFactory, AnthropicClient, OpenAIClient, OllamaClient
from .mode_manager import ModeManager, ChatMode
from .assessment import LearningAssessment, AssessmentResult
from .conversation import ConversationManager, ConversationMessage
from .main_interface import OpenAIUtilsInterface


class TestConfiguration(unittest.TestCase):
    """Test configuration management."""
    
    def setUp(self):
        self.config = AIConfig()
    
    def test_config_initialization(self):
        """Test that configuration initializes correctly."""
        self.assertIsNotNone(self.config.ANTHROPIC_MODEL)
        self.assertIsNotNone(self.config.OPENAI_MODEL)
        self.assertIsNotNone(self.config.OLLAMA_MODEL)
        self.assertIsNotNone(self.config.DEFAULT_MAX_TOKENS)
        self.assertIsNotNone(self.config.DEFAULT_TEMPERATURE)
    
    def test_default_client_type(self):
        """Test default client type configuration."""
        self.assertIn(self.config.DEFAULT_CLIENT_TYPE, ['anthropic', 'openai', 'ollama'])


class TestExceptions(unittest.TestCase):
    """Test custom exceptions."""
    
    def test_ai_api_error(self):
        """Test AIAPIError creation and string representation."""
        error = AIAPIError("Test error", "anthropic", 500)
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.client_type, "anthropic")
        self.assertEqual(error.status_code, 500)
        self.assertIn("Test error", str(error))
    
    def test_configuration_error(self):
        """Test ConfigurationError creation."""
        error = ConfigurationError("Config error")
        self.assertEqual(error.message, "Config error")
        self.assertIn("Config error", str(error))


class TestAPIClients(unittest.TestCase):
    """Test API client functionality."""
    
    def setUp(self):
        self.factory = APIClientFactory()
    
    def test_factory_initialization(self):
        """Test that factory initializes correctly."""
        self.assertIsNotNone(self.factory)
    
    @patch('openai_utils.api_clients.os.getenv')
    def test_client_type_detection(self, mock_getenv):
        """Test client type detection logic."""
        # Test Anthropic detection
        mock_getenv.side_effect = lambda key: "test_key" if key == "ANTHROPIC_API_KEY" else None
        client_type = self.factory._get_client_type()
        self.assertEqual(client_type, "anthropic")
        
        # Test OpenAI detection
        mock_getenv.side_effect = lambda key: "test_key" if key == "OPENAI_API_KEY" else None
        client_type = self.factory._get_client_type()
        self.assertEqual(client_type, "openai")
        
        # Test Ollama detection
        mock_getenv.side_effect = lambda key: "test_key" if key == "OLLAMA_BASE_URL" else None
        client_type = self.factory._get_client_type()
        self.assertEqual(client_type, "ollama")


class TestModeManager(unittest.TestCase):
    """Test mode management functionality."""
    
    def setUp(self):
        self.mode_manager = ModeManager()
    
    def test_mode_manager_initialization(self):
        """Test that mode manager initializes correctly."""
        self.assertIsNotNone(self.mode_manager)
        self.assertIsNotNone(self.mode_manager.base_modes)
        self.assertGreater(len(self.mode_manager.base_modes), 0)
    
    def test_chat_mode_creation(self):
        """Test ChatMode dataclass creation."""
        mode = ChatMode(label="Test Mode", prompt="Test prompt")
        self.assertEqual(mode.label, "Test Mode")
        self.assertEqual(mode.prompt, "Test prompt")
    
    def test_get_mode_system_prompt(self):
        """Test getting system prompt for a mode."""
        # Test with existing mode
        prompt = self.mode_manager.get_mode_system_prompt("Explorer")
        self.assertIsNotNone(prompt)
        self.assertIsInstance(prompt, str)
        
        # Test with non-existing mode
        prompt = self.mode_manager.get_mode_system_prompt("NonExistentMode")
        self.assertIsNotNone(prompt)  # Should return default prompt


class TestAssessment(unittest.TestCase):
    """Test assessment functionality."""
    
    def setUp(self):
        self.assessment = LearningAssessment()
    
    def test_assessment_initialization(self):
        """Test that assessment initializes correctly."""
        self.assertIsNotNone(self.assessment)
    
    def test_assessment_result_creation(self):
        """Test AssessmentResult dataclass creation."""
        result = AssessmentResult(
            ready=True,
            confidence=0.85,
            feedback="Good progress",
            recommendations=["Continue learning"],
            next_steps=["Practice more"]
        )
        self.assertTrue(result.ready)
        self.assertEqual(result.confidence, 0.85)
        self.assertEqual(result.feedback, "Good progress")
        self.assertEqual(len(result.recommendations), 1)
        self.assertEqual(len(result.next_steps), 1)
    
    def test_process_conversation_context(self):
        """Test conversation context processing."""
        messages = [
            {"content": "Hello", "is_ai": False},
            {"content": "Hi there!", "is_ai": True},
            {"content": "How are you?", "is_ai": False}
        ]
        
        context = self.assessment.process_conversation_context(messages)
        self.assertEqual(context["message_count"], 3)
        self.assertEqual(context["user_messages"], 2)
        self.assertEqual(context["ai_messages"], 1)
        self.assertGreater(context["total_content_length"], 0)


class TestConversationManager(unittest.TestCase):
    """Test conversation management functionality."""
    
    def setUp(self):
        self.conversation = ConversationManager()
    
    def test_conversation_initialization(self):
        """Test that conversation manager initializes correctly."""
        self.assertIsNotNone(self.conversation)
    
    def test_conversation_message_creation(self):
        """Test ConversationMessage dataclass creation."""
        message = ConversationMessage(
            role="user",
            content="Hello",
            metadata={"timestamp": "2024-01-01"}
        )
        self.assertEqual(message.role, "user")
        self.assertEqual(message.content, "Hello")
        self.assertEqual(message.metadata["timestamp"], "2024-01-01")
    
    def test_format_conversation_for_ai(self):
        """Test conversation formatting for AI."""
        messages = [
            {"content": "Hello", "is_ai": False},
            {"content": "Hi there!", "is_ai": True}
        ]
        
        formatted_messages, parameters = self.conversation.format_conversation_for_ai(
            messages, system_prompt="Test system prompt"
        )
        
        self.assertIsInstance(formatted_messages, list)
        self.assertIsInstance(parameters, dict)
        self.assertIn("max_tokens", parameters)
        self.assertIn("temperature", parameters)
        
        # Check that system prompt was added
        if formatted_messages:
            self.assertEqual(formatted_messages[0]["role"], "system")


class TestMainInterface(unittest.TestCase):
    """Test main interface functionality."""
    
    def setUp(self):
        self.interface = OpenAIUtilsInterface()
    
    def test_interface_initialization(self):
        """Test that main interface initializes correctly."""
        self.assertIsNotNone(self.interface)
        self.assertIsNotNone(self.interface.config)
        self.assertIsNotNone(self.interface.api_factory)
        self.assertIsNotNone(self.interface.mode_manager)
        self.assertIsNotNone(self.interface.assessment)
        self.assertIsNotNone(self.interface.conversation)
    
    def test_get_status(self):
        """Test status reporting."""
        status = self.interface.get_status()
        self.assertIsInstance(status, dict)
        self.assertIn("config", status)
        self.assertIn("api_factory", status)
        self.assertIn("mode_manager", status)
        self.assertIn("assessment", status)
        self.assertIn("conversation", status)
        self.assertIn("default_client_type", status)
        self.assertIn("available_clients", status)
    
    def test_get_config(self):
        """Test configuration access."""
        config = self.interface.get_config()
        self.assertIsInstance(config, AIConfig)


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility functions."""
    
    def test_import_all_functions(self):
        """Test that all backward compatibility functions can be imported."""
        from openai_utils import (
            get_client_type,
            get_ai_response,
            call_anthropic_api,
            call_openai_api,
            call_ollama_api,
            get_modes_for_room,
            generate_room_modes,
            get_mode_system_prompt,
            assess_learning_progression,
            get_progression_recommendation,
            get_next_learning_step,
            generate_chat_introduction,
            format_conversation_for_ai,
            process_conversation_context,
            get_config,
            get_status
        )
        
        # Test that functions exist and are callable
        self.assertTrue(callable(get_client_type))
        self.assertTrue(callable(get_ai_response))
        self.assertTrue(callable(call_anthropic_api))
        self.assertTrue(callable(call_openai_api))
        self.assertTrue(callable(call_ollama_api))
        self.assertTrue(callable(get_modes_for_room))
        self.assertTrue(callable(generate_room_modes))
        self.assertTrue(callable(get_mode_system_prompt))
        self.assertTrue(callable(assess_learning_progression))
        self.assertTrue(callable(get_progression_recommendation))
        self.assertTrue(callable(get_next_learning_step))
        self.assertTrue(callable(generate_chat_introduction))
        self.assertTrue(callable(format_conversation_for_ai))
        self.assertTrue(callable(process_conversation_context))
        self.assertTrue(callable(get_config))
        self.assertTrue(callable(get_status))


class TestIntegration(unittest.TestCase):
    """Test integration between modules."""
    
    def setUp(self):
        self.interface = OpenAIUtilsInterface()
    
    def test_full_workflow(self):
        """Test a complete workflow through the interface."""
        # Test configuration access
        config = self.interface.get_config()
        self.assertIsInstance(config, AIConfig)
        
        # Test status reporting
        status = self.interface.get_status()
        self.assertIsInstance(status, dict)
        
        # Test conversation formatting
        messages = [{"content": "Test message", "is_ai": False}]
        formatted_messages, parameters = self.interface.format_conversation_for_ai(messages)
        self.assertIsInstance(formatted_messages, list)
        self.assertIsInstance(parameters, dict)


def run_tests():
    """Run all tests and return results."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestConfiguration,
        TestExceptions,
        TestAPIClients,
        TestModeManager,
        TestAssessment,
        TestConversationManager,
        TestMainInterface,
        TestBackwardCompatibility,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result


if __name__ == "__main__":
    # Run tests when module is executed directly
    result = run_tests()
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print(f"\n✅ ALL TESTS PASSED!")
    else:
        print(f"\n❌ SOME TESTS FAILED!") 