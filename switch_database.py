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
    
    neon_url = input("Enter your Neon PostgreSQL URL: ").strip()
    
    if not neon_url.startswith('postgresql://'):
        print("❌ Invalid PostgreSQL URL. Should start with 'postgresql://'")
        return
    
    # Update .env file
    set_key('.env', 'DATABASE_URL', neon_url)
    
    # Test connection
    try:
        from app import app, db, seed_initial_data
        with app.app_context():
            # Test connection
            db.engine.connect()
            print("✅ Neon connection successful!")
            
            # Initialize if needed
            choice = input("Initialize database with tables and data? (y/N): ").lower()
            if choice == 'y':
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
        from app import app, db, User
        with app.app_context():
            # Test connection
            db.engine.connect()
            
            # Test query
            user_count = User.query.count()
            
            print("✅ Connection successful!")
            print(f"👥 Users in database: {user_count}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Try switching to SQLite for local development")

if __name__ == "__main__":
    main()