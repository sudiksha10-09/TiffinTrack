#!/usr/bin/env python3
"""
Database Integrity Checker for TiffinTrack
Checks database connection, tables, and data integrity
"""

import os
import sys
from dotenv import load_dotenv
from datetime import date

# Load environment variables
load_dotenv()

def check_connection():
    """Check database connection"""
    print("🔌 Testing Database Connection...")
    print("-" * 60)
    
    try:
        from app import app, db
        
        with app.app_context():
            # Test connection
            connection = db.engine.connect()
            connection.close()
            
            # Get database URL (masked)
            db_url = os.getenv('DATABASE_URL', 'Not set')
            if '@' in db_url:
                # Mask password
                parts = db_url.split('@')
                masked = parts[0].split(':')[0] + ':****@' + parts[1]
            else:
                masked = db_url
            
            print(f"✅ Connection successful")
            print(f"   Database: {masked}")
            return True
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def check_tables():
    """Check if all required tables exist and are accessible"""
    print("\n📊 Checking Database Tables...")
    print("-" * 60)
    
    try:
        from app import app, db, User, Plan, CustomerPlan, PausedDate, Bill, Menu, Payment, PaymentLog
        
        with app.app_context():
            tables = {
                'users': User,
                'plans': Plan,
                'customer_plans': CustomerPlan,
                'paused_dates': PausedDate,
                'bills': Bill,
                'menus': Menu,
                'payments': Payment,
                'payment_logs': PaymentLog
            }
            
            all_good = True
            total_records = 0
            
            for table_name, model in tables.items():
                try:
                    count = model.query.count()
                    total_records += count
                    status = "✅" if count > 0 else "⚠️ "
                    print(f"{status} {table_name:20} - {count:4} records")
                except Exception as e:
                    print(f"❌ {table_name:20} - Error: {str(e)[:40]}")
                    all_good = False
            
            print(f"\n   Total records: {total_records}")
            return all_good
            
    except Exception as e:
        print(f"❌ Table check failed: {e}")
        return False

def check_data_integrity():
    """Check data integrity and relationships"""
    print("\n🔍 Checking Data Integrity...")
    print("-" * 60)
    
    try:
        from app import app, db, User, Plan, CustomerPlan, Bill
        
        with app.app_context():
            issues = []
            
            # Check for orphaned customer plans
            orphaned_plans = db.session.query(CustomerPlan).filter(
                ~CustomerPlan.customer_id.in_(db.session.query(User.id))
            ).count()
            
            if orphaned_plans > 0:
                issues.append(f"⚠️  {orphaned_plans} customer plans with invalid customer_id")
            else:
                print("✅ No orphaned customer plans")
            
            # Check for orphaned bills
            orphaned_bills = db.session.query(Bill).filter(
                ~Bill.customer_id.in_(db.session.query(User.id))
            ).count()
            
            if orphaned_bills > 0:
                issues.append(f"⚠️  {orphaned_bills} bills with invalid customer_id")
            else:
                print("✅ No orphaned bills")
            
            # Check for active plans with past end dates
            expired_active = CustomerPlan.query.filter(
                CustomerPlan.is_active == True,
                CustomerPlan.end_date < date.today()
            ).count()
            
            if expired_active > 0:
                issues.append(f"⚠️  {expired_active} active plans with past end dates (should be inactive)")
            else:
                print("✅ No expired active plans")
            
            # Check for users without email
            users_no_email = User.query.filter(
                (User.email == None) | (User.email == '')
            ).count()
            
            if users_no_email > 0:
                issues.append(f"⚠️  {users_no_email} users without email")
            else:
                print("✅ All users have email")
            
            # Check for duplicate emails
            from sqlalchemy import func
            duplicate_emails = db.session.query(
                User.email,
                func.count(User.id)
            ).group_by(User.email).having(func.count(User.id) > 1).count()
            
            if duplicate_emails > 0:
                issues.append(f"⚠️  {duplicate_emails} duplicate email addresses")
            else:
                print("✅ No duplicate emails")
            
            if issues:
                print("\n⚠️  Issues Found:")
                for issue in issues:
                    print(f"   {issue}")
                return False
            else:
                print("\n✅ All integrity checks passed!")
                return True
            
    except Exception as e:
        print(f"❌ Integrity check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_statistics():
    """Show database statistics"""
    print("\n📈 Database Statistics...")
    print("-" * 60)
    
    try:
        from app import app, db, User, Plan, CustomerPlan, Bill
        
        with app.app_context():
            # User statistics
            total_users = User.query.count()
            admin_users = User.query.filter_by(is_admin=True).count()
            customer_users = User.query.filter_by(is_admin=False).count()
            
            print(f"👥 Users:")
            print(f"   Total:     {total_users}")
            print(f"   Admins:    {admin_users}")
            print(f"   Customers: {customer_users}")
            
            # Plan statistics
            total_plans = Plan.query.count()
            active_plans = Plan.query.filter_by(is_active=True).count()
            
            print(f"\n🍽️  Plans:")
            print(f"   Total:  {total_plans}")
            print(f"   Active: {active_plans}")
            
            # Subscription statistics
            total_subs = CustomerPlan.query.count()
            active_subs = CustomerPlan.query.filter(
                CustomerPlan.is_active == True,
                CustomerPlan.end_date >= date.today()
            ).count()
            
            print(f"\n📅 Subscriptions:")
            print(f"   Total:  {total_subs}")
            print(f"   Active: {active_subs}")
            
            # Bill statistics
            total_bills = Bill.query.count()
            paid_bills = Bill.query.filter_by(is_paid=True).count()
            unpaid_bills = Bill.query.filter_by(is_paid=False).count()
            
            if total_bills > 0:
                total_amount = db.session.query(db.func.sum(Bill.amount)).scalar() or 0
                paid_amount = db.session.query(db.func.sum(Bill.amount)).filter(
                    Bill.is_paid == True
                ).scalar() or 0
                
                print(f"\n💰 Bills:")
                print(f"   Total:  {total_bills} (₹{total_amount:,.2f})")
                print(f"   Paid:   {paid_bills} (₹{paid_amount:,.2f})")
                print(f"   Unpaid: {unpaid_bills} (₹{total_amount - paid_amount:,.2f})")
            
    except Exception as e:
        print(f"❌ Statistics failed: {e}")

def main():
    """Main function"""
    print("=" * 60)
    print("🍱 TiffinTrack Database Integrity Checker")
    print("=" * 60)
    print()
    
    # Check connection
    if not check_connection():
        print("\n❌ Cannot proceed without database connection")
        sys.exit(1)
    
    # Check tables
    if not check_tables():
        print("\n⚠️  Some tables have issues")
    
    # Check data integrity
    check_data_integrity()
    
    # Show statistics
    show_statistics()
    
    print("\n" + "=" * 60)
    print("✅ Database check complete!")
    print("=" * 60)
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Check cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
