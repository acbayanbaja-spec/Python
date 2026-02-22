# Quick Deploy Steps

## Step 1: Connect GitHub to Render ✅
- Click "GitHub" button on Render
- Authorize access

## Step 2: Push Code to GitHub

Run these commands in PowerShell:

```powershell
cd C:\xampp\htdocs\Python

# Check if git is initialized
git status

# If not initialized, run:
git init
git add .
git commit -m "Initial commit - Lost and Found System"

# Create repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

## Step 3: Select Repository on Render
- After connecting GitHub, select your repository
- Click "Connect"

## Step 4: Configure Settings
- **Name**: `seait-lost-and-found`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn run:app`
- **Region**: Singapore

## Step 5: Environment Variables
Add these in Render:
- `FLASK_ENV` = `production`
- `SECRET_KEY` = (generate one)
- `SESSION_COOKIE_SECURE` = `True`
- `DATABASE_URL` = **Leave empty** (auto-set when linking)

## Step 6: Link Database
- Go to "Connections" tab
- Link `seait_lost_and_found` database

## Step 7: Deploy!
- Click "Create Web Service"
- Wait 2-5 minutes
- Visit your URL!
