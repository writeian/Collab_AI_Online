#!/usr/bin/env python3
"""
Duplicate and Unused Script Identifier
Purpose: Identify duplicate files and unused scripts
Status: [ACTIVE]
Created: 2025-01-27
Author: writeian

Usage:
    python identify_duplicates.py

Output:
    - List of duplicate files
    - List of unused scripts
    - Cleanup recommendations
"""

import os
import hashlib
import json
from collections import defaultdict
from pathlib import Path

class DuplicateIdentifier:
    def __init__(self):
        self.duplicates = defaultdict(list)
        self.unused_scripts = []
        self.import_map = defaultdict(set)
        self.script_hashes = {}
        
    def scan_project(self):
        """Scan project for duplicates and unused scripts"""
        print("🔍 Scanning for duplicates and unused scripts...")
        
        # Get all Python scripts
        scripts = []
        for root, dirs, files in os.walk("."):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', 'venv', 'env'}]
            
            for file in files:
                if file.endswith('.py'):
                    script_path = Path(root) / file
                    scripts.append(script_path)
        
        print(f"✅ Found {len(scripts)} Python scripts")
        
        # Find duplicates by content hash
        self.find_duplicates_by_content(scripts)
        
        # Find duplicates by filename
        self.find_duplicates_by_name(scripts)
        
        # Build import map
        self.build_import_map(scripts)
        
        # Find unused scripts
        self.find_unused_scripts(scripts)
        
        return scripts
    
    def find_duplicates_by_content(self, scripts):
        """Find duplicate files by content hash"""
        print("🔍 Finding duplicates by content...")
        
        for script_path in scripts:
            try:
                with open(script_path, 'rb') as f:
                    content = f.read()
                    content_hash = hashlib.md5(content).hexdigest()
                    
                    self.script_hashes[str(script_path)] = content_hash
                    
                    if content_hash in self.duplicates:
                        self.duplicates[content_hash].append(str(script_path))
                    else:
                        self.duplicates[content_hash] = [str(script_path)]
                        
            except Exception as e:
                print(f"⚠️  Error reading {script_path}: {e}")
    
    def find_duplicates_by_name(self, scripts):
        """Find duplicate files by filename"""
        print("🔍 Finding duplicates by filename...")
        
        filename_groups = defaultdict(list)
        for script_path in scripts:
            filename_groups[script_path.name].append(str(script_path))
        
        # Find files with same name in different locations
        for filename, paths in filename_groups.items():
            if len(paths) > 1:
                # Check if they're actually different content
                different_content = False
                first_hash = None
                
                for path in paths:
                    if path in self.script_hashes:
                        if first_hash is None:
                            first_hash = self.script_hashes[path]
                        elif self.script_hashes[path] != first_hash:
                            different_content = True
                            break
                
                if different_content:
                    print(f"⚠️  Same filename, different content: {filename}")
                    for path in paths:
                        print(f"     {path}")
    
    def build_import_map(self, scripts):
        """Build map of what imports what"""
        print("🔗 Building import map...")
        
        for script_path in scripts:
            try:
                with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Extract imports
                imports = self.extract_imports(content)
                
                for imp in imports:
                    self.import_map[imp].add(str(script_path))
                    
            except Exception as e:
                print(f"⚠️  Error analyzing imports in {script_path}: {e}")
    
    def extract_imports(self, content):
        """Extract Python imports from content"""
        imports = set()
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('import '):
                # Handle: import module
                parts = line[7:].split()
                if parts:
                    imports.add(parts[0])
            elif line.startswith('from ') and ' import ' in line:
                # Handle: from module import ...
                parts = line[5:].split(' import ')
                if parts:
                    imports.add(parts[0])
        
        return imports
    
    def find_unused_scripts(self, scripts):
        """Find scripts that are not imported by any other script"""
        print("🔍 Finding unused scripts...")
        
        # Get all script names (without .py extension)
        all_script_names = set()
        for script_path in scripts:
            script_name = script_path.stem  # filename without extension
            all_script_names.add(script_name)
        
        # Find scripts that are not imported
        unused = []
        for script_path in scripts:
            script_name = script_path.stem
            
            # Skip if it's a main script or has special names
            if script_name in ['app', 'main', 'wsgi', '__init__']:
                continue
            
            # Check if this script is imported by any other script
            is_imported = False
            for imported_modules in self.import_map.values():
                for importing_script in imported_modules:
                    if script_name in importing_script:
                        is_imported = True
                        break
                if is_imported:
                    break
            
            if not is_imported:
                unused.append(str(script_path))
        
        self.unused_scripts = unused
    
    def generate_cleanup_plan(self):
        """Generate cleanup plan"""
        print("📋 Generating cleanup plan...")
        
        cleanup_plan = {
            "duplicate_groups": [],
            "unused_scripts": self.unused_scripts,
            "recommendations": [],
            "estimated_savings": {
                "duplicates": 0,
                "unused": 0,
                "total": 0
            }
        }
        
        # Process duplicate groups
        for content_hash, paths in self.duplicates.items():
            if len(paths) > 1:
                # Calculate size of one copy
                try:
                    size = os.path.getsize(paths[0])
                    savings = size * (len(paths) - 1)  # Keep one copy
                    
                    cleanup_plan["duplicate_groups"].append({
                        "content_hash": content_hash,
                        "paths": paths,
                        "copies": len(paths),
                        "size_bytes": size,
                        "savings_bytes": savings,
                        "recommended_keep": self.select_best_copy(paths)
                    })
                    
                    cleanup_plan["estimated_savings"]["duplicates"] += savings
                    
                except Exception as e:
                    print(f"⚠️  Error calculating size for {paths[0]}: {e}")
        
        # Calculate unused script savings
        for script_path in self.unused_scripts:
            try:
                size = os.path.getsize(script_path)
                cleanup_plan["estimated_savings"]["unused"] += size
            except Exception as e:
                print(f"⚠️  Error calculating size for {script_path}: {e}")
        
        cleanup_plan["estimated_savings"]["total"] = (
            cleanup_plan["estimated_savings"]["duplicates"] + 
            cleanup_plan["estimated_savings"]["unused"]
        )
        
        # Generate recommendations
        if cleanup_plan["duplicate_groups"]:
            cleanup_plan["recommendations"].append(
                f"Remove {len(cleanup_plan['duplicate_groups'])} duplicate groups"
            )
        
        if cleanup_plan["unused_scripts"]:
            cleanup_plan["recommendations"].append(
                f"Remove {len(cleanup_plan['unused_scripts'])} unused scripts"
            )
        
        return cleanup_plan
    
    def select_best_copy(self, paths):
        """Select the best copy to keep from duplicate group"""
        # Prefer files in root directory
        root_files = [p for p in paths if Path(p).parent == Path('.')]
        if root_files:
            return root_files[0]
        
        # Prefer files not in backup directories
        non_backup = [p for p in paths if 'backup' not in p.lower()]
        if non_backup:
            return non_backup[0]
        
        # Return the first one
        return paths[0]
    
    def print_results(self, cleanup_plan):
        """Print analysis results"""
        print("\n" + "="*80)
        print("🔍 DUPLICATE AND UNUSED SCRIPT ANALYSIS")
        print("="*80)
        
        # Duplicate groups
        print(f"\n📋 Duplicate Groups Found: {len(cleanup_plan['duplicate_groups'])}")
        for i, group in enumerate(cleanup_plan["duplicate_groups"][:5], 1):
            print(f"\n   Group {i}:")
            print(f"     Copies: {group['copies']}")
            print(f"     Size: {group['size_bytes'] / 1024:.1f} KB")
            print(f"     Savings: {group['savings_bytes'] / 1024:.1f} KB")
            print(f"     Keep: {group['recommended_keep']}")
            for path in group['paths']:
                print(f"     • {path}")
        
        if len(cleanup_plan["duplicate_groups"]) > 5:
            print(f"     ... and {len(cleanup_plan['duplicate_groups']) - 5} more groups")
        
        # Unused scripts
        print(f"\n🗑️  Unused Scripts Found: {len(cleanup_plan['unused_scripts'])}")
        for script in cleanup_plan["unused_scripts"][:10]:
            print(f"   • {script}")
        
        if len(cleanup_plan["unused_scripts"]) > 10:
            print(f"   ... and {len(cleanup_plan['unused_scripts']) - 10} more")
        
        # Savings summary
        savings = cleanup_plan["estimated_savings"]
        print(f"\n💰 Estimated Savings:")
        print(f"   Duplicates: {savings['duplicates'] / 1024:.1f} KB")
        print(f"   Unused: {savings['unused'] / 1024:.1f} KB")
        print(f"   Total: {savings['total'] / 1024:.1f} KB")
        
        # Recommendations
        print(f"\n🚨 Recommendations:")
        for rec in cleanup_plan["recommendations"]:
            print(f"   • {rec}")
        
        print("\n" + "="*80)
    
    def save_results(self, cleanup_plan):
        """Save results to JSON file"""
        with open("duplicate_analysis.json", "w") as f:
            json.dump(cleanup_plan, f, indent=2, default=str)
        
        print(f"✅ Results saved to: duplicate_analysis.json")

def main():
    """Main function"""
    print("🚀 Starting Duplicate and Unused Script Analysis...")
    
    identifier = DuplicateIdentifier()
    scripts = identifier.scan_project()
    
    cleanup_plan = identifier.generate_cleanup_plan()
    identifier.print_results(cleanup_plan)
    identifier.save_results(cleanup_plan)
    
    print(f"\n✅ Analysis complete!")
    print(f"📄 Results saved to: duplicate_analysis.json")
    print(f"📋 Ready for Phase 1.4: Create inventory database structure")

if __name__ == "__main__":
    main() 