#!/usr/bin/env python3
"""
Fix Expired Active Plans
Marks plans with past end dates as inactive
"""

import os
from dotenv import load_dotenv
from datetime import date

# Load environment variables
load_dotenv()

def fix_expired_plans():
    """Mark expired plans as inactive"""
    print("🔧 Fixing Expired Active Plans...")
    print("=" * 60)
    
    try:
        from app import app, db, CustomerPlan
        
        with app.app_context():
            # Find expired active plans
            expired_plans = CustomerPlan.query.filter(
                CustomerPlan.is_active == True,
                CustomerPlan.end_date < date.today()
            ).all()
            
            if not expired_plans:
                print("✅ No expired active plans found!")
                return True
            
            print(f"Found {len(expired_plans)} expired active plans:")
            print("-" * 60)
            
            for plan in expired_plans:
                print(f"Plan ID {plan.id}: Customer {plan.customer_id}, End Date: {plan.end_date}")
                plan.is_active = False
            
            db.session.commit()
            
            print("-" * 60)
            print(f"✅ Fixed {len(expired_plans)} expired plans!")
            return True
            
    except Exception as e:
        print(f"❌ Error fixing plans: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        if fix_expired_plans():
            print("\n✅ All done!")
        else:
            print("\n❌ Fix failed!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
