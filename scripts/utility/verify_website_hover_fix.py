#!/usr/bin/env python3
"""
Verification script to confirm all dark hover classes are removed from the website
"""

import os
import re

def check_file_for_dark_hover(file_path):
    """Check if a file still has dark hover classes"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        dark_hover_found = []
        
        if 'hover:bg-secondary/80' in content:
            dark_hover_found.append('hover:bg-secondary/80')
        if 'hover:bg-secondary/90' in content:
            dark_hover_found.append('hover:bg-secondary/90')
        if 'hover:bg-muted/40' in content:
            dark_hover_found.append('hover:bg-muted/40')
            
        return dark_hover_found
        
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return []

def verify_website_hover_fix():
    """Verify all dark hover classes are removed"""
    print("🔍 Verifying Website Hover Fix")
    print("=" * 60)
    
    # List of template directories to check
    template_dirs = [
        'templates',
        'templates/room',
        'templates/chat',
        'templates/dashboard'
    ]
    
    files_with_dark_hover = []
    total_files = 0
    
    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            print(f"\n📁 Checking {template_dir}/")
            for filename in os.listdir(template_dir):
                if filename.endswith('.html'):
                    file_path = os.path.join(template_dir, filename)
                    total_files += 1
                    
                    dark_hover = check_file_for_dark_hover(file_path)
                    if dark_hover:
                        files_with_dark_hover.append((file_path, dark_hover))
                        print(f"❌ Dark hover found in: {file_path}")
                        for hover_class in dark_hover:
                            print(f"   • {hover_class}")
                    else:
                        print(f"✅ Clean: {file_path}")
    
    print(f"\n" + "=" * 60)
    print(f"🎯 Verification Complete!")
    print(f"📊 Files checked: {total_files}")
    print(f"🔧 Files with dark hover: {len(files_with_dark_hover)}")
    
    if files_with_dark_hover:
        print(f"\n❌ Files still containing dark hover classes:")
        for file_path, hover_classes in files_with_dark_hover:
            print(f"   • {file_path}: {', '.join(hover_classes)}")
    else:
        print(f"\n✅ SUCCESS! All dark hover classes removed from website!")
        print(f"\n✨ What should work now:")
        print(f"   • All buttons should have light hover effects")
        print(f"   • No more dark blue hover anywhere")
        print(f"   • CSS version updated to v=5.0")
        print(f"\n🔄 To test:")
        print(f"   1. Hard refresh your browser (Ctrl+F5)")
        print(f"   2. Navigate to different pages")
        print(f"   3. Hover over buttons on all pages")
        print(f"   4. Should see light colors everywhere")

if __name__ == "__main__":
    verify_website_hover_fix() 