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
                print("Alembic migrations complete.")
            except Exception as e:
                print(f"Alembic migration warning: {e}")
                print("Continuing with app startup...")
        except Exception as e:
            print("Alembic migration failed:", e)
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
                        db.engine.execute("""
                            CREATE TABLE IF NOT EXISTS chat_notes (
                                id SERIAL PRIMARY KEY,
                                chat_id INTEGER NOT NULL UNIQUE REFERENCES chat(id),
                                room_id INTEGER NOT NULL REFERENCES room(id),
                                notes_content TEXT NOT NULL,
                                generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                                message_count INTEGER NOT NULL
                            );
                            CREATE INDEX IF NOT EXISTS ix_chat_notes_room_id ON chat_notes(room_id);
                            CREATE INDEX IF NOT EXISTS ix_chat_notes_generated_at ON chat_notes(generated_at);
                        """)
                        print("✓ chat_notes table created manually")
                    except Exception as create_error:
                        print(f"❌ Failed to create chat_notes table: {create_error}")
        except Exception as e:
            print(f"Table creation warning: {e}")
            print("Continuing with app startup...")


# Create the Flask application
print("🚀 CREATING FLASK APP WITH DEBUG LOGGING 🚀")
app = create_app()
print("🚀 FLASK APP CREATED - ADDING REQUEST LOGGING 🚀")

# Add logging to ALL requests to track what's happening
@app.before_request
def log_all_requests():
    from flask import request, current_app
    print(f"🌐🌐🌐 BEFORE_REQUEST: {request.method} {request.path} 🌐🌐🌐")
    current_app.logger.error(f"🌐🌐🌐 REQUEST: {request.method} {request.path} from {request.remote_addr} 🌐🌐🌐")
    if '/room/' in request.path:
        current_app.logger.error(f"🎯 ROOM REQUEST DETECTED: {request.path} 🎯")

@app.after_request  
def log_after_request(response):
    from flask import request, current_app, g
    if '/room/' in request.path:
        # Try to get the endpoint that handled this request
        endpoint = getattr(g, 'matched_endpoint', 'unknown')
        current_app.logger.error(f"🏁 RESPONSE: {request.path} → {response.status_code} (endpoint: {endpoint}) 🏁")
    return response

# Add endpoint logging
@app.url_value_preprocessor
def log_endpoint(endpoint, values):
    from flask import current_app, request, g
    g.matched_endpoint = endpoint
    if '/room/' in request.path:
        current_app.logger.error(f"🎯 ENDPOINT MATCHED: {request.path} → {endpoint} 🎯")

print("🚀 REQUEST LOGGING CONFIGURED 🚀")

# Test that our logging works
try:
    app.logger.error("🧪 TESTING APP LOGGER - THIS SHOULD APPEAR IN LOGS 🧪")
    print("🧪 LOGGER TEST EXECUTED 🧪")
except Exception as e:
    print(f"🚨 LOGGER TEST FAILED: {e}")

# List ALL registered routes to see what's handling room requests
print("🗺️ LISTING ALL FLASK ROUTES:")
for rule in app.url_map.iter_rules():
    if 'room' in rule.rule.lower():
        print(f"🗺️ ROUTE: {rule.rule} → {rule.endpoint} (methods: {rule.methods})")
print("🗺️ END ROUTE LIST")

# Automatically run Alembic migrations in production (e.g., on Railway)
run_production_migrations(app)


# Health check endpoint for Railway
@app.route("/health")
def health():
    """Health check endpoint for monitoring and deployment verification."""
    try:
        # Test database connection
        if app.config.get("SQLALCHEMY_DATABASE_URI"):
            with app.app_context():
                with db.engine.connect() as conn:
                    conn.execute(db.text("SELECT 1"))
            return {
                "status": "healthy",
                "message": "App is running - PHASE 3 RESTRUCTURING COMPLETE",
                "database": "connected",
                "version": "3.0.0",
                "deployment_test": "PHASE 3 SUCCESSFUL",
                "timestamp": "2025-01-27 15:00",
                "commit": "phase3-complete",
            }, 200
        else:
            return {
                "status": "healthy",
                "message": "App is running",
                "database": "not configured",
            }, 200
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": "error",
            "timestamp": datetime.now(datetime.UTC).isoformat(),
        }, 500


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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
# Force deployment Sun Sep 14 21:41:37 PDT 2025
