# Git Helper Usage Guide

## Problem
PowerShell often has display issues when running git commands, causing:
- Buffer overflow errors
- Garbled output
- Command interruption
- PSReadLine errors

## Solutions

### Option 1: Python Git Helper (Recommended)
Use the Python script for reliable git operations:

```bash
# Check status
python git_helper.py status

# Add files
python git_helper.py add templates/room/view.html templates/base.html

# Commit changes
python git_helper.py commit "Your commit message"

# Complete workflow (add + commit)
python git_helper.py workflow "Your commit message" templates/room/view.html templates/base.html static/css/components.css
```

### Option 2: Batch File
Use the batch file for simple operations:

```bash
# Check status
git_safe.bat status

# Add files
git_safe.bat add templates/room/view.html templates/base.html

# Commit changes
git_safe.bat commit "Your commit message"

# Complete workflow
git_safe.bat workflow "Your commit message" templates/room/view.html templates/base.html
```

### Option 3: PowerShell Helper (Advanced)
Load the PowerShell module:

```powershell
# Import the module
. .\git_helpers.ps1

# Use the safe functions
Get-GitStatusSafe
Add-GitFilesSafe -Files @("templates/room/view.html", "templates/base.html")
Commit-GitChangesSafe -Message "Your commit message"
```

## Best Practices

1. **Use Python helper for complex operations** - Most reliable
2. **Use batch file for simple operations** - Good for basic git commands
3. **Avoid direct PowerShell git commands** - Prone to display issues
4. **Always check status before committing** - Ensures you're committing the right files

## Common Workflow

```bash
# 1. Check what files are modified
python git_helper.py status

# 2. Add the files you want to commit
python git_helper.py add templates/room/view.html templates/base.html static/css/components.css

# 3. Commit with a descriptive message
python git_helper.py commit "Fix room page layout and improve expandable sections"

# Or do it all in one step:
python git_helper.py workflow "Fix room page layout and improve expandable sections" templates/room/view.html templates/base.html static/css/components.css
```

## Troubleshooting

- If Python helper fails, try the batch file
- If batch file fails, try the PowerShell helper
- Always check git status before committing
- Use descriptive commit messages 