# Quick script to push login page changes to GitHub
# This will work if Git is installed and repository is already set up

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploy Login Page Changes to Render" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Git is available
try {
    $gitVersion = git --version 2>&1
    Write-Host "Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Git is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "OR use GitHub Desktop instead (easier!): https://desktop.github.com/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installing, run this script again." -ForegroundColor Yellow
    pause
    exit
}

# Navigate to project directory
cd C:\xampp\htdocs\Python

Write-Host "Current directory: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

# Check if .git exists
if (-not (Test-Path .git)) {
    Write-Host "Git repository not initialized." -ForegroundColor Yellow
    Write-Host "Do you want to initialize it? (y/n)" -ForegroundColor Cyan
    $response = Read-Host
    if ($response -eq 'y' -or $response -eq 'Y') {
        git init
        Write-Host "Git initialized!" -ForegroundColor Green
    } else {
        Write-Host "Please set up your repository first. See DEPLOY_LOGIN_CHANGES.md" -ForegroundColor Yellow
        pause
        exit
    }
}

# Check git status
Write-Host "Checking for changes..." -ForegroundColor Cyan
git status

Write-Host ""
Write-Host "Do you want to commit and push these changes? (y/n)" -ForegroundColor Cyan
$response = Read-Host

if ($response -eq 'y' -or $response -eq 'Y') {
    # Add all changes
    Write-Host ""
    Write-Host "Adding files..." -ForegroundColor Cyan
    git add .
    
    # Commit
    Write-Host "Committing changes..." -ForegroundColor Cyan
    git commit -m "Update login page with Facebook-style design"
    
    # Check if remote exists
    $remote = git remote get-url origin 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "No remote repository configured." -ForegroundColor Yellow
        Write-Host "Please enter your GitHub repository URL:" -ForegroundColor Cyan
        Write-Host "Example: https://github.com/yourusername/lost-and-found.git" -ForegroundColor Gray
        $repoUrl = Read-Host
        git remote add origin $repoUrl
    }
    
    # Push
    Write-Host ""
    Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
    git push origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "SUCCESS! Changes pushed to GitHub!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Render will automatically deploy in 2-5 minutes." -ForegroundColor Yellow
        Write-Host "Check your Render dashboard to see deployment progress." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "After deployment, visit:" -ForegroundColor Cyan
        Write-Host "https://python-2057.onrender.com/auth/login" -ForegroundColor White
        Write-Host ""
        Write-Host "Tip: Clear browser cache (Ctrl+Shift+Delete) if you see old design." -ForegroundColor Gray
    } else {
        Write-Host ""
        Write-Host "ERROR: Push failed. Check the error message above." -ForegroundColor Red
        Write-Host "Make sure your GitHub repository is set up correctly." -ForegroundColor Yellow
    }
} else {
    Write-Host "Cancelled." -ForegroundColor Yellow
}

Write-Host ""
pause
