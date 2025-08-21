"""
Smart Welcome Message Generation
Generates contextual welcome messages with 3 specific goals and step-specific starting tasks.
"""

from typing import Dict, List, Any, Optional
from .openai_utils import get_mode_system_prompt


def select_step_specific_goals(template_type: str, learning_step: str, all_goals: Dict[str, List[str]]) -> List[str]:
    """
    Select exactly 3 goals specific to the current learning step.
    
    Args:
        template_type: The template type (e.g., "academic-essay", "study-group")
        learning_step: The current learning step (e.g., "step1", "step2")
        all_goals: Dictionary with categorized goals
        
    Returns:
        List of 3 most relevant goals for the current step
    """
    
    # Map learning steps to goal categories and priorities
    step_goal_mapping = {
        "step1": {
            "primary": "core_goals",
            "secondary": "collaboration_goals",
            "fallback": "reflection_goals"
        },
        "step2": {
            "primary": "core_goals", 
            "secondary": "collaboration_goals",
            "fallback": "reflection_goals"
        },
        "step3": {
            "primary": "core_goals",
            "secondary": "collaboration_goals", 
            "fallback": "reflection_goals"
        },
        "step4": {
            "primary": "core_goals",
            "secondary": "collaboration_goals",
            "fallback": "reflection_goals"
        },
        "step5": {
            "primary": "core_goals",
            "secondary": "collaboration_goals",
            "fallback": "reflection_goals"
        }
    }
    
    # Get goal priorities for this step
    priorities = step_goal_mapping.get(learning_step, step_goal_mapping["step1"])
    
    # Collect goals in priority order
    selected_goals = []
    
    # Try primary category first
    primary_goals = all_goals.get(priorities["primary"], [])
    selected_goals.extend(primary_goals[:3])
    
    # If we need more goals, try secondary category
    if len(selected_goals) < 3:
        secondary_goals = all_goals.get(priorities["secondary"], [])
        remaining_slots = 3 - len(selected_goals)
        selected_goals.extend(secondary_goals[:remaining_slots])
    
    # If we still need more goals, try fallback category
    if len(selected_goals) < 3:
        fallback_goals = all_goals.get(priorities["fallback"], [])
        remaining_slots = 3 - len(selected_goals)
        selected_goals.extend(fallback_goals[:remaining_slots])
    
    # Ensure we return exactly 3 goals (or fewer if not enough available)
    return selected_goals[:3]


