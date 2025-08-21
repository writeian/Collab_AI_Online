"""
Room blueprint initialization.
Registers all room-related routes and services.
"""

from flask import Blueprint

# Create main blueprint
room = Blueprint("room", __name__)

# Import route blueprints to ensure they're registered
from .routes import crud, templates, invitations, api

# Register route blueprints
room.register_blueprint(crud.crud_bp, url_prefix="")
room.register_blueprint(templates.templates_bp, url_prefix="/template")
room.register_blueprint(invitations.invitations_bp, url_prefix="/<int:room_id>")
room.register_blueprint(api.api_bp, url_prefix="/api")

# Import all routes to ensure they're registered
from .routes import crud, templates, invitations, api

# Export the main blueprint
__all__ = ['room']
