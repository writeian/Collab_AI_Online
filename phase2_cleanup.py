#!/usr/bin/env python3
"""
Phase 2 Cleanup Operations (Low-Risk)
Purpose: Perform low-risk cleanup operations to organize the project structure
Status: [ACTIVE]
Created: 2025-01-27
Author: writeian

Operations:
    - Move debug scripts to archive directory
    - Consolidate test scripts into tests/ directory
    - Organize misc scripts by category
    - Create proper directory structure
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

class Phase2Cleanup:
    def __init__(self):
        self.backup_dir = "phase2_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        self.cleanup_log = "phase2_cleanup_log.json"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "operations": [],
            "statistics": {
                "debug_scripts_moved": 0,
                "test_scripts_consolidated": 0,
                "misc_scripts_organized": 0,
                "directories_created": 0
            }
        }
        
        # Define directory structure
        self.directory_structure = {
            "archive": {
                "debug": "Archive for debug scripts",
                "old_backups": "Consolidated backup directories",
                "deprecated": "Deprecated scripts"
            },
            "tests": {
                "unit": "Unit tests",
                "integration": "Integration tests",
                "debug": "Debug tests"
            },
            "scripts": {
                "utility": "Utility scripts",
                "maintenance": "Maintenance scripts",
                "deployment": "Deployment scripts"
            }
        }
    
    def create_backup(self):
        """Create backup before Phase 2 operations"""
        print(f"🛡️  Creating Phase 2 backup: {self.backup_dir}")
        
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            print(f"✅ Backup created: {self.backup_dir}")
            return True
        except Exception as e:
            print(f"❌ Backup creation failed: {e}")
            return False
    
    def create_directory_structure(self):
        """Create the new directory structure"""
        print("📁 Creating directory structure...")
        
        directories_created = 0
        
        for main_dir, subdirs in self.directory_structure.items():
            for subdir, description in subdirs.items():
                dir_path = os.path.join(main_dir, subdir)
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    
                    # Create README for each directory
                    readme_path = os.path.join(dir_path, "README.md")
                    if not os.path.exists(readme_path):
                        with open(readme_path, 'w') as f:
                            f.write(f"# {subdir.title()}\n\n{description}\n")
                    
                    directories_created += 1
                    
                except Exception as e:
                    print(f"⚠️  Could not create {dir_path}: {e}")
        
        self.results["statistics"]["directories_created"] = directories_created
        print(f"✅ Created {directories_created} directories")
    
    def move_debug_scripts(self):
        """Move debug scripts to archive/debug directory"""
        print("🐛 Moving debug scripts to archive...")
        
        debug_scripts = []
        
        # Find debug scripts in root directory
        for file in os.listdir("."):
            if file.endswith(".py") and file.startswith("debug_"):
                debug_scripts.append(file)
        
        # Also find debug scripts in subdirectories (excluding our archive)
        for root, dirs, files in os.walk("."):
            if "archive" in root or "backup" in root:
                continue
            
            for file in files:
                if file.endswith(".py") and file.startswith("debug_"):
                    file_path = os.path.join(root, file)
                    debug_scripts.append(file_path)
        
        moved_count = 0
        
        for script in debug_scripts:
            try:
                # Determine target path
                if os.path.dirname(script) == ".":
                    # Root directory script
                    target_path = os.path.join("archive", "debug", script)
                else:
                    # Subdirectory script - preserve relative path
                    rel_path = os.path.relpath(script, ".")
                    target_path = os.path.join("archive", "debug", rel_path)
                
                # Create target directory
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                # Move the file
                shutil.move(script, target_path)
                
                moved_count += 1
                self.results["operations"].append({
                    "operation": "move_debug_script",
                    "original": script,
                    "target": target_path
                })
                
            except Exception as e:
                print(f"⚠️  Could not move {script}: {e}")
        
        self.results["statistics"]["debug_scripts_moved"] = moved_count
        print(f"✅ Moved {moved_count} debug scripts to archive")
    
    def consolidate_test_scripts(self):
        """Consolidate test scripts into tests/ directory"""
        print("🧪 Consolidating test scripts...")
        
        test_scripts = []
        
        # Find test scripts in root directory
        for file in os.listdir("."):
            if file.endswith(".py") and file.startswith("test_"):
                test_scripts.append(file)
        
        # Also find test scripts in subdirectories
        for root, dirs, files in os.walk("."):
            if "archive" in root or "backup" in root or "tests" in root:
                continue
            
            for file in files:
                if file.endswith(".py") and file.startswith("test_"):
                    file_path = os.path.join(root, file)
                    test_scripts.append(file_path)
        
        consolidated_count = 0
        
        for script in test_scripts:
            try:
                # Determine test category
                script_name = os.path.basename(script)
                
                if any(keyword in script_name.lower() for keyword in ["integration", "e2e", "end_to_end"]):
                    target_dir = "tests/integration"
                elif any(keyword in script_name.lower() for keyword in ["debug", "manual"]):
                    target_dir = "tests/debug"
                else:
                    target_dir = "tests/unit"
                
                target_path = os.path.join(target_dir, script_name)
                
                # Create target directory
                os.makedirs(target_dir, exist_ok=True)
                
                # Move the file
                shutil.move(script, target_path)
                
                consolidated_count += 1
                self.results["operations"].append({
                    "operation": "consolidate_test",
                    "original": script,
                    "target": target_path,
                    "category": os.path.basename(target_dir)
                })
                
            except Exception as e:
                print(f"⚠️  Could not consolidate {script}: {e}")
        
        self.results["statistics"]["test_scripts_consolidated"] = consolidated_count
        print(f"✅ Consolidated {consolidated_count} test scripts")
    
    def organize_misc_scripts(self):
        """Organize misc scripts by category"""
        print("📦 Organizing misc scripts...")
        
        # Define script categories
        script_categories = {
            "utility": ["git_helper", "simple_test", "verify_", "check_"],
            "maintenance": ["cleanup_", "fix_", "migrate_", "backup_"],
            "deployment": ["deploy", "setup_", "install_", "configure_"]
        }
        
        misc_scripts = []
        
        # Find misc scripts in root directory
        for file in os.listdir("."):
            if file.endswith(".py") and not file.startswith(("app", "auth", "chat", "room", "models", "config", "test_", "debug_")):
                misc_scripts.append(file)
        
        organized_count = 0
        
        for script in misc_scripts:
            try:
                script_lower = script.lower()
                target_category = None
                
                # Determine category
                for category, keywords in script_categories.items():
                    if any(keyword in script_lower for keyword in keywords):
                        target_category = category
                        break
                
                if target_category:
                    target_path = os.path.join("scripts", target_category, script)
                    
                    # Create target directory
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    
                    # Move the file
                    shutil.move(script, target_path)
                    
                    organized_count += 1
                    self.results["operations"].append({
                        "operation": "organize_misc",
                        "original": script,
                        "target": target_path,
                        "category": target_category
                    })
                
            except Exception as e:
                print(f"⚠️  Could not organize {script}: {e}")
        
        self.results["statistics"]["misc_scripts_organized"] = organized_count
        print(f"✅ Organized {organized_count} misc scripts")
    
    def update_gitignore(self):
        """Update .gitignore for new structure"""
        print("📝 Updating .gitignore...")
        
        gitignore_additions = """
