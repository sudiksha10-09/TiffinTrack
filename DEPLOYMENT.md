# 🚀 TiffinTrack Deployment Guide

This guide covers deploying TiffinTrack to various platforms.

## 📋 Prerequisites

- Python 3.9+
- Git
- Database (SQLite for development, PostgreSQL/MySQL for production)

## 🔧 Environment Configuration

### 1. Database Options

#### **SQLite (Development)**
```bash
DATABASE_URL=sqlite:///tiffintrack.db
```

#### **Neon PostgreSQL (Recommended for Production)**
```bash
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require
```

#### **MySQL**
```bash
DATABASE_URL=mysql+pymysql://root:password@localhost/tiffintrack
```

### 2. Environment Variables

Create `.env` file:
```bash
DATABASE_URL=your_database_url
SECRET_KEY=your_super_secret_key_here
ALLOWED_CITY=Navi Mumbai
ALLOWED_STATE=Maharashtra
```

## 🌐 Platform Deployments

### **Heroku Deployment**

1. **Install Heroku CLI**
2. **Create Heroku App**
   ```bash
   heroku create your-tiffintrack-app
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set DATABASE_URL=your_neon_postgresql_url
   heroku config:set SECRET_KEY=your_secret_key
   heroku config:set ALLOWED_CITY="Navi Mumbai"
   heroku config:set ALLOWED_STATE="Maharashtra"
   ```

4. **Create Procfile**
   ```bash
   echo "web: gunicorn app:app" > Procfile
   ```

5. **Add Gunicorn to requirements.txt**
   ```bash
   echo "gunicorn==21.2.0" >> requirements.txt
   ```

6. **Deploy**
   ```bash
   git add .
   git commit -m "Add Heroku deployment config"
   git push heroku main
   ```

7. **Initialize Database**
   ```bash
   heroku run python -c "from app import app, db, seed_initial_data; app.app_context().push(); db.create_all(); seed_initial_data()"
   ```

### **Railway Deployment**

1. **Connect GitHub Repository**
2. **Set Environment Variables**
   - `DATABASE_URL`: Your Neon PostgreSQL URL
   - `SECRET_KEY`: Your secret key
   - `ALLOWED_CITY`: Navi Mumbai
   - `ALLOWED_STATE`: Maharashtra

3. **Deploy automatically on push**

### **DigitalOcean App Platform**

1. **Create App from GitHub**
2. **Configure Environment Variables**
3. **Set Build Command**: `pip install -r requirements.txt`
4. **Set Run Command**: `gunicorn app:app`

### **Vercel Deployment**

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Create vercel.json**
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "app.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app.py"
       }
     ]
   }
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

## 🗄️ Database Setup

### **For New Deployment**

```bash
# Initialize database tables and seed data
python -c "from app import app, db, seed_initial_data; app.app_context().push(); db.create_all(); seed_initial_data()"
```

### **Default Login Credentials**

- **Admin**: `admin@tiffintrack.com` / `admin123`
- **Test Customers**: All use password `password123`
  - `rahul.sharma@email.com`
  - `priya.patel@email.com`
  - `amit.kumar@email.com`

## 🔒 Security Considerations

### **Production Checklist**

- [ ] Use strong `SECRET_KEY`
- [ ] Use production database (PostgreSQL/MySQL)
- [ ] Enable HTTPS
- [ ] Set `FLASK_ENV=production`
- [ ] Configure proper logging
- [ ] Set up database backups
- [ ] Use environment variables for all secrets
- [ ] Configure CORS if needed
- [ ] Set up monitoring

### **Environment Variables**

```bash
# Production settings
FLASK_ENV=production
DATABASE_URL=postgresql://...
SECRET_KEY=super-secret-production-key
ALLOWED_CITY=Navi Mumbai
ALLOWED_STATE=Maharashtra
```

## 📊 Monitoring & Maintenance

### **Health Check Endpoint**

Add to `app.py`:
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
```

### **Database Backup**

For PostgreSQL:
```bash
pg_dump $DATABASE_URL > backup.sql
```

For SQLite:
```bash
cp tiffintrack.db backup_$(date +%Y%m%d).db
```

## 🚀 Performance Optimization

### **Production WSGI Server**

Use Gunicorn instead of Flask dev server:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### **Static File Serving**

For production, serve static files through CDN or reverse proxy (Nginx).

## 🔧 Troubleshooting

### **Common Issues**

1. **Database Connection Error**
   - Check `DATABASE_URL` format
   - Verify database server is running
   - Check firewall settings

2. **Missing Tables Error**
   - Run database initialization command
   - Check migration status

3. **Static Files Not Loading**
   - Verify static file paths
   - Check file permissions
   - Configure web server for static files

### **Logs**

Check application logs:
```bash
# Heroku
heroku logs --tail

# Railway
railway logs

# Local
python app.py
```

## 📞 Support

For deployment issues:
1. Check the logs first
2. Verify environment variables
3. Test database connection
4. Check GitHub Issues
5. Contact support

---

**TiffinTrack** - Ready for production deployment! 🍱✨