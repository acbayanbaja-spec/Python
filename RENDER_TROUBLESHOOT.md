# Render GitHub Connection Troubleshooting

## Issue: "Configure your Git provider to give Render permission to access your repositories"

### Solution 1: Check GitHub App Permissions

1. Go to: https://github.com/settings/installations
2. Find "Render" in the list
3. Click **"Configure"** next to Render
4. Under **"Repository access"**, select:
   - **"All repositories"** (recommended for first time)
   - OR **"Only select repositories"** and select your specific repo
5. Click **"Save"** or **"Update"**

### Solution 2: Re-authorize Render

1. On Render page, click **"GitHub"** button again
2. You may need to:
   - Revoke and re-authorize
   - Grant additional permissions
3. Make sure to check all permission boxes

### Solution 3: Use Public Git Repository (Alternative)

If GitHub connection still doesn't work:

1. On Render "New Web Service" page
2. Click **"Public Git Repository"** tab (instead of Git Provider)
3. Enter your GitHub repository URL:
   ```
   https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   ```
4. Click **"Continue"**

**Note:** This only works if your repository is **Public**. For private repos, you must use Git Provider method.

### Solution 4: Check Repository Visibility

- Make sure your repository exists on GitHub
- If it's private, ensure Render has access (Solution 1)
- If it's public, you can use "Public Git Repository" method

### Solution 5: Clear Browser Cache

1. Clear browser cache/cookies for render.com
2. Log out and log back into Render
3. Try connecting GitHub again

## Quick Fix Steps:

1. ✅ Go to: https://github.com/settings/installations
2. ✅ Click "Configure" on Render app
3. ✅ Set "Repository access" to "All repositories"
4. ✅ Save changes
5. ✅ Go back to Render and refresh page
6. ✅ Your repositories should now appear!

## Still Not Working?

Try the "Public Git Repository" method:
- Click "Public Git Repository" tab
- Paste your GitHub repo URL
- Continue with deployment
