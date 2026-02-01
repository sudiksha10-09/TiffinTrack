#!/usr/bin/env python3
"""
Test script to verify billable days calculation
"""

from datetime import date, timedelta
from calendar import monthrange
from app import app, db, User, Plan, CustomerPlan, PausedDate

def test_billable_days():
    """Test the billable days calculation logic"""
    with app.app_context():
        print("🧪 Testing Billable Days Calculation")
        print("=" * 50)
        
        # Get a test customer
        customer = User.query.filter_by(email="rahul.sharma@email.com").first()
        if not customer:
            print("❌ Test customer not found")
            return
        
        print(f"👤 Testing for customer: {customer.fullname}")
        
        # Get current month info
        current_month = date.today().month
        current_year = date.today().year
        current_month_start = date(current_year, current_month, 1)
        current_month_end = date(current_year, current_month, monthrange(current_year, current_month)[1])
        
        print(f"📅 Current month: {current_month_start} to {current_month_end}")
        
        # Get customer's active plans
        active_plans = db.session.query(CustomerPlan, Plan).join(Plan).filter(
            CustomerPlan.customer_id == customer.id,
            CustomerPlan.is_active == True,
            CustomerPlan.end_date >= date.today()
        ).all()
        
        print(f"📋 Active plans: {len(active_plans)}")
        
        # Calculate plan days and billing
        total_plan_days = 0
        estimated_bill = 0
        
        for cp, plan in active_plans:
            # Calculate overlap with current month
            plan_start = max(cp.start_date, current_month_start)
            plan_end = min(cp.end_date, current_month_end)
            
            if plan_start <= plan_end:
                plan_days = (plan_end - plan_start).days + 1
                total_plan_days += plan_days
                
                print(f"  📦 {plan.name}:")
                print(f"     Plan period: {cp.start_date} to {cp.end_date}")
                print(f"     Month overlap: {plan_start} to {plan_end}")
                print(f"     Days in month: {plan_days}")
                print(f"     Daily rate: ₹{plan.daily_rate}")
                
                # Get paused days for this plan
                plan_paused = PausedDate.query.filter(
                    PausedDate.customer_id == customer.id,
                    PausedDate.pause_date >= plan_start,
                    PausedDate.pause_date <= plan_end
                ).count()
                
                billable_days = plan_days - plan_paused
                plan_cost = billable_days * plan.daily_rate
                estimated_bill += plan_cost
                
                print(f"     Paused days: {plan_paused}")
                print(f"     Billable days: {billable_days}")
                print(f"     Plan cost: ₹{plan_cost}")
                print()
        
        # Get total paused days this month
        paused_this_month = PausedDate.query.filter(
            PausedDate.customer_id == customer.id,
            db.extract('month', PausedDate.pause_date) == current_month,
            db.extract('year', PausedDate.pause_date) == current_year
        ).count()
        
        billable_days_total = total_plan_days - paused_this_month
        
        print("📊 SUMMARY:")
        print(f"   Total plan days this month: {total_plan_days}")
        print(f"   Total paused days this month: {paused_this_month}")
        print(f"   Total billable days: {billable_days_total}")
        print(f"   Estimated bill: ₹{estimated_bill}")
        print()
        
        # Show paused dates
        paused_dates = PausedDate.query.filter(
            PausedDate.customer_id == customer.id,
            db.extract('month', PausedDate.pause_date) == current_month,
            db.extract('year', PausedDate.pause_date) == current_year
        ).all()
        
        if paused_dates:
            print("⏸️  PAUSED DATES:")
            for pause in paused_dates:
                print(f"   {pause.pause_date}")
        else:
            print("⏸️  No paused dates this month")
        
        print("\n✅ Test completed successfully!")

if __name__ == "__main__":
    test_billable_days()