@echo off
REM Safe Git Operations for AI_Collab_Online
REM This batch file provides git commands that avoid PowerShell display issues

if "%1"=="status" (
    git status --porcelain
    goto :eof
)

if "%1"=="add" (
    if "%2"=="" (
        echo Usage: git_safe.bat add file1 file2 file3
        goto :eof
    )
    shift
    git add %*
    echo Files added successfully
    goto :eof
)

if "%1"=="commit" (
    if "%2"=="" (
        echo Usage: git_safe.bat commit "commit message"
        goto :eof
    )
    shift
    git commit -m "%*"
    echo Commit successful
    goto :eof
)

if "%1"=="workflow" (
    if "%2"=="" (
        echo Usage: git_safe.bat workflow "commit message" file1 file2 file3
        goto :eof
    )
    set COMMIT_MSG=%2
    shift
    shift
    echo Adding files...
    git add %*
    echo Committing changes...
    git commit -m "%COMMIT_MSG%"
    echo Git workflow completed successfully
    goto :eof
)

echo Usage:
echo   git_safe.bat status
echo   git_safe.bat add file1 file2 file3
echo   git_safe.bat commit "commit message"
echo   git_safe.bat workflow "commit message" file1 file2 file3 