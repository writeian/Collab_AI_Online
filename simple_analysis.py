#!/usr/bin/env python3
"""
Simple Inventory Analysis
Purpose: Analyze script categories and dependencies from inventory
Status: [ACTIVE]
Created: 2025-01-27
Author: writeian

Usage:
    python simple_analysis.py
"""

import os
import json
from collections import defaultdict, Counter
from pathlib import Path

def analyze_scripts():
    """Analyze scripts directly from the file system"""
    print("🚀 Starting Simple Inventory Analysis...")
    
    scripts = []
    categories = defaultdict(list)
    dependencies = Counter()
    
    # Scan for Python scripts
    for root, dirs, files in os.walk("."):
        # Skip common directories
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', 'venv', 'env'}]
        
        for file in files:
            if file.endswith('.py'):
                script_path = Path(root) / file
                script_info = analyze_script(script_path)
                if script_info:
                    scripts.append(script_info)
                    categories[script_info['category']].append(script_info)
    
    print(f"✅ Found {len(scripts)} Python scripts")
    
    # Generate analysis
    analysis = {
        "total_scripts": len(scripts),
        "categories": {},
        "consolidation_opportunities": [],
        "archive_candidates": [],
        "reorganization_plan": {}
    }
    
    # Analyze categories
    for category, category_scripts in categories.items():
        total_size = sum(s['size_kb'] for s in category_scripts)
        total_lines = sum(s['lines'] for s in category_scripts)
        
        analysis["categories"][category] = {
            "count": len(category_scripts),
            "total_size_kb": total_size,
            "total_lines": total_lines,
            "avg_size_kb": total_size / len(category_scripts) if category_scripts else 0,
            "scripts": [s['name'] for s in category_scripts]
        }
    
    # Find consolidation opportunities
    for category, category_scripts in categories.items():
        if len(category_scripts) >= 5:
            analysis["consolidation_opportunities"].append({
                "category": category,
                "count": len(category_scripts),
                "total_size_kb": sum(s['size_kb'] for s in category_scripts),
                "scripts": [s['name'] for s in category_scripts]
            })
    
    # Find archive candidates
    for script in scripts:
        if should_archive(script):
            analysis["archive_candidates"].append(script['path'])
    
    # Generate reorganization plan
    analysis["reorganization_plan"] = generate_reorganization_plan(analysis)
    
    return analysis

def analyze_script(script_path):
    """Analyze individual script"""
    try:
        stats = script_path.stat()
        
        # Read file content
        with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Count lines
        lines = content.split('\n')
        line_count = len(lines)
        
        # Determine category
        category = determine_category(script_path, content)
        
        # Determine status
        status = determine_status(script_path, content)
        
        return {
            "name": script_path.name,
            "path": str(script_path.relative_to(Path("."))),
            "size_kb": round(stats.st_size / 1024, 1),
            "lines": line_count,
            "category": category,
            "status": status,
            "last_modified": stats.st_mtime
        }
        
    except Exception as e:
        print(f"⚠️  Error analyzing {script_path}: {e}")
        return None

def determine_category(script_path, content):
    """Determine script category"""
    path_str = str(script_path).lower()
    
    # Core application
    if script_path.name in ['app.py', 'models.py', 'config.py', 'wsgi.py']:
        return "core"
    
    # Blueprint modules
    if script_path.name in ['auth.py', 'room.py', 'chat.py', 'dashboard.py']:
        return "blueprint"
    
    # AI integration
    if 'openai_utils' in path_str or script_path.name in ['openai_utils.py', 'rubric_templates.py']:
        return "ai"
    
    # Tests
    if 'test_' in script_path.name:
        if 'mobile' in path_str:
            return "testing_mobile"
        elif 'hover' in path_str or 'accordion' in path_str:
            return "testing_ui"
        elif 'room' in path_str:
            return "testing_room"
        elif 'chat' in path_str:
            return "testing_chat"
        elif 'form' in path_str:
            return "testing_form"
        elif 'ai' in path_str:
            return "testing_ai"
        else:
            return "testing_general"
    
    # Debug scripts
    if script_path.name.startswith('debug_'):
        return "debug"
    
    # Utilities
    if script_path.name in ['git_helper.py', 'simple_test.py', 'start_ngrok.py']:
        return "utility"
    
    # Deployment
    if 'deployment' in path_str:
        return "deployment"
    
    # Setup and configuration
    if script_path.name.startswith('setup_'):
        return "setup"
    
    # Cleanup files
    if 'cleanup_files' in path_str:
        return "cleanup"
    
    # Chat Interface Website
    if 'Chat Interface Website' in path_str:
        return "styling"
    
    return "misc"

