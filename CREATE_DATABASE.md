# Create PostgreSQL Database on Render

## You Need TWO Services:

1. **PostgreSQL Database** - Stores your data
2. **Python Web Service** - Runs your Flask app

## Step 1: Create PostgreSQL Database

1. Go to Render dashboard: https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `seait-lost-and-found-db` (or your choice)
   - **Database**: `seait_lost_and_found` (or leave default)
   - **User**: `seait_lost_and_found_user` (or leave default)
   - **Region**: Singapore (same as your web service)
   - **Plan**: Free (or Starter if you prefer)
4. Click **"Create Database"**
5. Wait for it to be created (1-2 minutes)

## Step 2: Get Database Connection URL

1. Click on your new PostgreSQL database
2. Go to **"Info"** or **"Connections"** tab
3. Copy the **Internal Database URL**
4. It will look like:
   ```
   postgresql://user:password@host:port/database_name
   ```

## Step 3: Set DATABASE_URL in Web Service

1. Go to your Python Web Service
2. Go to **"Environment"** tab
3. Add or update `DATABASE_URL`:
   - Key: `DATABASE_URL`
   - Value: (paste the Internal Database URL you copied)
4. Click **"Save Changes"**
5. Wait for redeploy

## Step 4: Initialize Database

After the web service redeploys:

1. Go to your Web Service → **"Shell"** tab (or use Logs)
2. Run these commands:
   ```bash
   flask db upgrade
   python seed_data.py
   ```

Or you can use Render's built-in terminal/console.

## Alternative: Use External Database URL

If you want to use the database you already have:

1. Go to your existing PostgreSQL database on Render
2. Copy the **External Database URL** (if you have one)
3. Use that in your web service's `DATABASE_URL`

But the **Internal Database URL** is recommended for services on the same Render account.
