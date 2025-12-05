@echo off
echo ========================================
echo Deploy Sarvam Voice Agent to Render
echo ========================================
echo.

cd /d "%~dp0"

echo Step 1: Initialize Git Repository
echo ========================================
echo.

git init
if errorlevel 1 (
    echo Error: Git is not installed or not in PATH
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo.
echo Step 2: Add all files to Git
echo ========================================
git add .

echo.
echo Step 3: Commit files
echo ========================================
git commit -m "Initial commit - Sarvam Voice Agent for Render deployment"

echo.
echo ========================================
echo Git repository initialized successfully!
echo ========================================
echo.
echo NEXT STEPS:
echo.
echo 1. Create a GitHub repository:
echo    Go to: https://github.com/new
echo    Name: sarvam-voice-agent
echo    Visibility: Private (recommended)
echo    Click "Create repository"
echo.
echo 2. Copy your GitHub repository URL
echo    Example: https://github.com/YOUR_USERNAME/sarvam-voice-agent.git
echo.
echo 3. Run these commands (replace YOUR_USERNAME):
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/sarvam-voice-agent.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 4. Then go to Render:
echo    https://dashboard.render.com/
echo    Click "New +" -^> "Web Service"
echo    Connect your GitHub repository
echo.
echo 5. See RENDER_DEPLOYMENT.md for detailed instructions
echo.
echo ========================================

pause
