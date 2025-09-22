@echo off
echo =========================================
echo 🧹 PULSE PROJECT CLEANUP SCRIPT
echo =========================================
echo This script will clean up your Pulse project
echo and prepare it for GitHub
echo.
echo Press any key to continue...
pause >nul
echo.

:: Navigate to your Pulse project directory
cd /d "C:\Users\dhrit\Projects\social-media-analyzer-clean"

echo 📁 Working in directory: %CD%
echo.

echo 🗑️  Step 1: Removing unnecessary files...
echo.

:: Remove the empty "New folder" if it exists
if exist "New folder" (
    echo ✅ Removing empty "New folder"...
    rmdir "New folder" /s /q
    echo    Done!
) else (
    echo ✅ No empty folders found (good!)
)

:: Fix the .gitignore typo
if exist ".gitingore" (
    echo ✅ Fixing .gitignore filename typo...
    ren ".gitingore" ".gitignore"
    echo    Fixed: .gitingore → .gitignore
) else (
    echo ✅ .gitignore filename is already correct
)

:: Remove Python cache directories
if exist "__pycache__" (
    echo ✅ Removing Python cache files...
    rmdir "__pycache__" /s /q
    echo    Removed __pycache__ directory
) else (
    echo ✅ No Python cache files found (good!)
)

:: Remove any .pyc files
echo ✅ Cleaning up compiled Python files...
del /s /q *.pyc >nul 2>&1
echo    Cleaned .pyc files

:: Create logs directory if it doesn't exist
if not exist "logs" (
    echo ✅ Creating logs directory...
    mkdir logs
    echo    Created logs/ directory
) else (
    echo ✅ Logs directory already exists
)

:: Move log files to logs directory
if exist "*.log" (
    echo ✅ Organizing log files...
    move *.log logs\ >nul 2>&1
    echo    Moved log files to logs/ directory
) else (
    echo ✅ Log files already organized
)

echo.
echo ========================================
echo ✅ CLEANUP COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo 📋 Your clean Pulse project now contains:
echo.
dir /b
echo.
echo 🎯 Next step: Create .gitignore and README files
echo.
echo Press any key to continue...
pause >nul