#!/usr/bin/env python3
"""
main.py
Purpose: Main Flask application entry point for AI Collab Online
Status: [ACTIVE]
Created: 2025-01-27
Author: writeian

Main application entry point with health checks and production migrations
"""

import os
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for

# Import the application factory
from src.app import create_app, db

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
    print("✓ Loaded environment variables from .env file")
except ImportError:
    print(
        "⚠️ python-dotenv not installed - environment variables may not be loaded from .env"
    )
except Exception as e:
    print(f"⚠️ Could not load .env file: {e}")


def run_production_migrations(app):
    """Run Alembic migrations in production environment."""
    if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("FLASK_ENV") == "production":
        try:
            from alembic.config import Config
            from alembic import command

            print("Running Alembic migrations...")
            alembic_cfg = Config("alembic.ini")
            # Try to run migrations, but don't fail if tables don't exist yet
            try:
                command.upgrade(alembic_cfg, "head")
                print("✅ Alembic migrations complete.")
                app.config["MIGRATION_STATUS"] = "applied"
            except Exception as e:
                print(f"⚠️ Alembic migration warning: {e}")
                print("Continuing with app startup...")
                app.config["MIGRATION_ERROR"] = str(e)
        except Exception as e:
            print(f"❌ Alembic migration failed: {e}")
            app.config["MIGRATION_ERROR"] = str(e)
            # Don't crash - let app continue
            print("Continuing with app startup...")
        
        # Ensure basic tables exist using the created app context
        try:
            print("Ensuring basic tables exist...")
            from src.app import db
            with app.app_context():
                db.create_all()
                print("✓ Basic tables ensured")
                
                # CRITICAL: Manually create chat_notes table (migration system broken)
                try:
                    from src.models import ChatNotes
                    ChatNotes.query.first()  # Test if table exists
                    print("✓ chat_notes table exists")
                except Exception:
                    print("⚠️ chat_notes table missing, creating manually...")
                    try:
                        with db.engine.connect() as conn:
                            conn.execute(db.text("""
                                CREATE TABLE IF NOT EXISTS chat_notes (
                                    id SERIAL PRIMARY KEY,
                                    chat_id INTEGER NOT NULL UNIQUE REFERENCES chat(id),
                                    room_id INTEGER NOT NULL REFERENCES room(id),
                                    notes_content TEXT NOT NULL,
                                    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                                    message_count INTEGER NOT NULL
                                )
                            """))
                            conn.execute(db.text("CREATE INDEX IF NOT EXISTS ix_chat_notes_room_id ON chat_notes(room_id)"))
                            conn.execute(db.text("CREATE INDEX IF NOT EXISTS ix_chat_notes_generated_at ON chat_notes(generated_at)"))
                            conn.commit()
                        print("✓ chat_notes table created manually")
                    except Exception as create_error:
                        print(f"❌ Failed to create chat_notes table: {create_error}")
                
                # CRITICAL: Manually create pinned_items table (migration system broken)
                try:
                    from src.models import PinnedItem
                    PinnedItem.query.first()  # Test if table exists
                    print("✓ pinned_items table exists")
                except Exception:
                    print("⚠️ pinned_items table missing, creating manually...")
                    try:
                        # Detect if PostgreSQL or SQLite
                        is_postgres = 'postgresql' in str(db.engine.url)
                        
                        with db.engine.connect() as conn:
                            if is_postgres:
                                # PostgreSQL-specific SQL (includes is_shared column)
                                conn.execute(db.text("""
                                    CREATE TABLE IF NOT EXISTS pinned_items (
                                        id SERIAL PRIMARY KEY,
                                        user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                                        room_id INTEGER NOT NULL REFERENCES room(id) ON DELETE CASCADE,
                                        chat_id INTEGER NOT NULL REFERENCES chat(id) ON DELETE CASCADE,
                                        message_id INTEGER REFERENCES message(id) ON DELETE CASCADE,
                                        comment_id INTEGER REFERENCES comment(id) ON DELETE CASCADE,
                                        role VARCHAR(20),
                                        content TEXT NOT NULL,
                                        is_shared BOOLEAN NOT NULL DEFAULT FALSE,
                                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                                        CONSTRAINT check_exactly_one_item CHECK (
                                            (message_id IS NOT NULL AND comment_id IS NULL) OR
                                            (message_id IS NULL AND comment_id IS NOT NULL)
                                        )
                                    )
                                """))
                                conn.execute(db.text("CREATE UNIQUE INDEX IF NOT EXISTS unique_user_message_pin ON pinned_items(user_id, message_id) WHERE message_id IS NOT NULL"))
                                conn.execute(db.text("CREATE UNIQUE INDEX IF NOT EXISTS unique_user_comment_pin ON pinned_items(user_id, comment_id) WHERE comment_id IS NOT NULL"))
                                conn.execute(db.text("CREATE INDEX IF NOT EXISTS ix_pinned_items_user_id ON pinned_items(user_id)"))
                                conn.execute(db.text("CREATE INDEX IF NOT EXISTS ix_pinned_items_room_id ON pinned_items(room_id)"))
                                conn.execute(db.text("CREATE INDEX IF NOT EXISTS ix_pinned_items_chat_id ON pinned_items(chat_id)"))
                                conn.execute(db.text("CREATE INDEX IF NOT EXISTS ix_pins_user_chat ON pinned_items(user_id, chat_id)"))
                                conn.execute(db.text("CREATE INDEX IF NOT EXISTS ix_pinned_items_chat_shared ON pinned_items(chat_id, is_shared)"))
                                conn.execute(db.text("CREATE INDEX IF NOT EXISTS ix_pinned_items_room_shared ON pinned_items(room_id, is_shared)"))
                            else:
                                # SQLite-compatible SQL (includes is_shared column)
                                conn.execute(db.text("""
                                    CREATE TABLE IF NOT EXISTS pinned_items (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        user_id INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
                                        room_id INTEGER NOT NULL REFERENCES room(id) ON DELETE CASCADE,
                                        chat_id INTEGER NOT NULL REFERENCES chat(id) ON DELETE CASCADE,
                                        message_id INTEGER REFERENCES message(id) ON DELETE CASCADE,
                                        comment_id INTEGER REFERENCES comment(id) ON DELETE CASCADE,
                                        role VARCHAR(20),
                                        content TEXT NOT NULL,
                                        is_shared INTEGER NOT NULL DEFAULT 0,
                                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                                        CHECK (
                                            (message_id IS NOT NULL AND comment_id IS NULL) OR
                                            (message_id IS NULL AND comment_id IS NOT NULL)
                                        )
                                    )
                                """))
                                conn.execute(db.text("CREATE UNIQUE INDEX IF NOT EXISTS unique_user_message_pin ON pinned_items(user_id, message_id)"))
                                conn.execute(db.text("CREATE UNIQUE INDEX IF NOT EXISTS unique_user_comment_pin ON pinned_items(user_id, comment_id)"))
                                conn.execute(db.text("CREATE INDEX IF NOT EXISTS ix_pinned_items_user_id ON pinned_items(user_id)"))
                                conn.execute(db.text("CREATE INDEX IF NOT EXISTS ix_pinned_items_room_id ON pinned_items(room_id)"))
                                conn.execute(db.text("CREATE INDEX IF NOT EXISTS ix_pinned_items_chat_id ON pinned_items(chat_id)"))
                                conn.execute(db.text("CREATE INDEX IF NOT EXISTS ix_pins_user_chat ON pinned_items(user_id, chat_id)"))
                                conn.execute(db.text("CREATE INDEX IF NOT EXISTS ix_pinned_items_chat_shared ON pinned_items(chat_id, is_shared)"))
                                conn.execute(db.text("CREATE INDEX IF NOT EXISTS ix_pinned_items_room_shared ON pinned_items(room_id, is_shared)"))
                            conn.commit()
                        print("✓ pinned_items table created manually")
                    except Exception as create_error:
                        print(f"❌ Failed to create pinned_items table: {create_error}")
                
                # PHASE B: Add is_shared column to pinned_items for shared pins feature
                try:
                    with db.engine.connect() as conn:
                        result = conn.execute(db.text("SELECT is_shared FROM pinned_items LIMIT 1"))
                        result.close()
                    print("✓ is_shared column exists")
                except Exception as check_error:
                    print(f"⚠️ is_shared column missing ({check_error}), adding...")
                    try:
                        is_postgres = 'postgresql' in str(db.engine.url)
                        with db.engine.connect() as conn:
                            if is_postgres:
                                conn.execute(db.text("""
                                    ALTER TABLE pinned_items 
                                    ADD COLUMN IF NOT EXISTS is_shared BOOLEAN NOT NULL DEFAULT FALSE
                                """))
                                conn.execute(db.text("""
                                    CREATE INDEX IF NOT EXISTS ix_pinned_items_chat_shared 
                                        ON pinned_items(chat_id, is_shared)
                                """))
                                conn.execute(db.text("""
                                    CREATE INDEX IF NOT EXISTS ix_pinned_items_room_shared 
                                        ON pinned_items(room_id, is_shared)
                                """))
                            else:
                                # SQLite: BOOLEAN stored as INTEGER
                                conn.execute(db.text("""
                                    ALTER TABLE pinned_items 
                                    ADD COLUMN is_shared INTEGER NOT NULL DEFAULT 0
                                """))
                                try:
                                    conn.execute(db.text("""
                                        CREATE INDEX ix_pinned_items_chat_shared 
                                            ON pinned_items(chat_id, is_shared)
                                    """))
                                    conn.execute(db.text("""
                                        CREATE INDEX ix_pinned_items_room_shared 
                                            ON pinned_items(room_id, is_shared)
                                    """))
                                except Exception:
                                    pass  # Indexes may already exist
                            conn.commit()
                        print("✓ is_shared column added")
                    except Exception as alter_error:
                        print(f"❌ Failed to add is_shared column: {alter_error}")
        except Exception as e:
            print(f"Table creation warning: {e}")
            print("Continuing with app startup...")


