# Plan Description Length Fix

## Problem
When adding a new plan with a long description, you get this error:
```
sqlalchemy.exc.DataError: (psycopg2.errors.StringDataRightTruncation) 
value too long for type character varying(255)
```

## Root Cause
The `plans.description` column is defined as `VARCHAR(255)`, which limits descriptions to 255 characters. Your Gulab Jamun description is longer than this.

## Solution
Change the column type from `VARCHAR(255)` to `TEXT` to allow unlimited length descriptions.

## Fix Steps

### Option 1: Using SQL (Recommended - Fastest)

1. **Connect to your AWS database:**
```bash
# Get your database connection string from .env
cat .env | grep DATABASE_URL

# Connect using psql
psql "your_database_url_here"
```

2. **Run the SQL command:**
```sql
ALTER TABLE plans ALTER COLUMN description TYPE TEXT;
```

3. **Verify the change:**
```sql
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'plans' AND column_name = 'description';
```

Expected output:
```
 column_name | data_type | character_maximum_length 
-------------+-----------+-------------------------
 description | text      | 
```

4. **Restart your application:**
```bash
sudo systemctl restart tiffintrack
```

### Option 2: Using Alembic Migration

1. **Run the migration:**
```bash
cd ~/TiffinTrack
source venv/bin/activate
flask db upgrade
```

2. **Restart the application:**
```bash
sudo systemctl restart tiffintrack
```

### Option 3: Manual Database Update (If you don't have psql)

You can use any PostgreSQL client or the Neon dashboard:

1. Go to your Neon dashboard
2. Open the SQL Editor
3. Run this command:
```sql
ALTER TABLE plans ALTER COLUMN description TYPE TEXT;
```
4. Restart your application

## Code Changes Made

### app.py (Line 343)
```python
# Before:
description = db.Column(db.String(255))

# After:
description = db.Column(db.Text)  # Changed to Text for longer descriptions
```

## Testing

After applying the fix, try adding your plan again:

1. Go to Admin Dashboard → Manage Plans
2. Click "Add New Plan"
3. Fill in the details with your long description
4. Upload image
5. Click "Create Plan"

The plan should now be created successfully!

## Verification

Check that the plan was created:
```bash
# On AWS server
sudo journalctl -u tiffintrack -n 20 --no-pager
```

You should see:
```
Plan 'Gulab Jamun' created successfully!
```

## Benefits of TEXT Column

- ✅ Unlimited length (up to 1GB in PostgreSQL)
- ✅ No truncation errors
- ✅ Better for detailed descriptions
- ✅ Same performance as VARCHAR for short text
- ✅ More flexible for future content

## Rollback (If Needed)

If you need to revert:
```sql
ALTER TABLE plans ALTER COLUMN description TYPE VARCHAR(255);
```

Note: This will truncate any descriptions longer than 255 characters!

## Related Files

- `app.py` - Model definition updated
- `FIX_PLAN_DESCRIPTION.sql` - SQL script to run
- `migrations/versions/update_plan_description_to_text.py` - Alembic migration

## Quick Fix Command

If you just want to fix it quickly:
```bash
# SSH into AWS
ssh ubuntu@your-server-ip

# Run SQL directly
echo "ALTER TABLE plans ALTER COLUMN description TYPE TEXT;" | \
  psql "$(grep DATABASE_URL ~/TiffinTrack/.env | cut -d '=' -f2-)"

# Restart app
sudo systemctl restart tiffintrack

# Test
curl -I https://your-domain.com
```

## Prevention

To prevent similar issues in the future:

1. Use `Text` for any field that might have long content:
   - Descriptions
   - Comments
   - Notes
   - Messages
   - Content

2. Use `String(length)` only for:
   - Names (100-200 chars)
   - Emails (255 chars)
   - Phone numbers (20 chars)
   - Short codes (50 chars)

## Status

- ✅ Code updated in app.py
- ✅ Migration script created
- ✅ SQL script created
- ⏳ Database needs to be updated (run SQL command)
- ⏳ Application needs restart

---

**Last Updated:** February 24, 2026
**Priority:** High (Blocking plan creation)
**Impact:** Low (Simple column type change)
