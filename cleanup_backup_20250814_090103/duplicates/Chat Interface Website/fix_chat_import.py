#!/usr/bin/env python3
"""
Fix for the Flask import issue in chat.py
This script will add the missing import for current_app
"""

import re
from pathlib import Path

def fix_chat_imports(chat_file_path):
    """Fix the missing current_app import in chat.py"""
    
    # Read the current file
    with open(chat_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if current_app is already imported
    if 'from flask import current_app' in content or 'current_app' in content.split('\n')[0:20]:
        print("✅ current_app import already exists")
        return
    
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
    else:
        # Add new Flask import line
        lines.insert(0, 'from flask import current_app')
    
    # Write the fixed content back
    with open(chat_file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Fixed imports in {chat_file_path}")

def main():
    """Main function to fix the chat.py imports"""
    print("🔧 Fixing Flask imports in chat.py")
    print("=" * 40)
    
    # Look for chat.py in the current directory
    chat_file = Path.cwd() / "chat.py"
    
    if not chat_file.exists():
        print("❌ Error: chat.py not found in current directory")
        print("Please run this script from your AI Collab Online project root")
        return
    
    fix_chat_imports(chat_file)
    
    print("\n🎉 Import fix complete!")
    print("Now try your chat functionality again.")

if __name__ == "__main__":
    main() 