"""
Quick script to test Render PostgreSQL connection
Run this after setting your DATABASE_URL
"""
import os
from app import create_app, db

def test_render_connection():
    """Test connection to Render PostgreSQL database"""
    print("=" * 60)
    print("Render PostgreSQL Connection Test")
    print("=" * 60)
    
    # Check DATABASE_URL
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("\n[ERROR] DATABASE_URL not set!")
        print("\nTo set it, run one of these:")
        print("\nPowerShell:")
        print('  $env:DATABASE_URL="postgresql://seait_lost_and_found_user:PASSWORD@dpg-d6dd5ip4tr6s73co3uhg-a:5432/seait_lost_and_found"')
        print("\nOr create a .env file with:")
        print('  DATABASE_URL=postgresql://seait_lost_and_found_user:PASSWORD@dpg-d6dd5ip4tr6s73co3uhg-a:5432/seait_lost_and_found')
        return False
    
    # Mask password in output
    if '@' in db_url:
        parts = db_url.split('@')
        if '://' in parts[0]:
            protocol_user = parts[0].split('://')
            if len(protocol_user) == 2:
                user_pass = protocol_user[1]
                if ':' in user_pass:
                    user = user_pass.split(':')[0]
                    masked = f"{protocol_user[0]}://{user}:***@{parts[1]}"
                    print(f"\n[OK] DATABASE_URL is set")
                    print(f"  Connection: {masked}")
    
    print("\nTesting connection...")
    print("Note: Using external URL for local testing")
    print("      Render will use internal URL automatically when deployed")
    
    try:
        app = create_app()
        with app.app_context():
            # Test connection
            conn = db.engine.connect()
            print("[OK] Database connection successful!")
            conn.close()
            
            # Check tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"[OK] Found {len(tables)} tables:")
                for table in tables:
                    print(f"    - {table}")
            else:
                print("[WARNING] No tables found. You need to run migrations:")
                print("   flask db init")
                print("   flask db migrate -m 'Initial migration'")
                print("   flask db upgrade")
            
            # Test query if users table exists
            if 'users' in tables:
                from app.models.user import User
                try:
                    user_count = User.query.count()
                    print(f"\n[OK] Query test successful! Found {user_count} users.")
                    if user_count == 0:
                        print("  [TIP] Run 'python seed_data.py' to create admin user")
                except Exception as e:
                    print(f"[WARNING] Query test failed: {e}")
            
            print("\n" + "=" * 60)
            print("[SUCCESS] Connection test completed successfully!")
            print("=" * 60)
            return True
            
    except Exception as e:
        print(f"\n[ERROR] Connection failed!")
        print(f"  Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify password is correct in DATABASE_URL")
        print("2. Check if database is accessible from your IP")
        print("3. Ensure database is running on Render")
        print("4. Check firewall/network settings")
        print("5. Verify hostname, port, username, and database name")
        print("\n" + "=" * 60)
        return False

if __name__ == '__main__':
    test_render_connection()
