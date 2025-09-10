# AI Collab Online

Collaborative, rubric‑aware, AI‑assisted writing spaces for teams and educators.

[![GitHub](https://img.shields.io/badge/GitHub-Open%20Source-green?style=for-the-badge)](https://github.com/writeian/Collab_AI_Online)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

## 🌐 Live

- Production: https://collab.up.railway.app
- Healthcheck: https://collab.up.railway.app/health

## 🚀 Quick Start (Local)

```bash
git clone https://github.com/writeian/Collab_AI_Online.git
cd Collab_AI_Online
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp env_template.txt .env  # add your keys (see Environment Variables)
alembic upgrade head
python run.py
```

**View on GitHub**: https://github.com/writeian/Collab_AI_Online

---

## 📋 Branches

- Production on Railway: `feature/railway-deployment`
- Development: `dev`

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

### 🎯 Template / Unified Editor
- **7 Pre-built templates** for different use cases (Study Group, Business Hub, Academic Essay, etc.)
- **Unified create/edit page** (`/room/create/learning-steps`) with goals → proposal → refine → create
- **Mobile-responsive design** with collapsible goal categories

### 🤖 AI-Powered Collaboration
- **Anthropic Claude integration** with contextual responses
- **Learning step progression** (10 stages: Explore → Focus → Draft → Revise)
- **AI response toggle** with persistent per-chat preferences
- **Google Docs integration** for document analysis

### 📊 Admin & Reports
- **Comprehensive analytics** for student progress tracking
- **Users report**: `/admin/users` and CSV export `/admin/users.csv`
- **Pending invite repair** (admin‑only) to clear legacy invitations
- **System instructions management** for custom AI prompts
- **Member management** with role-based permissions

### 💬 Chat Experience
- Focus mode toggle in chat to maximize writing space
- Rubric-aware "Assess Progress" with structured recommendations
- **Modular Flask blueprint architecture** with 85% type coverage
- **SQLAlchemy 2.0** with Alembic migrations
- **Production-ready** with Railway and Digital Ocean deployment
- **Comprehensive testing** with pytest and mypy

---

## 🆕 Notable Updates
- Single, unified create/edit flow for rooms (legacy create page removed)
- Anthropic 529 handling: retry + goal‑aware fallback (template inference, then Academic Essay as last resort)
- ENV‑based admin allowlist: `ADMIN_EMAILS`
- Email via SendGrid (Single Sender or Domain Auth)

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

## ⚙️ Environment Variables

Create `.env` (or set Railway Variables):

Required
```
SECRET_KEY=your_secret
FLASK_ENV=development
DATABASE_URL=postgresql+psycopg2://...  # or omit to use SQLite locally
ANTHROPIC_API_KEY=sk-ant-...
```

Email (SendGrid)
```
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.***
EMAIL_FROM=your_verified_sender@example.com
EMAIL_FROM_NAME=AI Collab Online
EMAIL_REPLY_TO=support@example.com
```

Admin allowlist
```
ADMIN_EMAILS=you@example.com,other@example.org
```

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
1. **Connect Repository**: Link this GitHub repo to your Railway project
2. **Start Command**: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120` (already in `railway.toml`)
3. **Healthcheck**: `/health` (already in `railway.toml`)
4. **Environment Variables**: Set `SECRET_KEY`, `ANTHROPIC_API_KEY`, `DATABASE_URL`, etc.
5. **Database**: Use PostgreSQL for production. Run migrations: `alembic upgrade head`
6. **Endpoint Name**: Set a friendly slug in Service → Networking (globally unique)
7. **Deploy**: Deploy from the UI or by pushing to your deployment branch

**📖 [Complete Railway Deployment Guide](RAILWAY_DEPLOYMENT.md)**

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

### Custom Domains (Railway)
- Recommended: add a subdomain like `app.yourdomain.com`
- Create a CNAME to your `*.up.railway.app` endpoint, verify in Railway Networking
- If verification fails, ensure DNS is set to DNS-only during initial verification and try again

---

## 🧪 Trial Mode (Optional/Future)

Offer limited, server-enforced guest trials (e.g., 1 room, 1 chat, 6 messages) without registration, with a clean upgrade path to a full account.

- Design doc: `docs/trial_sessions_option_2.md`
- Highlights: DB-backed counters, expiry/cleanup, adoption on signup, and abuse safeguards

---

## 🛟 Troubleshooting

- Anthropic 529 (service overloaded):
  - The app retries briefly and falls back to goal‑aware templates. Check Anthropic status and org limits.
  - Ensure `ANTHROPIC_API_KEY` is set on the correct service and org.

- Endpoint slug errors (Railway): endpoint names are globally unique. Try a different slug (Service → Networking → Endpoint name)
- Custom domains: add CNAME to your service’s `*.up.railway.app`; if using Cloudflare, set DNS-only during verification
- Static asset 404s on Linux: ensure case-sensitive paths (e.g., `Static/` vs `static/`)
- JSON POSTs and CSRF: app includes a global fetch wrapper that sends `X-CSRFToken` automatically

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

## 📁 Project Structure (high level)

```
Collab_AI_Online/
├── src/                          # Main application source
│   ├── app/                      # Flask blueprints
│   │   ├── room/                # Room routes (create/edit flow, services, utils)
│   │   ├── chat.py              # Chat functionality
│   │   ├── auth.py              # Authentication
│   │   ├── admin.py             # Admin dashboard & reports
│   │   ├── analytics.py         # Analytics endpoints
│   │   ├── achievements.py      # Gamification
│   │   └── access_control.py    # Permission & guards
│   ├── models/                   # Database models
│   ├── utils/                    # Utility functions
│   └── config/                   # Configuration
├── templates/                    # HTML templates
│   └── room/                     # Unified learning steps create/edit
├── tests/                        # Test suite
├── migrations/                   # Database migrations
└── requirements.txt              # Python dependencies
```

**Type Coverage**: 85% of functions have comprehensive type hints for better code quality and IDE support.
 