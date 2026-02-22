# PowerShell script to push code to GitHub
# Run this after installing Git

Write-Host "Pushing code to GitHub..." -ForegroundColor Green

# Navigate to project directory
cd C:\xampp\htdocs\Python

# Initialize git (if not already done)
if (-not (Test-Path .git)) {
    git init
    Write-Host "Git initialized" -ForegroundColor Yellow
}

# Add all files
git add .

# Commit
git commit -m "Initial commit - Lost and Found System"

# Add remote (replace YOUR_USERNAME with your GitHub username)
Write-Host "`nPlease enter your GitHub username:" -ForegroundColor Cyan
$username = Read-Host

git remote add origin "https://github.com/$username/lost-and-found.git" 2>$null
if ($LASTEXITCODE -ne 0) {
    git remote set-url origin "https://github.com/$username/lost-and-found.git"
}

# Push to GitHub
git branch -M main
git push -u origin main

Write-Host "`nDone! Check your GitHub repository." -ForegroundColor Green
