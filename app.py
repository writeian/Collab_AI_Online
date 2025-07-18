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


def create_app(config_name=None):
    app = Flask(__name__)
    
    # Get configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        db.create_all()

    # Register Blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(room, url_prefix='/room')
    app.register_blueprint(chat, url_prefix='/chat')
    app.register_blueprint(dashboard, url_prefix='/dashboard')
    app.register_blueprint(google_auth, url_prefix='/auth/google')
    
    # Health check endpoint for Railway
    @app.route('/health')
    def health():
        try:
            # Test basic app functionality
            from models import db
            db.engine.execute('SELECT 1')  # Test database connection
            return {'status': 'healthy', 'database': 'connected'}, 200
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}, 500
    
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

    # Context processor to make current user available to all templates
    @app.context_processor
    def inject_user():
        from access_control import get_current_user
        return dict(user=get_current_user())

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
