#!/usr/bin/env python3
"""
Git Helper Script for AI_Collab_Online
Provides reliable git operations without PowerShell display issues
"""

import subprocess
import sys
import os

def run_git_command(command, capture_output=True):
    """Run a git command and return the result"""
    try:
        result = subprocess.run(
            ['git'] + command,
            capture_output=capture_output,
            text=True,
            check=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
        return None

def git_status():
    """Get git status in a clean format"""
    result = run_git_command(['status', '--porcelain'])
    if result:
        return result.stdout.strip()
    return None

def git_add(files):
    """Add files to git"""
    if isinstance(files, str):
        files = [files]
    
    result = run_git_command(['add'] + files)
    if result:
        print("✅ Files added successfully")
        return True
    else:
        print("❌ Failed to add files")
        return False

def git_commit(message):
    """Commit changes with message"""
    result = run_git_command(['commit', '-m', message])
    if result:
        print("✅ Commit successful")
        return True
    else:
        print("❌ Failed to commit")
        return False

def git_workflow(files, message):
    """Complete git workflow: add and commit"""
    print("🔄 Starting git workflow...")
    
    # Add files
    if not git_add(files):
        return False
    
    # Commit changes
    if not git_commit(message):
        return False
    
    print("✅ Git workflow completed successfully")
    return True

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python git_helper.py status")
        print("  python git_helper.py add file1 file2 file3")
        print("  python git_helper.py commit 'commit message'")
        print("  python git_helper.py workflow 'commit message' file1 file2 file3")
        return
    
    command = sys.argv[1]
    
    if command == "status":
        status = git_status()
        if status:
            print("Git Status:")
            print(status)
        else:
            print("Failed to get git status")
    
    elif command == "add":
        if len(sys.argv) < 3:
            print("Usage: python git_helper.py add file1 file2 file3")
            return
        files = sys.argv[2:]
        git_add(files)
    
    elif command == "commit":
        if len(sys.argv) < 3:
            print("Usage: python git_helper.py commit 'commit message'")
            return
        message = sys.argv[2]
        git_commit(message)
    
    elif command == "workflow":
        if len(sys.argv) < 4:
            print("Usage: python git_helper.py workflow 'commit message' file1 file2 file3")
            return
        message = sys.argv[2]
        files = sys.argv[3:]
        git_workflow(files, message)
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main() 