def determine_status(script_path, content):
    """Determine script status"""
    content_lower = content.lower()
    
    # Check for deprecation indicators
    if any(word in content_lower for word in ['deprecated', 'legacy', 'old', 'backup']):
        return "deprecated"
    
    # Check if it's a backup file
    if 'backup' in script_path.name or 'backup' in str(script_path):
        return "archived"
    
    # Check if it's in cleanup_files
    if 'cleanup_files' in str(script_path):
        return "archived"
    
    return "active"

def should_archive(script):
    """Determine if script should be archived"""
    return script['status'] in ['archived', 'deprecated']

def generate_reorganization_plan(analysis):
    """Generate reorganization plan"""
    plan = {
        "new_structure": {
            "src/": {
                "core/": ["app.py", "models.py", "config.py"],
                "blueprints/": ["auth.py", "room.py", "chat.py", "dashboard.py"],
                "ai/": ["openai_utils/", "rubric_templates.py"],
                "utils/": ["git_helper.py", "simple_test.py"]
            },
            "tests/": {
                "unit/": "Unit tests",
                "integration/": "Integration tests",
                "ui/": "UI tests",
                "mobile/": "Mobile tests",
                "ai/": "AI integration tests"
            },
            "scripts/": {
                "dev/": "Development utilities",
                "deploy/": "Deployment scripts",
                "maintenance/": "Maintenance scripts"
            },
            "tools/": "One-off tools and utilities",
            "archive/": "Archived scripts by date"
        },
        "estimated_impact": {
            "scripts_before": analysis["total_scripts"],
            "scripts_after_cleanup": analysis["total_scripts"] - len(analysis["archive_candidates"]),
            "reduction_percentage": (len(analysis["archive_candidates"]) / analysis["total_scripts"]) * 100 if analysis["total_scripts"] > 0 else 0
        }
    }
    
    return plan

def print_analysis(analysis):
    """Print analysis results"""
    print("\n" + "="*80)
    print("📊 SIMPLE INVENTORY ANALYSIS RESULTS")
    print("="*80)
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Total Scripts: {analysis['total_scripts']}")
    
    print(f"\n📁 Categories:")
    for category, stats in analysis["categories"].items():
        print(f"   {category}: {stats['count']} scripts ({stats['total_size_kb']:.1f} KB)")
    
    print(f"\n🔧 Consolidation Opportunities:")
    for opportunity in analysis["consolidation_opportunities"][:5]:
        print(f"   • {opportunity['category']}: {opportunity['count']} scripts ({opportunity['total_size_kb']:.1f} KB)")
    
    print(f"\n🗄️  Archive Candidates:")
    print(f"   Total: {len(analysis['archive_candidates'])} scripts")
    for candidate in analysis["archive_candidates"][:10]:
        print(f"   • {candidate}")
    if len(analysis["archive_candidates"]) > 10:
        print(f"   ... and {len(analysis['archive_candidates']) - 10} more")
    
    print(f"\n📋 Reorganization Impact:")
    impact = analysis["reorganization_plan"]["estimated_impact"]
    print(f"   Scripts before: {impact['scripts_before']}")
    print(f"   Scripts after cleanup: {impact['scripts_after_cleanup']}")
    print(f"   Reduction: {impact['reduction_percentage']:.1f}%")
    
    print("\n" + "="*80)

def main():
    """Main function"""
    analysis = analyze_scripts()
    print_analysis(analysis)
    
    # Save analysis to JSON
    with open("simple_analysis.json", "w") as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"\n✅ Analysis complete!")
    print(f"📄 Results saved to: simple_analysis.json")
    print(f"📋 Ready for Phase 1.3: Identify duplicate and unused scripts")

if __name__ == "__main__":
    main() 