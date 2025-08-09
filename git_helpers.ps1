# Git Helper Script for AI_Collab_Online
# This script provides improved git commands that handle PowerShell display issues

# Disable PSReadLine temporarily for git operations
function Disable-PSReadLine {
    if (Get-Module PSReadLine) {
        Remove-Module PSReadLine -Force
    }
}

# Re-enable PSReadLine after git operations
function Enable-PSReadLine {
    Import-Module PSReadLine -Force
}

# Safe git status command
function Get-GitStatusSafe {
    Disable-PSReadLine
    try {
        git status --porcelain
    }
    finally {
        Enable-PSReadLine
    }
}

# Safe git add command
function Add-GitFilesSafe {
    param([string[]]$Files)
    
    Disable-PSReadLine
    try {
        git add $Files
        Write-Host "Files added successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "Error adding files: $($_.Exception.Message)" -ForegroundColor Red
    }
    finally {
        Enable-PSReadLine
    }
}

# Safe git commit command
function Commit-GitChangesSafe {
    param([string]$Message)
    
    Disable-PSReadLine
    try {
        git commit -m $Message
        Write-Host "Commit successful" -ForegroundColor Green
    }
    catch {
        Write-Host "Error committing: $($_.Exception.Message)" -ForegroundColor Red
    }
    finally {
        Enable-PSReadLine
    }
}

# Complete git workflow
function Invoke-GitWorkflow {
    param(
        [string[]]$Files,
        [string]$CommitMessage
    )
    
    Write-Host "Starting git workflow..." -ForegroundColor Yellow
    
    # Add files
    Add-GitFilesSafe -Files $Files
    
    # Commit changes
    Commit-GitChangesSafe -Message $CommitMessage
    
    Write-Host "Git workflow completed" -ForegroundColor Green
}

# Export functions for use
Export-ModuleMember -Function * 