#!/usr/bin/env python3
"""
Diagnostic script to check database location and status.
Run this to see where your database is stored and if it exists.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database():
    """Check database location and status."""
    print("=" * 60)
    print("Database Diagnostic Tool")
    print("=" * 60)
    print()
    
    # Get the database path
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    db_path = os.path.join(instance_path, 'app.db')
    
    print(f"Expected database location:")
    print(f"  Directory: {instance_path}")
    print(f"  File: {db_path}")
    print()
    
    # Check if directory exists
    if os.path.exists(instance_path):
        print(f"✓ Instance directory exists")
    else:
        print(f"✗ Instance directory does NOT exist")
        print(f"  It will be created automatically when you run the app")
    
    print()
    
    # Check if database file exists
    if os.path.exists(db_path):
        print(f"✓ Database file EXISTS")
        file_size = os.path.getsize(db_path)
        print(f"  Size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
        
        # Try to check if it's a valid SQLite database
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check for users table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if cursor.fetchone():
                print(f"✓ Database has 'users' table")
                
                # Count users
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                print(f"  Number of users: {user_count}")
                
                if user_count > 0:
                    # List users
                    cursor.execute("SELECT id, username, email, created_at FROM users")
                    users = cursor.fetchall()
                    print(f"  Users in database:")
                    for user_id, username, email, created_at in users:
                        print(f"    - ID {user_id}: {username} ({email}) - Created: {created_at}")
            else:
                print(f"✗ Database exists but 'users' table not found")
                print(f"  The database may be corrupted or not initialized")
            
            conn.close()
        except Exception as e:
            print(f"✗ Error reading database: {e}")
    else:
        print(f"✗ Database file does NOT exist")
        print(f"  This means:")
        print(f"    - No users have been registered yet, OR")
        print(f"    - The app hasn't been run yet, OR")
        print(f"    - The database was deleted")
        print(f"  The database will be created automatically when you:")
        print(f"    1. Run the app (python app.py)")
        print(f"    2. Register your first user account")
    
    print()
    print("=" * 60)
    print("Troubleshooting:")
    print("=" * 60)
    print()
    print("If your account isn't persisting:")
    print("1. Make sure you're running the app from the project directory")
    print("2. Check that the database file exists (see above)")
    print("3. Try registering again - the account should be saved")
    print("4. After registering, check this script again to verify the user exists")
    print()
    print("To reset everything (delete all users and data):")
    print(f"  rm -rf {instance_path}")
    print()

if __name__ == '__main__':
    check_database()

