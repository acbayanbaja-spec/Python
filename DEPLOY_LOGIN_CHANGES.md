# How to Deploy Login Page Changes to Render

Your new Facebook-style login page is ready locally, but it needs to be pushed to GitHub so Render can deploy it.

## Option 1: Using GitHub Desktop (EASIEST - Recommended for Windows)

1. **Download GitHub Desktop** (if not installed):
   - Go to: https://desktop.github.com/
   - Install and sign in with your GitHub account

2. **Open your repository in GitHub Desktop**:
   - File → Add Local Repository
   - Browse to: `C:\xampp\htdocs\Python`
   - Click "Add repository"

3. **Commit and Push**:
   - You'll see the changed files (especially `app/templates/auth/login.html`)
   - At the bottom left, write a commit message: "Update login page with Facebook-style design"
   - Click "Commit to main"
   - Click "Push origin" button at the top

4. **Wait for Render to Deploy**:
   - Render will automatically detect the push
   - Go to your Render dashboard
   - Watch the "Events" tab - it should show "Deploy in progress"
   - Wait 2-5 minutes for deployment to complete

5. **Check your site**:
   - Visit: https://python-2057.onrender.com/auth/login
   - You should see the new Facebook-style design!

---

## Option 2: Using Git Command Line

### Step 1: Install Git (if not installed)
1. Download from: https://git-scm.com/download/win
2. Install with default settings
3. Restart your terminal/PowerShell

### Step 2: Navigate to your project
```powershell
cd C:\xampp\htdocs\Python
```

### Step 3: Check Git status
```powershell
git status
```

### Step 4: Add and commit changes
```powershell
git add .
git commit -m "Update login page with Facebook-style design"
```

### Step 5: Push to GitHub
```powershell
git push origin main
```

### Step 6: Wait for Render deployment
- Check Render dashboard
- Wait 2-5 minutes
- Visit your site to see changes

---

## Option 3: Manual Upload via Render Dashboard (Not Recommended)

If Git is not working, you can manually upload files:

1. Go to Render dashboard → Your Web Service
2. Go to "Settings" tab
3. Scroll to "Build & Deploy"
4. You can't directly upload files, but you can:
   - Use Render's "Manual Deploy" after pushing to GitHub
   - Or use Render's file editor (limited)

**Best option: Use GitHub Desktop (Option 1)**

---

## Troubleshooting

### If changes still don't appear:
1. **Clear browser cache**: Press `Ctrl + Shift + Delete` and clear cached images
2. **Hard refresh**: Press `Ctrl + F5` on the login page
3. **Check Render logs**: Go to Render dashboard → Logs tab to see if there are errors
4. **Verify deployment**: Check Render dashboard → Events tab to confirm deployment completed

### If you see old design:
- The browser might be caching the old page
- Try incognito/private browsing mode
- Or wait a few minutes and try again

---

## Files Changed
- `app/templates/auth/login.html` - Complete redesign with Facebook-style layout
- `app/static/images/README.md` - Instructions for adding logo and team photos
