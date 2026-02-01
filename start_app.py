#!/usr/bin/env python3
"""
TiffinTrack Application Starter
Ensures database is working before starting the app
"""

import os
import sys
from dotenv import load_dotenv

def check_database():
    """Check and initialize database if needed"""
    print("🔍 Checking database connection...")
    
    try:
        from app import app, db, seed_initial_data, User
        
        with app.app_context():
            # Test connection
            db.engine.connect()
            
            # Check if database has data
            user_count = User.query.count()
            
            if user_count == 0:
                print("📊 Database is empty, initializing...")
                db.create_all()
                seed_initial_data()
                print("✅ Database initialized with sample data")
            else:
                print(f"✅ Database ready with {user_count} users")
                
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        
        # Try to initialize SQLite database
        print("🔄 Attempting to create SQLite database...")
        try:
            # Force SQLite
            os.environ['DATABASE_URL'] = 'sqlite:///tiffintrack.db'
            
            from app import app, db, seed_initial_data
            with app.app_context():
                db.create_all()
                seed_initial_data()
            
            print("✅ SQLite database created successfully")
            return True
            
        except Exception as init_error:
            print(f"❌ Failed to initialize database: {init_error}")
            return False

def main():
    """Main startup function"""
    print("🍱 TiffinTrack Application Starter")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check database
    if not check_database():
        print("❌ Cannot start application - database issues")
        print("💡 Try running: python switch_database.py")
        sys.exit(1)
    
    # Start the application
    print("🚀 Starting TiffinTrack...")
    print("📱 Access at: http://127.0.0.1:5000")
    print("👤 Admin: admin@tiffintrack.com / admin123")
    print("=" * 40)
    
    try:
        from app import app
        app.run(debug=True, host='127.0.0.1', port=5000)
    except KeyboardInterrupt:
        print("\n👋 TiffinTrack stopped by user")
    except Exception as e:
        print(f"❌ Application error: {e}")

if __name__ == "__main__":
    main()