# Create the Flask application
print("🚀 CREATING FLASK APP WITH DEBUG LOGGING 🚀")
app = create_app()
print("🚀 FLASK APP CREATED - ADDING REQUEST LOGGING 🚀")

# Clean startup - removed excessive debug logging

# Automatically run Alembic migrations in production (e.g., on Railway)
run_production_migrations(app)


# Liveness check - Is the process alive?
@app.route("/health")
def health():
    """
    Liveness probe: Returns 200 as long as the process is running.
    Does NOT check database - use /ready for that.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }, 200


# Readiness check - Is the app ready to serve traffic?
@app.route("/ready")
def ready():
    """
    Readiness probe: Returns 200 only when database is connected and migrations applied.
    Used by load balancers to determine if traffic should be routed here.
    """
    from time import time as current_time
    
    checks = {}
    overall_status = 200
    
    # Database connection check (with timeout)
    db_start = current_time()
    try:
        # Short timeout (2s) to fail fast if DB is unreachable
        with db.engine.connect().execution_options(timeout=2.0) as conn:
            conn.execute(db.text("SELECT 1"))
        
        latency_ms = int((current_time() - db_start) * 1000)
        checks["database"] = {
            "status": "connected",
            "latency_ms": latency_ms
        }
    except Exception as e:
        checks["database"] = {
            "status": "error",
            "message": str(e)[:200]  # Truncate long error messages
        }
        overall_status = 503
    
    # Check for DB initialization errors
    if app.config.get("DB_INIT_ERROR"):
        checks["db_init"] = {
            "status": "error",
            "message": app.config["DB_INIT_ERROR"][:200]
        }
        overall_status = 503
    
    # Check for migration errors
    if app.config.get("MIGRATION_ERROR"):
        checks["migrations"] = {
            "status": "error", 
            "message": app.config["MIGRATION_ERROR"][:200]
        }
        overall_status = 503
    elif app.config.get("MIGRATION_STATUS") == "applied":
        checks["migrations"] = {"status": "applied"}
    
    return {
        "status": "ready" if overall_status == 200 else "not_ready",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.1.0"
    }, overall_status


# Test endpoint to list all routes
@app.route("/routes")
def list_routes():
    """List all registered routes for debugging."""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(
            {
                "endpoint": rule.endpoint,
                "methods": list(rule.methods),
                "rule": str(rule),
            }
        )
    return {"routes": routes}



# Debug: Check deployed code version
@app.route("/version")
def version_check():
    """Check which commit/version is deployed."""
    import subprocess
    try:
        commit = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode().strip()
    except:
        commit = 'unknown'
    
    return {
        "commit": commit,
        "has_pin_logging": True,  # This line added in commit aff3088
        "has_nested_transaction": True,  # This line added in commit acbec7a
        "timestamp": datetime.utcnow().isoformat()
    }, 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
# Force deployment Sun Sep 14 21:41:37 PDT 2025
