#!/usr/bin/env python3
"""
Current Organizational Issues Documenter
Purpose: Document all current organizational issues in the project
Status: [ACTIVE]
Created: 2025-01-27
Author: writeian

Usage:
    python document_issues.py

Output:
    - Comprehensive issues report
    - Priority matrix
    - Impact assessment
    - Recommendations
"""

import sqlite3
import json
import os
from datetime import datetime
from collections import defaultdict

class IssuesDocumenter:
    def __init__(self):
        self.db_file = "script_inventory.db"
        self.issues_file = "organizational_issues.json"
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
    
    def analyze_organizational_issues(self):
        """Analyze and document all organizational issues"""
        print("🔍 Analyzing organizational issues...")
        
        issues = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "total_issues": 0,
                "critical_issues": 0,
                "high_priority": 0,
                "medium_priority": 0,
                "low_priority": 0
            },
            "issues": [],
            "summary": {},
            "recommendations": []
        }
        
        # Analyze different types of issues
        issues["issues"].extend(self.analyze_file_organization_issues())
        issues["issues"].extend(self.analyze_duplication_issues())
        issues["issues"].extend(self.analyze_test_script_issues())
        issues["issues"].extend(self.analyze_documentation_issues())
        issues["issues"].extend(self.analyze_naming_issues())
        issues["issues"].extend(self.analyze_backup_issues())
        issues["issues"].extend(self.analyze_dependency_issues())
        issues["issues"].extend(self.analyze_maintenance_issues())
        
        # Calculate summary statistics
        issues["metadata"]["total_issues"] = len(issues["issues"])
        issues["metadata"]["critical_issues"] = len([i for i in issues["issues"] if i["priority"] == "critical"])
        issues["metadata"]["high_priority"] = len([i for i in issues["issues"] if i["priority"] == "high"])
        issues["metadata"]["medium_priority"] = len([i for i in issues["issues"] if i["priority"] == "medium"])
        issues["metadata"]["low_priority"] = len([i for i in issues["issues"] if i["priority"] == "low"])
        
        # Generate summary
        issues["summary"] = self.generate_summary(issues["issues"])
        
        # Generate recommendations
        issues["recommendations"] = self.generate_recommendations(issues["issues"])
        
        return issues
    
    def analyze_file_organization_issues(self):
        """Analyze file organization issues"""
        print("📁 Analyzing file organization issues...")
        
        issues = []
        cursor = self.conn.cursor()
        
        # Issue: Too many scripts in root directory
        cursor.execute("SELECT COUNT(*) FROM scripts WHERE path NOT LIKE '%/%'")
        root_scripts = cursor.fetchone()[0]
        
        if root_scripts > 20:
            issues.append({
                "id": "ORG_001",
                "category": "file_organization",
                "title": "Too many scripts in root directory",
                "description": f"There are {root_scripts} scripts in the root directory, making it cluttered and difficult to navigate.",
                "impact": "high",
                "priority": "high",
                "affected_scripts": root_scripts,
                "recommendation": "Move scripts to appropriate subdirectories based on their category and purpose.",
                "effort": "medium"
            })
        
        # Issue: Misc category too large
        cursor.execute("SELECT COUNT(*) FROM scripts WHERE category = 'misc'")
        misc_count = cursor.fetchone()[0]
        
        if misc_count > 10:
            issues.append({
                "id": "ORG_002",
                "category": "file_organization",
                "title": "Large misc category needs categorization",
                "description": f"There are {misc_count} scripts in the 'misc' category that need proper categorization.",
                "impact": "medium",
                "priority": "medium",
                "affected_scripts": misc_count,
                "recommendation": "Review and recategorize misc scripts into appropriate categories.",
                "effort": "low"
            })
        
        # Issue: No clear directory structure
        cursor.execute("SELECT DISTINCT path FROM scripts WHERE path LIKE '%/%'")
        paths = cursor.fetchall()
        
        directory_structure = defaultdict(int)
        for path in paths:
            parts = path[0].split('/')
            if len(parts) > 1:
                directory_structure[parts[0]] += 1
        
        if len(directory_structure) > 10:
            issues.append({
                "id": "ORG_003",
                "category": "file_organization",
                "title": "Inconsistent directory structure",
                "description": f"Scripts are scattered across {len(directory_structure)} different directories without clear organization.",
                "impact": "high",
                "priority": "high",
                "affected_scripts": sum(directory_structure.values()),
                "recommendation": "Implement standardized directory structure with clear naming conventions.",
                "effort": "high"
            })
        
        return issues
    
    def analyze_duplication_issues(self):
        """Analyze duplication issues"""
        print("🔄 Analyzing duplication issues...")
        
        issues = []
        
        # Load duplicate analysis if available
        if os.path.exists("duplicate_analysis.json"):
            with open("duplicate_analysis.json", "r") as f:
                duplicate_data = json.load(f)
            
            duplicate_groups = duplicate_data.get("duplicate_groups", [])
            total_savings = duplicate_data.get("estimated_savings", {}).get("total", 0)
            
            if duplicate_groups:
                issues.append({
                    "id": "DUP_001",
                    "category": "duplication",
                    "title": "Massive file duplication",
                    "description": f"There are {len(duplicate_groups)} duplicate groups with {total_savings/1024:.1f} KB of wasted space.",
                    "impact": "high",
                    "priority": "critical",
                    "affected_scripts": len(duplicate_groups),
                    "recommendation": "Remove duplicate files, keeping only the primary copies.",
                    "effort": "low"
                })
        
        return issues
    
    def analyze_test_script_issues(self):
        """Analyze test script organization issues"""
        print("🧪 Analyzing test script issues...")
        
        issues = []
        cursor = self.conn.cursor()
        
        # Issue: Too many test scripts
        cursor.execute("SELECT COUNT(*) FROM scripts WHERE category = 'testing'")
        test_count = cursor.fetchone()[0]
        
        if test_count > 100:
            issues.append({
                "id": "TEST_001",
                "category": "testing",
                "title": "Test script proliferation",
                "description": f"There are {test_count} test scripts, making test management difficult.",
                "impact": "medium",
                "priority": "medium",
                "affected_scripts": test_count,
                "recommendation": "Consolidate similar tests and implement test organization standards.",
                "effort": "medium"
            })
        
        # Issue: Test scripts in root directory
        cursor.execute("SELECT COUNT(*) FROM scripts WHERE category = 'testing' AND path NOT LIKE '%/%'")
        root_tests = cursor.fetchone()[0]
        
        if root_tests > 0:
            issues.append({
                "id": "TEST_002",
                "category": "testing",
                "title": "Test scripts in root directory",
                "description": f"There are {root_tests} test scripts in the root directory instead of a tests/ directory.",
                "impact": "medium",
                "priority": "medium",
                "affected_scripts": root_tests,
                "recommendation": "Move all test scripts to a dedicated tests/ directory.",
                "effort": "low"
            })
        
        return issues
    
    def analyze_documentation_issues(self):
        """Analyze documentation issues"""
        print("📚 Analyzing documentation issues...")
        
        issues = []
        cursor = self.conn.cursor()
        
        # Issue: Missing purpose documentation
        cursor.execute("SELECT COUNT(*) FROM scripts WHERE purpose LIKE '%No purpose documented%'")
        no_purpose = cursor.fetchone()[0]
        
        if no_purpose > 0:
            issues.append({
                "id": "DOC_001",
                "category": "documentation",
                "title": "Missing script documentation",
                "description": f"There are {no_purpose} scripts without documented purpose.",
                "impact": "medium",
                "priority": "medium",
                "affected_scripts": no_purpose,
                "recommendation": "Add docstrings or purpose comments to all scripts.",
                "effort": "medium"
            })
        
        return issues
    
    def analyze_naming_issues(self):
        """Analyze naming convention issues"""
        print("🏷️  Analyzing naming issues...")
        
        issues = []
        cursor = self.conn.cursor()
        
        # Issue: Inconsistent naming patterns
        cursor.execute("SELECT name FROM scripts WHERE name LIKE 'test_%'")
        test_names = cursor.fetchall()
        
        naming_patterns = defaultdict(int)
        for name in test_names:
            parts = name[0].split('_')
            if len(parts) >= 2:
                pattern = '_'.join(parts[:2])
                naming_patterns[pattern] += 1
        
        inconsistent_patterns = [pattern for pattern, count in naming_patterns.items() if count > 5]
        
        if inconsistent_patterns:
            issues.append({
                "id": "NAM_001",
                "category": "naming",
                "title": "Inconsistent test naming patterns",
                "description": f"Multiple test naming patterns detected: {', '.join(inconsistent_patterns[:5])}",
                "impact": "low",
                "priority": "low",
                "affected_scripts": sum(naming_patterns.values()),
                "recommendation": "Standardize test naming conventions across the project.",
                "effort": "low"
            })
        
        return issues
    
    def analyze_backup_issues(self):
        """Analyze backup and archive issues"""
        print("🗄️  Analyzing backup issues...")
        
        issues = []
        cursor = self.conn.cursor()
        
        # Issue: Too many backup directories
        cursor.execute("SELECT COUNT(*) FROM scripts WHERE path LIKE '%backup%'")
        backup_scripts = cursor.fetchone()[0]
        
        if backup_scripts > 50:
            issues.append({
                "id": "BAK_001",
                "category": "backup",
                "title": "Excessive backup proliferation",
                "description": f"There are {backup_scripts} scripts in backup directories, creating confusion.",
                "impact": "medium",
                "priority": "high",
                "affected_scripts": backup_scripts,
                "recommendation": "Consolidate backup directories and implement proper backup strategy.",
                "effort": "medium"
            })
        
        # Issue: Backup scripts in active directories
        cursor.execute("SELECT COUNT(*) FROM scripts WHERE status = 'archived' AND path NOT LIKE '%backup%'")
        archived_in_active = cursor.fetchone()[0]
        
        if archived_in_active > 0:
            issues.append({
                "id": "BAK_002",
                "category": "backup",
                "title": "Archived scripts in active directories",
                "description": f"There are {archived_in_active} archived scripts in active directories.",
                "impact": "medium",
                "priority": "medium",
                "affected_scripts": archived_in_active,
                "recommendation": "Move archived scripts to dedicated archive directories.",
                "effort": "low"
            })
        
        return issues
    
    def analyze_dependency_issues(self):
        """Analyze dependency management issues"""
        print("🔗 Analyzing dependency issues...")
        
        issues = []
        
        # This would require more detailed dependency analysis
        # For now, we'll note that dependency tracking is incomplete
        issues.append({
            "id": "DEP_001",
            "category": "dependencies",
            "title": "Incomplete dependency tracking",
            "description": "Dependency relationships between scripts are not fully mapped.",
            "impact": "medium",
            "priority": "medium",
            "affected_scripts": "unknown",
            "recommendation": "Implement comprehensive dependency mapping and analysis.",
            "effort": "high"
        })
        
        return issues
    
    def analyze_maintenance_issues(self):
        """Analyze maintenance and lifecycle issues"""
        print("🔧 Analyzing maintenance issues...")
        
        issues = []
        cursor = self.conn.cursor()
        
        # Issue: No lifecycle tracking
        issues.append({
            "id": "MAINT_001",
            "category": "maintenance",
            "title": "No script lifecycle management",
            "description": "There's no systematic approach to managing script lifecycle (creation, updates, deprecation, deletion).",
            "impact": "high",
            "priority": "high",
            "affected_scripts": "all",
            "recommendation": "Implement script lifecycle management system with regular review cycles.",
            "effort": "medium"
        })
        
        # Issue: No automated cleanup processes
        issues.append({
            "id": "MAINT_002",
            "category": "maintenance",
            "title": "No automated cleanup processes",
            "description": "No automated processes exist for identifying and cleaning up unused or outdated scripts.",
            "impact": "medium",
            "priority": "medium",
            "affected_scripts": "all",
            "recommendation": "Implement automated cleanup processes and maintenance scripts.",
            "effort": "high"
        })
        
        return issues
    
    def generate_summary(self, issues):
        """Generate summary of all issues"""
        summary = {
            "by_category": defaultdict(int),
            "by_priority": defaultdict(int),
            "by_impact": defaultdict(int),
            "total_affected_scripts": 0
        }
        
        for issue in issues:
            summary["by_category"][issue["category"]] += 1
            summary["by_priority"][issue["priority"]] += 1
            summary["by_impact"][issue["impact"]] += 1
            
            if isinstance(issue["affected_scripts"], int):
                summary["total_affected_scripts"] += issue["affected_scripts"]
        
        return dict(summary)
    
    def generate_recommendations(self, issues):
        """Generate prioritized recommendations"""
        recommendations = []
        
        # Group issues by priority
        critical_issues = [i for i in issues if i["priority"] == "critical"]
        high_priority = [i for i in issues if i["priority"] == "high"]
        medium_priority = [i for i in issues if i["priority"] == "medium"]
        low_priority = [i for i in issues if i["priority"] == "low"]
        
        # Critical recommendations
        if critical_issues:
            recommendations.append({
                "priority": "critical",
                "title": "Immediate Action Required",
                "description": f"Address {len(critical_issues)} critical issues immediately",
                "issues": [i["id"] for i in critical_issues],
                "effort": "high",
                "timeline": "1-2 weeks"
            })
        
        # High priority recommendations
        if high_priority:
            recommendations.append({
                "priority": "high",
                "title": "High Priority Cleanup",
                "description": f"Address {len(high_priority)} high priority issues",
                "issues": [i["id"] for i in high_priority],
                "effort": "medium",
                "timeline": "2-4 weeks"
            })
        
        # Medium priority recommendations
        if medium_priority:
            recommendations.append({
                "priority": "medium",
                "title": "Organizational Improvements",
                "description": f"Address {len(medium_priority)} medium priority issues",
                "issues": [i["id"] for i in medium_priority],
                "effort": "medium",
                "timeline": "1-2 months"
            })
        
        # Low priority recommendations
        if low_priority:
            recommendations.append({
                "priority": "low",
                "title": "Long-term Improvements",
                "description": f"Address {len(low_priority)} low priority issues",
                "issues": [i["id"] for i in low_priority],
                "effort": "low",
                "timeline": "2-3 months"
            })
        
        return recommendations
    
    def save_issues_report(self, issues):
        """Save issues report to JSON file"""
        with open(self.issues_file, "w") as f:
            json.dump(issues, f, indent=2, default=str)
        
        print(f"✅ Issues report saved to: {self.issues_file}")
    
    def print_issues_summary(self, issues):
        """Print issues summary to console"""
        print("\n" + "="*80)
        print("🚨 ORGANIZATIONAL ISSUES SUMMARY")
        print("="*80)
        
        metadata = issues["metadata"]
        print(f"\n📊 Overall Statistics:")
        print(f"   Total Issues: {metadata['total_issues']}")
        print(f"   Critical: {metadata['critical_issues']}")
        print(f"   High Priority: {metadata['high_priority']}")
        print(f"   Medium Priority: {metadata['medium_priority']}")
        print(f"   Low Priority: {metadata['low_priority']}")
        
        summary = issues["summary"]
        print(f"\n📁 Issues by Category:")
        for category, count in summary["by_category"].items():
            print(f"   {category}: {count} issues")
        
        print(f"\n🚨 Critical Issues:")
        critical_issues = [i for i in issues["issues"] if i["priority"] == "critical"]
        for issue in critical_issues:
            print(f"   • {issue['title']}: {issue['description']}")
        
        print(f"\n📋 Top Recommendations:")
        for rec in issues["recommendations"][:3]:
            print(f"   • {rec['title']}: {rec['description']}")
        
        print("\n" + "="*80)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def main():
    """Main function"""
    print("🚀 Documenting Current Organizational Issues...")
    
    documenter = IssuesDocumenter()
    
    if not documenter.connect_database():
        return
    
    try:
        # Analyze issues
        issues = documenter.analyze_organizational_issues()
        
        # Save and display results
        documenter.save_issues_report(issues)
        documenter.print_issues_summary(issues)
        
        print(f"\n✅ Issues documentation complete!")
        print(f"📄 Report saved to: {documenter.issues_file}")
        print(f"📋 Phase 1 Complete - Ready for Phase 2: Immediate Cleanup")
        
    finally:
        documenter.close()

if __name__ == "__main__":
    main() 