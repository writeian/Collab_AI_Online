#!/usr/bin/env python3
"""
Script to fix all dark hover classes across the entire website
"""

import os
import re

def fix_hover_classes_in_file(file_path):
    """Fix hover classes in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix all dark hover classes
        content = re.sub(r'hover:bg-secondary/80', 'hover:bg-gray-100', content)
        content = re.sub(r'hover:bg-secondary/90', 'hover:bg-gray-100', content)
        content = re.sub(r'hover:bg-muted/40', 'hover:bg-gray-50', content)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def fix_all_hover_classes():
    """Fix hover classes in all HTML files"""
    print("🎯 Fixing All Dark Hover Classes Across Website")
    print("=" * 60)
    
    # List of template directories to process
    template_dirs = [
        'templates',
        'templates/room',
        'templates/chat',
        'templates/dashboard'
    ]
    
    files_fixed = 0
    total_files = 0
    
    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            print(f"\n📁 Processing {template_dir}/")
            for filename in os.listdir(template_dir):
                if filename.endswith('.html'):
                    file_path = os.path.join(template_dir, filename)
                    total_files += 1
                    
                    if fix_hover_classes_in_file(file_path):
                        print(f"✅ Fixed: {file_path}")
                        files_fixed += 1
                    else:
                        print(f"⏭️  No changes: {file_path}")
    
    print(f"\n" + "=" * 60)
    print(f"🎯 Fix Complete!")
    print(f"📊 Files processed: {total_files}")
    print(f"🔧 Files fixed: {files_fixed}")
    print(f"\n✨ All dark hover classes replaced:")
    print(f"   • hover:bg-secondary/80 → hover:bg-gray-100")
    print(f"   • hover:bg-secondary/90 → hover:bg-gray-100")
    print(f"   • hover:bg-muted/40 → hover:bg-gray-50")
    print(f"\n🔄 Next steps:")
    print(f"   1. Update CSS version in base.html")
    print(f"   2. Hard refresh browser to see changes")

if __name__ == "__main__":
    fix_all_hover_classes() 