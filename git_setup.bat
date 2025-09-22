@echo off
echo =========================================
echo 🚀 PULSE - GIT & GITHUB SETUP SCRIPT
echo =========================================
echo.
echo This script will:
echo 1. Set up Git for your Pulse project
echo 2. Create your first commit
echo 3. Help you upload to GitHub
echo.
echo Press any key to continue...
pause >nul
echo.

:: Navigate to your Pulse project directory
cd /d "C:\Users\dhrit\Projects\social-media-analyzer-clean"

echo 📁 Working in directory: %CD%
echo.

:: Check if git is installed
echo 🔍 Step 1: Checking if Git is installed...
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Git is not installed or not found in PATH
    echo.
    echo Please install Git first:
    echo 1. Go to: https://git-scm.com/download/windows
    echo 2. Download and install Git
    echo 3. Restart your computer
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)

echo ✅ Git is installed and ready!
echo.

:: Configure Git user (first time setup)
echo 🔧 Step 2: Configuring Git user settings...
echo.
echo We need to set up your Git identity for commits.
echo This will be shown in your commit history.
echo.

set /p GIT_NAME="Enter your full name (e.g., John Smith): "
set /p GIT_EMAIL="Enter your email address (same as GitHub): "

if "%GIT_NAME%"=="" (
    echo ❌ Name cannot be empty. Please try again.
    pause
    exit /b 1
)

if "%GIT_EMAIL%"=="" (
    echo ❌ Email cannot be empty. Please try again.
    pause
    exit /b 1
)

echo.
echo 📝 Setting up Git with:
echo    Name: %GIT_NAME%
echo    Email: %GIT_EMAIL%
echo.

git config --global user.name "%GIT_NAME%"
git config --global user.email "%GIT_EMAIL%"

echo ✅ Git user configuration complete!
echo.

:: Initialize git repository
echo 🔧 Step 3: Initializing Git repository...
git init
if errorlevel 1 (
    echo ❌ Failed to initialize Git repository
    pause
    exit /b 1
)

:: Set default branch to main
git branch -M main
echo ✅ Git repository initialized with 'main' branch
echo.

:: Add all files to staging
echo 📝 Step 4: Adding files to Git...
echo.
echo Files that will be added to Git:
git add .
git status --short
echo.
echo ✅ All files staged for commit
echo.

:: Create initial commit
echo 💾 Step 5: Creating your first commit...
git commit -m "Initial commit: Pulse - AI-Powered Social Media Review Analyzer

🌊 Pulse - Transform customer feedback into actionable insights

Features:
✅ Universal web scraper for review sites (Trustpilot, Glassdoor, etc.)
✅ AI-powered sentiment analysis with GPT-4
✅ Topic modeling and trend analysis  
✅ Beautiful Streamlit web interface
✅ Professional Excel reports with insights
✅ CLI and web interface options
✅ Ethical scraping with rate limiting
✅ Comprehensive logging and error handling

Built with: Python, Streamlit, OpenAI GPT-4, BeautifulSoup, Selenium"

if errorlevel 1 (
    echo ❌ Failed to create commit
    pause
    exit /b 1
)

echo ✅ Initial commit created successfully!
echo.

:: GitHub repository setup instructions
echo 🌐 Step 6: GitHub Repository Setup
echo ==========================================
echo.
echo Now you need to create a repository on GitHub:
echo.
echo 📋 Instructions:
echo 1. Open your web browser
echo 2. Go to: https://github.com/new
echo 3. Repository settings:
echo    • Repository name: pulse
echo    • Description: AI-Powered Social Media Review Analyzer
echo    • Public or Private: (your choice)
echo    • Initialize with README: NO (uncheck this!)
echo    • Add .gitignore: NO (we already have one)
echo    • Add license: NO (we already have one)
echo 4. Click 'Create repository'
echo 5. Copy the repository URL from the next page
echo.
echo The URL will look like: https://github.com/yourusername/pulse.git
echo.
pause

echo.
set /p GITHUB_URL="🔗 Paste your GitHub repository URL here: "

if "%GITHUB_URL%"=="" (
    echo ❌ No GitHub URL provided. Exiting...
    echo You can run this script again later with the URL.
    pause
    exit /b 1
)

:: Validate URL format (basic check)
echo %GITHUB_URL% | findstr /i "github.com" >nul
if errorlevel 1 (
    echo ❌ This doesn't look like a GitHub URL
    echo Make sure it looks like: https://github.com/yourusername/pulse.git
    pause
    exit /b 1
)

echo.
echo 🔗 Step 7: Connecting to GitHub...
git remote add origin %GITHUB_URL%
if errorlevel 1 (
    echo ❌ Failed to add GitHub remote
    pause
    exit /b 1
)

echo ✅ Connected to GitHub repository
echo.

echo 🚀 Step 8: Uploading Pulse to GitHub...
echo This may take a moment...
echo.

git push -u origin main
if errorlevel 1 (
    echo.
    echo ❌ Push failed. This could be because:
    echo    • Authentication issues
    echo    • Repository doesn't exist on GitHub  
    echo    • Wrong repository URL
    echo    • Network connection issues
    echo.
    echo 💡 Try these solutions:
    echo 1. Make sure you created the repository on GitHub
    echo 2. Check your internet connection
    echo 3. Verify the repository URL is correct
    echo 4. You may need to authenticate with GitHub
    echo.
    echo You can try pushing manually later with:
    echo    git push -u origin main
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo 🎉 SUCCESS! PULSE IS NOW ON GITHUB!
echo ========================================
echo.
echo ✅ Your Pulse project is now available at:
echo    %GITHUB_URL%
echo.
echo 📋 What you can do now:
echo    • View your code on GitHub
echo    • Share your project with others
echo    • Track changes with Git
echo    • Collaborate with team members
echo.
echo 🔧 Useful Git commands for future updates:
echo    git add .                    # Stage changes
echo    git commit -m "message"      # Save changes
echo    git push                     # Upload to GitHub
echo    git status                   # Check what's changed
echo    git log --oneline            # View history
echo.
echo 🎯 Next steps:
echo    1. Visit your GitHub repository
echo    2. Add a description and tags
echo    3. Consider making it public to share
echo    4. Start working on new features!
echo.
pause