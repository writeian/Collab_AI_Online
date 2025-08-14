"""
Pre-built rubric templates for common learning steps.
These templates provide a foundation that users can customize for their specific needs.
"""

import json
from models import RubricCriterion, RubricLevel, RoomRubric

# Default rubric templates for common learning steps
RUBRIC_TEMPLATES = {
    "explore": {
        "name": "Explore & Evaluate Significance",
        "progression_threshold": 2.5,
        "criteria": [
            {
                "name": "Topic Identification",
                "description": "Student has identified a specific research topic",
                "weight": 1.0,
                "order": 1,
                "levels": [
                    {
                        "level": "Emerging",
                        "score": 1,
                        "description": "Broad topic area identified",
                        "examples": ["climate change", "social media effects"]
                    },
                    {
                        "level": "Developing",
                        "score": 2,
                        "description": "More specific topic with some focus",
                        "examples": ["climate change impact on agriculture", "social media and mental health"]
                    },
                    {
                        "level": "Proficient",
                        "score": 3,
                        "description": "Well-defined, researchable topic",
                        "examples": ["temperature effects on corn yields in Midwest US", "Instagram usage patterns and teen depression rates"]
                    },
                    {
                        "level": "Exemplary",
                        "score": 4,
                        "description": "Highly specific, compelling topic with clear significance",
                        "examples": ["20-year temperature trends impact on corn yields in Iowa: economic and food security implications"]
                    }
                ]
            },
            {
                "name": "Personal Connection",
                "description": "Student demonstrates personal interest and motivation",
                "weight": 0.8,
                "order": 2,
                "levels": [
                    {
                        "level": "Emerging",
                        "score": 1,
                        "description": "Shows basic interest in topic",
                        "examples": ["I think this is interesting", "I want to learn more"]
                    },
                    {
                        "level": "Developing",
                        "score": 2,
                        "description": "Demonstrates some personal motivation",
                        "examples": ["This relates to my experience", "I'm curious about this"]
                    },
                    {
                        "level": "Proficient",
                        "score": 3,
                        "description": "Clear personal connection established",
                        "examples": ["This affects my community", "I've experienced this personally"]
                    },
                    {
                        "level": "Exemplary",
                        "score": 4,
                        "description": "Strong intrinsic motivation with clear personal stakes",
                        "examples": ["This directly impacts my future career goals", "I want to help solve this problem"]
                    }
                ]
            },
            {
                "name": "Question Development",
                "description": "Student has begun formulating research questions",
                "weight": 1.2,
                "order": 3,
                "levels": [
                    {
                        "level": "Emerging",
                        "score": 1,
                        "description": "Basic questions about the topic",
                        "examples": ["What is this?", "How does this work?"]
                    },
                    {
                        "level": "Developing",
                        "score": 2,
                        "description": "More specific questions emerging",
                        "examples": ["What causes this?", "How does this affect people?"]
                    },
                    {
                        "level": "Proficient",
                        "score": 3,
                        "description": "Clear, researchable questions formulated",
                        "examples": ["What specific factors contribute to this outcome?", "How does this vary across different populations?"]
                    },
                    {
                        "level": "Exemplary",
                        "score": 4,
                        "description": "Sophisticated questions with clear research potential",
                        "examples": ["What are the causal mechanisms and how do they interact?", "What are the long-term implications and potential solutions?"]
                    }
                ]
            }
        ]
    },
    
    "focus": {
        "name": "Narrow to a Researchable Question",
        "progression_threshold": 2.5,
        "criteria": [
            {
                "name": "Question Specificity",
                "description": "Student has developed a focused, researchable question",
                "weight": 1.0,
                "order": 1,
                "levels": [
                    {
                        "level": "Emerging",
                        "score": 1,
                        "description": "Broad, general questions",
                        "examples": ["What is climate change?", "How does social media work?"]
                    },
                    {
                        "level": "Developing",
                        "score": 2,
                        "description": "More specific but still broad questions",
                        "examples": ["How does climate change affect agriculture?", "What are the effects of social media?"]
                    },
                    {
                        "level": "Proficient",
                        "score": 3,
                        "description": "Focused, researchable questions",
                        "examples": ["How do rising temperatures affect corn yields in the Midwest?", "How does Instagram usage impact teen self-esteem?"]
                    },
                    {
                        "level": "Exemplary",
                        "score": 4,
                        "description": "Highly specific, compelling research questions",
                        "examples": ["What is the relationship between temperature increases and corn yield declines in Iowa from 2000-2020?", "How does daily Instagram usage duration correlate with depression scores in 15-17 year olds?"]
                    }
                ]
            },
            {
                "name": "Research Feasibility",
                "description": "Question can be realistically researched with available resources",
                "weight": 1.0,
                "order": 2,
                "levels": [
                    {
                        "level": "Emerging",
                        "score": 1,
                        "description": "Question too broad or impossible to research",
                        "examples": ["What is the meaning of life?", "How do aliens think?"]
                    },
                    {
                        "level": "Developing",
                        "score": 2,
                        "description": "Question possible but would require extensive resources",
                        "examples": ["How does climate change affect all agriculture worldwide?", "What are all the effects of social media?"]
                    },
                    {
                        "level": "Proficient",
                        "score": 3,
                        "description": "Question researchable with reasonable effort",
                        "examples": ["How does climate change affect corn farming in the US?", "How does social media affect teen mental health?"]
                    },
                    {
                        "level": "Exemplary",
                        "score": 4,
                        "description": "Question perfectly scoped for available resources and time",
                        "examples": ["How do temperature changes affect corn yields in Iowa?", "How does Instagram usage affect depression in high school students?"]
                    }
                ]
            }
        ]
    },
    
    "context": {
        "name": "Find Authoritative Sources",
        "progression_threshold": 2.5,
        "criteria": [
            {
                "name": "Source Evaluation",
                "description": "Student can evaluate source credibility and authority",
                "weight": 1.0,
                "order": 1,
                "levels": [
                    {
                        "level": "Emerging",
                        "score": 1,
                        "description": "Uses any source without evaluation",
                        "examples": ["Wikipedia articles", "Random blog posts"]
                    },
                    {
                        "level": "Developing",
                        "score": 2,
                        "description": "Recognizes some credible sources",
                        "examples": ["News websites", "Government websites"]
                    },
                    {
                        "level": "Proficient",
                        "score": 3,
                        "description": "Evaluates author credentials and publication quality",
                        "examples": ["Peer-reviewed journals", "Expert-authored books"]
                    },
                    {
                        "level": "Exemplary",
                        "score": 4,
                        "description": "Sophisticated evaluation of bias, methodology, and relevance",
                        "examples": ["Primary research studies", "Expert analysis with clear methodology"]
                    }
                ]
            },
            {
                "name": "Source Diversity",
                "description": "Student uses a variety of appropriate source types",
                "weight": 0.8,
                "order": 2,
                "levels": [
                    {
                        "level": "Emerging",
                        "score": 1,
                        "description": "Uses only one type of source",
                        "examples": ["Only websites", "Only books"]
                    },
                    {
                        "level": "Developing",
                        "score": 2,
                        "description": "Uses 2-3 different source types",
                        "examples": ["Websites and books", "Articles and reports"]
                    },
                    {
                        "level": "Proficient",
                        "score": 3,
                        "description": "Uses multiple source types appropriately",
                        "examples": ["Academic articles, books, expert interviews", "Primary and secondary sources"]
                    },
                    {
                        "level": "Exemplary",
                        "score": 4,
                        "description": "Sophisticated use of diverse, high-quality sources",
                        "examples": ["Primary research, expert analysis, statistical data", "Multiple perspectives and methodologies"]
                    }
                ]
            }
        ]
    }
}

