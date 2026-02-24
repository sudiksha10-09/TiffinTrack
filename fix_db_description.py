#!/usr/bin/env python3
"""
Fix the plans.description column to allow unlimited length
Run this script on your AWS server to fix the database schema
"""

import os
import sys
from sqlalchemy import create_engine, text

def fix_description_column():
    """Change description column from VARCHAR(255) to TEXT"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ Error: DATABASE_URL not found in environment")
        print("Make sure you're running this from the TiffinTrack directory with .env loaded")
        sys.exit(1)
    
    print("🔧 TiffinTrack Database Fix")
    print("=" * 50)
    print(f"📊 Database: {database_url.split('@')[1] if '@' in database_url else 'local'}")
    print()
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Connect and execute
        with engine.connect() as conn:
            print("📝 Changing description column from VARCHAR(255) to TEXT...")
            
            # Execute the ALTER TABLE command
            conn.execute(text("ALTER TABLE plans ALTER COLUMN description TYPE TEXT;"))
            conn.commit()
            
            print("✅ Column type changed successfully!")
            print()
            
            # Verify the change
            print("🔍 Verifying the change...")
            result = conn.execute(text("""
                SELECT column_name, data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'plans' AND column_name = 'description';
            """))
            
            row = result.fetchone()
            if row:
                print(f"   Column: {row[0]}")
                print(f"   Type: {row[1]}")
                print(f"   Max Length: {row[2] if row[2] else 'Unlimited ✅'}")
            
            print()
            print("✅ Database fix completed successfully!")
            print()
            print("Next steps:")
            print("1. Restart the application: sudo systemctl restart tiffintrack")
            print("2. Try adding your plan again")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check your DATABASE_URL in .env")
        print("2. Make sure you have database access")
        print("3. Try running manually in psql")
        sys.exit(1)

if __name__ == "__main__":
    fix_description_column()
