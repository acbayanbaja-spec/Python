# Fix Database Connection Error

## Error: `database "seait_lost_and_found" does not exist`

### Solution 1: Check Actual Database Name in Render

1. Go to your Render dashboard
2. Click on your **PostgreSQL database** (not the web service)
3. Check the database name - it might be slightly different
4. Common variations:
   - `seait_lost_and_found`
   - `seaitlostandfound`
   - `seait_lost_and_found_db`
   - Or something else

### Solution 2: Get Correct DATABASE_URL

1. In your PostgreSQL database page on Render
2. Go to **"Info"** or **"Connections"** tab
3. Copy the **Internal Database URL**
4. It should look like:
   ```
   postgresql://seait_lost_and_found_user:PASSWORD@dpg-d6dd5ip4tr6s73co3uhg-a/DATABASE_NAME
   ```
5. Note the actual database name at the end

### Solution 3: Update DATABASE_URL in Web Service

1. Go to your Web Service → **Environment** tab
2. Find `DATABASE_URL` variable
3. Update it with the correct Internal Database URL from your PostgreSQL database
4. Make sure there are no extra spaces or newlines
5. Click **"Save Changes"**
6. Wait for redeploy

### Solution 4: Verify Database Exists

If the database doesn't exist:
1. Go to your PostgreSQL database on Render
2. Check if it's actually running
3. The database should have been created when you set it up
4. If not, you may need to create it manually or check Render's database setup
