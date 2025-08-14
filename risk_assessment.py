#!/usr/bin/env python3
"""
Cleanup Risk Assessment
Purpose: Analyze which cleanup actions could break the program
Status: [ACTIVE]
Created: 2025-01-27
Author: writeian

Usage:
    python risk_assessment.py

Output:
    - Risk assessment for each cleanup action
    - Safe vs risky operations
    - Backup recommendations
"""

import sqlite3
import json
import os
from pathlib import Path

class RiskAssessment:
    def __init__(self):
        self.db_file = "script_inventory.db"
        self.risk_file = "cleanup_risk_assessment.json"
        self.conn = None
        
    def connect_database(self):
        """Connect to the inventory database"""
        try:
            self.conn = sqlite3.connect(self.db_file)
            print(f"✅ Connected to {self.db_file}")
            return True
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            return False
    
    def analyze_cleanup_risks(self):
        """Analyze risks for each cleanup action"""
        print("⚠️  Analyzing cleanup risks...")
        
        risks = {
            "metadata": {
                "generated": "2025-01-27",
                "total_operations": 0,
                "safe_operations": 0,
                "low_risk": 0,
                "medium_risk": 0,
                "high_risk": 0
            },
            "operations": [],
            "recommendations": []
        }
        
        # Analyze each cleanup operation
        risks["operations"].extend(self.assess_duplicate_removal_risk())
        risks["operations"].extend(self.assess_archive_movement_risk())
        risks["operations"].extend(self.assess_test_consolidation_risk())
        risks["operations"].extend(self.assess_directory_restructure_risk())
        risks["operations"].extend(self.assess_documentation_risk())
        risks["operations"].extend(self.assess_backup_cleanup_risk())
        
        # Calculate statistics
        risks["metadata"]["total_operations"] = len(risks["operations"])
        risks["metadata"]["safe_operations"] = len([op for op in risks["operations"] if op["risk_level"] == "safe"])
        risks["metadata"]["low_risk"] = len([op for op in risks["operations"] if op["risk_level"] == "low"])
        risks["metadata"]["medium_risk"] = len([op for op in risks["operations"] if op["risk_level"] == "medium"])
        risks["metadata"]["high_risk"] = len([op for op in risks["operations"] if op["risk_level"] == "high"])
        
        # Generate recommendations
        risks["recommendations"] = self.generate_risk_recommendations(risks["operations"])
        
        return risks
    
    def assess_duplicate_removal_risk(self):
        """Assess risk of removing duplicate files"""
        print("🔄 Assessing duplicate removal risks...")
        
        operations = []
        
        # Load duplicate analysis
        if os.path.exists("duplicate_analysis.json"):
            with open("duplicate_analysis.json", "r") as f:
                duplicate_data = json.load(f)
            
            duplicate_groups = duplicate_data.get("duplicate_groups", [])
            
            for group in duplicate_groups:
                files = group.get("files", [])
                if len(files) > 1:
                    # Check if any duplicates are in core directories
                    core_files = [f for f in files if self.is_core_file(f)]
                    backup_files = [f for f in files if "backup" in f.lower()]
                    
                    if core_files:
                        # High risk if core files are involved
                        operations.append({
                            "operation": "remove_duplicate",
                            "target": files,
                            "risk_level": "high",
                            "reason": "Core application files involved in duplication",
                            "safeguard": "Keep all core files, remove only backup duplicates",
                            "backup_required": True
                        })
                    elif backup_files:
                        # Medium risk for backup duplicates
                        operations.append({
                            "operation": "remove_duplicate",
                            "target": files,
                            "risk_level": "medium",
                            "reason": "Backup files involved in duplication",
                            "safeguard": "Verify backup integrity before removal",
                            "backup_required": True
                        })
                    else:
                        # Low risk for test/debug duplicates
                        operations.append({
                            "operation": "remove_duplicate",
                            "target": files,
                            "risk_level": "low",
                            "reason": "Test/debug files only",
                            "safeguard": "Keep newest version, remove older duplicates",
                            "backup_required": False
                        })
        
        return operations
    
    def assess_archive_movement_risk(self):
        """Assess risk of moving files to archive"""
        print("🗄️  Assessing archive movement risks...")
        
        operations = []
        cursor = self.conn.cursor()
        
        # Check debug scripts
        cursor.execute("SELECT path, name FROM scripts WHERE category = 'debug' AND status = 'archived'")
        debug_scripts = cursor.fetchall()
        
        for script in debug_scripts:
            path, name = script
            if self.is_core_file(path):
                operations.append({
                    "operation": "move_to_archive",
                    "target": f"{path}/{name}",
                    "risk_level": "high",
                    "reason": "Debug script in core directory",
                    "safeguard": "Verify script is not imported by core modules",
                    "backup_required": True
                })
            else:
                operations.append({
                    "operation": "move_to_archive",
                    "target": f"{path}/{name}",
                    "risk_level": "low",
                    "reason": "Debug script in non-core location",
                    "safeguard": "Move to archive/debug/ subdirectory",
                    "backup_required": False
                })
        
        return operations
    
    def assess_test_consolidation_risk(self):
        """Assess risk of consolidating test scripts"""
        print("🧪 Assessing test consolidation risks...")
        
        operations = []
        cursor = self.conn.cursor()
        
        # Check test scripts in root directory
        cursor.execute("SELECT name FROM scripts WHERE category = 'testing' AND path NOT LIKE '%/%'")
        root_tests = cursor.fetchall()
        
        for test in root_tests:
            test_name = test[0]
            if self.is_critical_test(test_name):
                operations.append({
                    "operation": "move_test",
                    "target": test_name,
                    "risk_level": "medium",
                    "reason": "Critical test script in root directory",
                    "safeguard": "Update import paths after moving",
                    "backup_required": True
                })
            else:
                operations.append({
                    "operation": "move_test",
                    "target": test_name,
                    "risk_level": "low",
                    "reason": "Non-critical test script",
                    "safeguard": "Move to tests/ directory",
                    "backup_required": False
                })
        
        return operations
    
    def assess_directory_restructure_risk(self):
        """Assess risk of directory restructuring"""
        print("📁 Assessing directory restructure risks...")
        
        operations = []
        cursor = self.conn.cursor()
        
        # Check core application files
        core_files = [
            "app.py", "models.py", "auth.py", "room.py", "chat.py",
            "config.py", "wsgi.py", "requirements.txt"
        ]
        
        for file in core_files:
            if os.path.exists(file):
                operations.append({
                    "operation": "restructure_core",
                    "target": file,
                    "risk_level": "high",
                    "reason": "Core application file - moving could break imports",
                    "safeguard": "Update all import statements and deployment scripts",
                    "backup_required": True
                })
        
        # Check blueprint files
        cursor.execute("SELECT path, name FROM scripts WHERE category = 'blueprint'")
        blueprint_scripts = cursor.fetchall()
        
        for script in blueprint_scripts:
            path, name = script
            operations.append({
                "operation": "restructure_blueprint",
                "target": f"{path}/{name}",
                "risk_level": "medium",
                "reason": "Blueprint file - moving requires import updates",
                "safeguard": "Update Flask blueprint registrations",
                "backup_required": True
            })
        
        return operations
    
    def assess_documentation_risk(self):
        """Assess risk of documentation updates"""
        print("📚 Assessing documentation risks...")
        
        operations = []
        
        # Documentation updates are generally safe
        operations.append({
            "operation": "add_documentation",
            "target": "scripts without docstrings",
            "risk_level": "safe",
            "reason": "Adding documentation doesn't change functionality",
            "safeguard": "Use standard docstring format",
            "backup_required": False
        })
        
        return operations
    
    def assess_backup_cleanup_risk(self):
        """Assess risk of backup cleanup"""
        print("🗄️  Assessing backup cleanup risks...")
        
        operations = []
        
        # Backup cleanup is generally safe if done carefully
        operations.append({
            "operation": "consolidate_backups",
            "target": "backup directories",
            "risk_level": "low",
            "reason": "Backup files are not part of active application",
            "safeguard": "Keep at least one backup of each important file",
            "backup_required": False
        })
        
        return operations
    
    def is_core_file(self, file_path):
        """Check if file is part of core application"""
        core_patterns = [
            "app.py", "models.py", "auth.py", "room.py", "chat.py",
            "config.py", "wsgi.py", "requirements.txt", "openai_utils",
            "templates/", "static/", "migrations/"
        ]
        
        file_path_lower = file_path.lower()
        return any(pattern in file_path_lower for pattern in core_patterns)
    
    def is_critical_test(self, test_name):
        """Check if test is critical for application functionality"""
        critical_tests = [
            "test_auth", "test_models", "test_app", "test_chat",
            "test_room", "test_openai", "test_integration"
        ]
        
        test_name_lower = test_name.lower()
        return any(critical in test_name_lower for critical in critical_tests)
    
    def generate_risk_recommendations(self, operations):
        """Generate risk-based recommendations"""
        recommendations = []
        
        # Group by risk level
        high_risk = [op for op in operations if op["risk_level"] == "high"]
        medium_risk = [op for op in operations if op["risk_level"] == "medium"]
        low_risk = [op for op in operations if op["risk_level"] == "low"]
        safe = [op for op in operations if op["risk_level"] == "safe"]
        
        if high_risk:
            recommendations.append({
                "priority": "critical",
                "title": "High-Risk Operations Require Special Care",
                "description": f"{len(high_risk)} operations have high risk of breaking the application",
                "operations": [op["operation"] for op in high_risk],
                "safeguards": [
                    "Create full backup before any high-risk operations",
                    "Test in development environment first",
                    "Update all import statements and references",
                    "Verify application functionality after each operation"
                ]
            })
        
        if medium_risk:
            recommendations.append({
                "priority": "high",
                "title": "Medium-Risk Operations Need Testing",
                "description": f"{len(medium_risk)} operations have medium risk",
                "operations": [op["operation"] for op in medium_risk],
                "safeguards": [
                    "Test changes in development environment",
                    "Update import paths and references",
                    "Verify functionality after changes"
                ]
            })
        
        if low_risk:
            recommendations.append({
                "priority": "medium",
                "title": "Low-Risk Operations Can Proceed",
                "description": f"{len(low_risk)} operations have low risk",
                "operations": [op["operation"] for op in low_risk],
                "safeguards": [
                    "Keep backups of original files",
                    "Test basic functionality after changes"
                ]
            })
        
        if safe:
            recommendations.append({
                "priority": "low",
                "title": "Safe Operations",
                "description": f"{len(safe)} operations are safe to perform",
                "operations": [op["operation"] for op in safe],
                "safeguards": [
                    "No special safeguards required"
                ]
            })
        
        return recommendations
    
    def save_risk_assessment(self, risks):
        """Save risk assessment to JSON file"""
        with open(self.risk_file, "w") as f:
            json.dump(risks, f, indent=2, default=str)
        
        print(f"✅ Risk assessment saved to: {self.risk_file}")
    
    def print_risk_summary(self, risks):
        """Print risk summary to console"""
        print("\n" + "="*80)
        print("⚠️  CLEANUP RISK ASSESSMENT")
        print("="*80)
        
        metadata = risks["metadata"]
        print(f"\n📊 Risk Statistics:")
        print(f"   Total Operations: {metadata['total_operations']}")
        print(f"   Safe: {metadata['safe_operations']}")
        print(f"   Low Risk: {metadata['low_risk']}")
        print(f"   Medium Risk: {metadata['medium_risk']}")
        print(f"   High Risk: {metadata['high_risk']}")
        
        print(f"\n🚨 High-Risk Operations:")
        high_risk_ops = [op for op in risks["operations"] if op["risk_level"] == "high"]
        for op in high_risk_ops[:5]:  # Show first 5
            print(f"   • {op['operation']}: {op['reason']}")
        
        print(f"\n🟡 Medium-Risk Operations:")
        medium_risk_ops = [op for op in risks["operations"] if op["risk_level"] == "medium"]
        for op in medium_risk_ops[:5]:  # Show first 5
            print(f"   • {op['operation']}: {op['reason']}")
        
        print(f"\n📋 Key Safeguards:")
        for rec in risks["recommendations"]:
            if rec["priority"] in ["critical", "high"]:
                print(f"   • {rec['title']}: {rec['description']}")
        
        print("\n" + "="*80)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def main():
    """Main function"""
    print("⚠️  Analyzing Cleanup Risks...")
    
    assessor = RiskAssessment()
    
    if not assessor.connect_database():
        return
    
    try:
        # Analyze risks
        risks = assessor.analyze_cleanup_risks()
        
        # Save and display results
        assessor.save_risk_assessment(risks)
        assessor.print_risk_summary(risks)
        
        print(f"\n✅ Risk assessment complete!")
        print(f"📄 Report saved to: {assessor.risk_file}")
        
    finally:
        assessor.close()

if __name__ == "__main__":
    main() 