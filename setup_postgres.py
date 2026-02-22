"""
Script to help set up PostgreSQL connection
Run this to test your PostgreSQL connection
"""
import os
from app import create_app, db
from app.models.user import User

def test_connection():
    """Test database connection"""
    app = create_app()
    
    with app.app_context():
        try:
            # Test connection
            db.engine.connect()
            print("✓ Database connection successful!")
            
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"✓ Found {len(tables)} tables: {', '.join(tables)}")
            else:
                print("⚠ No tables found. Run migrations: flask db upgrade")
            
            # Test query
            try:
                user_count = User.query.count()
                print(f"✓ Query test successful! Found {user_count} users.")
            except Exception as e:
                print(f"⚠ Query test failed (tables may not exist): {e}")
                print("   Run: flask db upgrade")
            
            return True
        except Exception as e:
            print(f"✗ Database connection failed!")
            print(f"  Error: {e}")
            print("\nTroubleshooting:")
            print("1. Check DATABASE_URL is set correctly")
            print("2. Verify PostgreSQL server is running")
            print("3. Check username, password, host, and database name")
            print("4. Ensure database exists")
            print("5. Check firewall/network settings")
            return False

if __name__ == '__main__':
    print("=" * 50)
    print("PostgreSQL Connection Test")
    print("=" * 50)
    
    # Check if DATABASE_URL is set
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        print(f"✓ DATABASE_URL is set")
        # Mask password in output
        if '@' in db_url:
            parts = db_url.split('@')
            if ':' in parts[0]:
                user_pass = parts[0].split('://')[1] if '://' in parts[0] else parts[0]
                if ':' in user_pass:
                    user = user_pass.split(':')[0]
                    masked = f"{db_url.split('://')[0]}://{user}:***@{parts[1]}"
                    print(f"  Connection: {masked}")
    else:
        print("⚠ DATABASE_URL not set - will use SQLite")
        print("  To use PostgreSQL, set DATABASE_URL environment variable")
        print("  Example: export DATABASE_URL='postgresql://user:pass@host:5432/db'")
    
    print("\nTesting connection...")
    test_connection()
    print("=" * 50)
