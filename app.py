from flask import Flask
from models import db
import os
from config import config
from sqlalchemy import create_engine, text

# Import Blueprints
from auth import auth
from room import room
from chat import chat
from dashboard import dashboard
from google_auth import google_auth
from analytics import analytics

# Ensure message table has required columns in production

def ensure_message_columns():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        return
    engine = create_engine(db_url)
    with engine.connect() as conn:
        # Check if columns exist
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='message'"))
        columns = [row[0] for row in result.fetchall()]
        if 'parent_message_id' not in columns:
            print("Adding parent_message_id column to message table...")
            conn.execute(text("ALTER TABLE message ADD COLUMN parent_message_id INTEGER"))
            conn.execute(text("ALTER TABLE message ADD CONSTRAINT fk_message_parent_message_id_message FOREIGN KEY(parent_message_id) REFERENCES message(id)"))
        if 'is_truncated' not in columns:
            print("Adding is_truncated column to message table...")
            conn.execute(text("ALTER TABLE message ADD COLUMN is_truncated BOOLEAN NOT NULL DEFAULT FALSE"))
        conn.commit()

# Automatically run Alembic migrations in production (e.g., on Railway)
if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("FLASK_ENV") == "production":
    ensure_message_columns()
    try:
        from alembic.config import Config
        from alembic import command
        print("Running Alembic migrations...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("Alembic migrations complete.")
    except Exception as e:
        print("Alembic migration failed:", e)


def create_app(config_name=None):
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
    # Ensure static files are served in production
    if app.config.get('ENV') == 'production':
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
    # Get configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    print("SQLALCHEMY_DATABASE_URI:", app.config.get('SQLALCHEMY_DATABASE_URI'))

    # Initialize database only if database URL is available
    if app.config.get('SQLALCHEMY_DATABASE_URI'):
        db.init_app(app)
        
        # Only create tables if database URL is available
        try:
            with app.app_context():
                db.create_all()
        except Exception as e:
            print(f"Warning: Could not initialize database: {e}")
    else:
        print("Warning: No database URL configured - skipping database initialization")
        # Create a minimal app without database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        db.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(room, url_prefix='/room')
    app.register_blueprint(chat, url_prefix='/chat')
    app.register_blueprint(dashboard, url_prefix='/dashboard')
    app.register_blueprint(google_auth, url_prefix='/auth/google')
    app.register_blueprint(analytics, url_prefix='/analytics')
    
    # Health check endpoint for Railway
    @app.route('/health')
    def health():
        try:
            # Test database connection
            from models import db
            if app.config.get('SQLALCHEMY_DATABASE_URI'):
                with app.app_context():
                    with db.engine.connect() as conn:
                        conn.execute(db.text('SELECT 1'))
                return {'status': 'healthy', 'message': 'App is running', 'database': 'connected'}, 200
            else:
                return {'status': 'healthy', 'message': 'App is running', 'database': 'not configured'}, 200
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e), 'database': 'error'}, 500
    
    # Test route to verify app is working
    @app.route('/test')
    def test():
        return {'status': 'ok', 'message': 'App is working', 'routes': ['/health', '/setup-db', '/migrate-db']}
    
    # Database setup endpoint
    @app.route('/setup-db')
    def setup_database():
        try:
            from models import db
            with app.app_context():
                db.create_all()
            return {'status': 'success', 'message': 'Database tables created'}, 200
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, 500
    
    # Database migration endpoint
    @app.route('/migrate-db')
    def migrate_database():
        """Migrate database to add new profile fields"""
        try:
            # Import the User model to ensure it's loaded
            from models import User, db
            
            # Create all tables (this will add missing columns)
            db.create_all()
            
            # Check if we need to add columns manually
            with db.engine.connect() as conn:
                # Check if new columns exist (PostgreSQL syntax)
                result = conn.execute(db.text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'user' AND table_schema = 'public'
                """))
                columns = [row[0] for row in result.fetchall()]
                
                missing_columns = []
                expected_columns = [
                    'full_name', 'institution', 'department', 'research_area', 
                    'role', 'primary_use_case', 'team_size', 'heard_from',
                    'receive_updates', 'contact_for_research', 'reset_token', 
                    'reset_token_expiry'
                ]
                
                for col in expected_columns:
                    if col not in columns:
                        missing_columns.append(col)
                
                if missing_columns:
                    # Add missing columns
                    for col in missing_columns:
                        if col in ['receive_updates', 'contact_for_research']:
                            conn.execute(db.text(f"ALTER TABLE \"user\" ADD COLUMN {col} BOOLEAN DEFAULT FALSE"))
                        elif col == 'reset_token_expiry':
                            conn.execute(db.text(f"ALTER TABLE \"user\" ADD COLUMN {col} TIMESTAMP"))
                        else:
                            conn.execute(db.text(f"ALTER TABLE \"user\" ADD COLUMN {col} VARCHAR(200)"))
                    
                    conn.commit()
                    return f"Database migrated successfully. Added columns: {', '.join(missing_columns)}"
                else:
                    return "Database is already up to date."
                    
        except Exception as e:
            return f"Migration error: {str(e)}"
    
    # Database reset endpoint (WARNING: This will delete all data!)
    @app.route('/reset-db')
    def reset_database():
        """Reset database - DELETE ALL DATA!"""
        try:
            from models import db, User, Room, RoomMember, Chat, Message, Comment, CustomPrompt, PromptRecord, GoogleAuth
            
            with app.app_context():
                # Delete all data in the correct order (respecting foreign keys)
                db.session.query(Comment).delete()
                db.session.query(Message).delete()
                db.session.query(PromptRecord).delete()
                db.session.query(Chat).delete()
                db.session.query(RoomMember).delete()
                db.session.query(CustomPrompt).delete()
                db.session.query(Room).delete()
                db.session.query(GoogleAuth).delete()
                db.session.query(User).delete()
                
                # Commit the changes
                db.session.commit()
                
                return {
                    'status': 'success', 
                    'message': 'Database reset successfully. All users and data have been deleted.',
                    'warning': 'You will need to register again to use the app.'
                }
                
        except Exception as e:
            db.session.rollback()
            return {
                'status': 'error', 
                'message': f'Database reset failed: {str(e)}'
            }
    
    # Debug static files endpoint
    @app.route('/debug-static')
    def debug_static():
        import os
        static_path = os.path.join(app.root_path, 'static')
        css_path = os.path.join(static_path, 'style.css')
        return {
            'static_folder': app.static_folder,
            'static_url_path': app.static_url_path,
            'static_path_exists': os.path.exists(static_path),
            'css_file_exists': os.path.exists(css_path),
            'css_file_size': os.path.getsize(css_path) if os.path.exists(css_path) else 0
        }
    
    # Redirect root to room index
    @app.route('/')
    def root():
        from flask import redirect, url_for
        return redirect(url_for('room.index'))

    # About page
    @app.route('/about')
    def about():
        from flask import render_template
        return render_template('about.html')

    # Admin route to view users
    @app.route('/admin/users')
    def admin_users():
        from models import User
        from flask import render_template
        users = User.query.all()
        return render_template('admin_users.html', users=users)
    
    # Admin route to view analytics
    @app.route('/admin/analytics')
    def admin_analytics():
        from flask import render_template
        return render_template('admin_analytics.html')

    # Context processor to make current user available to all templates
    @app.context_processor
    def inject_user():
        from access_control import get_current_user
        return dict(user=get_current_user())

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
