#!/usr/bin/env python3
"""
Add Real Users to TiffinTrack Database
Adds 3 real-like users: Diksha Shitole, Tanishka Singh, Pooja Ware
"""

import os
import sys
from dotenv import load_dotenv
from datetime import date, timedelta

# Load environment variables
load_dotenv()

def check_database_integrity():
    """Check database connection and integrity"""
    print("🔍 Checking Database Integrity...")
    print("=" * 60)
    
    try:
        from app import app, db, User, Plan, CustomerPlan, Bill
        
        with app.app_context():
            # Test connection
            db.engine.connect()
            print("✅ Database connection successful")
            
            # Check tables exist
            tables = {
                'users': User,
                'plans': Plan,
                'customer_plans': CustomerPlan,
                'bills': Bill
            }
            
            print("\n📊 Table Status:")
            print("-" * 60)
            
            for table_name, model in tables.items():
                try:
                    count = model.query.count()
                    print(f"✅ {table_name:20} - {count} records")
                except Exception as e:
                    print(f"❌ {table_name:20} - Error: {e}")
                    return False
            
            print("\n✅ All tables are accessible and healthy!")
            return True
            
    except Exception as e:
        print(f"❌ Database integrity check failed: {e}")
        return False

def add_real_users():
    """Add 3 real-like users to the database"""
    print("\n👥 Adding Real Users...")
    print("=" * 60)
    
    try:
        from app import app, db, User
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
            # Define users
            users_data = [
                {
                    'fullname': 'Diksha Shitole',
                    'email': 'diksha.shitole@email.com',
                    'password': 'diksha123',
                    'phone': '9876543210',
                    'addr1': 'Flat 101, Building A',
                    'addr2': 'Sector 17',
                    'area': 'Vashi',
                    'city': 'Navi Mumbai',
                    'state': 'Maharashtra',
                    'pincode': '400703'
                },
                {
                    'fullname': 'Tanishka Singh',
                    'email': 'tanishka.singh@email.com',
                    'password': 'tanishka123',
                    'phone': '9876543211',
                    'addr1': 'Flat 202, Tower B',
                    'addr2': 'Sector 8',
                    'area': 'Nerul',
                    'city': 'Navi Mumbai',
                    'state': 'Maharashtra',
                    'pincode': '400706'
                },
                {
                    'fullname': 'Pooja Ware',
                    'email': 'pooja.ware@email.com',
                    'password': 'pooja123',
                    'phone': '9876543212',
                    'addr1': 'Flat 303, Residency',
                    'addr2': 'Sector 21',
                    'area': 'Kharghar',
                    'city': 'Navi Mumbai',
                    'state': 'Maharashtra',
                    'pincode': '410210'
                }
            ]
            
            user_ids = []
            
            for user_data in users_data:
                # Check if user already exists
                existing_user = User.query.filter_by(email=user_data['email']).first()
                
                if existing_user:
                    print(f"⏭️  {user_data['fullname']:20} - Already exists (ID: {existing_user.id})")
                    user_ids.append(existing_user.id)
                    continue
                
                # Create new user
                new_user = User(
                    fullname=user_data['fullname'],
                    email=user_data['email'],
                    password=generate_password_hash(user_data['password']),
                    phone=user_data['phone'],
                    addr1=user_data['addr1'],
                    addr2=user_data['addr2'],
                    area=user_data['area'],
                    city=user_data['city'],
                    state=user_data['state'],
                    pincode=user_data['pincode'],
                    is_admin=False
                )
                
                db.session.add(new_user)
                db.session.flush()  # Get the ID
                
                print(f"✅ {user_data['fullname']:20} - Added (ID: {new_user.id})")
                user_ids.append(new_user.id)
            
            db.session.commit()
            
            print("\n📋 User Credentials:")
            print("-" * 60)
            for user_data in users_data:
                print(f"\n{user_data['fullname']}:")
                print(f"  Email:    {user_data['email']}")
                print(f"  Password: {user_data['password']}")
                print(f"  Phone:    {user_data['phone']}")
                print(f"  Area:     {user_data['area']}, {user_data['city']}")
            
            return user_ids
            
    except Exception as e:
        print(f"❌ Error adding users: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return []

def add_sample_subscriptions(user_ids):
    """Add sample subscriptions for the new users"""
    print("\n🍽️  Adding Sample Subscriptions...")
    print("=" * 60)
    
    try:
        from app import app, db, Plan, CustomerPlan, User
        
        with app.app_context():
            # Get available plans
            plans = Plan.query.filter_by(is_active=True).all()
            
            if not plans:
                print("⚠️  No active plans found. Skipping subscriptions.")
                return
            
            # Re-fetch users in this context
            users = [User.query.get(uid) for uid in user_ids]
            
            # Add subscriptions for each user
            today = date.today()
            
            subscriptions = [
                # Diksha - Premium plan for 30 days
                {
                    'user': users[0],
                    'plan': plans[0] if len(plans) > 0 else None,
                    'start_date': today,
                    'end_date': today + timedelta(days=30)
                },
                # Tanishka - Different plan for 15 days
                {
                    'user': users[1],
                    'plan': plans[1] if len(plans) > 1 else plans[0],
                    'start_date': today,
                    'end_date': today + timedelta(days=15)
                },
                # Pooja - Another plan for 7 days
                {
                    'user': users[2],
                    'plan': plans[2] if len(plans) > 2 else plans[0],
                    'start_date': today,
                    'end_date': today + timedelta(days=7)
                }
            ]
            
            for sub in subscriptions:
                if not sub['plan'] or not sub['user']:
                    continue
                
                # Check if subscription already exists
                existing = CustomerPlan.query.filter_by(
                    customer_id=sub['user'].id,
                    plan_id=sub['plan'].id,
                    is_active=True
                ).first()
                
                if existing:
                    print(f"⏭️  {sub['user'].fullname:20} - Already has {sub['plan'].name}")
                    continue
                
                # Create subscription
                customer_plan = CustomerPlan(
                    customer_id=sub['user'].id,
                    plan_id=sub['plan'].id,
                    start_date=sub['start_date'],
                    end_date=sub['end_date'],
                    is_active=True
                )
                
                db.session.add(customer_plan)
                
                days = (sub['end_date'] - sub['start_date']).days + 1
                print(f"✅ {sub['user'].fullname:20} - {sub['plan'].name} ({days} days)")
            
            db.session.commit()
            print("\n✅ Sample subscriptions added!")
            
    except Exception as e:
        print(f"❌ Error adding subscriptions: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("🍱 TiffinTrack - Add Real Users")
    print("=" * 60)
    print()
    
    # Check database integrity
    if not check_database_integrity():
        print("\n❌ Database integrity check failed!")
        print("Please fix database issues before adding users.")
        sys.exit(1)
    
    # Add users
    user_ids = add_real_users()
    
    if not user_ids:
        print("\n❌ Failed to add users!")
        sys.exit(1)
    
    # Add sample subscriptions
    if len(user_ids) == 3:
        add_sample_subscriptions(user_ids)
    
    print("\n" + "=" * 60)
    print("✅ All Done!")
    print("=" * 60)
    print("\nYou can now:")
    print("1. Login with any of the new user credentials")
    print("2. Test the customer dashboard")
    print("3. Generate bills for these users")
    print("4. Send payment reminders")
    print()
    print("Admin Panel: http://your-domain.com/admin")
    print("Customer Login: http://your-domain.com/login")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
