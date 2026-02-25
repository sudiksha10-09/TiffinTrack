# TiffinTrack Utility Scripts

This folder contains utility scripts for database management, testing, and maintenance.

## Scripts

### Database Management

**`check_db.py`**
- Checks database connection and integrity
- Validates table structure and relationships
- Shows statistics (users, plans, bills, subscriptions)
- Identifies data integrity issues (orphaned records, expired plans, duplicates)

Usage:
```bash
python scripts/check_db.py
```

**`add_users.py`**
- Adds test users to the database
- Creates sample subscriptions for testing
- Includes: Diksha Shitole, Tanishka Singh, Pooja Ware

Usage:
```bash
python scripts/add_users.py
```

**`fix_expired_plans.py`**
- Marks expired active plans as inactive
- Fixes data inconsistencies
- Should be run periodically or as a cron job

Usage:
```bash
python scripts/fix_expired_plans.py
```

### Testing & Utilities

**`test_utils.py`**
- Testing utilities and helper functions
- Used by test suite

**`utils.py`**
- Common utility functions
- Shared across the application

## Notes

- All scripts require the application to be properly configured (`.env` file)
- Database scripts connect to the configured database (Neon PostgreSQL or SQLite)
- Run scripts from the project root directory