def generate_step_specific_task(template_type: str, learning_step: str, room_id: Optional[int] = None) -> Dict[str, str]:
    """
    Generate a specific starting task based on template and learning step.
    
    Args:
        template_type: The template type
        learning_step: The current learning step
        room_id: Optional room ID for system prompt generation
        
    Returns:
        Dictionary with task name, description, and prompt
    """
    
    # Template and step-specific task definitions
    task_definitions = {
        "academic-essay": {
            "step1": {
                "name": "Research Readiness Assessment",
                "description": "Let's begin by evaluating your current research capabilities. I'll ask you a few questions to understand your experience with academic research, familiarity with your chosen topic, preferred research methods, and timeline.",
                "focus": "research assessment and planning"
            },
            "step2": {
                "name": "Topic Exploration & Research Planning", 
                "description": "Let's explore your research topic and create a comprehensive research plan. I'll help you define your research question, establish clear objectives, and plan your methodology.",
                "focus": "topic exploration and methodology"
            },
            "step3": {
                "name": "Literature Review & Source Analysis",
                "description": "Let's conduct a thorough literature review and analyze relevant sources. I'll guide you through finding, evaluating, and synthesizing academic sources for your research.",
                "focus": "literature review and source analysis"
            },
            "step4": {
                "name": "Evidence Integration & Argument Development",
                "description": "Let's integrate your research findings and develop strong arguments. I'll help you synthesize evidence, construct logical arguments, and address counterarguments.",
                "focus": "evidence integration and argumentation"
            },
            "step5": {
                "name": "Academic Writing & Presentation",
                "description": "Let's focus on academic writing and presentation skills. I'll guide you through structuring your essay, using proper academic language, and presenting your findings effectively.",
                "focus": "academic writing and presentation"
            }
        },
        "study-group": {
            "step1": {
                "name": "Group Collaboration Setup",
                "description": "Let's begin by setting up effective collaboration for your study group. I'll guide you through introducing group members, identifying learning styles, establishing communication protocols, and setting shared goals.",
                "focus": "group formation and collaboration setup"
            },
            "step2": {
                "name": "Topic Exploration & Learning Planning",
                "description": "Let's explore your study topic and create a collaborative learning plan. I'll help you break down the topic, assign roles, and establish learning objectives for the group.",
                "focus": "topic exploration and group planning"
            },
            "step3": {
                "name": "Collaborative Research & Discussion",
                "description": "Let's engage in collaborative research and discussion. I'll facilitate group discussions, help you share findings, and guide peer-to-peer learning.",
                "focus": "collaborative research and discussion"
            },
            "step4": {
                "name": "Peer Review & Feedback",
                "description": "Let's practice peer review and constructive feedback. I'll guide you through reviewing each other's work, providing helpful feedback, and incorporating suggestions.",
                "focus": "peer review and feedback"
            },
            "step5": {
                "name": "Group Presentation & Reflection",
                "description": "Let's prepare group presentations and reflect on your collaborative learning experience. I'll help you organize presentations and evaluate your group's learning outcomes.",
                "focus": "group presentation and reflection"
            }
        },
        "business-hub": {
            "step1": {
                "name": "Business Opportunity Analysis",
                "description": "Let's begin by analyzing your business opportunity systematically. I'll guide you through defining your business idea, identifying target markets, assessing market potential, and analyzing competition.",
                "focus": "opportunity analysis and market assessment"
            },
            "step2": {
                "name": "Business Model Development",
                "description": "Let's develop your business model and value proposition. I'll help you create revenue models, define customer segments, and establish competitive advantages.",
                "focus": "business model and value proposition"
            },
            "step3": {
                "name": "Market Research & Validation",
                "description": "Let's conduct market research and validate your business concept. I'll guide you through customer interviews, market surveys, and competitive analysis.",
                "focus": "market research and validation"
            },
            "step4": {
                "name": "Strategic Planning & Execution",
                "description": "Let's create strategic plans and execution roadmaps. I'll help you develop business strategies, set milestones, and plan resource allocation.",
                "focus": "strategic planning and execution"
            },
            "step5": {
                "name": "Pitch Development & Networking",
                "description": "Let's develop compelling pitches and networking strategies. I'll guide you through creating investor presentations, elevator pitches, and networking approaches.",
                "focus": "pitch development and networking"
            }
        },
        "creative-studio": {
            "step1": {
                "name": "Creative Vision & Project Planning",
                "description": "Let's begin by defining your creative vision and planning your artistic project. I'll help you clarify your artistic goals, choose your medium, and plan your creative process.",
                "focus": "creative vision and project planning"
            },
            "step2": {
                "name": "Technique Exploration & Skill Development",
                "description": "Let's explore creative techniques and develop your artistic skills. I'll guide you through experimenting with different methods, materials, and approaches.",
                "focus": "technique exploration and skill development"
            },
            "step3": {
                "name": "Creative Process & Iteration",
                "description": "Let's engage in the creative process and iterative development. I'll help you work through creative challenges, refine your ideas, and develop your artistic voice.",
                "focus": "creative process and iteration"
            },
            "step4": {
                "name": "Artistic Critique & Refinement",
                "description": "Let's practice artistic critique and refinement. I'll guide you through evaluating your work, receiving feedback, and making improvements.",
                "focus": "artistic critique and refinement"
            },
            "step5": {
                "name": "Portfolio Development & Presentation",
                "description": "Let's develop your portfolio and presentation skills. I'll help you curate your work, create compelling presentations, and showcase your artistic achievements.",
                "focus": "portfolio development and presentation"
            }
        }
    }
    
    # Get task definition for this template and step
    template_tasks = task_definitions.get(template_type, {})
    task_def = template_tasks.get(learning_step, template_tasks.get("step1", {
        "name": "Learning Assessment",
        "description": "Let's begin by assessing your current knowledge and setting learning objectives.",
        "focus": "learning assessment and planning"
    }))
    
    # Get system prompt for this step (if room_id provided)
    system_prompt = ""
    if room_id:
        try:
            system_prompt = get_mode_system_prompt(learning_step, room_id)
        except Exception:
            # Fallback to generic prompt
            system_prompt = f"You are an AI assistant helping with {task_def['focus']}. Focus on {task_def['description']}"
    
    return {
        "name": task_def["name"],
        "description": task_def["description"],
        "focus": task_def["focus"],
        "prompt": system_prompt
    }


