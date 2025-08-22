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


def run_production_migrations():
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


# Automatically run Alembic migrations in production (e.g., on Railway)
run_production_migrations()

# Create the Flask application
app = create_app()


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
