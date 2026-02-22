# Script to reconnect local repository to GitHub

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Reconnect Repository to GitHub" -ForegroundColor Cyan
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
    pause
    exit
}

# Navigate to project directory
cd C:\xampp\htdocs\Python

Write-Host "Current directory: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

# Check if .git exists
if (-not (Test-Path .git)) {
    Write-Host "ERROR: No Git repository found in this directory." -ForegroundColor Red
    Write-Host "Please initialize Git first: git init" -ForegroundColor Yellow
    pause
    exit
}

# Check current remote
Write-Host "Checking current remote configuration..." -ForegroundColor Cyan
$currentRemote = git remote get-url origin 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "Current remote: $currentRemote" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Do you want to update it? (y/n)" -ForegroundColor Cyan
    $update = Read-Host
    if ($update -eq 'y' -or $update -eq 'Y') {
        git remote remove origin
        Write-Host "Old remote removed." -ForegroundColor Green
    } else {
        Write-Host "Keeping current remote." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To push changes, run:" -ForegroundColor Cyan
        Write-Host "  git add ." -ForegroundColor White
        Write-Host "  git commit -m 'Your message'" -ForegroundColor White
        Write-Host "  git push origin main" -ForegroundColor White
        pause
        exit
    }
} else {
    Write-Host "No remote configured." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Enter your GitHub repository URL:" -ForegroundColor Cyan
Write-Host "Example: https://github.com/yourusername/python.git" -ForegroundColor Gray
Write-Host "Or: https://github.com/yourusername/lost-and-found.git" -ForegroundColor Gray
Write-Host ""
$repoUrl = Read-Host "Repository URL"

if ([string]::IsNullOrWhiteSpace($repoUrl)) {
    Write-Host "ERROR: Repository URL cannot be empty." -ForegroundColor Red
    pause
    exit
}

# Add remote
Write-Host ""
Write-Host "Adding remote repository..." -ForegroundColor Cyan
git remote add origin $repoUrl

if ($LASTEXITCODE -eq 0) {
    Write-Host "Remote added successfully!" -ForegroundColor Green
    
    # Verify
    Write-Host ""
    Write-Host "Verifying remote..." -ForegroundColor Cyan
    git remote -v
    
    Write-Host ""
    Write-Host "Do you want to push your code now? (y/n)" -ForegroundColor Cyan
    $push = Read-Host
    
    if ($push -eq 'y' -or $push -eq 'Y') {
        Write-Host ""
        Write-Host "Checking for changes..." -ForegroundColor Cyan
        git status
        
        Write-Host ""
        Write-Host "Adding all files..." -ForegroundColor Cyan
        git add .
        
        Write-Host "Committing changes..." -ForegroundColor Cyan
        $commitMsg = Read-Host "Enter commit message (or press Enter for default)"
        if ([string]::IsNullOrWhiteSpace($commitMsg)) {
            $commitMsg = "Update login page and reconnect repository"
        }
        git commit -m $commitMsg
        
        Write-Host ""
        Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
        git branch -M main 2>$null
        git push -u origin main
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "SUCCESS! Repository reconnected!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Your code has been pushed to GitHub." -ForegroundColor Green
            Write-Host "Render will automatically deploy in 2-5 minutes." -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Check your site:" -ForegroundColor Cyan
            Write-Host "https://python-2057.onrender.com/auth/login" -ForegroundColor White
        } else {
            Write-Host ""
            Write-Host "ERROR: Push failed." -ForegroundColor Red
            Write-Host "Possible reasons:" -ForegroundColor Yellow
            Write-Host "  - Repository doesn't exist on GitHub" -ForegroundColor Yellow
            Write-Host "  - Authentication failed (need to set up credentials)" -ForegroundColor Yellow
            Write-Host "  - Branch name mismatch" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Try using GitHub Desktop instead for easier authentication." -ForegroundColor Cyan
        }
    } else {
        Write-Host ""
        Write-Host "Remote configured. Push manually when ready:" -ForegroundColor Yellow
        Write-Host "  git add ." -ForegroundColor White
        Write-Host "  git commit -m 'Your message'" -ForegroundColor White
        Write-Host "  git push -u origin main" -ForegroundColor White
    }
} else {
    Write-Host ""
    Write-Host "ERROR: Failed to add remote." -ForegroundColor Red
    Write-Host "Check your repository URL and try again." -ForegroundColor Yellow
}

Write-Host ""
pause
