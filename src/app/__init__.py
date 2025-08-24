"""
Application package for AI Collab Online
Contains core Flask application and blueprints
"""

from flask import Flask, request
import os as _os
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import FlaskForm
import re

# Create SQLAlchemy instance for app package
db = SQLAlchemy()
# Create CSRF protection instance
csrf = CSRFProtect()
# Create rate limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=None  # Will be configured per environment
)


def markdown_filter(text):
    """Convert basic markdown to HTML."""
    if not text:
        return text
    
    # Convert line breaks to <br> tags
    text = text.replace('\n', '<br>')
    
    # Convert **text** to <strong>text</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Convert *text* to <em>text</em>
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    return text


def create_app(config_name=None):
    """Application factory pattern for Flask app creation."""
    from src.config.settings import config

    # Note: Repository uses capitalized directories `Static/` and `Templates/` at project root.
    # Linux filesystems are case-sensitive, so we must point Flask to the exact paths.
    # Resolve absolute paths for static and template folders to avoid case-sensitivity issues in production
    _here = _os.path.dirname(__file__)
    _root = _os.path.abspath(_os.path.join(_here, '..', '..'))
    # Packaged static lives alongside this file under src/app/static
    _static_abs = _os.path.join(_here, 'static')
    _templates_abs = _os.path.join(_root, 'templates')  # lowercase in repo

    app = Flask(
        __name__,
        static_folder=_static_abs,
        static_url_path="/static",
        template_folder=_templates_abs,
    )

    # Get configuration
    if config_name is None:
        import os

        config_name = os.getenv("FLASK_ENV", "development")

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize database
    db.init_app(app)

    # Eagerly import models and ensure tables exist
    from src import models as _models
    with app.app_context():
        db.create_all()
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Disable CSRF for development
    if app.debug:
        app.config['WTF_CSRF_ENABLED'] = False
    
    # Initialize rate limiting with environment-specific storage
    if app.config.get('FLASK_ENV') == 'production':
        # Production: Use Redis if available, otherwise database
        redis_url = app.config.get('REDIS_URL')
        if redis_url:
            limiter.init_app(app, storage_uri=redis_url)
        else:
            # Fallback to database storage
            db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
            if db_url and 'postgresql' in db_url:
                # Use PostgreSQL for rate limiting
                limiter.init_app(app, storage_uri=f"{db_url}?sslmode=disable")
            else:
                # Use SQLite for rate limiting
                limiter.init_app(app, storage_uri="sqlite:///instance/rate_limits.db")
    else:
        # Development: Use in-memory storage (faster for development)
        limiter.init_app(app)
    
    # Add security headers
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # CSP configuration that allows CDN resources

        # Set CSRF cookie for JS fetch
        try:
            token = generate_csrf()
            response.set_cookie('csrf_token', token, secure=not app.debug, httponly=False, samesite='Lax', path='/')
        except Exception:
            pass

        # CSP configuration that allows CDN resources
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://unpkg.com; style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; img-src 'self' data:; connect-src 'self';"
        if not app.config.get('TESTING', False) and not app.debug:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
    
    # Register custom template filters
    app.jinja_env.filters['markdown'] = markdown_filter

    # Debug: Log static/template paths and CSS existence at startup
    try:
        import os as __os
        css_paths = [
            __os.path.join(app.static_folder or '', 'css', 'globals.css'),
            __os.path.join(app.static_folder or '', 'css', 'components.css'),
            __os.path.join(app.static_folder or '', 'css', 'style.css'),
        ]
        print(f"[static] static_folder={app.static_folder}")
        print(f"[static] template_folder={app.template_folder}")
        for p in css_paths:
            print(f"[static] exists({p})={__os.path.exists(p)}")
    except Exception as _e:
        print(f"[static] startup static check failed: {_e}")

    # Register blueprints
    from src.app.auth import auth
    from src.app.chat import chat
    from src.app.room import room
    from src.app.dashboard import dashboard
    from src.app.google_auth import google_auth
    from src.app.analytics import analytics

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(chat, url_prefix="/chat")
    app.register_blueprint(room, url_prefix="/room")
    app.register_blueprint(dashboard, url_prefix="/dashboard")
    app.register_blueprint(google_auth, url_prefix="/auth/google")
    app.register_blueprint(analytics, url_prefix="/analytics")

    # Add main routes
    @app.route("/")
    def index():
        """Root endpoint - redirect to rooms page."""
        from flask import redirect, url_for

        return redirect(url_for("room.room_crud.index"))

    @app.route("/about")
    def about():
        """About page."""
        from flask import render_template

        return render_template("about.html")

    @app.route("/landing")
    def landing():
        """Landing page."""
        from flask import render_template

        return render_template("landing.html")
    
    @app.route("/metrics")
    def metrics():
        """Application metrics endpoint for monitoring."""
        from flask import jsonify
        from datetime import datetime, timedelta
        
        try:
            # Import models only when needed to avoid conflicts
            from src.models import User, Room, Chat, Message
            
            # Basic metrics
            total_users = User.query.count()
            total_rooms = Room.query.count()
            total_chats = Chat.query.count()
            total_messages = Message.query.count()
            
            # Recent activity (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_users = User.query.filter(User.created_at >= yesterday).count()
            recent_rooms = Room.query.filter(Room.created_at >= yesterday).count()
            recent_messages = Message.query.filter(Message.timestamp >= yesterday).count()
            
            return jsonify({
                "status": "healthy",
                "metrics": {
                    "total_users": total_users,
                    "total_rooms": total_rooms,
                    "total_chats": total_chats,
                    "total_messages": total_messages,
                    "recent_activity": {
                        "new_users_24h": recent_users,
                        "new_rooms_24h": recent_rooms,
                        "new_messages_24h": recent_messages
                    }
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500

    # Lightweight endpoint to verify static file availability in prod
    @app.route("/__static_check")
    def __static_check():
        import os as __os
        try:
            base = app.static_folder or ''
            files = {
                'static_folder': base,
                'globals_css': __os.path.join(base, 'css', 'globals.css'),
                'components_css': __os.path.join(base, 'css', 'components.css'),
                'style_css': __os.path.join(base, 'css', 'style.css'),
            }
            exists = {k + '_exists': __os.path.exists(v) if k != 'static_folder' else True for k, v in files.items()}
            return {
                'ok': True,
                **files,
                **exists
            }
        except Exception as e:
            return { 'ok': False, 'error': str(e) }, 500

    # Targeted fallback route to serve CSS from the configured Static/css directory
    # This guards against case/path mismatches causing 404s on /static/css/* in production
    @app.route("/static/css/<path:filename>")
    def __static_css_fallback(filename: str):
        try:
            from flask import send_from_directory
            import os as __os
            _abs_css = __os.path.join(app.static_folder or '', 'css')
            return send_from_directory(_abs_css, filename, mimetype='text/css')
        except Exception as e:
            return (f"CSS not found: {filename}", 404)

    # Non-conflicting assets route we fully control (bypasses Flask's built-in static rule)
    @app.route("/assets/css/<path:filename>")
    def assets_css(filename: str):
        try:
            from flask import send_from_directory
            import os as __os
            _abs_css = __os.path.join(app.static_folder or '', 'css')
            return send_from_directory(_abs_css, filename, mimetype='text/css')
        except Exception:
            return ("Not found", 404)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        from flask import render_template
        import logging
        
        logging.warning(f"404 error: {request.url} from {request.remote_addr}")
        return (
            render_template(
                "error.html",
                error_code=404,
                error_title="Page Not Found",
                error_message="The page you are looking for does not exist.",
            ),
            404,
        )

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        from flask import render_template, request
        from src.app import db
        import logging
        
        logging.error(f"500 error: {error} from {request.remote_addr} at {request.url}")
        db.session.rollback()
        return (
            render_template(
                "error.html",
                error_code=500,
                error_title="Internal Server Error",
                error_message="Something went wrong on our end. Please try again later.",
            ),
            500,
        )

    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 errors."""
        from flask import render_template, request
        import logging
        
        logging.warning(f"403 error: {request.url} from {request.remote_addr}")
        return (
            render_template(
                "error.html",
                error_code=403,
                error_title="Access Forbidden",
                error_message="You do not have permission to access this resource.",
            ),
            403,
        )

    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 errors."""
        from flask import render_template, request
        import logging
        
        logging.warning(f"400 error: {request.url} from {request.remote_addr}")
        return (
            render_template(
                "error.html",
                error_code=400,
                error_title="Bad Request",
                error_message="The request could not be processed. Please check your input and try again.",
            ),
            400,
        )

    return app
