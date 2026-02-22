# Render.com Setup Guide

## Step 1: Get Your Database Password

1. Go to your Render dashboard: https://dashboard.render.com
2. Click on your PostgreSQL database (`seait_lost_and_found`)
3. Go to the "Info" or "Connections" tab
4. Copy the **Internal Database URL** or find the password
5. The password should be visible in the connection string

## Step 2: Construct DATABASE_URL

Your DATABASE_URL format should be:
```
postgresql://seait_lost_and_found_user:PASSWORD@dpg-d6dd5ip4tr6s73co3uhg-a:5432/seait_lost_and_found
```

Replace `PASSWORD` with your actual password from Render.

## Step 3: Set Environment Variable Locally (for testing)

### Windows PowerShell:
```powershell
$env:DATABASE_URL="postgresql://seait_lost_and_found_user:YOUR_PASSWORD@dpg-d6dd5ip4tr6s73co3uhg-a:5432/seait_lost_and_found"
```

### Windows CMD:
```cmd
set DATABASE_URL=postgresql://seait_lost_and_found_user:YOUR_PASSWORD@dpg-d6dd5ip4tr6s73co3uhg-a:5432/seait_lost_and_found
```

### Create .env file (recommended):
Create a `.env` file in the project root:
```
DATABASE_URL=postgresql://seait_lost_and_found_user:YOUR_PASSWORD@dpg-d6dd5ip4tr6s73co3uhg-a:5432/seait_lost_and_found
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
```

## Step 4: Test Connection

Run the test script:
```bash
python setup_postgres.py
```

## Step 5: Initialize Database

```bash
# Install python-dotenv to load .env file
pip install python-dotenv

# Run migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Seed data
python seed_data.py
```

## Step 6: Deploy to Render

1. **Create a Web Service on Render:**
   - Go to Render dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository (or use Render's Git)

2. **Configure Build Settings:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`

3. **Set Environment Variables:**
   - Go to your Web Service → Environment
   - Add these variables:
     - `DATABASE_URL`: (Render will auto-detect if database is in same account)
     - `SECRET_KEY`: Generate a strong random key
     - `FLASK_ENV`: `production`
     - `SESSION_COOKIE_SECURE`: `True` (if using HTTPS)

4. **Link Database:**
   - In your Web Service settings
   - Go to "Connections" or "Environment"
   - Link your PostgreSQL database
   - Render will automatically set `DATABASE_URL`

## Step 7: Custom Domain (Optional)

1. In your Web Service settings
2. Go to "Custom Domains"
3. Add your domain
4. Follow DNS configuration instructions

## Quick Connection Test

After setting DATABASE_URL, test with:
```bash
python setup_postgres.py
```
