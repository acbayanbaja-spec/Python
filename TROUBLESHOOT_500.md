# Troubleshooting 500 Internal Server Error on Render

## Step 1: Check Render Logs

1. Go to your Render dashboard
2. Click on your web service
3. Click the **"Logs"** tab
4. Look for error messages (usually in red)
5. Copy the error message

Common errors you might see:
- Database connection errors
- Missing environment variables
- Import errors
- Module not found errors

## Common Issues & Fixes

### Issue 1: DATABASE_URL Not Set

**Error:** `sqlalchemy.exc.OperationalError` or database connection errors

**Fix:**
1. Go to Environment tab
2. Add `DATABASE_URL` with your internal database URL:
   ```
   postgresql://seait_lost_and_found_user:JcujN1AassCE1pQddkPPyWiOh7BRtfKu@dpg-d6dd5ip4tr6s73co3uhg-a/seait_lost_and_found
   ```

### Issue 2: Missing SECRET_KEY

**Error:** `RuntimeError: SECRET_KEY not set`

**Fix:**
1. Go to Environment tab
2. Add `SECRET_KEY` with a random string:
   ```
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

### Issue 3: Missing Dependencies

**Error:** `ModuleNotFoundError` or `ImportError`

**Fix:**
1. Check if all packages are in `requirements.txt`
2. Check build logs to see if installation failed

### Issue 4: Import Errors

**Error:** Import errors in logs

**Fix:**
- Check if all files are pushed to GitHub
- Verify `run.py` exists and is correct

## Quick Checklist

- [ ] Check Logs tab for specific error
- [ ] Verify DATABASE_URL is set
- [ ] Verify SECRET_KEY is set
- [ ] Verify FLASK_ENV=production
- [ ] Check if build completed successfully
- [ ] Verify all files are in GitHub repository
