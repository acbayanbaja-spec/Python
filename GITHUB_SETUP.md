# GitHub Setup Guide

## Option 1: Create New Repository on GitHub

1. Go to https://github.com
2. Click the "+" icon → "New repository"
3. Name it: `seait-lost-and-found` (or your choice)
4. Set to **Public** (or Private if you have GitHub Pro)
5. **DO NOT** initialize with README, .gitignore, or license
6. Click "Create repository"

## Option 2: Push Your Code

After creating the repository, GitHub will show you commands. Use these:

```bash
# Navigate to your project folder
cd C:\xampp\htdocs\Python

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Lost and Found System"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/seait-lost-and-foun
d.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Important: .gitignore

Make sure `.gitignore` includes:
- `.env` (contains passwords - NEVER commit this!)
- `__pycache__/`
- `*.pyc`
- `lost_found.db` (SQLite database)
- `app/static/uploads/` (uploaded files)

Your `.gitignore` should already have these.
