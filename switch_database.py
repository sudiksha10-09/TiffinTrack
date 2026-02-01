#!/usr/bin/env python3
"""
Database Switcher for TiffinTrack
Easily switch between SQLite (development) and Neon PostgreSQL (production)
"""

import os
import sys
from dotenv import load_dotenv, set_key

def switch_to_sqlite():
    """Switch to SQLite database for local development"""
    print("🔄 Switching to SQLite database...")
    
    # Update .env file
    set_key('.env', 'DATABASE_URL', 'sqlite:///tiffintrack.db')
    
    # Initialize database
    try:
        from app import app, db, seed_initial_data
        with app.app_context():
            db.create_all()
            seed_initial_data()
        print("✅ SQLite database initialized successfully!")
        print("📍 Database file: tiffintrack.db")
        print("🚀 You can now run: python app.py")
    except Exception as e:
        print(f"❌ Error initializing SQLite: {e}")

def switch_to_neon():
    """Switch to Neon PostgreSQL database"""
    print("🔄 Switching to Neon PostgreSQL...")
    
    # Default Neon URL (pre-configured)
    default_neon_url = "postgresql://neondb_owner:npg_nsMXcjJ1pB9t@ep-red-paper-ah0u6oe0-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
    
    print("Using pre-configured Neon PostgreSQL database...")
    neon_url = input(f"Press Enter to use default Neon URL, or enter custom URL: ").strip()
    
    if not neon_url:
        neon_url = default_neon_url
        print("✅ Using default Neon PostgreSQL configuration")
    
    if not neon_url.startswith('postgresql://'):
        print("❌ Invalid PostgreSQL URL. Should start with 'postgresql://'")
        return
    
    # Update .env file
    set_key('.env', 'DATABASE_URL', neon_url)
    
    # Test connection
    try:
        from app import app, db, User, Plan
        with app.app_context():
            # Test connection
            db.engine.connect()
            print("✅ Neon connection successful!")
            
            # Show current data
            user_count = User.query.count()
            plan_count = Plan.query.count()
            print(f"📊 Database contains {user_count} users and {plan_count} plans")
            
            # Initialize if needed
            if user_count == 0:
                choice = input("Database is empty. Initialize with sample data? (Y/n): ").lower()
                if choice != 'n':
                    from app import seed_initial_data
                    db.create_all()
                    seed_initial_data()
                    print("✅ Neon database initialized!")
            
        print("🚀 You can now run: python app.py")
    except Exception as e:
        print(f"❌ Error connecting to Neon: {e}")
        print("💡 Switching back to SQLite...")
        switch_to_sqlite()

def show_current_database():
    """Show current database configuration"""
    load_dotenv()
    db_url = os.getenv('DATABASE_URL', 'Not set')
    
    print("📊 Current Database Configuration:")
    print("-" * 40)
    
    if 'sqlite' in db_url.lower():
        print("🗄️  Type: SQLite (Development)")
        print(f"📁 File: {db_url.replace('sqlite:///', '')}")
    elif 'postgresql' in db_url.lower():
        print("🌐 Type: PostgreSQL (Production)")
        # Hide password in URL
        safe_url = db_url.split('@')[1] if '@' in db_url else db_url
        print(f"🔗 Host: {safe_url.split('/')[0]}")
    else:
        print("❓ Type: Unknown")
    
    print(f"🔧 Full URL: {db_url[:50]}{'...' if len(db_url) > 50 else ''}")

def main():
    """Main menu for database switching"""
    print("🍱 TiffinTrack Database Switcher")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Show current database")
        print("2. Switch to SQLite (Development)")
        print("3. Switch to Neon PostgreSQL (Production)")
        print("4. Test current connection")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            show_current_database()
        elif choice == '2':
            switch_to_sqlite()
        elif choice == '3':
            switch_to_neon()
        elif choice == '4':
            test_connection()
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")

def test_connection():
    """Test current database connection"""
    print("🔍 Testing database connection...")
    
    try:
        from app import app, db, User, Plan
        with app.app_context():
            # Test connection
            db.engine.connect()
            
            # Test query
            user_count = User.query.count()
            plan_count = Plan.query.count()
            
            print("✅ Connection successful!")
            print(f"👥 Users in database: {user_count}")
            print(f"🍱 Plans in database: {plan_count}")
            
            # Show database type
            db_url = os.getenv('DATABASE_URL', '')
            if 'postgresql' in db_url.lower():
                print("🌐 Database type: Neon PostgreSQL")
            elif 'sqlite' in db_url.lower():
                print("🗄️  Database type: SQLite")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Try switching to SQLite for local development")

if __name__ == "__main__":
    main()