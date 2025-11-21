@echo off
echo ========================================
echo   Railway Deployment Script
echo ========================================
echo.

echo [1/4] Staging changes...
git add .

echo [2/4] Committing...
git commit -m "Remove Dockerfile, use Railway Nixpacks"

echo [3/4] Pushing to GitHub...
git push

echo.
echo ========================================
echo   DONE! Railway will auto-deploy now!
echo ========================================
echo.
echo Check Railway dashboard for deployment status
echo.
pause