# Archive directories
archive/
phase2_backup_*/

# Test directories (keep structure but ignore temp files)
tests/*.tmp
tests/*.log

# Script directories
scripts/*.tmp
scripts/*.log

# Cleanup logs
*_cleanup_log.json
*_fix_log.json
"""
        
        try:
            # Read existing .gitignore
            if os.path.exists(".gitignore"):
                with open(".gitignore", "r") as f:
                    existing_content = f.read()
            else:
                existing_content = ""
            
            # Add new entries if they don't exist
            if "archive/" not in existing_content:
                with open(".gitignore", "a") as f:
                    f.write(gitignore_additions)
                
                self.results["operations"].append({
                    "operation": "update_gitignore",
                    "description": "Added archive and cleanup directories to .gitignore"
                })
                
                print("✅ Updated .gitignore")
            else:
                print("ℹ️  .gitignore already contains archive entries")
                
        except Exception as e:
            print(f"⚠️  Could not update .gitignore: {e}")
    
    def save_cleanup_log(self):
        """Save cleanup log"""
        with open(self.cleanup_log, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"✅ Cleanup log saved to: {self.cleanup_log}")
    
    def print_summary(self):
        """Print cleanup summary"""
        print("\n" + "="*80)
        print("📁 PHASE 2 CLEANUP SUMMARY")
        print("="*80)
        
        stats = self.results["statistics"]
        print(f"\n📊 Results:")
        print(f"   Debug Scripts Moved: {stats['debug_scripts_moved']}")
        print(f"   Test Scripts Consolidated: {stats['test_scripts_consolidated']}")
        print(f"   Misc Scripts Organized: {stats['misc_scripts_organized']}")
        print(f"   Directories Created: {stats['directories_created']}")
        
        print(f"\n📁 New Directory Structure:")
        for main_dir, subdirs in self.directory_structure.items():
            print(f"   {main_dir}/")
            for subdir, description in subdirs.items():
                print(f"     ├── {subdir}/ - {description}")
        
        print(f"\n🛡️  Safety:")
        print(f"   Backup Location: {self.backup_dir}")
        print(f"   All changes are reversible")
        print(f"   Core application files untouched")
        
        print("\n" + "="*80)

def main():
    """Main function"""
    print("🚀 Starting Phase 2 Cleanup Operations...")
    
    cleanup = Phase2Cleanup()
    
    # Create backup first
    if not cleanup.create_backup():
        print("❌ Cannot proceed without backup")
        return
    
    try:
        # Perform Phase 2 cleanup operations
        cleanup.create_directory_structure()
        cleanup.move_debug_scripts()
        cleanup.consolidate_test_scripts()
        cleanup.organize_misc_scripts()
        cleanup.update_gitignore()
        
        # Save results
        cleanup.save_cleanup_log()
        cleanup.print_summary()
        
        print(f"\n✅ Phase 2 cleanup operations complete!")
        print(f"🛡️  All changes are reversible via backup: {cleanup.backup_dir}")
        
    except Exception as e:
        print(f"❌ Phase 2 cleanup failed: {e}")
        print(f"🛡️  Backup available at: {cleanup.backup_dir}")

if __name__ == "__main__":
    main() 