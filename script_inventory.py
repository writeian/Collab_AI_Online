#!/usr/bin/env python3
"""
Script Inventory Generator
Purpose: Generate comprehensive inventory of all Python scripts in the project
Status: [ACTIVE]
Created: 2025-01-27
Author: writeian

Usage:
    python script_inventory.py

Output:
    - Complete inventory in YAML format
    - Summary statistics
    - Recommendations for cleanup
"""

import os
import yaml
import ast
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter
import re

class ScriptInventory:
    def __init__(self):
        self.project_root = Path(".")
        self.inventory_file = "scripts_inventory.yaml"
        self.scripts = []
        self.categories = defaultdict(list)
        self.imports = defaultdict(set)
        self.dependencies = Counter()
        
    def scan_project(self):
        """Scan entire project for Python scripts"""
        print("🔍 Scanning project for Python scripts...")
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip common directories to ignore
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', 'venv', 'env'}]
            
            for file in files:
                if file.endswith('.py'):
                    script_path = Path(root) / file
                    script_info = self.analyze_script(script_path)
                    if script_info:
                        self.scripts.append(script_info)
                        self.categorize_script(script_info)
        
        print(f"✅ Found {len(self.scripts)} Python scripts")
        return self.scripts
    
    def analyze_script(self, script_path):
        """Analyze individual script and extract metadata"""
        try:
            stats = script_path.stat()
            
            # Read file content
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Count lines
            lines = content.split('\n')
            line_count = len(lines)
            code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            
            # Extract imports
            imports = self.extract_imports(content)
            
            # Determine category and status
            category, subcategory = self.determine_category(script_path)
            status = self.determine_status(script_path, content)
            
            # Extract purpose from docstring or comments
            purpose = self.extract_purpose(content)
            
            script_info = {
                "name": script_path.name,
                "path": str(script_path.relative_to(self.project_root)),
                "size_kb": round(stats.st_size / 1024, 1),
                "lines": {
                    "total": line_count,
                    "code": code_lines,
                    "comments": line_count - code_lines
                },
                "last_modified": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d"),
                "category": category,
                "subcategory": subcategory,
                "status": status,
                "purpose": purpose,
                "imports": list(imports),
                "dependencies": self.analyze_dependencies(imports)
            }
            
            # Track imports for dependency analysis
            for imp in imports:
                self.imports[script_path.name].add(imp)
                self.dependencies[imp] += 1
            
            return script_info
            
        except Exception as e:
            print(f"⚠️  Error analyzing {script_path}: {e}")
            return None
    
    def extract_imports(self, content):
        """Extract Python imports from file content"""
        imports = set()
        
        # Simple regex-based import extraction
        import_patterns = [
            r'^import\s+(\w+)',
            r'^from\s+(\w+)\s+import',
            r'^from\s+(\w+\.\w+)\s+import'
        ]
        
        for line in content.split('\n'):
            line = line.strip()
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    imports.add(match.group(1))
                    break
        
        return imports
    
    def determine_category(self, script_path):
        """Determine script category based on path and content"""
        path_str = str(script_path).lower()
        
        # Core application
        if script_path.name in ['app.py', 'models.py', 'config.py', 'wsgi.py']:
            return "core", "application"
        
        # Blueprint modules
        if script_path.name in ['auth.py', 'room.py', 'chat.py', 'dashboard.py', 'google_auth.py', 'analytics.py']:
            return "core", "blueprint"
        
        # AI integration
        if 'openai_utils' in path_str:
            return "ai", "integration"
        if script_path.name in ['openai_utils.py', 'openai_utils_original.py', 'rubric_templates.py']:
            return "ai", "templates"
        
        # Tests
        if 'test_' in script_path.name:
            if 'mobile' in path_str:
                return "testing", "mobile"
            elif 'hover' in path_str:
                return "testing", "ui"
            elif 'accordion' in path_str:
                return "testing", "ui"
            elif 'room' in path_str:
                return "testing", "room"
            elif 'chat' in path_str:
                return "testing", "chat"
            elif 'form' in path_str:
                return "testing", "form"
            elif 'ai' in path_str:
                return "testing", "ai"
            else:
                return "testing", "general"
        
        # Debug scripts
        if script_path.name.startswith('debug_'):
            return "debug", "troubleshooting"
        
        # Utilities
        if script_path.name in ['git_helper.py', 'simple_test.py', 'start_ngrok.py']:
            return "utility", "development"
        
        # Deployment
        if 'deployment' in path_str:
            return "deployment", "production"
        
        # Setup and configuration
        if script_path.name.startswith('setup_') or 'setup' in path_str:
            return "utility", "setup"
        
        # Verification
        if script_path.name.startswith('verify_'):
            return "utility", "verification"
        
        # Cleanup files
        if 'cleanup_files' in path_str:
            return "debug", "cleanup"
        
        # Chat Interface Website
        if 'Chat Interface Website' in path_str:
            return "utility", "styling"
        
        return "misc", "unknown"
    
    def determine_status(self, script_path, content):
        """Determine script status based on content and context"""
        content_lower = content.lower()
        
        # Check for deprecation indicators
        if any(word in content_lower for word in ['deprecated', 'legacy', 'old', 'backup']):
            return "deprecated"
        
        # Check for experimental indicators
        if any(word in content_lower for word in ['experimental', 'test', 'trial']):
            return "experimental"
        
        # Check if it's a backup file
        if 'backup' in script_path.name or 'backup' in str(script_path):
            return "archived"
        
        # Check if it's in cleanup_files
        if 'cleanup_files' in str(script_path):
            return "archived"
        
        # Check if it's a duplicate
        if self.is_duplicate(script_path):
            return "duplicate"
        
        return "active"
    
    def is_duplicate(self, script_path):
        """Check if script is a duplicate"""
        name = script_path.name
        duplicates = [s for s in self.scripts if s['name'] == name]
        return len(duplicates) > 0
    
    def extract_purpose(self, content):
        """Extract purpose from docstring or comments"""
        lines = content.split('\n')
        
        # Look for docstring
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            if '"""' in line or "'''" in line:
                # Extract docstring content
                docstring = ""
                for j in range(i, min(i + 5, len(lines))):
                    docstring += lines[j] + " "
                return docstring.strip()[:100] + "..." if len(docstring) > 100 else docstring.strip()
        
        # Look for purpose comments
        for line in lines[:10]:
            if 'purpose:' in line.lower() or 'purpose:' in line.lower():
                return line.strip()
        
        return "No purpose documented"
    
    def analyze_dependencies(self, imports):
        """Analyze script dependencies"""
        dependencies = []
        
        # Common external dependencies
        external_deps = {
            'flask', 'sqlalchemy', 'openai', 'anthropic', 'requests', 
            'selenium', 'pytest', 'unittest', 'yaml', 'json', 'os', 'sys'
        }
        
        for imp in imports:
            if imp in external_deps:
                dependencies.append(imp)
        
        return dependencies
    
    def categorize_script(self, script_info):
        """Categorize script for summary"""
        category = script_info['category']
        subcategory = script_info['subcategory']
        self.categories[f"{category}/{subcategory}"].append(script_info)
    
    def generate_summary(self):
        """Generate summary statistics"""
        summary = {
            "total_scripts": len(self.scripts),
            "total_size_kb": sum(s['size_kb'] for s in self.scripts),
            "total_lines": sum(s['lines']['total'] for s in self.scripts),
            "categories": {},
            "status_distribution": dict(Counter(s['status'] for s in self.scripts)),
            "top_dependencies": self.dependencies.most_common(10),
            "largest_scripts": sorted(self.scripts, key=lambda x: x['size_kb'], reverse=True)[:10],
            "recent_scripts": sorted(self.scripts, key=lambda x: x['last_modified'], reverse=True)[:10]
        }
        
        # Category breakdown
        for category, scripts in self.categories.items():
            summary["categories"][category] = {
                "count": len(scripts),
                "size_kb": sum(s['size_kb'] for s in scripts),
                "lines": sum(s['lines']['total'] for s in scripts)
            }
        
        return summary
    
    def generate_recommendations(self):
        """Generate cleanup recommendations"""
        recommendations = {
            "immediate_actions": [],
            "archive_candidates": [],
            "consolidation_opportunities": [],
            "documentation_needs": []
        }
        
        # Find scripts to archive
        for script in self.scripts:
            if script['status'] in ['archived', 'deprecated', 'duplicate']:
                recommendations["archive_candidates"].append(script['path'])
            
            if script['purpose'] == "No purpose documented":
                recommendations["documentation_needs"].append(script['path'])
        
        # Find consolidation opportunities
        test_scripts = [s for s in self.scripts if s['category'] == 'testing']
        test_categories = defaultdict(list)
        for script in test_scripts:
            test_categories[script['subcategory']].append(script)
        
        for category, scripts in test_categories.items():
            if len(scripts) > 5:  # More than 5 scripts in same category
                recommendations["consolidation_opportunities"].append({
                    "category": category,
                    "count": len(scripts),
                    "scripts": [s['name'] for s in scripts]
                })
        
        # Immediate actions
        if len(recommendations["archive_candidates"]) > 0:
            recommendations["immediate_actions"].append(f"Archive {len(recommendations['archive_candidates'])} scripts")
        
        if len(recommendations["documentation_needs"]) > 0:
            recommendations["immediate_actions"].append(f"Add documentation to {len(recommendations['documentation_needs'])} scripts")
        
        return recommendations
    
    def save_inventory(self):
        """Save inventory to YAML file"""
        inventory_data = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "total_scripts": len(self.scripts),
                "project": "AI Collab Online"
            },
            "scripts": self.scripts,
            "summary": self.generate_summary(),
            "recommendations": self.generate_recommendations()
        }
        
        with open(self.inventory_file, 'w', encoding='utf-8') as f:
            yaml.dump(inventory_data, f, default_flow_style=False, indent=2, allow_unicode=True)
        
        print(f"✅ Inventory saved to {self.inventory_file}")
    
    def print_summary(self):
        """Print summary to console"""
        summary = self.generate_summary()
        recommendations = self.generate_recommendations()
        
        print("\n" + "="*60)
        print("📊 SCRIPT INVENTORY SUMMARY")
        print("="*60)
        
        print(f"\n📈 Overall Statistics:")
        print(f"   Total Scripts: {summary['total_scripts']}")
        print(f"   Total Size: {summary['total_size_kb']:.1f} KB")
        print(f"   Total Lines: {summary['total_lines']:,}")
        
        print(f"\n📁 Categories:")
        for category, stats in summary['categories'].items():
            print(f"   {category}: {stats['count']} scripts ({stats['size_kb']:.1f} KB)")
        
        print(f"\n📊 Status Distribution:")
        for status, count in summary['status_distribution'].items():
            print(f"   {status}: {count} scripts")
        
        print(f"\n🔗 Top Dependencies:")
        for dep, count in summary['top_dependencies'][:5]:
            print(f"   {dep}: {count} scripts")
        
        print(f"\n📦 Largest Scripts:")
        for script in summary['largest_scripts'][:5]:
            print(f"   {script['name']}: {script['size_kb']:.1f} KB ({script['lines']['total']} lines)")
        
        print(f"\n🚨 Recommendations:")
        for action in recommendations['immediate_actions']:
            print(f"   • {action}")
        
        if recommendations['archive_candidates']:
            print(f"\n🗄️  Archive Candidates ({len(recommendations['archive_candidates'])}):")
            for script in recommendations['archive_candidates'][:10]:
                print(f"   • {script}")
            if len(recommendations['archive_candidates']) > 10:
                print(f"   ... and {len(recommendations['archive_candidates']) - 10} more")
        
        print("\n" + "="*60)

def main():
    """Main function to run the inventory generation"""
    print("🚀 Starting Script Inventory Generation...")
    
    inventory = ScriptInventory()
    inventory.scan_project()
    inventory.save_inventory()
    inventory.print_summary()
    
    print(f"\n✅ Inventory generation complete!")
    print(f"📄 Full inventory saved to: {inventory.inventory_file}")
    print(f"📋 Next step: Review recommendations and begin Phase 1.2")

if __name__ == "__main__":
    main() 