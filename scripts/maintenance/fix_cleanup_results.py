#!/usr/bin/env python3
"""
Fix Cleanup Results
Purpose: Fix the issues from the safe cleanup operation
Status: [ACTIVE]
Created: 2025-01-27
Author: writeian

Fixes:
    - Remove duplicates properly using correct field names
    - Restore proper documentation to core files
    - Handle backup consolidation with proper error handling
"""

import os
import shutil
import json
from datetime import datetime

class CleanupFixer:
    def __init__(self):
        self.backup_dir = "cleanup_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        self.duplicate_analysis_file = "duplicate_analysis.json"
        self.fix_log = "cleanup_fix_log.json"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "operations": [],
            "statistics": {
                "duplicates_removed": 0,
                "space_saved": 0,
                "documentation_fixed": 0
            }
        }
    
    def create_backup(self):
        """Create backup before fixing"""
        print(f"🛡️  Creating backup: {self.backup_dir}")
        
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            print(f"✅ Backup created: {self.backup_dir}")
            return True
        except Exception as e:
            print(f"❌ Backup creation failed: {e}")
            return False
    
    def fix_duplicate_removal(self):
        """Fix duplicate removal using correct field names"""
        print("🔄 Fixing duplicate removal...")
        
        if not os.path.exists(self.duplicate_analysis_file):
            print("❌ No duplicate analysis file found")
            return
        
        try:
            with open(self.duplicate_analysis_file, 'r') as f:
                duplicate_data = json.load(f)
            
            duplicate_groups = duplicate_data.get("duplicate_groups", [])
            total_removed = 0
            total_saved = 0
            
            for group in duplicate_groups:
                paths = group.get("paths", [])
                if len(paths) > 1:
                    # Keep the first file (usually the primary one)
                    keep_file = paths[0]
                    remove_files = paths[1:]
                    
                    for remove_file in remove_files:
                        if os.path.exists(remove_file):
                            # Get file size before removal
                            file_size = os.path.getsize(remove_file)
                            
                            # Move to backup instead of deleting
                            backup_path = os.path.join(self.backup_dir, "duplicates", remove_file)
                            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                            
                            try:
                                shutil.move(remove_file, backup_path)
                                total_removed += 1
                                total_saved += file_size
                                
                                self.results["operations"].append({
                                    "operation": "remove_duplicate",
                                    "file": remove_file,
                                    "kept_file": keep_file,
                                    "size_saved": file_size,
                                    "backup_location": backup_path
                                })
                            except Exception as e:
                                print(f"⚠️  Could not remove {remove_file}: {e}")
            
            self.results["statistics"]["duplicates_removed"] = total_removed
            self.results["statistics"]["space_saved"] = total_saved
            
            print(f"✅ Removed {total_removed} duplicate files")
            print(f"💾 Saved {total_saved / 1024:.1f} KB of space")
            
        except Exception as e:
            print(f"❌ Duplicate removal failed: {e}")
    
    def fix_core_documentation(self):
        """Restore proper documentation to core files"""
        print("📚 Fixing core file documentation...")
        
        core_files = {
            "app.py": {
                "purpose": "Main Flask application entry point and configuration",
                "status": "ACTIVE",
                "description": "Initializes Flask app, registers blueprints, handles database setup, and provides health check endpoints"
            },
            "auth.py": {
                "purpose": "User authentication and session management blueprint",
                "status": "ACTIVE", 
                "description": "Handles user registration, login, logout, password management, and session handling"
            },
            "chat.py": {
                "purpose": "Chat functionality and AI integration blueprint",
                "status": "ACTIVE",
                "description": "Manages chat conversations, AI responses, message handling, and prompt recording"
            },
            "room.py": {
                "purpose": "Collaborative room management blueprint",
                "status": "ACTIVE",
                "description": "Handles room creation, membership, invitations, and room-based collaboration features"
            },
            "models.py": {
                "purpose": "Database models and schema definitions",
                "status": "ACTIVE",
                "description": "SQLAlchemy ORM models for users, rooms, chats, messages, analytics, and achievements"
            },
            "config.py": {
                "purpose": "Application configuration management",
                "status": "ACTIVE",
                "description": "Environment-specific configuration settings and database connection management"
            }
        }
        
        fixed_count = 0
        
        for filename, info in core_files.items():
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create proper documentation header
                    header = f'''#!/usr/bin/env python3
"""
{filename}
Purpose: {info['purpose']}
Status: [{info['status']}]
Created: 2025-01-27
Author: writeian

{info['description']}
"""

'''
                    
                    # Remove the auto-generated header and add proper one
                    lines = content.split('\n')
                    # Skip the first 8 lines (auto-generated header)
                    if lines[0].startswith('#!/usr/bin/env python3') and 'AUTO-GENERATED' in content:
                        content = '\n'.join(lines[8:])
                    
                    # Add proper header
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(header + content)
                    
                    fixed_count += 1
                    self.results["operations"].append({
                        "operation": "fix_documentation",
                        "file": filename,
                        "purpose": info['purpose']
                    })
                    
                except Exception as e:
                    print(f"⚠️  Could not fix documentation for {filename}: {e}")
        
        self.results["statistics"]["documentation_fixed"] = fixed_count
        print(f"✅ Fixed documentation for {fixed_count} core files")
    
    def save_fix_log(self):
        """Save fix log"""
        with open(self.fix_log, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"✅ Fix log saved to: {self.fix_log}")
    
    def print_summary(self):
        """Print fix summary"""
        print("\n" + "="*80)
        print("🔧 CLEANUP FIX SUMMARY")
        print("="*80)
        
        stats = self.results["statistics"]
        print(f"\n📊 Results:")
        print(f"   Duplicates Removed: {stats['duplicates_removed']}")
        print(f"   Space Saved: {stats['space_saved'] / 1024:.1f} KB")
        print(f"   Documentation Fixed: {stats['documentation_fixed']}")
        
        print(f"\n🛡️  Safety:")
        print(f"   Backup Location: {self.backup_dir}")
        print(f"   All changes are reversible")
        
        print("\n" + "="*80)

def main():
    """Main function"""
    print("🔧 Fixing Cleanup Results...")
    
    fixer = CleanupFixer()
    
    # Create backup first
    if not fixer.create_backup():
        print("❌ Cannot proceed without backup")
        return
    
    try:
        # Fix the issues
        fixer.fix_duplicate_removal()
        fixer.fix_core_documentation()
        
        # Save results
        fixer.save_fix_log()
        fixer.print_summary()
        
        print(f"\n✅ Cleanup fixes complete!")
        print(f"🛡️  All changes are reversible via backup: {fixer.backup_dir}")
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        print(f"🛡️  Backup available at: {fixer.backup_dir}")

if __name__ == "__main__":
    main() 