"""
Template route handlers.
Handles template-related operations for room creation.
"""

from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from typing import Any, Dict, List
from src.app import db
from src.models import Room, User
from ..services.room_service import RoomService
from ..types import RoomCreationData
from ..utils.room_utils import get_invitation_count
from src.app.access_control import get_current_user, require_login
from src.utils.openai_utils import get_available_templates, generate_room_modes
from src.app.goals import generate_template_goals, get_supported_templates

templates_bp = Blueprint('room_templates', __name__)

@templates_bp.route("/<template_type>")
@require_login
def template_wizard(template_type: str) -> Any:
    """Display template wizard for the specified template type."""
    try:
        # Validate template type
        valid_templates = [
            "study-group", "business-hub", "creative-studio", 
            "writing-workshop", "learning-lab", "community-space", "academic-essay"
        ]
        
        if template_type not in valid_templates:
            flash("Invalid template type.", "error")
            return redirect(url_for("room.room_crud.index"))
        
        user = get_current_user()
        
        return render_template(
            f"room/templates/{template_type}.html",
            template_type=template_type,
            user=user,
            invitation_count=get_invitation_count(user)
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in template wizard: {e}")
        flash("Failed to load template wizard. Please try again.", "error")
        return redirect(url_for("room.room_crud.create_room"))

@templates_bp.route("/load/<template_type>")
@require_login
def load_template(template_type: str) -> Any:
    """Load a specific template configuration."""
    try:
        user = get_current_user()
        
        # Validate template type
        supported_templates = get_supported_templates()
        if template_type not in supported_templates:
            return jsonify({"error": "Invalid template type"}), 400
        
        # Generate template goals
        template_goals = generate_template_goals(template_type, {})
        
        # Get template-specific modes
        try:
            # Create a temporary room-like object for mode generation
            temp_room = type('obj', (object,), {
                'id': 0,
                'name': f'{template_type.replace("-", " ").title()} Room',
                'goals': '\n'.join(template_goals.get('core_goals', [])),
                'description': f'A {template_type.replace("-", " ")} room'
            })
            
            modes = generate_room_modes(temp_room, template_name=template_type)
            
        except Exception as mode_error:
            current_app.logger.warning(f"Mode generation failed for template {template_type}: {mode_error}")
            modes = {}
        
        return jsonify({
            "success": True,
            "template": {
                "type": template_type,
                "name": template_type.replace("-", " ").title(),
                "goals": template_goals,
                "modes": [
                    {
                        "key": key,
                        "label": mode.label,
                        "prompt": mode.prompt
                    }
                    for key, mode in modes.items()
                ] if modes else []
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error loading template {template_type}: {e}")
        return jsonify({"error": "Failed to load template"}), 500

@templates_bp.route("/<template_type>/generate-goals", methods=["POST"])
@require_login
def generate_template_goals(template_type: str) -> Any:
    """Generate learning goals based on template wizard answers."""
    try:
        # Validate request data
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        answers = data.get("answers", {})
        if not isinstance(answers, dict):
            return jsonify({"error": "Answers must be a dictionary"}), 400
        
        # Generate goals with proper error handling
        try:
            # Use new categorized goals for all supported templates
            supported_templates = ["study-group", "business-hub", "creative-studio", "writing-workshop", "learning-lab", "community-space", "academic-essay"]
            
            if template_type in supported_templates:
                from src.app.goals import generate_categorized_goals
                goals = generate_categorized_goals(template_type, answers)
                if not goals or not isinstance(goals, dict):
                    raise ValueError("Categorized goal generation returned invalid result")
            else:
                # For unsupported templates, return empty categorized goals
                current_app.logger.warning(f"Unsupported template type requested: {template_type}")
                goals = {
                    "core_goals": [],
                    "collaboration_goals": [],
                    "reflection_goals": []
                }
            
            return jsonify({
                "success": True, 
                "goals": goals,
                "template_type": template_type
            })
            
        except ValueError as ve:
            current_app.logger.error(f"Validation error in goal generation: {ve}")
            return jsonify({"error": "Invalid input data provided"}), 400
        except Exception as ge:
            current_app.logger.error(f"Goal generation error: {ge}")
            return jsonify({"error": "Failed to generate goals"}), 500
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error in generate_template_goals: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@templates_bp.route("/<template_type>/create-room", methods=["POST"])
@require_login
def create_template_room(template_type: str) -> Any:
    """Create a room from template wizard data."""
    try:
        # Validate request data
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract and validate required fields
        goals = data.get("goals", "").strip()
        room_name = data.get("room_name", "").strip()
        room_description = data.get("room_description", "").strip()
        group_size = data.get("group_size", "").strip()
        
        # Validate required fields
        if not room_name:
            return jsonify({"error": "Room name is required"}), 400
        
        if len(room_name) > 100:
            return jsonify({"error": "Room name must be 100 characters or less"}), 400
        
        if len(room_description) > 500:
            return jsonify({"error": "Room description must be 500 characters or less"}), 400
        
        # Validate group size
        valid_group_sizes = ["small", "medium", "large", "individual"]
        if group_size and group_size not in valid_group_sizes:
            return jsonify({"error": "Invalid group size"}), 400
        
        user = get_current_user()
        
        # Generate unique room name to avoid conflicts
        from src.utils.room_descriptions import generate_unique_room_name, generate_room_short_description
        unique_room_name = generate_unique_room_name(room_name, user.id)
        
        # Generate short description for template rooms
        short_description = generate_room_short_description(
            template_type=template_type,
            room_name=room_name,
            group_size=group_size,
            goals=goals
        )
        
        # Create the room
        from src.models import Room, CustomPrompt
        room = Room(
            name=unique_room_name,
            description=room_description,
            short_description=short_description,
            goals=goals,
            group_size=group_size,
            owner_id=user.id,
            is_active=True
        )
        db.session.add(room)
        db.session.flush()  # Get the room ID
        
        # Generate modes based on goals
        try:
            from src.utils.openai_utils import generate_room_modes
            modes = generate_room_modes(room, template_name=template_type)
            
            # Save generated modes as custom prompts
            if modes:
                for mode_key, mode_info in modes.items():
                    custom_prompt = CustomPrompt(
                        mode_key=mode_key,
                        label=mode_info.label,
                        prompt=mode_info.prompt,
                        room_id=room.id,
                        created_by=user.id,
                    )
                    db.session.add(custom_prompt)
            
        except Exception as mode_error:
            current_app.logger.warning(f"Mode generation failed for room {room.id}: {mode_error}")
            # Continue without modes - room will still be created
        
        db.session.commit()
        
        current_app.logger.info(f"Template room created successfully: {room.name} (ID: {room.id}) by user {user.id}")
        
        return jsonify({
            "success": True, 
            "room_id": room.id,
            "room_name": room.name,
            "original_name": room_name,
            "redirect_url": url_for("room.room_crud.view_room", room_id=room.id)
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating template room: {e}")
        return jsonify({"error": "Failed to create room. Please try again."}), 500

@templates_bp.route("/preview/<template_type>")
@require_login
def preview_template(template_type: str) -> Any:
    """Preview a template with its goals and structure."""
    try:
        user = get_current_user()
        
        # Validate template type
        supported_templates = get_supported_templates()
        if template_type not in supported_templates:
            flash("Invalid template type.", "error")
            return redirect(url_for('room.room_templates.template_wizard'))
        
        # Generate template goals
        template_goals = generate_template_goals(template_type, {})
        
        # Get template info
        template_info = supported_templates.get(template_type, {})
        
        return render_template(
            "room/templates/preview.html",
            template_type=template_type,
            template_info=template_info,
            template_goals=template_goals,
            user=user,
            invitation_count=get_invitation_count(user)
        )
        
    except Exception as e:
        current_app.logger.error(f"Error previewing template {template_type}: {e}")
        flash("Failed to preview template. Please try again.", "error")
        return redirect(url_for('room.room_templates.template_wizard'))

@templates_bp.route("/list")
@require_login
def list_templates() -> Any:
    """List all available templates."""
    try:
        user = get_current_user()
        
        # Get available templates
        available_templates = get_available_templates()
        supported_templates = get_supported_templates()
        
        return jsonify({
            "success": True,
            "templates": {
                "available": available_templates,
                "supported": supported_templates
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error listing templates: {e}")
        return jsonify({"error": "Failed to list templates"}), 500

@templates_bp.route("/goals/<template_type>")
@require_login
def get_template_goals(template_type: str) -> Any:
    """Get goals for a specific template type."""
    try:
        # Validate template type
        supported_templates = get_supported_templates()
        if template_type not in supported_templates:
            return jsonify({"error": "Invalid template type"}), 400
        
        # Get additional parameters
        answers = {}
        for key in ['subject', 'group_size', 'essay_type', 'business_type', 
                   'creative_medium', 'writing_type', 'learning_style', 
                   'community_type', 'skill_level']:
            value = request.args.get(key)
            if value:
                answers[key] = value
        
        # Generate goals
        template_goals = generate_template_goals(template_type, answers)
        
        return jsonify({
            "success": True,
            "goals": template_goals
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting template goals for {template_type}: {e}")
        return jsonify({"error": "Failed to get template goals"}), 500
