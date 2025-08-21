# AI Collab Online 🤖

**A collaborative AI-powered writing platform for teams and educators**

[![GitHub](https://img.shields.io/badge/GitHub-Open%20Source-green?style=for-the-badge)](https://github.com/writeian/Collab_AI_Online)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Type Coverage](https://img.shields.io/badge/Type%20Coverage-85%25-green?style=for-the-badge)](https://github.com/writeian/Collab_AI_Online)

## 🚀 Quick Start

```bash
git clone https://github.com/writeian/Collab_AI_Online.git
cd AI_Collab_Online
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python run.py
```

**Live Demo**: [Coming Soon] | **[View on GitHub](https://github.com/writeian/Collab_AI_Online)**

---

## 🎯 What It Does

AI Collab Online is a **collaborative writing platform** that helps teams and educators create better content together using AI assistance.

### **For Educators:**
- **Create learning environments** with pre-built templates (Study Groups, Academic Essays, Writing Workshops)
- **Guide students** through structured 10-step writing processes
- **Track progress** with comprehensive analytics and achievement systems
- **Customize AI prompts** for different learning stages and subjects

### **For Writing Teams:**
- **Collaborate in dedicated rooms** with real-time messaging and AI assistance
- **Use specialized templates** for different project types (Business Hub, Creative Studio)
- **Organize goals** with collapsible categories to reduce cognitive overload
- **Toggle AI responses** on/off per conversation for flexible collaboration

### **For Content Creators:**
- **Import Google Docs** for AI analysis and feedback
- **Use contextual AI** that adapts responses based on your current writing stage
- **Manage multiple projects** with organized room-based workspaces
- **Get instant feedback** on writing quality and structure

### **Key Benefits:**
- 🚀 **Get started in minutes** with 7 pre-built templates
- 🤖 **AI that understands context** - Responses adapt to your learning stage
- 👥 **Built for collaboration** - Real-time messaging with threaded discussions
- 📱 **Works everywhere** - Mobile-responsive design for any device
- 🎯 **Structured learning** - 10-step progression from exploration to final polish

---

## ✨ Core Features

### 🎯 Template Wizard System
- **7 Pre-built templates** for different use cases (Study Group, Business Hub, Academic Essay, etc.)
- **4-step guided setup** with auto-populated goals and AI modes
- **Mobile-responsive design** with collapsible goal categories

### 🤖 AI-Powered Collaboration
- **Anthropic Claude integration** with contextual responses
- **Learning step progression** (10 stages: Explore → Focus → Draft → Revise)
- **AI response toggle** with persistent per-chat preferences
- **Google Docs integration** for document analysis

### 📊 Instructor Dashboard
- **Comprehensive analytics** for student progress tracking
- **Achievement system** with gamification elements
- **System instructions management** for custom AI prompts
- **Member management** with role-based permissions

### 🏗️ Modern Architecture
- **Modular Flask blueprint architecture** with 85% type coverage
- **SQLAlchemy 2.0** with Alembic migrations
- **Production-ready** with Railway and Digital Ocean deployment
- **Comprehensive testing** with pytest and mypy

---

## 🆕 Recent Major Updates

### ✅ Backend Modularization (August 2025)
**1,536-line monolithic file** → **5 focused modules** with clear separation of concerns
- **100% functionality preserved** with enhanced type safety
- **Improved maintainability** and testability

### ✅ Type Safety Implementation (August 2025)
**85% type coverage** across the codebase with mypy integration
- **Enhanced IDE support** and developer experience
- **Runtime safety** improvements

### 🔄 Goal Categorization UX (In Progress)
**Study Group template** fully implemented with collapsible goal categories
- **6 remaining templates** ready for implementation
- **Reduced cognitive load** for better user experience

**[📋 View Complete Development History](CHANGELOG.md)**

---

## 🛠️ Technology Stack

### Backend
- **Flask 3.1.1** with modular blueprint architecture
- **SQLAlchemy 2.0.41** with Alembic migrations
- **SQLite** (development) / **PostgreSQL** (production)
- **Custom session-based authentication** with Google OAuth support

### Frontend
- **Tailwind CSS** with responsive design
- **Jinja2 templates** with modern component structure
- **Vanilla JavaScript** with ES6+ features
- **Mobile-optimized** with progressive enhancement

### AI Services
- **Anthropic Claude API** for intelligent responses
- **Contextual learning modes** based on educational stages
- **Error handling** with graceful fallbacks

### Deployment
- **Railway** with automatic deployments
- **Digital Ocean** with Nginx + Gunicorn
- **Built-in health checks** and monitoring
- **SSL certificates** and security headers

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Anthropic API key
- Google Cloud Project (for Google Docs integration)

### Installation
```bash
# Clone the repository
git clone https://github.com/writeian/Collab_AI_Online.git
cd AI_Collab_Online

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your Anthropic API key

# Run the application
python run.py
```

### Environment Variables
Create a `.env` file in the root directory:

```env
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///instance/ai_collab.db

# Flask settings
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

---

## 🔧 Development

### Code Quality
```bash
# Run all tests
python -m pytest

# Type checking with mypy
python -m mypy src/app/ --ignore-missing-imports

# Linting with flake8
python -m flake8 src/ --max-line-length=120
```

### Project Structure
```
AI_Collab_Online/
├── src/                    # Main application
│   ├── app/               # Flask blueprints
│   ├── models/            # Database models
│   ├── utils/             # Utilities & AI integration
│   └── config/            # Configuration
├── templates/             # HTML templates
├── tests/                 # Test suite
├── scripts/               # Development utilities
└── deployment/            # Deployment configs
```

**Full structure**: [See detailed breakdown](#detailed-project-structure)

---

## 🚀 Deployment

### Railway Deployment
1. **Connect Repository**: Link your GitHub repository to Railway
2. **Environment Variables**: Set all required environment variables
3. **Database**: Railway automatically provisions PostgreSQL
4. **Deploy**: Railway automatically deploys on every push to main

### Digital Ocean Deployment
```bash
# Run automated deployment script
bash deployment/deploy.sh
```

### Manual Deployment
```bash
# Install production dependencies
pip install -r requirements_production.txt

# Set production environment variables
export FLASK_ENV=production
export DATABASE_URL=your_postgresql_url

# Run migrations
alembic upgrade head

# Start production server
gunicorn src.wsgi:app
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for detailed information and check our [GitHub Issues](https://github.com/writeian/Collab_AI_Online/issues) for current needs.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Style & Quality
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for all functions
- **Include type hints for all new functions**
- Run mypy for type checking: `python -m mypy src/ --ignore-missing-imports`
- Run flake8 for linting: `python -m flake8 src/ --max-line-length=120`

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/writeian/Collab_AI_Online/issues)
- **Discussions**: [GitHub Discussions](https://github.com/writeian/Collab_AI_Online/discussions)

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Anthropic** for providing the Claude API
- **Flask** community for the excellent web framework
- **Tailwind CSS** for the beautiful styling system
- **All contributors** who have helped improve this platform

---

**Made with ❤️ for educators and writers everywhere**

---

## 📁 Detailed Project Structure

```
AI_Collab_Online/
├── src/                          # Main application source
│   ├── app/                      # Flask blueprints
│   │   ├── goals/                # Goal generation module
│   │   ├── room.py              # Room management (✅ Typed)
│   │   ├── chat.py              # Chat functionality (✅ Typed)
│   │   ├── auth.py              # Authentication (✅ Typed)
│   │   ├── dashboard.py         # Instructor dashboard (✅ Typed)
│   │   ├── analytics.py         # Analytics & monitoring (✅ Typed)
│   │   ├── achievements.py      # Gamification system (✅ Typed)
│   │   └── access_control.py    # Permission system (✅ Typed)
│   ├── models/                   # Database models
│   ├── utils/                    # Utility functions
│   └── config/                   # Configuration
├── templates/                    # HTML templates
│   └── room/
│       └── templates/           # Template wizard HTML files
├── tests/                        # Test suite
├── migrations/                   # Database migrations
└── requirements.txt              # Python dependencies
```

**Type Coverage**: 85% of functions have comprehensive type hints for better code quality and IDE support.
 