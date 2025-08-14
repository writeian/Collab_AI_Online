#!/usr/bin/env python3
"""
Inventory Database Structure Creator
Purpose: Create a comprehensive database structure for script inventory management
Status: [ACTIVE]
Created: 2025-01-27
Author: writeian

Usage:
    python create_inventory_db.py

Output:
    - SQLite database with script inventory
    - JSON schema definition
    - Database documentation
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class InventoryDatabase:
    def __init__(self):
        self.db_file = "script_inventory.db"
        self.schema_file = "inventory_schema.json"
        self.conn = None
        
    def create_database(self):
        """Create the inventory database with all tables"""
        print("🗄️  Creating inventory database...")
        
        self.conn = sqlite3.connect(self.db_file)
        cursor = self.conn.cursor()
        
        # Create tables
        self.create_scripts_table(cursor)
        self.create_categories_table(cursor)
        self.create_dependencies_table(cursor)
        self.create_duplicates_table(cursor)
        self.create_lifecycle_table(cursor)
        self.create_metadata_table(cursor)
        
        self.conn.commit()
        print(f"✅ Database created: {self.db_file}")
        
    def create_scripts_table(self, cursor):
        """Create main scripts table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT UNIQUE NOT NULL,
                size_bytes INTEGER NOT NULL,
                size_kb REAL NOT NULL,
                lines_total INTEGER NOT NULL,
                lines_code INTEGER NOT NULL,
                lines_comments INTEGER NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                status TEXT NOT NULL,
                purpose TEXT,
                last_modified TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
    def create_categories_table(self, cursor):
        """Create categories table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                parent_category TEXT,
                color_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
    def create_dependencies_table(self, cursor):
        """Create dependencies table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                script_id INTEGER NOT NULL,
                dependency_name TEXT NOT NULL,
                dependency_type TEXT NOT NULL,
                is_external BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (script_id) REFERENCES scripts (id),
                UNIQUE(script_id, dependency_name)
            )
        ''')
        
    def create_duplicates_table(self, cursor):
        """Create duplicates table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS duplicates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT NOT NULL,
                script_id INTEGER NOT NULL,
                is_primary BOOLEAN DEFAULT FALSE,
                recommended_keep BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (script_id) REFERENCES scripts (id)
            )
        ''')
        
    def create_lifecycle_table(self, cursor):
        """Create lifecycle tracking table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lifecycle (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                script_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                status_from TEXT,
                status_to TEXT,
                notes TEXT,
                performed_by TEXT,
                performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (script_id) REFERENCES scripts (id)
            )
        ''')
        
    def create_metadata_table(self, cursor):
        """Create metadata table for additional script information"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                script_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (script_id) REFERENCES scripts (id),
                UNIQUE(script_id, key)
            )
        ''')
        
    def populate_categories(self):
        """Populate categories table with predefined categories"""
        print("📁 Populating categories...")
        
        categories = [
            ("core", "Core application files", None, "#FF6B6B"),
            ("blueprint", "Flask blueprint modules", None, "#4ECDC4"),
            ("ai", "AI integration and utilities", None, "#45B7D1"),
            ("testing", "Test files and test utilities", None, "#96CEB4"),
            ("debug", "Debug and troubleshooting scripts", None, "#FFEAA7"),
            ("utility", "Utility and helper scripts", None, "#DDA0DD"),
            ("deployment", "Deployment and production scripts", None, "#98D8C8"),
            ("setup", "Setup and configuration scripts", None, "#F7DC6F"),
            ("cleanup", "Cleanup and maintenance scripts", None, "#BB8FCE"),
            ("styling", "Styling and UI-related scripts", None, "#85C1E9"),
            ("misc", "Miscellaneous scripts", None, "#F8C471"),
            
            # Subcategories
            ("testing_unit", "Unit tests", "testing", "#96CEB4"),
            ("testing_integration", "Integration tests", "testing", "#96CEB4"),
            ("testing_ui", "UI tests", "testing", "#96CEB4"),
            ("testing_mobile", "Mobile tests", "testing", "#96CEB4"),
            ("testing_chat", "Chat functionality tests", "testing", "#96CEB4"),
            ("testing_room", "Room functionality tests", "testing", "#96CEB4"),
            ("testing_form", "Form tests", "testing", "#96CEB4"),
            ("testing_ai", "AI integration tests", "testing", "#96CEB4"),
            ("testing_general", "General tests", "testing", "#96CEB4"),
            
            ("ai_integration", "AI service integration", "ai", "#45B7D1"),
            ("ai_templates", "AI templates and prompts", "ai", "#45B7D1"),
            
            ("utility_development", "Development utilities", "utility", "#DDA0DD"),
            ("utility_verification", "Verification utilities", "utility", "#DDA0DD"),
            ("utility_setup", "Setup utilities", "utility", "#DDA0DD"),
        ]
        
        cursor = self.conn.cursor()
        for category, description, parent, color in categories:
            cursor.execute('''
                INSERT OR REPLACE INTO categories (name, description, parent_category, color_code)
                VALUES (?, ?, ?, ?)
            ''', (category, description, parent, color))
        
        self.conn.commit()
        print(f"✅ Populated {len(categories)} categories")
        
    def load_existing_data(self):
        """Load data from existing analysis files"""
        print("📊 Loading existing analysis data...")
        
        scripts_data = []
        
        # Load from simple_analysis.json if it exists
        if os.path.exists("simple_analysis.json"):
            with open("simple_analysis.json", "r") as f:
                data = json.load(f)
                # Process categories data
                for category, stats in data.get("categories", {}).items():
                    for script_name in stats.get("scripts", []):
                        # This is a simplified approach - in reality we'd need to scan files
                        pass
        
        # Load from duplicate_analysis.json if it exists
        if os.path.exists("duplicate_analysis.json"):
            with open("duplicate_analysis.json", "r") as f:
                data = json.load(f)
                # Process duplicate data
                pass
        
        return scripts_data
        
    def scan_and_populate_scripts(self):
        """Scan project and populate scripts table"""
        print("🔍 Scanning project and populating scripts...")
        
        cursor = self.conn.cursor()
        script_count = 0
        
        for root, dirs, files in os.walk("."):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', 'venv', 'env'}]
            
            for file in files:
                if file.endswith('.py'):
                    script_path = Path(root) / file
                    script_info = self.analyze_script(script_path)
                    if script_info:
                        self.insert_script(cursor, script_info)
                        script_count += 1
        
        self.conn.commit()
        print(f"✅ Populated {script_count} scripts")
        
    def analyze_script(self, script_path):
        """Analyze individual script and return metadata"""
        try:
            stats = script_path.stat()
            
            # Read file content
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Count lines
            lines = content.split('\n')
            line_count = len(lines)
            code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            comment_lines = line_count - code_lines
            
            # Determine category and status
            category, subcategory = self.determine_category(script_path, content)
            status = self.determine_status(script_path, content)
            
            # Extract purpose
            purpose = self.extract_purpose(content)
            
            return {
                "name": script_path.name,
                "path": str(script_path.relative_to(Path("."))),
                "size_bytes": stats.st_size,
                "size_kb": round(stats.st_size / 1024, 1),
                "lines_total": line_count,
                "lines_code": code_lines,
                "lines_comments": comment_lines,
                "category": category,
                "subcategory": subcategory,
                "status": status,
                "purpose": purpose,
                "last_modified": datetime.fromtimestamp(stats.st_mtime).isoformat()
            }
            
        except Exception as e:
            print(f"⚠️  Error analyzing {script_path}: {e}")
            return None
    
    def determine_category(self, script_path, content):
        """Determine script category"""
        path_str = str(script_path).lower()
        
        # Core application
        if script_path.name in ['app.py', 'models.py', 'config.py', 'wsgi.py']:
            return "core", "application"
        
        # Blueprint modules
        if script_path.name in ['auth.py', 'room.py', 'chat.py', 'dashboard.py']:
            return "blueprint", "module"
        
        # AI integration
        if 'openai_utils' in path_str or script_path.name in ['openai_utils.py', 'rubric_templates.py']:
            return "ai", "integration"
        
        # Tests
        if 'test_' in script_path.name:
            if 'mobile' in path_str:
                return "testing", "mobile"
            elif 'hover' in path_str or 'accordion' in path_str:
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
        if script_path.name.startswith('setup_'):
            return "utility", "setup"
        
        # Cleanup files
        if 'cleanup_files' in path_str:
            return "cleanup", "maintenance"
        
        # Chat Interface Website
        if 'Chat Interface Website' in path_str:
            return "styling", "ui"
        
        return "misc", "unknown"
    
    def determine_status(self, script_path, content):
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
    
    def extract_purpose(self, content):
        """Extract purpose from docstring or comments"""
        lines = content.split('\n')
        
        # Look for docstring
        for i, line in enumerate(lines[:10]):
            if '"""' in line or "'''" in line:
                docstring = ""
                for j in range(i, min(i + 5, len(lines))):
                    docstring += lines[j] + " "
                return docstring.strip()[:100] + "..." if len(docstring) > 100 else docstring.strip()
        
        # Look for purpose comments
        for line in lines[:10]:
            if 'purpose:' in line.lower():
                return line.strip()
        
        return "No purpose documented"
    
    def insert_script(self, cursor, script_info):
        """Insert script into database"""
        cursor.execute('''
            INSERT OR REPLACE INTO scripts 
            (name, path, size_bytes, size_kb, lines_total, lines_code, lines_comments,
             category, subcategory, status, purpose, last_modified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            script_info["name"],
            script_info["path"],
            script_info["size_bytes"],
            script_info["size_kb"],
            script_info["lines_total"],
            script_info["lines_code"],
            script_info["lines_comments"],
            script_info["category"],
            script_info["subcategory"],
            script_info["status"],
            script_info["purpose"],
            script_info["last_modified"]
        ))
    
    def create_schema_documentation(self):
        """Create schema documentation"""
        print("📋 Creating schema documentation...")
        
        schema = {
            "database_name": "script_inventory.db",
            "description": "Comprehensive script inventory management system",
            "tables": {
                "scripts": {
                    "description": "Main scripts table with metadata",
                    "columns": {
                        "id": "Primary key",
                        "name": "Script filename",
                        "path": "Relative path to script",
                        "size_bytes": "File size in bytes",
                        "size_kb": "File size in KB",
                        "lines_total": "Total number of lines",
                        "lines_code": "Number of code lines",
                        "lines_comments": "Number of comment lines",
                        "category": "Script category",
                        "subcategory": "Script subcategory",
                        "status": "Script status (active/archived/deprecated)",
                        "purpose": "Script purpose description",
                        "last_modified": "Last modification timestamp",
                        "created_at": "Record creation timestamp",
                        "updated_at": "Record update timestamp"
                    }
                },
                "categories": {
                    "description": "Script categories and their metadata",
                    "columns": {
                        "id": "Primary key",
                        "name": "Category name",
                        "description": "Category description",
                        "parent_category": "Parent category if hierarchical",
                        "color_code": "Color code for UI display",
                        "created_at": "Record creation timestamp"
                    }
                },
                "dependencies": {
                    "description": "Script dependencies and imports",
                    "columns": {
                        "id": "Primary key",
                        "script_id": "Foreign key to scripts table",
                        "dependency_name": "Name of dependency",
                        "dependency_type": "Type of dependency (internal/external)",
                        "is_external": "Whether dependency is external",
                        "created_at": "Record creation timestamp"
                    }
                },
                "duplicates": {
                    "description": "Duplicate file tracking",
                    "columns": {
                        "id": "Primary key",
                        "content_hash": "MD5 hash of file content",
                        "script_id": "Foreign key to scripts table",
                        "is_primary": "Whether this is the primary copy",
                        "recommended_keep": "Whether this copy should be kept",
                        "created_at": "Record creation timestamp"
                    }
                },
                "lifecycle": {
                    "description": "Script lifecycle tracking",
                    "columns": {
                        "id": "Primary key",
                        "script_id": "Foreign key to scripts table",
                        "action": "Action performed (archive/move/delete)",
                        "status_from": "Previous status",
                        "status_to": "New status",
                        "notes": "Action notes",
                        "performed_by": "Who performed the action",
                        "performed_at": "When action was performed"
                    }
                },
                "metadata": {
                    "description": "Additional script metadata",
                    "columns": {
                        "id": "Primary key",
                        "script_id": "Foreign key to scripts table",
                        "key": "Metadata key",
                        "value": "Metadata value",
                        "created_at": "Record creation timestamp"
                    }
                }
            }
        }
        
        with open(self.schema_file, "w") as f:
            json.dump(schema, f, indent=2)
        
        print(f"✅ Schema documentation created: {self.schema_file}")
    
    def generate_summary_report(self):
        """Generate summary report from database"""
        print("📊 Generating summary report...")
        
        cursor = self.conn.cursor()
        
        # Get basic statistics
        cursor.execute("SELECT COUNT(*) FROM scripts")
        total_scripts = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(size_bytes) FROM scripts")
        total_size = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(lines_total) FROM scripts")
        total_lines = cursor.fetchone()[0] or 0
        
        # Get category breakdown
        cursor.execute('''
            SELECT category, COUNT(*), SUM(size_bytes), SUM(lines_total)
            FROM scripts 
            GROUP BY category 
            ORDER BY COUNT(*) DESC
        ''')
        categories = cursor.fetchall()
        
        # Get status breakdown
        cursor.execute('''
            SELECT status, COUNT(*)
            FROM scripts 
            GROUP BY status 
            ORDER BY COUNT(*) DESC
        ''')
        statuses = cursor.fetchall()
        
        # Create report
        report = {
            "generated": datetime.now().isoformat(),
            "summary": {
                "total_scripts": total_scripts,
                "total_size_bytes": total_size,
                "total_size_kb": round(total_size / 1024, 1),
                "total_lines": total_lines
            },
            "categories": [
                {
                    "category": cat[0],
                    "count": cat[1],
                    "size_bytes": cat[2],
                    "size_kb": round(cat[2] / 1024, 1) if cat[2] else 0,
                    "lines": cat[3]
                }
                for cat in categories
            ],
            "statuses": [
                {
                    "status": status[0],
                    "count": status[1]
                }
                for status in statuses
            ]
        }
        
        with open("inventory_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Summary report created: inventory_report.json")
        
        # Print summary
        print(f"\n📊 INVENTORY DATABASE SUMMARY")
        print(f"="*50)
        print(f"Total Scripts: {total_scripts}")
        print(f"Total Size: {report['summary']['total_size_kb']:.1f} KB")
        print(f"Total Lines: {total_lines:,}")
        
        print(f"\n📁 Categories:")
        for cat in categories[:5]:
            print(f"   {cat[0]}: {cat[1]} scripts ({round(cat[2]/1024, 1) if cat[2] else 0:.1f} KB)")
        
        print(f"\n📊 Statuses:")
        for status in statuses:
            print(f"   {status[0]}: {status[1]} scripts")
        
        print(f"\n" + "="*50)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def main():
    """Main function"""
    print("🚀 Creating Inventory Database Structure...")
    
    db = InventoryDatabase()
    
    try:
        # Create database and tables
        db.create_database()
        
        # Populate categories
        db.populate_categories()
        
        # Scan and populate scripts
        db.scan_and_populate_scripts()
        
        # Create schema documentation
        db.create_schema_documentation()
        
        # Generate summary report
        db.generate_summary_report()
        
        print(f"\n✅ Inventory database structure complete!")
        print(f"📄 Database: {db.db_file}")
        print(f"📄 Schema: {db.schema_file}")
        print(f"📄 Report: inventory_report.json")
        print(f"📋 Ready for Phase 1.5: Document current organizational issues")
        
    finally:
        db.close()

if __name__ == "__main__":
    main() 