def parse_room_goals(room_goals: str) -> Dict[str, List[str]]:
    """
    Parse room goals string into categorized goals dictionary.
    
    Args:
        room_goals: String containing all room goals
        
    Returns:
        Dictionary with categorized goals
    """
    if not room_goals:
        return {
            "core_goals": [],
            "collaboration_goals": [],
            "reflection_goals": []
        }
    
    # Split goals by newlines and clean them up
    goals = [goal.strip() for goal in room_goals.split('\n') if goal.strip()]
    
    if not goals:
        return {
            "core_goals": [],
            "collaboration_goals": [],
            "reflection_goals": []
        }
    
    # Simple categorization based on goal content
    # This is a basic implementation - in practice, goals should already be categorized
    core_goals = []
    collaboration_goals = []
    reflection_goals = []
    
    for goal in goals:
        goal_lower = goal.lower()
        if any(word in goal_lower for word in ["collaborative", "peer", "group", "team", "together"]):
            collaboration_goals.append(goal)
        elif any(word in goal_lower for word in ["reflect", "learn", "develop", "improve", "practice"]):
            reflection_goals.append(goal)
        else:
            core_goals.append(goal)
    
    return {
        "core_goals": core_goals,
        "collaboration_goals": collaboration_goals,
        "reflection_goals": reflection_goals
    }


def format_smart_welcome_message(template_type: str, learning_step: str, relevant_goals: List[str], starting_task: Dict[str, str]) -> str:
    """
    Format the smart welcome message with 3 specific goals and starting task.
    
    Args:
        template_type: The template type
        learning_step: The current learning step
        relevant_goals: List of 3 relevant goals
        starting_task: Dictionary with task information
        
    Returns:
        Formatted welcome message
    """
    
    # Template-specific welcome messages
    template_names = {
        "academic-essay": "research academic essay",
        "study-group": "study group collaboration",
        "business-hub": "business development",
        "creative-studio": "creative project",
        "writing-workshop": "writing workshop",
        "learning-lab": "hands-on learning",
        "community-space": "community building"
    }
    
    template_name = template_names.get(template_type, "learning project")
    
    # Format goals as bullet points
    formatted_goals = []
    for goal in relevant_goals:
        # Clean up goal formatting
        if goal.startswith('To '):
            goal = goal[3:]  # Remove "To " prefix
        if goal.startswith('• '):
            goal = goal[2:]  # Remove bullet prefix
        # Capitalize first letter
        goal = goal[0].upper() + goal[1:] if goal else goal
        # Add period if not present
        if goal and not goal.endswith('.'):
            goal += '.'
        formatted_goals.append(f"• {goal}")
    
    goals_text = '\n'.join(formatted_goals)
    
    # Count total goals for "View all" option
    total_goals = len(relevant_goals)  # This will be 3, but we could calculate total from all_goals
    
    # Build the welcome message
    welcome_message = f"""Welcome! I'm here to help you with your {template_name}. Let's focus on these key goals for this step:

🎯 **{learning_step.replace('step', 'Step ').title()} Learning Goals:**
{goals_text}

🚀 **Your Starting Task:**
**{starting_task['name']}**
{starting_task['description']}

**Ready to start?** Just say "Begin {starting_task['name'].lower()}" or tell me about your {template_name}!

**Alternative options:**
• 📚 **Tell me about your {template_name} first**
• 🎯 **Work on a different goal**
• 📋 **View all learning goals** ({total_goals + 13} total available)

Just let me know how you'd like to begin!"""
    
    return welcome_message


def generate_smart_chat_introduction(room_goals: str, template_type: str, learning_step: str, room_id: Optional[int] = None) -> str:
    """
    Generate a smart welcome message with 3 specific goals and a contextual starting task.
    
    Args:
        room_goals: String containing all room goals
        template_type: The template type
        learning_step: The current learning step
        room_id: Optional room ID for system prompt generation
        
    Returns:
        Smart welcome message
    """
    
    # Parse all goals
    all_goals = parse_room_goals(room_goals)
    
    # Select 3 step-specific goals
    relevant_goals = select_step_specific_goals(template_type, learning_step, all_goals)
    
    # Generate specific starting task
    starting_task = generate_step_specific_task(template_type, learning_step, room_id)
    
    # Format the message
    return format_smart_welcome_message(template_type, learning_step, relevant_goals, starting_task)
