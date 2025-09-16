@echo off
echo 🚀 PUSHING TO GITHUB - MedAgg Healthcare
echo ================================================

echo 🔄 Initializing Git...
git init

echo 🔄 Adding all files...
git add .

echo 🔄 Committing files...
git commit -m "MedAgg Healthcare POC - Conversational AI System"

echo 🔄 Setting up remote...
git branch -M main

echo.
echo ✅ READY TO PUSH!
echo.
echo 📋 NEXT STEPS:
echo 1. Go to https://github.com/new
echo 2. Create repository: medagg-healthcare
echo 3. Copy the repository URL
echo 4. Run: git remote add origin YOUR_REPO_URL
echo 5. Run: git push -u origin main
echo.
echo 🔑 TUNNEL PASSWORD: password
echo.
pause

