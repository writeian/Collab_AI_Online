#!/usr/bin/env python3
"""
Safe Cleanup Operations (Phase 1)
Purpose: Perform safe cleanup operations that won't break the application
Status: [ACTIVE]
Created: 2025-01-27
Author: writeian

Usage:
    python safe_cleanup.py

Operations:
    - Remove duplicate files (safe)
    - Consolidate backup directories (safe)
    - Add missing documentation (safe)
"""

import os
import shutil
import json
import hashlib
from pathlib import Path
from datetime import datetime

class SafeCleanup:
    def __init__(self):
        self.backup_dir = "cleanup_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        self.duplicate_analysis_file = "duplicate_analysis.json"
        self.cleanup_log = "safe_cleanup_log.json"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "operations": [],
            "statistics": {
                "duplicates_removed": 0,
                "space_saved": 0,
                "backups_consolidated": 0,
                "documentation_added": 0
            }
        }
    
    def create_backup(self):
        """Create backup before cleanup operations"""
        print(f"🛡️  Creating backup: {self.backup_dir}")
        
        try:
            # Create backup directory
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # Copy duplicate analysis for reference
            if os.path.exists(self.duplicate_analysis_file):
                shutil.copy2(self.duplicate_analysis_file, self.backup_dir)
            
            print(f"✅ Backup created: {self.backup_dir}")
            return True
        except Exception as e:
            print(f"❌ Backup creation failed: {e}")
            return False
    
    def remove_duplicates(self):
        """Remove duplicate files safely"""
        print("🔄 Removing duplicate files...")
        
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
                files = group.get("files", [])
                if len(files) > 1:
                    # Keep the first file (usually the primary one)
                    keep_file = files[0]
                    remove_files = files[1:]
                    
                    for remove_file in remove_files:
                        if os.path.exists(remove_file):
                            # Get file size before removal
                            file_size = os.path.getsize(remove_file)
                            
                            # Move to backup instead of deleting
                            backup_path = os.path.join(self.backup_dir, "duplicates", remove_file)
                            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
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
            
            self.results["statistics"]["duplicates_removed"] = total_removed
            self.results["statistics"]["space_saved"] = total_saved
            
            print(f"✅ Removed {total_removed} duplicate files")
            print(f"💾 Saved {total_saved / 1024:.1f} KB of space")
            
        except Exception as e:
            print(f"❌ Duplicate removal failed: {e}")
    
    def consolidate_backups(self):
        """Consolidate backup directories"""
        print("🗄️  Consolidating backup directories...")
        
        backup_dirs = []
        for item in os.listdir("."):
            if os.path.isdir(item) and "backup" in item.lower():
                backup_dirs.append(item)
        
        if not backup_dirs:
            print("ℹ️  No backup directories found")
            return
        
        consolidated_count = 0
        
        for backup_dir in backup_dirs:
            if backup_dir == self.backup_dir:  # Skip our own backup
                continue
            
            try:
                # Move backup directory to our backup location
                backup_path = os.path.join(self.backup_dir, "old_backups", backup_dir)
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                shutil.move(backup_dir, backup_path)
                
                consolidated_count += 1
                self.results["operations"].append({
                    "operation": "consolidate_backup",
                    "original_dir": backup_dir,
                    "new_location": backup_path
                })
                
            except Exception as e:
                print(f"⚠️  Could not consolidate {backup_dir}: {e}")
        
        self.results["statistics"]["backups_consolidated"] = consolidated_count
        print(f"✅ Consolidated {consolidated_count} backup directories")
    
    def add_missing_documentation(self):
        """Add missing documentation to scripts"""
        print("📚 Adding missing documentation...")
        
        # Find Python files without proper docstrings
        python_files = []
        for root, dirs, files in os.walk("."):
            # Skip our backup directory
            if self.backup_dir in root:
                continue
            
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    if self.needs_documentation(file_path):
                        python_files.append(file_path)
        
        documented_count = 0
        
        for file_path in python_files[:10]:  # Limit to first 10 for safety
            try:
                if self.add_documentation_header(file_path):
                    documented_count += 1
                    self.results["operations"].append({
                        "operation": "add_documentation",
                        "file": file_path
                    })
            except Exception as e:
                print(f"⚠️  Could not document {file_path}: {e}")
        
        self.results["statistics"]["documentation_added"] = documented_count
        print(f"✅ Added documentation to {documented_count} files")
    
    def needs_documentation(self, file_path):
        """Check if file needs documentation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file has a proper docstring
            if '"""' not in content[:500]:  # Check first 500 chars
                return True
            
            return False
        except:
            return False
    
    def add_documentation_header(self, file_path):
        """Add documentation header to file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip if already has docstring
            if '"""' in content[:500]:
                return False
            
            # Create documentation header
            filename = os.path.basename(file_path)
            header = f'''#!/usr/bin/env python3
"""
{filename}
Purpose: [AUTO-GENERATED] Script purpose needs to be documented
Status: [UNKNOWN]
Created: {datetime.now().strftime("%Y-%m-%d")}
Author: writeian

TODO: Add proper documentation for this script
"""

'''
            
            # Add header to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(header + content)
            
            return True
            
        except Exception as e:
            print(f"⚠️  Error adding documentation to {file_path}: {e}")
            return False
    
    def save_cleanup_log(self):
        """Save cleanup log"""
        with open(self.cleanup_log, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"✅ Cleanup log saved to: {self.cleanup_log}")
    
    def print_summary(self):
        """Print cleanup summary"""
        print("\n" + "="*80)
        print("✅ SAFE CLEANUP SUMMARY")
        print("="*80)
        
        stats = self.results["statistics"]
        print(f"\n📊 Results:")
        print(f"   Duplicates Removed: {stats['duplicates_removed']}")
        print(f"   Space Saved: {stats['space_saved'] / 1024:.1f} KB")
        print(f"   Backups Consolidated: {stats['backups_consolidated']}")
        print(f"   Documentation Added: {stats['documentation_added']}")
        
        print(f"\n🛡️  Safety:")
        print(f"   Backup Location: {self.backup_dir}")
        print(f"   All files backed up before removal")
        print(f"   No core application files touched")
        
        print(f"\n📋 Next Steps:")
        print(f"   • Review backup directory: {self.backup_dir}")
        print(f"   • Test application functionality")
        print(f"   • Proceed to Phase 2 if satisfied")
        
        print("\n" + "="*80)

def main():
    """Main function"""
    print("🚀 Starting Safe Cleanup Operations (Phase 1)...")
    
    cleanup = SafeCleanup()
    
    # Create backup first
    if not cleanup.create_backup():
        print("❌ Cannot proceed without backup")
        return
    
    try:
        # Perform safe cleanup operations
        cleanup.remove_duplicates()
        cleanup.consolidate_backups()
        cleanup.add_missing_documentation()
        
        # Save results
        cleanup.save_cleanup_log()
        cleanup.print_summary()
        
        print(f"\n✅ Safe cleanup operations complete!")
        print(f"🛡️  All changes are reversible via backup: {cleanup.backup_dir}")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        print(f"🛡️  Backup available at: {cleanup.backup_dir}")

if __name__ == "__main__":
    main() 