#!/usr/bin/env python3
"""
settings.py
Purpose: Application configuration management
Status: [ACTIVE]
Created: 2025-01-27
Author: writeian

Environment-specific configuration settings and database connection management
"""

import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

# Insecure development-only fallback. Fine for local dev; PRODUCTION MUST NOT use
# this — ProductionConfig.init_app() fails fast if SECRET_KEY resolves to this.
DEV_FALLBACK_SECRET_KEY = "dev-secret-key-change-in-production"


class Config:
    """Base configuration class"""

    SECRET_KEY = os.environ.get("SECRET_KEY") or DEV_FALLBACK_SECRET_KEY
    # SQLite fallback: use project instance folder (works on Mac/Linux/Windows)
    _config_dir = os.path.dirname(os.path.abspath(__file__))
    _project_root = os.path.abspath(os.path.join(_config_dir, "..", ".."))
    _instance_dir = os.path.join(_project_root, "instance")
    _sqlite_path = os.path.join(_instance_dir, "ai_collab.db")
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or f"sqlite:///{_sqlite_path}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database connection pooling for better performance (PostgreSQL only)
    if os.environ.get("DATABASE_URL") and "postgresql" in os.environ.get("DATABASE_URL", ""):
        # Per-process pool (each Gunicorn worker has its own engine). With gthread, many
        # concurrent requests share this pool. Total worst-case connections ≈
        # GUNICORN_WORKERS * (DB_POOL_SIZE + DB_POOL_MAX_OVERFLOW)—keep under Postgres max_connections.
        _pool = int(os.environ.get("DB_POOL_SIZE", "10"))
        _overflow = int(os.environ.get("DB_POOL_MAX_OVERFLOW", "12"))
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': _pool,
            'pool_recycle': 300,
            'pool_pre_ping': True,
            'max_overflow': _overflow,
        }
    else:
        # SQLite configuration (no pooling needed)
        SQLALCHEMY_ENGINE_OPTIONS = {}

    # Static asset configuration for production
    STATIC_FOLDER = "static"
    STATIC_URL_PATH = "/static"

    # Cache configuration for mobile assets
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year for static assets

    # Caching configuration
    CACHE_TYPE = "simple"  # Use Redis in production
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = "ai_collab_"
    
    # Session caching
    SESSION_TYPE = "filesystem"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Mobile-specific settings
    MOBILE_CACHE_VERSION = "2.0"  # Version for cache busting
    MOBILE_FEATURES_ENABLED = True

    # Production-specific settings
    PRODUCTION_MODE = os.environ.get("FLASK_ENV") == "production"

    # Asset compression settings
    COMPRESS_HTML = True
    COMPRESS_CSS = True
    COMPRESS_JS = True

    # AI Service settings
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() == "true"
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3")

    # Rate limiting settings
    REDIS_URL = os.getenv("REDIS_URL")

    # Feature flags
    REFINE_V2_ENABLED = os.getenv("REFINE_V2_ENABLED", "false").lower() == "true"

    # Trial mode (scaffold)
    TRIAL_ENABLED = os.getenv("TRIAL_ENABLED", "false").lower() == "true"
    TRIAL_TTL_DAYS = int(os.getenv("TRIAL_TTL_DAYS", "7") or 7)
    TRIAL_MAX_REFINES = int(os.getenv("TRIAL_MAX_REFINES", "3") or 3)

    # Room limits
    ROOM_MAX_CHATS = int(os.getenv("ROOM_MAX_CHATS", "25") or 25)

    # Google Docs settings
    GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv(
        "GOOGLE_SERVICE_ACCOUNT_FILE", "service-account-key.json"
    )

    # Production settings
    DEBUG = False
    TESTING = False

    # Security settings
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    
    # Logging
    LOG_LEVEL = "INFO"
    
    # Enhanced logging configuration
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
            'file': {
                'level': 'INFO',
                'formatter': 'detailed',
                'class': 'logging.FileHandler',
                'filename': 'logs/ai_collab.log',
                'mode': 'a',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default', 'file'],
                'level': 'INFO',
                'propagate': True
            },
            'src': {
                'handlers': ['default', 'file'],
                'level': 'INFO',
                'propagate': False,
            },
        }
    }

    @staticmethod
    def init_app(app):
        """Initialize application-specific settings."""
        pass


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    TESTING = False

    # Development-specific mobile settings
    MOBILE_CACHE_VERSION = "dev"
    MOBILE_FEATURES_ENABLED = True


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    TESTING = False

    # Production-specific mobile settings
    MOBILE_CACHE_VERSION = "2.0"
    MOBILE_FEATURES_ENABLED = True

    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Static asset optimization
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year

    # Production logging
    LOG_LEVEL = "WARNING"

    @classmethod
    def init_app(cls, app):
        """Initialize production-specific settings."""
        Config.init_app(app)

        # Fail fast: never run production with a missing or default SECRET_KEY.
        # A known/absent key means sessions are signed with a value that is public
        # in the repo -> forgeable sessions / auth bypass.
        secret_key = (app.config.get("SECRET_KEY") or "").strip()
        if not secret_key or secret_key == DEV_FALLBACK_SECRET_KEY:
            raise RuntimeError(
                "SECRET_KEY is not set (or is the insecure default) in production. "
                "Set a strong, unique SECRET_KEY environment variable before starting. "
                'Generate one with: python -c "import secrets; print(secrets.token_hex(32))"'
            )

        # Production logging setup
        import logging
        from logging.handlers import RotatingFileHandler

        if not app.debug and not app.testing:
            # File logging
            if not os.path.exists("logs"):
                os.makedirs("logs", exist_ok=True)
            file_handler = RotatingFileHandler(
                "logs/ai_collab.log", maxBytes=10240, backupCount=10
            )
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
                )
            )
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

            app.logger.setLevel(logging.INFO)
            app.logger.info("AI Collab Online startup")


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    # Disable mobile features for testing
    MOBILE_FEATURES_ENABLED = False


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
