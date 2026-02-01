# 🔧 TiffinTrack Troubleshooting Guide

## 🗄️ Database Connection Issues

### **Neon PostgreSQL Connection Error**

**Error**: `could not translate host name "ep-xxx.us-east-1.aws.neon.tech" to address: Name or service not known`

**Possible Causes & Solutions:**

#### 1. **Network Connectivity Issues**
```bash
# Test DNS resolution
nslookup ep-red-paper-ah0u6oe0-pooler.c-3.us-east-1.aws.neon.tech

# Test internet connectivity
ping google.com
```

**Solutions:**
- Check your internet connection
- Try using a different DNS server (8.8.8.8, 1.1.1.1)
- Disable VPN if using one
- Check firewall settings

#### 2. **Neon Database Status**
- Check [Neon Status Page](https://status.neon.tech/)
- Verify your Neon project is active
- Check if your database was paused due to inactivity

#### 3. **Connection String Issues**
```bash
# Verify your connection string format
postgresql://username:password@host:port/database?sslmode=require
```

**Common Issues:**
- Expired password
- Incorrect hostname
- Missing SSL parameters
- Wrong database name

#### 4. **Quick Fix: Switch to SQLite**
For immediate development, switch to SQLite:

```bash
# Edit .env file
DATABASE_URL=sqlite:///tiffintrack.db

# Initialize database
python -c "from app import app, db, seed_initial_data; app.app_context().push(); db.create_all(); seed_initial_data()"
```

### **Neon Connection Troubleshooting Steps**

#### **Step 1: Verify Neon Project**
1. Go to [Neon Console](https://console.neon.tech/)
2. Check if your project exists and is active
3. Verify the connection string is correct

#### **Step 2: Test Connection**
```python
# Test connection script
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = "your_neon_url_here"

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

#### **Step 3: Check Network**
```bash
# Windows
nslookup ep-red-paper-ah0u6oe0-pooler.c-3.us-east-1.aws.neon.tech

# Test with curl
curl -I https://ep-red-paper-ah0u6oe0-pooler.c-3.us-east-1.aws.neon.tech
```

#### **Step 4: Alternative Connection Methods**

**Direct Connection (without pooler):**
```
postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require
```

**With different SSL mode:**
```
postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=prefer
```

## 🚀 Development vs Production Setup

### **Development (Recommended)**
```bash
# .env
DATABASE_URL=sqlite:///tiffintrack.db
SECRET_KEY=dev-secret-key
```

### **Production**
```bash
# .env
DATABASE_URL=postgresql://username:password@neon-host/dbname?sslmode=require
SECRET_KEY=super-secure-production-key
```

## 🔄 Database Migration Issues

### **SQLite to PostgreSQL Migration**

1. **Backup SQLite Data**
```python
# backup_sqlite.py
import sqlite3
import json

conn = sqlite3.connect('tiffintrack.db')
conn.row_factory = sqlite3.Row

# Export users
cursor = conn.execute("SELECT * FROM users")
users = [dict(row) for row in cursor.fetchall()]

# Save to JSON
with open('backup.json', 'w') as f:
    json.dump({'users': users}, f, default=str)

print("Backup completed!")
```

2. **Restore to PostgreSQL**
```python
# restore_postgresql.py
from app import app, db, User
import json

with app.app_context():
    with open('backup.json', 'r') as f:
        data = json.load(f)
    
    for user_data in data['users']:
        user_data.pop('id', None)  # Let DB generate new ID
        user = User(**user_data)
        db.session.add(user)
    
    db.session.commit()
    print("Restore completed!")
```

## 🐛 Common Application Errors

### **Import Errors**
```bash
# Missing dependencies
pip install -r requirements.txt

# Python path issues
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### **Template Errors**
```bash
# Template not found
# Check templates/ directory structure
# Verify template names in routes
```

### **Static File Issues**
```bash
# CSS/JS not loading
# Check static/ directory
# Verify Flask static configuration
```

## 🔍 Debug Mode

### **Enable Detailed Logging**
```python
# Add to app.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set environment variable
export FLASK_DEBUG=1
```

### **Database Query Logging**
```python
# Add to app.py
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

## 📞 Getting Help

### **Check These First:**
1. ✅ Internet connection working
2. ✅ Database service is running
3. ✅ Environment variables are set
4. ✅ Dependencies are installed
5. ✅ Python version compatibility (3.9+)

### **Collect Debug Information:**
```bash
# System info
python --version
pip list | grep -E "(Flask|SQLAlchemy|psycopg2)"

# Database connection test
python -c "from app import app, db; app.app_context().push(); print('DB URI:', app.config['SQLALCHEMY_DATABASE_URI'][:50])"

# Network test
ping google.com
nslookup your-neon-host.com
```

### **Create Issue Report:**
When reporting issues, include:
- Error message (full traceback)
- Python version
- Operating system
- Database type (SQLite/PostgreSQL)
- Steps to reproduce
- Environment variables (without sensitive data)

## 🎯 Quick Solutions

| Problem | Quick Fix |
|---------|-----------|
| **Neon connection fails** | Switch to SQLite for development |
| **Database not found** | Run database initialization script |
| **Import errors** | `pip install -r requirements.txt` |
| **Template not found** | Check template file names and paths |
| **Static files 404** | Verify static/ directory structure |
| **Permission denied** | Check file permissions and ownership |

---

**Need more help?** Create an issue on GitHub with detailed error information! 🚀