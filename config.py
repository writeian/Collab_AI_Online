import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI Service settings
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    USE_OLLAMA = os.getenv('USE_OLLAMA', 'false').lower() == 'true'
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'gemma3')
    
    # Google Docs settings
    GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'service-account-key.json')
    
    # Production settings
    DEBUG = False
    TESTING = False
    
    # Security settings
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Logging
    LOG_LEVEL = 'INFO'
    
    @staticmethod
    def init_app(app):
        """Initialize application-specific settings."""
        pass

class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    # SQLite for development
    SQLALCHEMY_DATABASE_URI = 'sqlite:///ai_collab.db'
    
    # Development-specific settings
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Production configuration."""
    
    # PostgreSQL for production
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    # Production security settings
    SESSION_COOKIE_SECURE = False  # Set to False for HTTP, True for HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'  # Changed from 'Strict' to 'Lax' for better compatibility
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    @classmethod
    def init_app(cls, app):
        """Initialize production-specific settings."""
        Config.init_app(app)
        
        # Production logging setup
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            # File logging
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/ai_collab.log', maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('AI Collab Online startup')

class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = True
    
    # In-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 