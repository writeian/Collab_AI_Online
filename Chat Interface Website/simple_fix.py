#!/usr/bin/env python3
"""
Simple fix for the Flask import issue in chat.py
Run this script from your AI Collab Online project directory
"""

import os
import sys
from pathlib import Path

def fix_chat_imports():
    """Fix the missing current_app import in chat.py"""
    
    # Get the current directory
    current_dir = Path.cwd()
    chat_file = current_dir / "chat.py"
    
    print(f"🔧 Looking for chat.py in: {current_dir}")
    
    if not chat_file.exists():
        print("❌ Error: chat.py not found in current directory")
        print("Please run this script from your AI Collab Online project root")
        return False
    
    print(f"✅ Found chat.py: {chat_file}")
    
    # Read the current file
    with open(chat_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if current_app is already imported
    if 'current_app' in content.split('\n')[0:20]:
        print("✅ current_app import already exists")
        return True
    
    # Find the Flask imports section
    lines = content.split('\n')
    
    # Look for existing Flask imports
    flask_import_line = None
    for i, line in enumerate(lines):
        if line.strip().startswith('from flask import'):
            flask_import_line = i
            break
    
    if flask_import_line is not None:
        # Add current_app to existing Flask import
        existing_import = lines[flask_import_line]
        if 'current_app' not in existing_import:
            # Add current_app to the import
            if existing_import.endswith(','):
                lines[flask_import_line] = existing_import + ' current_app'
            else:
                lines[flask_import_line] = existing_import + ', current_app'
            print(f"✅ Added current_app to existing Flask import")
        else:
            print("✅ current_app already in Flask import")
    else:
        # Add new Flask import line
        lines.insert(0, 'from flask import current_app')
        print("✅ Added new Flask import with current_app")
    
    # Write the fixed content back
    with open(chat_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Fixed imports in {chat_file}")
    return True

def main():
    """Main function to fix the chat.py imports"""
    print("🔧 Fixing Flask imports in chat.py")
    print("=" * 40)
    
    success = fix_chat_imports()
    
    if success:
        print("\n🎉 Import fix complete!")
        print("Now try your chat functionality again.")
        print("\n📋 Next steps:")
        print("1. Test your chat functionality")
        print("2. If you haven't already, run the styling setup script:")
        print("   python setup_ai_collab_styling.py")
    else:
        print("\n❌ Fix failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 