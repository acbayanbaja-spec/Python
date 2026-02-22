"""
Quick script to check if Render environment is configured correctly
Run this locally to verify your setup before deploying
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("Render Deployment Checklist")
print("=" * 60)

# Check DATABASE_URL
database_url = os.environ.get('DATABASE_URL')
if database_url:
    print("[OK] DATABASE_URL is set")
    if database_url.startswith('postgresql://'):
        print("[OK] Database URL format is correct (postgresql://)")
    elif database_url.startswith('postgres://'):
        print("[WARN] Database URL uses 'postgres://' (will be auto-converted)")
    else:
        print("[ERROR] Database URL format might be incorrect")
    # Don't print the full URL for security
    print(f"   Database: {database_url.split('@')[-1] if '@' in database_url else 'Unknown'}")
else:
    print("[ERROR] DATABASE_URL is NOT set")
    print("   This is OK for local development (uses SQLite)")
    print("   But REQUIRED for Render deployment!")

# Check SECRET_KEY
secret_key = os.environ.get('SECRET_KEY')
if secret_key and secret_key != 'dev-secret-key-change-in-production':
    print("[OK] SECRET_KEY is set")
else:
    print("[WARN] SECRET_KEY is not set or using default")
    print("   Generate one: python -c \"import secrets; print(secrets.token_hex(32))\"")
    print("   Add to Render environment variables")

# Check FLASK_ENV
flask_env = os.environ.get('FLASK_ENV', 'development')
print(f"[INFO] FLASK_ENV: {flask_env}")

# Check PORT
port = os.environ.get('PORT', '5000')
print(f"[INFO] PORT: {port}")

print("\n" + "=" * 60)
print("Render Environment Variables Checklist:")
print("=" * 60)
print("In Render Dashboard -> Your Web Service -> Environment:")
print("")
print("Required:")
print("  [ ] DATABASE_URL = postgresql://... (INTERNAL URL)")
print("  [ ] SECRET_KEY = <random-secret-key>")
print("")
print("Optional:")
print("  [ ] FLASK_ENV = production")
print("  [ ] PORT = 10000 (auto-set by Render)")
print("")
print("=" * 60)
print("Next Steps:")
print("=" * 60)
print("1. Push your code to GitHub")
print("2. In Render, verify DATABASE_URL is set (INTERNAL URL)")
print("3. In Render, set SECRET_KEY if not set")
print("4. Click 'Manual Deploy' -> 'Deploy latest commit'")
print("5. Wait 2-5 minutes")
print("6. Test: https://python-2057.onrender.com/health")
print("7. Test: https://python-2057.onrender.com/auth/login")
print("=" * 60)
