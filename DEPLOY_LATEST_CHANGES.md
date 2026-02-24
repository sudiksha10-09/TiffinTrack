# Deploy Latest Changes to AWS

## What's New

### 1. Multi-Plan Management System ✨
- Customers can have multiple active plans simultaneously
- Plans are categorized as "Running" and "Upcoming"
- Cancel upcoming plans before they start
- Add new plans without disrupting existing ones
- Better dashboard visualization

### 2. Plan Description Fix 🔧
- Changed description field from VARCHAR(255) to TEXT
- Allows unlimited length descriptions
- Character counter in admin form
- Better UI for plan creation

### 3. Login Page Cleanup 🎨
- Removed demo credentials box
- Cleaner, more professional look
- Better form positioning

## Deployment Steps

### Step 1: Pull Latest Code

```bash
# SSH into your AWS server
ssh ubuntu@your-server-ip

# Navigate to project
cd ~/TiffinTrack

# Pull latest changes
git fetch origin
git pull origin main
```

### Step 2: Fix Database Schema

**IMPORTANT:** Run this SQL command to fix the description column:

```bash
# Option A: Using the automated script
chmod +x fix_description.sh
./fix_description.sh

# Option B: Manual SQL command
echo "ALTER TABLE plans ALTER COLUMN description TYPE TEXT;" | \
  psql "$(grep DATABASE_URL .env | cut -d '=' -f2-)"
```

**Or use Neon Dashboard:**
1. Go to https://console.neon.tech
2. Open SQL Editor
3. Run: `ALTER TABLE plans ALTER COLUMN description TYPE TEXT;`

### Step 3: Restart Application

```bash
# Restart the service
sudo systemctl restart tiffintrack

# Check status
sudo systemctl status tiffintrack

# Check logs for any errors
sudo journalctl -u tiffintrack -n 50 --no-pager
```

### Step 4: Verify Deployment

1. **Check Application is Running:**
```bash
curl -I https://your-domain.com
# Should return: HTTP/2 200
```

2. **Test Login Page:**
- Visit your site
- Click "Sign In"
- Verify demo credentials box is gone ✅
- Form should be positioned nicely ✅

3. **Test Multi-Plan System:**
- Login as customer
- Go to dashboard
- Check if plans are categorized as "Running" and "Upcoming" ✅
- Try adding a new plan ✅
- Verify existing plans remain active ✅

4. **Test Plan Creation:**
- Login as admin
- Go to "Manage Plans"
- Click "Add New Plan"
- Write a LONG description (500+ characters) ✅
- Should save without errors ✅

## Verification Checklist

- [ ] Code pulled successfully
- [ ] Database schema updated (description is TEXT)
- [ ] Application restarted
- [ ] No errors in logs
- [ ] Login page looks clean (no demo box)
- [ ] Dashboard shows running/upcoming plans
- [ ] Can add new plans without deleting existing ones
- [ ] Can create plans with long descriptions
- [ ] Character counter works in admin form

## Troubleshooting

### If Application Won't Start

```bash
# Check logs
sudo journalctl -u tiffintrack -n 100 --no-pager

# Check if port is in use
sudo lsof -i :8000

# Restart manually
cd ~/TiffinTrack
source venv/bin/activate
gunicorn --bind 0.0.0.0:8000 app:app
```

### If Database Update Fails

```bash
# Check database connection
psql "$(grep DATABASE_URL .env | cut -d '=' -f2-)" -c "SELECT version();"

# Try manual update
psql "$(grep DATABASE_URL .env | cut -d '=' -f2-)" << EOF
ALTER TABLE plans ALTER COLUMN description TYPE TEXT;
\q
EOF
```

### If Plans Not Showing Correctly

```bash
# Check database
psql "$(grep DATABASE_URL .env | cut -d '=' -f2-)" -c "
SELECT id, name, start_date, end_date, is_active 
FROM customer_plans 
WHERE customer_id = 1 
ORDER BY start_date;
"
```

## Rollback Plan

If something goes wrong:

```bash
# Revert to previous commit
cd ~/TiffinTrack
git reset --hard f2b61a6

# Restart
sudo systemctl restart tiffintrack
```

## Post-Deployment Tasks

1. **Test with Real Users:**
   - Have a customer try subscribing to multiple plans
   - Verify billing calculations are correct
   - Check pause calendar works with multiple plans

2. **Monitor Logs:**
```bash
# Watch logs in real-time
sudo journalctl -u tiffintrack -f
```

3. **Update Documentation:**
   - Inform customers about multi-plan feature
   - Update help/FAQ if needed

## Summary of Changes

### Files Modified:
- `app.py` - Multi-plan logic, description field fix
- `templates/customer_dashboard_professional.html` - Running/upcoming plans display
- `templates/login_professional.html` - Removed demo credentials
- `templates/admin_plan_form.html` - Character counter

### Files Added:
- `MULTI_PLAN_SYSTEM.md` - Multi-plan documentation
- `MULTI_PLAN_UPDATE_SUMMARY.md` - Update summary
- `PLAN_DESCRIPTION_FIX.md` - Description fix guide
- `PLAN_FIXES_SUMMARY.md` - Fixes summary
- `FIX_PLAN_DESCRIPTION.sql` - SQL fix script
- `fix_description.sh` - Automated fix script
- `QUICK_FIX.md` - Quick reference
- `DEPLOY_LATEST_CHANGES.md` - This file

### Database Changes:
- `plans.description`: VARCHAR(255) → TEXT

## Support

If you encounter any issues:

1. Check the logs: `sudo journalctl -u tiffintrack -n 100`
2. Verify database connection: Check `.env` file
3. Test manually: Run `python app.py` to see errors
4. Check documentation files for specific issues

---

**Deployment Date:** February 24, 2026
**Version:** 2.1
**Status:** Ready for Production ✅
