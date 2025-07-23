from flask import Flask
from models import db
import os
from config import config

# Import Blueprints
from auth import auth
from room import room
from chat import chat
from dashboard import dashboard
from google_auth import google_auth
from analytics import analytics

# Automatically run Alembic migrations in production (e.g., on Railway)
if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("FLASK_ENV") == "production":
    try:
        from alembic.config import Config
        from alembic import command
        print("Running Alembic migrations...")
        alembic_cfg = Config("alembic.ini")
        # Only run migrations if tables don't exist to avoid conflicts
        command.upgrade(alembic_cfg, "head")
        print("Alembic migrations complete.")
    except Exception as e:
        print("Alembic migration failed:", e)
        # Continue anyway - the app will handle table creation
    
    # Also ensure achievement tables exist
    try:
        print("Ensuring achievement tables exist...")
        from models import db, UserModeUsage, Achievement
        
        # Create a temporary app context
        temp_app = Flask(__name__)
        temp_app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
        temp_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(temp_app)
        
        with temp_app.app_context():
            # Create achievement tables if they don't exist
            UserModeUsage.__table__.create(db.engine, checkfirst=True)
            Achievement.__table__.create(db.engine, checkfirst=True)
            print("✓ Achievement tables ensured")
    except Exception as e:
        print(f"Achievement table creation failed: {e}")


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
                
                # Also check and create achievement tables
                try:
                    # Create tables directly using SQL to avoid import issues
                    with db.engine.connect() as conn:
                        # Create user_mode_usage table
                        conn.execute(db.text("""
                            CREATE TABLE IF NOT EXISTS user_mode_usage (
                                id SERIAL PRIMARY KEY,
                                user_id INTEGER NOT NULL REFERENCES "user"(id),
                                room_id INTEGER NOT NULL REFERENCES room(id),
                                mode VARCHAR(32) NOT NULL,
                                first_used_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                                last_used_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                                usage_count INTEGER NOT NULL DEFAULT 1,
                                UNIQUE(user_id, room_id, mode)
                            )
                        """))
                        
                        # Create achievement table
                        conn.execute(db.text("""
                            CREATE TABLE IF NOT EXISTS achievement (
                                id SERIAL PRIMARY KEY,
                                user_id INTEGER NOT NULL REFERENCES "user"(id),
                                room_id INTEGER NOT NULL REFERENCES room(id),
                                achievement_type VARCHAR(50) NOT NULL,
                                earned_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                                UNIQUE(user_id, room_id, achievement_type)
                            )
                        """))
                        
                        conn.commit()
                    achievement_status = "✓ Achievement tables ensured"
                except Exception as e:
                    achievement_status = f"⚠ Achievement tables error: {str(e)}"
                
                return {
                    'status': 'healthy', 
                    'message': 'App is running - ACHIEVEMENTS FIXED - AUTO DEPLOY TEST', 
                    'database': 'connected',
                    'achievement_tables': achievement_status,
                    'version': '4.0',
                    'deployment_test': 'AUTO DEPLOY WORKING',
                    'timestamp': '2024-07-23 22:45'
                }, 200
            else:
                return {'status': 'healthy', 'message': 'App is running', 'database': 'not configured'}, 200
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e), 'database': 'error'}, 500
    
    # Test endpoint to list all routes
    @app.route('/routes')
    def list_routes():
        """List all available routes for debugging"""
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': str(rule)
            })
        return {'routes': routes}
    
    # Simple migration endpoint
    @app.route('/migrate-db')
    def migrate_database():
        """Simple migration to create achievement tables"""
        try:
            from models import db, UserModeUsage, Achievement
            
            # Create achievement tables
            UserModeUsage.__table__.create(db.engine, checkfirst=True)
            Achievement.__table__.create(db.engine, checkfirst=True)
            
            return "✅ Achievement tables created successfully!"
            
        except Exception as e:
            return f"❌ Migration error: {str(e)}"
    
    # Debug database endpoint (available in all environments)
    @app.route('/debug-db')
    def debug_database():
        """Check database tables and schema"""
        try:
            from models import db, UserModeUsage, Achievement
            
            with db.engine.connect() as conn:
                # Check if achievement tables exist
                result = conn.execute(db.text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name IN ('user_mode_usage', 'achievement')
                """))
                existing_tables = [row[0] for row in result.fetchall()]
                
                # Check user table columns
                result = conn.execute(db.text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'user' AND table_schema = 'public'
                """))
                user_columns = [row[0] for row in result.fetchall()]
                
                # Check if there are any achievements in the database
                achievement_count = 0
                if 'achievement' in existing_tables:
                    result = conn.execute(db.text("SELECT COUNT(*) FROM achievement"))
                    achievement_count = result.fetchone()[0]
                
                # Check if there are any mode usage records
                usage_count = 0
                if 'user_mode_usage' in existing_tables:
                    result = conn.execute(db.text("SELECT COUNT(*) FROM user_mode_usage"))
                    usage_count = result.fetchone()[0]
                
                return {
                    'achievement_tables_exist': 'user_mode_usage' in existing_tables and 'achievement' in existing_tables,
                    'existing_tables': existing_tables,
                    'achievement_count': achievement_count,
                    'usage_count': usage_count,
                    'user_columns': user_columns,
                    'database_url': str(db.engine.url).replace(db.engine.url.password, '***') if db.engine.url.password else str(db.engine.url)
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    if app.config.get('ENV') != 'production':
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

    # Add a simple test route at the end
    @app.route('/test-simple')
    def test_simple():
        return "Hello from Flask! App is working."

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
