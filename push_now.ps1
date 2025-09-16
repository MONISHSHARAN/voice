Write-Host "🚀 PUSHING TO GITHUB NOW!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Yellow

# Initialize git if needed
if (-not (Test-Path ".git")) {
    git init
}

# Add all files
git add .

# Commit
git commit -m "MedAgg Healthcare POC - Clean Version"

# Set main branch
git branch -M main

Write-Host "✅ READY TO PUSH!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 CREATE GITHUB REPO:" -ForegroundColor Cyan
Write-Host "1. Go to https://github.com/new" -ForegroundColor White
Write-Host "2. Name: medagg-healthcare" -ForegroundColor White
Write-Host "3. Click Create Repository" -ForegroundColor White
Write-Host ""
Write-Host "🔗 THEN RUN:" -ForegroundColor Cyan
Write-Host "git remote add origin https://github.com/YOUR_USERNAME/medagg-healthcare.git" -ForegroundColor White
Write-Host "git push -u origin main" -ForegroundColor White
Write-Host ""
Write-Host "🔑 TUNNEL PASSWORD: password" -ForegroundColor Magenta