def create_default_rubric_for_room(room, step_key):
    """
    Create a default rubric for a specific learning step in a room.
    
    Args:
        room: Room object
        step_key: Learning step key (e.g., 'explore', 'focus', 'context')
    
    Returns:
        tuple: (room_rubric, criteria_list, levels_list) - all objects that need to be added to session
    """
    if step_key not in RUBRIC_TEMPLATES:
        return None
    
    template = RUBRIC_TEMPLATES[step_key]
    
    # Create the room rubric
    room_rubric = RoomRubric(
        room_id=room.id,
        step_key=step_key,
        progression_threshold=template["progression_threshold"]
    )
    
    criteria_list = []
    levels_list = []
    
    # Create criteria and levels
    for criterion_data in template["criteria"]:
        criterion = RubricCriterion(
            room_id=room.id,
            step_key=step_key,
            name=criterion_data["name"],
            description=criterion_data["description"],
            weight=criterion_data["weight"],
            order=criterion_data["order"]
        )
        criteria_list.append(criterion)
        
        # Create levels for this criterion
        for level_data in criterion_data["levels"]:
            level = RubricLevel(
                level=level_data["level"],
                score=level_data["score"],
                description=level_data["description"],
                examples=json.dumps(level_data["examples"])
            )
            criterion.levels.append(level)
            levels_list.append(level)
    
    return (room_rubric, criteria_list, levels_list)

def get_rubric_template(step_key):
    """
    Get the rubric template for a specific learning step.
    
    Args:
        step_key: Learning step key
    
    Returns:
        Template dictionary or None if not found
    """
    return RUBRIC_TEMPLATES.get(step_key)

def get_available_rubric_steps():
    """
    Get list of learning steps that have rubric templates.
    
    Returns:
        List of step keys
    """
    return list(RUBRIC_TEMPLATES.keys()) 