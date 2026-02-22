# Deployment Guide - PostgreSQL & Free Domain Setup

## Database Configuration

The application automatically switches between SQLite (development) and PostgreSQL (production) based on the `DATABASE_URL` environment variable.

### Current Setup
- **Development**: Uses SQLite (`lost_found.db`) when `DATABASE_URL` is not set
- **Production**: Uses PostgreSQL when `DATABASE_URL` is set

## Free PostgreSQL Hosting Options

### Option 1: ElephantSQL (Recommended - Free Tier)
1. Go to https://www.elephantsql.com/
2. Sign up for a free account
3. Create a new instance (Tiny Turtle - Free)
4. Copy the connection URL (format: `postgresql://user:password@host:port/database`)
5. Set as `DATABASE_URL` environment variable

### Option 2: Supabase (Free Tier)
1. Go to https://supabase.com/
2. Create a new project
3. Go to Settings → Database
4. Copy the connection string
5. Format: `postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`

### Option 3: Railway (Free Tier with Credit)
1. Go to https://railway.app/
2. Create a new project
3. Add PostgreSQL database
4. Copy the connection URL from the database service

### Option 4: Render (Free Tier)
1. Go to https://render.com/
2. Create a new PostgreSQL database
3. Copy the Internal Database URL

## Setting Up Environment Variables

### For Local Development with PostgreSQL

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production

# Session Configuration (for production)
SESSION_COOKIE_SECURE=False
```

### For Production Deployment

Set environment variables on your hosting platform:

**Heroku:**
```bash
heroku config:set DATABASE_URL=postgresql://...
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production
```

**PythonAnywhere:**
- Go to Web tab → Environment variables
- Add `DATABASE_URL` and `SECRET_KEY`

**Render:**
- Go to Environment tab
- Add environment variables

## Free Domain & Hosting Options

### Option 1: Render (Recommended)
- **Free tier**: Yes
- **PostgreSQL**: Free tier available
- **Custom domain**: Free subdomain (yourapp.onrender.com)
- **Steps**:
  1. Connect your GitHub repository
  2. Set build command: `pip install -r requirements.txt`
  3. Set start command: `gunicorn run:app`
  4. Add PostgreSQL database
  5. Set environment variables

### Option 2: Railway
- **Free tier**: $5 credit/month
- **PostgreSQL**: Included
- **Custom domain**: Free subdomain
- **Steps**:
  1. Connect GitHub
  2. Deploy from repository
  3. Add PostgreSQL service
  4. Set environment variables

### Option 3: PythonAnywhere
- **Free tier**: Yes (limited)
- **PostgreSQL**: Available
- **Custom domain**: Free subdomain
- **Steps**:
  1. Upload your code
  2. Configure web app
  3. Set up PostgreSQL database
  4. Configure environment variables

### Option 4: Fly.io
- **Free tier**: Yes
- **PostgreSQL**: Available
- **Custom domain**: Free subdomain
- **Steps**:
  1. Install flyctl
  2. Run `fly launch`
  3. Add PostgreSQL: `fly postgres create`
  4. Attach to app: `fly postgres attach`

## Migration from SQLite to PostgreSQL

### Step 1: Install PostgreSQL Client (if needed)
```bash
pip install psycopg2-binary
```

### Step 2: Set DATABASE_URL
```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql://user:password@host:port/database"

# Linux/Mac
export DATABASE_URL="postgresql://user:password@host:port/database"
```

### Step 3: Run Migrations
```bash
# Initialize migrations (if not done)
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### Step 4: Seed Data (Optional)
```bash
python seed_data.py
```

## Testing Database Connection

Create a test script `test_db.py`:

```python
from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Test connection
    try:
        users = User.query.count()
        print(f"✓ Database connected! Found {users} users.")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
```

## Production Checklist

- [ ] Set `DATABASE_URL` environment variable
- [ ] Set `SECRET_KEY` to a strong random value
- [ ] Set `FLASK_ENV=production`
- [ ] Set `SESSION_COOKIE_SECURE=True` (if using HTTPS)
- [ ] Run database migrations
- [ ] Seed initial data (admin user)
- [ ] Configure static file serving
- [ ] Set up SSL/HTTPS
- [ ] Configure domain name
- [ ] Set up monitoring/logging

## Example .env File

```env
# Production Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Flask Settings
FLASK_ENV=production
SECRET_KEY=generate-a-strong-random-key-here

# Session Security (for HTTPS)
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# Optional: Custom Port
PORT=5000
```

## Troubleshooting

### Connection Issues
- Check if PostgreSQL is accessible from your hosting provider
- Verify username, password, host, and database name
- Check firewall settings
- Ensure SSL is configured if required

### Migration Issues
- Make sure `DATABASE_URL` is set before running migrations
- Check database user has CREATE TABLE permissions
- Verify Flask-Migrate is installed

### Performance
- Use connection pooling for production
- Consider using read replicas for high traffic
- Monitor database performance
