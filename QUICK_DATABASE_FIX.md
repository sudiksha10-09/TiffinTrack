# Quick Database Fix for AWS

## The Problem
Your database still has `description VARCHAR(255)` but the code expects `TEXT`.

## The Fix (Choose One Method)

### Method 1: Using Python Script (Recommended)

```bash
cd ~/TiffinTrack

# Pull latest code
git pull origin main

# Run the fix script
python3 fix_db_description.py

# Restart app
sudo systemctl restart tiffintrack
```

### Method 2: Using Bash Script

```bash
cd ~/TiffinTrack

# Make executable
chmod +x fix_description.sh

# Run it
./fix_description.sh

# Restart app
sudo systemctl restart tiffintrack
```

### Method 3: Direct Python One-Liner

```bash
cd ~/TiffinTrack

# Load env and run fix
python3 -c "
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    conn.execute(text('ALTER TABLE plans ALTER COLUMN description TYPE TEXT;'))
    conn.commit()
    print('✅ Fixed!')
"

# Restart app
sudo systemctl restart tiffintrack
```

### Method 4: Using Neon Dashboard (Easiest)

1. Go to https://console.neon.tech
2. Login to your account
3. Select your TiffinTrack project
4. Click "SQL Editor" in the left sidebar
5. Paste this SQL:
   ```sql
   ALTER TABLE plans ALTER COLUMN description TYPE TEXT;
   ```
6. Click "Run" button
7. You should see "ALTER TABLE" success message
8. Go back to AWS and restart:
   ```bash
   sudo systemctl restart tiffintrack
   ```

## Verify It Worked

```bash
# Check logs - should see no more VARCHAR errors
sudo journalctl -u tiffintrack -n 20 --no-pager

# Try adding your Gulab Jamun plan again
# It should work now!
```

## Why This Happened

The code was updated to use `TEXT` instead of `VARCHAR(255)`, but the database schema wasn't updated yet. This is a one-time migration that needs to be run.

---

**Recommended:** Use Method 4 (Neon Dashboard) - it's the easiest and most reliable!
