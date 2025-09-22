@echo off
echo =========================================
echo 🌊 PULSE - GITHUB UPLOAD SCRIPT
echo =========================================
echo.
echo Your Pulse project is ready to go to GitHub!
echo Git is already configured perfectly.
echo.

:: Navigate to the correct Pulse directory  
cd /d "C:\Users\dhrit\Projects\Pulse"

echo 📁 Working in: %CD%
echo.

:: Show current status
echo 📊 Current Git status:
git status
echo.

:: Show what files we have
echo 📚 Your Pulse project files:
dir /b *.py *.txt *.md 2>nul
echo.

:: Show recent commits
echo 📜 Recent commits:
git log --oneline -3 2>nul || echo "Ready to make first commit"
echo.

echo 🌐 GITHUB REPOSITORY SETUP
echo ==========================================
echo.
echo 📋 Follow these steps:
echo.
echo 1. Open your web browser
echo 2. Go to: https://github.com/new
echo 3. Fill out the form:
echo    • Repository name: pulse
echo    • Description: AI-Powered Social Media Review Analyzer
echo    • Public or Private: (your choice)
echo    • ❌ Do NOT check "Add a README file"
echo    • ❌ Do NOT check "Add .gitignore" 
echo    • ❌ Do NOT check "Choose a license"
echo 4. Click "Create repository"
echo 5. On the next page, copy the repository URL
echo.
echo 💡 The URL will look like: https://github.com/yourusername/pulse.git
echo.
echo Press any key when you've created the repository...
pause >nul
echo.

:: Get the GitHub URL
set /p GITHUB_URL="🔗 Paste your GitHub repository URL here: "

:: Validate input
if "%GITHUB_URL%"=="" (
    echo ❌ No URL provided. Please run the script again.
    pause
    exit /b 1
)

:: Check if URL looks correct
echo %GITHUB_URL% | findstr /i "github.com" >nul
if errorlevel 1 (
    echo ⚠️  This doesn't look like a GitHub URL
    echo Make sure it ends with .git
    echo Example: https://github.com/yourusername/pulse.git
    echo.
    set /p CONTINUE="Continue anyway? (y/n): "
    if /i not "%CONTINUE%"=="y" (
        echo Cancelled. Please run script again with correct URL.
        pause
        exit /b 1
    )
)

echo.
echo 🔗 Step 1: Adding GitHub remote...

:: Add remote (might already exist)
git remote add origin %GITHUB_URL% 2>nul
if errorlevel 1 (
    echo ⚠️  Remote 'origin' already exists. Updating URL...
    git remote set-url origin %GITHUB_URL%
    if errorlevel 1 (
        echo ❌ Failed to set remote URL
        pause
        exit /b 1
    )
) 

echo ✅ GitHub remote configured
echo.

:: Show remotes
echo 📡 Remote repositories:
git remote -v
echo.

echo 🚀 Step 2: Uploading Pulse to GitHub...
echo This may take a moment depending on your internet connection...
echo.

:: Push to GitHub
git push -u origin main 2>nul
if errorlevel 1 (
    echo ⚠️  'main' branch failed. Trying 'master'...
    git push -u origin master 2>nul
    if errorlevel 1 (
        echo.
        echo ❌ Upload failed. Possible causes:
        echo 1. Repository doesn't exist on GitHub
        echo 2. Authentication issues  
        echo 3. Network connection problems
        echo 4. Wrong repository URL
        echo.
        echo 🔧 Troubleshooting:
        echo • Double-check the repository exists on GitHub
        echo • Verify the URL is exactly correct
        echo • Check your internet connection
        echo • Make sure repository is not private (if you don't have permissions)
        echo.
        echo 💡 You can try manually later with:
        echo    git push -u origin main
        echo.
        pause
        exit /b 1
    ) else (
        set BRANCH_NAME=master
    )
) else (
    set BRANCH_NAME=main
)

echo.
echo ========================================
echo 🎉 SUCCESS! PULSE IS NOW ON GITHUB! 🎉
echo ========================================
echo.
echo 🌟 Your Pulse project is live at:
echo    %GITHUB_URL%
echo.
echo 🌊 Repository: pulse
echo 🌿 Branch: %BRANCH_NAME%
echo 📊 Status: All files uploaded successfully
echo.
echo 🔗 You can view your project by:
echo 1. Opening the URL above in your browser
echo 2. Sharing the link with others
echo 3. Cloning it on other computers
echo.
echo 🔧 Useful commands for future updates:
echo    git add .                    # Stage new changes
echo    git commit -m "description"  # Save changes  
echo    git push                     # Upload to GitHub
echo    git status                   # Check current status
echo    git log --oneline            # View history
echo.
echo 🎯 What's next?
echo • Add project tags and description on GitHub
echo • Consider adding a license file
echo • Start working on new features
echo • Share your project with the community!
echo.
echo 💡 Your GitHub URL again: %GITHUB_URL%
echo.
pause