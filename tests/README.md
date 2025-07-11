# AI_Collab_Teams Test Suite

This directory contains comprehensive tests for the AI_Collab_Teams application.

## 📁 Test Files

### `test_models.py`
Tests for database models and relationships:
- User creation and password hashing
- Room creation and management
- Room member relationships
- Chat creation and properties
- Comment system functionality
- Custom prompt management
- Database relationships and constraints

### `test_routes.py`
Tests for Flask routes and web functionality:
- Authentication (login, register, logout)
- Room management (create, view, join)
- Chat functionality (create, view, comment)
- Dashboard access and permissions
- Route protection and unauthorized access
- Form validation and data processing

### `test_ai_integration.py`
Tests for AI integration features:
- Writing mode system validation
- System instructions retrieval
- Custom prompt override functionality
- AI response generation (mocked)
- Anthropic fallback mechanism
- Chat mode validation
- AI context handling

### `test_dashboard.py`
Tests for instructor dashboard functionality:
- Dashboard access and permissions
- Room statistics calculation
- Chat mode analytics
- Member activity tracking
- Custom prompt management
- Comment analytics and threading
- System instructions management
- Room filtering and search

## 🚀 Running Tests

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test File
```bash
python run_tests.py test_models
python run_tests.py test_routes
python run_tests.py test_ai_integration
python run_tests.py test_dashboard
```

### Run Individual Test Classes
```bash
python -m unittest tests.test_models.TestModels
python -m unittest tests.test_routes.TestRoutes
python -m unittest tests.test_ai_integration.TestAIIntegration
python -m unittest tests.test_dashboard.TestDashboard
```

### Run Specific Test Methods
```bash
python -m unittest tests.test_models.TestModels.test_user_creation
python -m unittest tests.test_routes.TestRoutes.test_login_route
```

## 🧪 Test Configuration

### Database
- Tests use in-memory SQLite database (`sqlite:///:memory:`)
- Each test gets a fresh database instance
- No data persists between tests

### Mocking
- AI API calls are mocked to avoid external dependencies
- No actual API keys required for testing
- Tests can run offline

### Test Data
- Helper methods create realistic test data
- Tests cover various scenarios and edge cases
- Data is cleaned up after each test

## 📊 Test Coverage

### Models (test_models.py)
- ✅ User model and authentication
- ✅ Room model and relationships
- ✅ RoomMember model and permissions
- ✅ Chat model and mode validation
- ✅ Comment model and threading
- ✅ CustomPrompt model and override

### Routes (test_routes.py)
- ✅ Authentication routes
- ✅ Room management routes
- ✅ Chat creation and viewing
- ✅ Comment system routes
- ✅ Dashboard access control
- ✅ Form validation and errors

### AI Integration (test_ai_integration.py)
- ✅ Writing mode system
- ✅ System instructions retrieval
- ✅ Custom prompt override
- ✅ AI response generation (mocked)
- ✅ Fallback mechanisms
- ✅ Context handling

### Dashboard (test_dashboard.py)
- ✅ Instructor dashboard access
- ✅ Room statistics and analytics
- ✅ Member activity tracking
- ✅ Chat mode analytics
- ✅ Custom prompt management
- ✅ Comment analytics

## 🔧 Test Environment Setup

### Prerequisites
- Python 3.8+
- Virtual environment activated
- All dependencies installed

### Environment Variables
Tests don't require actual API keys, but you can set them for integration testing:
```bash
export ANTHROPIC_API_KEY=your_key_here
export OPENAI_API_KEY=your_key_here
```

### Database Setup
Tests automatically create and destroy test databases. No manual setup required.

## 📈 Test Results

The test runner provides:
- Detailed test output with pass/fail status
- Summary statistics (total tests, failures, errors)
- Success rate percentage
- Detailed error messages for failures
- Exit codes for CI/CD integration

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're in the project root directory
2. **Database Errors**: Tests use in-memory database, no external setup needed
3. **Mock Errors**: AI tests use mocked responses, no API calls made
4. **Permission Errors**: Tests run with test configuration, no file system access needed

### Debug Mode
Run tests with verbose output:
```bash
python -m unittest -v tests.test_models
```

### Isolated Testing
Run tests in isolation to identify specific issues:
```bash
python -m unittest tests.test_models.TestModels.test_user_creation -v
```

## 📝 Adding New Tests

### Test File Structure
```python
import unittest
from app import create_app
from models import db, User, Room

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_new_feature(self):
        # Test implementation
        pass
```

### Test Naming Conventions
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Best Practices
- Each test should be independent
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies
- Clean up test data in tearDown 