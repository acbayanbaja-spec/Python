# Complete Render.com Deployment Guide

## Step 1: Create .env File (Local Testing)

Create a file named `.env` in your project root with:

```env
# Render PostgreSQL Database - External URL (for local testing)
DATABASE_URL=postgresql://seait_lost_and_found_user:JcujN1AassCE1pQddkPPyWiOh7BRtfKu@dpg-d6dd5ip4tr6s73co3uhg-a.singapore-postgres.render.com:5432/seait_lost_and_found

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=seait-lost-found-secret-key-2024-change-this

# Session Configuration (set to True when using HTTPS)
SESSION_COOKIE_SECURE=False
```

## Step 2: Test Database Connection Locally

```bash
python connect_render_db.py
```

If successful, proceed to Step 3.

## Step 3: Initialize Database

```bash
# Initialize Flask migrations
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migration to create tables
flask db upgrade

# Seed initial data (admin user)
python seed_data.py
```

## Step 4: Deploy Web Service to Render

### 4.1 Create Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository:
   - If not connected: Click "Connect GitHub" and authorize
   - Select your repository
   - Or use Render's Git if you prefer

### 4.2 Configure Build Settings

- **Name**: `seait-lost-and-found` (or your preferred name)
- **Environment**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  gunicorn run:app
  ```
- **Region**: Choose closest to you (Singapore recommended since your DB is there)

### 4.3 Set Environment Variables

Go to **Environment** tab and add:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | Generate a strong random key (use: `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `SESSION_COOKIE_SECURE` | `True` |
| `DATABASE_URL` | **Leave this EMPTY** - Render will auto-set it when you link the database |

### 4.4 Link PostgreSQL Database

1. In your Web Service settings, go to **"Connections"** tab
2. Click **"Link Resource"**
3. Select your PostgreSQL database: `seait_lost_and_found`
4. Render will automatically:
   - Set `DATABASE_URL` to the internal URL
   - Allow the web service to connect to the database

### 4.5 Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repository
   - Install dependencies
   - Build your app
   - Start the service
3. Wait for deployment to complete (usually 2-5 minutes)

## Step 5: Run Database Migrations on Render

After deployment, you need to run migrations on Render:

### Option A: Using Render Shell (Recommended)

1. Go to your Web Service on Render
2. Click **"Shell"** tab
3. Run these commands:
   ```bash
   flask db upgrade
   python seed_data.py
   ```

### Option B: Using Render Console

1. Go to your Web Service
2. Click **"Events"** or **"Logs"**
3. Use the built-in terminal or SSH

## Step 6: Get Your Free Domain

1. After deployment, your app will have a URL like:
   `https://seait-lost-and-found.onrender.com`
2. To use a custom domain:
   - Go to your Web Service → **"Settings"**
   - Scroll to **"Custom Domains"**
   - Click **"Add Custom Domain"**
   - Enter your domain (e.g., `lostfound.seait.edu`)
   - Follow DNS configuration instructions

## Step 7: Verify Deployment

1. Visit your Render URL: `https://your-app-name.onrender.com`
2. You should see the login page
3. Login with:
   - Email: `admin@seait.edu`
   - Password: `admin123`

## Important Notes

### Database URLs:
- **Internal URL** (used by Render services): 
  `postgresql://seait_lost_and_found_user:JcujN1AassCE1pQddkPPyWiOh7BRtfKu@dpg-d6dd5ip4tr6s73co3uhg-a/seait_lost_and_found`
  
- **External URL** (for local testing): 
  `postgresql://seait_lost_and_found_user:JcujN1AassCE1pQddkPPyWiOh7BRtfKu@dpg-d6dd5ip4tr6s73co3uhg-a.singapore-postgres.render.com:5432/seait_lost_and_found`

### Security:
- Never commit `.env` file to Git (it's in `.gitignore`)
- Change `SECRET_KEY` in production
- Use strong passwords
- Enable HTTPS (Render does this automatically)

### Troubleshooting:

**Connection Issues:**
- Verify database is running on Render
- Check environment variables are set correctly
- Ensure database is linked to web service

**Migration Issues:**
- Make sure `DATABASE_URL` is set (Render auto-sets it when linked)
- Run `flask db upgrade` in Render shell

**App Not Starting:**
- Check logs in Render dashboard
- Verify `gunicorn` is in requirements.txt
- Check start command is correct

## Quick Commands Reference

```bash
# Local testing
python connect_render_db.py          # Test connection
flask db upgrade                      # Run migrations
python seed_data.py                   # Seed data

# Generate secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

## Next Steps After Deployment

1. ✅ Test login functionality
2. ✅ Create additional admin/staff users
3. ✅ Configure custom domain (if needed)
4. ✅ Set up monitoring/alerts
5. ✅ Configure backups for database
6. ✅ Review and update security settings
