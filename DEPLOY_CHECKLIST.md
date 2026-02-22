# ✅ Render Deployment Checklist

## ✅ Completed Steps

- [x] PostgreSQL database created on Render
- [x] Database connection tested successfully
- [x] Database tables created
- [x] Initial data seeded (admin, staff, students)
- [x] Application code ready

## 📋 Next Steps: Deploy to Render

### Step 1: Push Code to GitHub (if not already done)

```bash
git init
git add .
git commit -m "Initial commit - Lost and Found System"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### Step 2: Create Web Service on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account (if not connected)
4. Select your repository
5. Click **"Connect"**

### Step 3: Configure Build Settings

**Name:** `seait-lost-and-found` (or your choice)

**Settings:**
- **Environment:** `Python 3`
- **Build Command:** 
  ```
  pip install -r requirements.txt
  ```
- **Start Command:** 
  ```
  gunicorn run:app
  ```
- **Region:** Singapore (recommended, same as your database)

### Step 4: Set Environment Variables

Go to **"Environment"** tab and add:

| Key | Value | Notes |
|-----|-------|-------|
| `FLASK_ENV` | `production` | Required |
| `SECRET_KEY` | `[Generate one]` | Use: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `SESSION_COOKIE_SECURE` | `True` | For HTTPS |
| `DATABASE_URL` | **LEAVE EMPTY** | Render will auto-set when you link database |

### Step 5: Link PostgreSQL Database

1. In your Web Service settings
2. Go to **"Connections"** tab
3. Click **"Link Resource"**
4. Select: `seait_lost_and_found` (your PostgreSQL database)
5. Render will automatically:
   - Set `DATABASE_URL` to internal URL
   - Allow web service to connect

### Step 6: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (2-5 minutes)
3. Check logs for any errors

### Step 7: Verify Database (Already Done!)

✅ Your database is already set up with:
- All tables created
- Admin user: `admin@seait.edu` / `admin123`
- Staff user: `staff@seait.edu` / `staff123`
- Sample data loaded

**No need to run migrations or seed data again!**

### Step 8: Test Your Deployment

1. Visit your Render URL: `https://your-app-name.onrender.com`
2. You should see the login page
3. Login with: `admin@seait.edu` / `admin123`

### Step 9: Set Up Custom Domain (Optional)

1. Go to your Web Service → **"Settings"**
2. Scroll to **"Custom Domains"**
3. Click **"Add Custom Domain"**
4. Enter your domain (e.g., `lostfound.seait.edu`)
5. Follow DNS configuration instructions
6. Wait for SSL certificate (automatic)

## 🔐 Your Database Credentials

**Internal URL (used by Render):**
```
postgresql://seait_lost_and_found_user:JcujN1AassCE1pQddkPPyWiOh7BRtfKu@dpg-d6dd5ip4tr6s73co3uhg-a/seait_lost_and_found
```

**External URL (for local testing):**
```
postgresql://seait_lost_and_found_user:JcujN1AassCE1pQddkPPyWiOh7BRtfKu@dpg-d6dd5ip4tr6s73co3uhg-a.singapore-postgres.render.com:5432/seait_lost_and_found
```

## 📝 Important Notes

1. **DATABASE_URL**: Don't set it manually - Render will auto-set it when you link the database
2. **Free Tier**: Render free tier may spin down after inactivity (takes ~30 seconds to wake up)
3. **HTTPS**: Automatically enabled by Render
4. **Custom Domain**: Free subdomain is `your-app.onrender.com`

## 🐛 Troubleshooting

**App won't start:**
- Check logs in Render dashboard
- Verify `gunicorn` is in requirements.txt
- Check start command is correct

**Database connection errors:**
- Ensure database is linked in Connections tab
- Verify database is running
- Check environment variables

**Can't login:**
- Database is already seeded - use `admin@seait.edu` / `admin123`
- Check if database connection is working

## 🎉 Success!

Once deployed, your app will be live at:
- **Free URL**: `https://your-app-name.onrender.com`
- **Custom Domain**: (if configured)

Your database is ready and all data is loaded!
