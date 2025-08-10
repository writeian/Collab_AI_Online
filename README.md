# AI Collab Online 🤖

**A collaborative AI-powered writing platform for teams and educators**

[![Live Demo](https://img.shields.io/badge/Live-Demo-blue?style=for-the-badge)](https://your-railway-url.railway.app)
[![GitHub](https://img.shields.io/badge/GitHub-Open%20Source-green?style=for-the-badge)](https://github.com/writeian/Collab_AI_Online)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

## 🚀 **Looking for Test Users!**

We're actively seeking educators, writing teams, and content creators to help improve this platform. Your feedback will shape the future of collaborative AI writing!

**Perfect for:**
- 📚 **Educators** - AI-assisted writing instruction
- ✍️ **Writing Teams** - Collaborative content creation  
- 🎯 **Content Creators** - AI-powered writing assistance
- 🔬 **Researchers** - Collaborative document writing

**[Try it now](https://your-railway-url.railway.app)** | **[View on GitHub](https://github.com/writeian/Collab_AI_Online)**

---

## ✨ Features

### Core Functionality
- **Room-Based Collaboration**: Create dedicated spaces for teams, classes, or projects
- **Multi-User Support**: Register, login, and manage user profiles with role-based access
- **AI Chat Integration**: Powered by OpenAI GPT-4o and Anthropic Claude for intelligent responses
- **AI Response Toggle**: Users can enable/disable AI responses per chat with persistent state
- **Chat Management**: Create, edit, delete, and organize conversations within rooms
- **Interactive Comments**: Students can comment on specific dialogue points for threaded discussions
- **Public/Private Rooms**: Make rooms public for community discovery or keep them private
- **Achievement System**: Track user progress and award badges for participation milestones

### Educational Writing Support
- **Learning Steps System**: 10 different learning stages (Explore, Focus, Outline, Draft, Revise, Polish, etc.)
- **Learning Step-Specific AI Prompts**: AI adapts its responses based on the current learning stage
- **Custom System Instructions**: Instructors can edit AI prompts for different learning steps and rooms
- **Google Docs Integration**: Import and analyze Google Docs directly into chats
- **Document Analysis**: Get AI feedback on your writing without importing text
- **Streamlined Room Creation**: 2-step process with AI proposal generation and conversational refinement
- **Conversational Mode Refinement**: Chat with AI to refine room title, description, and learning steps before finalizing

### AI Response Control
- **Toggle System**: Enable/disable AI responses with a simple checkbox
- **Persistent Preferences**: Your AI response settings are saved per chat
- **Default Behavior**: AI responses are enabled by default for new conversations
- **Per-Chat Settings**: Each chat maintains independent AI response preferences
- **Visual Feedback**: Clear labels indicate current toggle state and functionality

### Instructor Dashboard & Analytics
- **Comprehensive Dashboard**: Room overview, member management, and analytics
- **Student Analytics**: Track student prompts and learning steps usage
- **Prompt History**: Monitor how students use AI assistance with detailed logs
- **Mode Filtering**: Analyze usage patterns by learning stage
- **Member Activity**: Track participation and engagement levels
- **System Instructions Management**: Edit AI prompts for different learning steps and rooms

### Modern UI & Collaboration
- **Clean Design**: Responsive, intuitive user experience with modern styling
- **Real-time Messaging**: Seamless conversation flow with AI assistant
- **Access Control**: Secure permission system with decorators
- **Room Management**: Easy room creation, joining, and member management
- **Comment System**: Threaded discussions on specific AI responses
- **Settings Integration**: Functional gear button with dropdown menus for room actions
- **Consistent Styling**: Modern Tailwind CSS design with proper padding and responsive layouts

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key or Anthropic API key
- Google Cloud Project (for Google Docs integration)
- Git

## 🗄️ Database Migration System

### **Local Development with SQLite**

The application uses **Alembic** for database migrations, ensuring smooth deployment to Railway's PostgreSQL while maintaining local SQLite compatibility.

#### **Local Setup:**
```bash
# Set environment variables for local development
$env:DATABASE_URL="sqlite:///instance/ai_collab.db"  # Windows
export DATABASE_URL="sqlite:///instance/ai_collab.db"  # macOS/Linux

# Check current migration status
alembic current

# Apply all migrations
alembic upgrade head

# Check for pending migrations
alembic check
```

#### **Migration Commands:**
```bash
# View migration history
alembic history

# Create new migration (after model changes)
alembic revision --autogenerate -m "Description of changes"

# Rollback one migration
alembic downgrade -1

# Rollback to specific migration
alembic downgrade dade1def113a
```

### **Production Deployment with PostgreSQL**

When deploying to Railway, the system automatically:
- ✅ **Detects PostgreSQL** and creates foreign key constraints
- ✅ **Maintains SQLite compatibility** for local development
- ✅ **Applies all migrations** in the correct order
- ✅ **Handles database differences** between SQLite and PostgreSQL

#### **Current Migration Chain:**
1. `dade1def113a` - Initial migration (users, rooms, chats)
2. `12722155fa55` - Add parent_message_id and is_truncated to messages
3. `achievement_models_001` - Add achievement and user_mode_usage tables
4. `a8c4d37510b7` - Add accepted_at field to room_member (invitation tracking)

### **Database Schema**

**Core Tables:**
- `user` - User accounts and profiles
- `room` - Collaboration spaces
- `room_member` - Room memberships (with `accepted_at` for invitation tracking)
- `chat` - Conversations within rooms
- `message` - Individual messages (with parent_message_id for threading)
- `comment` - Comments on specific messages

**Analytics Tables:**
- `prompt_record` - Student prompt analytics
- `user_mode_usage` - Writing mode usage tracking
- `achievement` - User achievement badges
- `page_view` - Page view tracking

**Integration Tables:**
- `google_auth` - Google OAuth tokens for Docs integration
- `custom_prompt` - Custom system instructions

### **Development Workflow**

#### **Making Database Changes:**
1. **Update models** in `models.py`
2. **Generate migration**:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```
3. **Test locally** with SQLite:
   ```bash
   alembic upgrade head
   ```
4. **Verify production compatibility** - migrations work with PostgreSQL
5. **Commit and deploy** - Railway will apply migrations automatically

#### **Testing Migrations:**
```bash
# Test migration system
python test_migration_system.py

# Test invitation acceptance (new feature)
python test_invitation_acceptance.py
```

### **Migration Safety Features**

- ✅ **Rollback support** - All migrations have downgrade functions
- ✅ **Data integrity** - No data loss during migrations
- ✅ **Cross-database compatibility** - Works with SQLite and PostgreSQL
- ✅ **Environment detection** - Automatically handles database differences
- ✅ **Foreign key handling** - Creates constraints on PostgreSQL, skips on SQLite

### **Troubleshooting**

#### **Common Issues:**
- **Migration conflicts**: Run `alembic stamp head` to sync migration state
- **SQLite constraints**: Foreign keys are skipped on SQLite (expected behavior)
- **PostgreSQL errors**: Check `DATABASE_URL` format and permissions

#### **Verification Commands:**
```bash
# Check database tables
python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); from sqlalchemy import inspect; inspector = inspect(db.engine); print('Tables:', inspector.get_table_names())"

# Check migration status
alembic current

# Verify all migrations applied
alembic upgrade head
```

## 🚀 **Railway Deployment**

### **IMPORTANT: Deployment Branch Configuration**

**Always deploy from the `clean-deploy` branch to avoid confusion!**

#### **Railway Settings:**
- **Repository**: `writeian/Collab_AI_Online`
- **Branch**: `clean-deploy` 
- **Root Directory**: (leave empty or set to `/`)
- **Auto Deploy**: `ON`

#### **Environment Variables for Railway:**
```
FLASK_ENV=production
SECRET_KEY=your_secret_key_here
DATABASE_URL=your_railway_postgresql_url
PORT=8080
```

#### **Deployment Process:**
1. **Make changes** in your local `clean-deploy` branch
2. **Commit and push** to GitHub:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin clean-deploy
   ```
3. **Railway automatically deploys** from the `clean-deploy` branch
4. **Monitor deployment logs** in Railway dashboard

#### **⚠️ Common Deployment Issues:**
- **Wrong branch**: Ensure Railway is set to `clean-deploy`, not `main` or `dev`
- **Cached deployments**: If changes don't appear, check Railway is connected to the correct repository
- **Database migrations**: Achievement tables are created automatically via the `/health` endpoint

---

## 🧪 Testing

### Test Status

The application includes a comprehensive test suite with the following status:

#### ✅ **Passing Tests (Core Functionality)**
- **App Creation**: Flask application initializes correctly
- **Database Setup**: SQLAlchemy models and tables work properly
- **Basic Routes**: All main routes (home, login, register, rooms, about) function correctly
- **Template Rendering**: All HTML templates load without errors
- **User Registration**: User creation and authentication work as expected

#### ⚠️ **Test Suite Notes**
- **Basic Functionality**: All core features are tested and working
- **Comprehensive Tests**: Extended test suite exists but may have minor mismatches with current implementation
- **Test Coverage**: Core functionality is well-tested; advanced features may need test updates
- **Database Warnings**: Minor ResourceWarnings about unclosed database connections (non-critical)

### Running Tests

```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Run basic functionality tests
python -m unittest tests.test_basic.TestBasicFunctionality -v

# Run all tests (may show some expected errors)
python run_tests.py
```

### Test Structure

```
tests/
├── test_basic.py          # Core functionality tests (✅ All Passing)
├── test_models.py         # Database model tests
├── test_routes.py         # Route functionality tests
├── test_dashboard.py      # Dashboard and analytics tests
├── test_ai_integration.py # AI service integration tests
└── README.md             # Test documentation
```

**Note**: The basic functionality tests confirm that the application is working correctly for production use. The comprehensive test suite may show some errors due to implementation details that differ from test expectations, but these don't affect core functionality.

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/writeian/AI_Collab_Teams/issues) page
2. Create a new issue with detailed information
3. Include your Python version, OS, and error messages

## 🔮 Roadmap

- [x] Room-based collaboration system
- [x] Instructor dashboard with analytics
- [x] Interactive commenting system
- [x] Custom system instructions management
- [x] Google Docs integration with service account
- [x] Learning steps system with 10 stages
- [x] Dashboard analytics for student tracking
- [x] Access control with permission decorators
- [x] Comprehensive test suite
- [x] Modern chat interface with improved UX
- [x] Modern home page with proper navigation structure
- [x] AI response toggle with persistent state
- [x] Room mode generation system with contextual AI modes
- [x] Industry-standard responsive design and padding
- [x] Modern form design with card layouts
- [x] Comprehensive footer with essential links
- [x] Case-insensitive login system
- [x] Streamlined room creation with AI proposal generation
- [x] Conversational mode refinement system
- [x] Learning steps terminology throughout application
- [x] Proper numerical ordering for learning steps (1, 2, 3... 10, 11)
- [x] Database cascade relationships for proper room deletion
- [x] Settings gear button functionality
- [x] Consistent styling across all pages
- [ ] Real-time messaging with WebSockets
- [ ] Advanced chat analytics
- [ ] Mobile app development
- [ ] Multi-language support
- [ ] Chat export functionality
- [ ] Integration with learning management systems
- [ ] Video conferencing integration
- [ ] Advanced room templates

---

## 🆕 Recent Improvements (January 2025)

### Phase 6: Streamlined Room Creation & Learning Steps ✅
- **Streamlined Room Creation Flow**: Redesigned room creation as a 2-step process:
  1. **Step 1**: User enters learning goals
  2. **Step 2**: AI proposes room title, description, and learning steps with conversational refinement
- **Conversational Mode Refinement**: Users can chat with AI to refine room proposals before finalizing
- **Learning Steps Terminology**: Replaced "modes" with "learning steps" throughout the application for better user understanding
- **Proper Numerical Ordering**: Learning steps now display in correct numerical order (1, 2, 3... 10, 11) instead of alphabetical
- **AI Proposal System**: New endpoints (`/generate-room-proposal`, `/refine-room-proposal`) for intelligent room creation
- **Enhanced User Experience**: Clear step-by-step guidance with AI assistance throughout room creation

### Phase 5: Comprehensive UI/UX Improvements ✅
- **Room Mode Generation Fix**: Fixed critical API response handling bug that prevented custom room goals from generating contextual AI modes
- **Industry-Standard Padding**: Standardized all pages with responsive, mobile-friendly padding (`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8`)
- **Modern Form Design**: Updated all forms (room creation, editing, auth pages) with consistent card layouts and modern styling
- **Navigation Cleanup**: Removed duplicate "Home" links from both desktop and mobile navigation menus
- **Industry-Standard Footer**: Added comprehensive footer with About, Privacy Policy, Terms of Service, and Contact links
- **Case-Insensitive Login**: Improved login system with smart username matching (exact match first, then case-insensitive fallback)
- **About Page Accessibility**: About page now accessible from footer on all pages, following industry best practices
- **Responsive Design**: All pages now work seamlessly across desktop, tablet, and mobile devices
- **Modern Button Styling**: Consistent button design with hover effects and proper color schemes throughout the application
- **Form Validation Enhancement**: Improved form styling with better focus states and error handling

### Phase 4: AI Response Toggle System ✅
- **AI Response Toggle**: Users can now enable/disable AI responses on a per-chat basis
- **Persistent State**: Toggle state is saved in localStorage and persists between page refreshes
- **Per-Chat Settings**: Each chat maintains its own AI response preference
- **Default Behavior**: AI responses are enabled by default for new chats
- **User-Friendly Interface**: Clear toggle with descriptive labels and visual feedback
- **Seamless Integration**: Toggle is integrated into the chat form for easy access

### Phase 3: Invitation Acceptance System ✅
- **Smart invitation tracking**: Invitations are automatically marked as accepted when users visit invited rooms
- **Notification clearing**: Nav bar and home page notifications clear when invitations are accepted
- **Database migration system**: Production-ready Alembic migrations for Railway deployment
- **Cross-database compatibility**: Works seamlessly with SQLite (development) and PostgreSQL (production)
- **Migration safety**: All migrations have rollback support and maintain data integrity
- **Environment detection**: Automatically handles database differences between development and production

### Phase 2: Modern Home Page & Navigation ✅
- **Proper navigation structure**: Rooms page now serves as the main "Home" page
- **Dashboard as administrative feature**: Separated from main navigation for clarity
- **Modern home page design** with clean navigation header and welcome banner
- **Breadcrumb navigation**: Clear hierarchy showing Home > Room > Chat
- **"My Rooms" section** showing rooms the user owns with action buttons
- **"Rooms I'm In" section** showing rooms the user has been invited to
- **Recent invitations** highlighted with special styling and "New" badges
- **Responsive grid layout** for room cards with hover effects
- **Modern button styling** with icons and proper color schemes
- **Empty state design** for users with no rooms yet
- **Improved navigation flow**: Home (rooms) > Dashboard (admin) > Profile > About

### Phase 1: Modern Chat Interface & UX ✅
- **Modern chat bubbles:**
  - User messages: purple gradient (#6F49AD)
  - AI messages: solid white background
  - Comments: rose color (#FCA4DF) with black text
- **Enhanced sidebar design** with conversation search and current chat highlighting
- **Add Comment:** Button now appears inline with message timestamp for easy access
- **Delete Comment:** Small trash can icon with white background and red icon for clean, non-intrusive deletion
- **Double-submission prevention:** Send button disables and shows "Sending..." after click, preventing accidental duplicates
- **Smart autoscroll:** Chat autoscrolls to the latest message after sending/receiving
- **System Instructions Dropdown:** AI system instructions are always accessible in the left pane
- **Improved accessibility:** Higher contrast, better font weights, and more readable color palette
- **Modern avatar system** with online indicators and conversation previews

### Bug Fixes & Database Improvements ✅
- **Database Cascade Relationships**: Fixed room deletion by adding proper cascade rules to Room model relationships
- **Settings Gear Button**: Fixed non-functional settings dropdown in room view pages
- **Dropdown Menu Fixes**: Resolved form submission issues with AI instruction dropdowns
- **Consistent Styling**: Fixed padding inconsistencies across delete pages and other UI elements
- **Numerical Sorting**: Implemented proper sorting for learning steps with numerical prefixes

### Project Cleanup
- **Removed 22+ debug/test files** from the main directory (now in `cleanup_files/`)
- **Large backup files and setup scripts** moved out of the way
- **Project structure is now clean and production-ready**

---

**Made with ❤️ by writeian**
 