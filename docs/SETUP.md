# TiffinTrack Setup Guide

Complete setup guide for deploying and configuring TiffinTrack.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Database Setup](#database-setup)
3. [Email Configuration](#email-configuration)
4. [Deployment](#deployment)
5. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL database
- Stripe account (for payments)
- Gmail account (for emails)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/TiffinTrack.git
cd TiffinTrack

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env

# Initialize database
flask db upgrade

# Run application
python app.py
```

Visit http://localhost:5000

---

## Database Setup

### Option 1: Neon (Recommended for Production)

1. Sign up at https://neon.tech
2. Create new project
3. Copy connection string
4. Add to .env:
```bash
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
```

### Option 2: Local PostgreSQL

```bash
# Install PostgreSQL
sudo apt install postgresql

# Create database
sudo -u postgres createdb tiffintrack

# Add to .env
DATABASE_URL=postgresql://postgres:password@localhost/tiffintrack
```

### Fix Description Column (One-time)

If you get "value too long for type character varying(255)" error:

```bash
# Run the fix script
python3 fix_db_description.py

# Or manually in psql
psql "$DATABASE_URL" -c "ALTER TABLE plans ALTER COLUMN description TYPE TEXT;"
```

---

## Email Configuration

### Gmail Setup (5 minutes)

1. **Get App Password:**
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification
   - Go to App passwords
   - Create password for "Mail" → "TiffinTrack"
   - Copy 16-character password

2. **Update .env:**
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SENDER_EMAIL=your-email@gmail.com
SENDER_NAME=TiffinTrack
```

3. **Test:**
```bash
python3 test_email.py
```

### SendGrid (Production)

1. Sign up at https://sendgrid.com
2. Verify sender email
3. Create API key
4. Update .env:
```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SENDER_EMAIL=noreply@yourdomain.com
SENDER_NAME=TiffinTrack
```

---

## Deployment

### AWS EC2 Deployment

1. **Setup Server:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv nginx -y

# Clone repository
cd ~
git clone https://github.com/yourusername/TiffinTrack.git
cd TiffinTrack

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure Environment:**
```bash
# Create .env file
nano .env

# Add your configuration (see .env.example)
```

3. **Setup Systemd Service:**
```bash
sudo nano /etc/systemd/system/tiffintrack.service
```

Add:
```ini
[Unit]
Description=TiffinTrack Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/TiffinTrack
Environment="PATH=/home/ubuntu/TiffinTrack/venv/bin"
ExecStart=/home/ubuntu/TiffinTrack/venv/bin/gunicorn -w 3 -b 127.0.0.1:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

4. **Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/tiffintrack
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /home/ubuntu/TiffinTrack/static;
    }
}
```

5. **Enable and Start:**
```bash
# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/tiffintrack /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Start TiffinTrack
sudo systemctl enable tiffintrack
sudo systemctl start tiffintrack
```

### Update Deployment

```bash
cd ~/TiffinTrack
git pull origin main
sudo systemctl restart tiffintrack
```

---

## Troubleshooting

### Database Issues

**Error: "value too long for type character varying(255)"**
```bash
python3 fix_db_description.py
```

**Error: "could not connect to server"**
- Check DATABASE_URL in .env
- Verify database is running
- Check firewall settings

### Email Issues

**Error: "Email service is not configured"**
- Check all SMTP_* variables in .env
- Restart application

**Error: "Authentication failed"**
- Gmail: Use App Password, not regular password
- Verify credentials are correct

**Emails go to spam**
- Normal for first few emails
- Use SendGrid for better deliverability

### Application Issues

**Error: "Port already in use"**
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
sudo systemctl restart tiffintrack
```

**Check logs:**
```bash
sudo journalctl -u tiffintrack -n 50 --no-pager
```

**Restart application:**
```bash
sudo systemctl restart tiffintrack
```

---

## Environment Variables

Complete .env configuration:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# Flask
SECRET_KEY=your-secret-key-change-this
FLASK_ENV=production

# Stripe
STRIPE_SECRET_KEY=sk_live_your_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_key

# Email (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
SENDER_NAME=TiffinTrack

# Application
UPLOAD_FOLDER=static/uploads/dishes
MAX_CONTENT_LENGTH=16777216
```

---

## Default Credentials

After seeding the database:

**Admin:**
- Email: admin@tiffintrack.com
- Password: admin123

**Customer:**
- Email: rahul.sharma@email.com
- Password: password123

**⚠️ Change these in production!**

---

## Useful Commands

```bash
# Check application status
sudo systemctl status tiffintrack

# View logs
sudo journalctl -u tiffintrack -f

# Restart application
sudo systemctl restart tiffintrack

# Test email
python3 test_email.py

# Fix database
python3 fix_db_description.py

# Database migrations
flask db upgrade
```

---

## Support

For issues:
1. Check logs: `sudo journalctl -u tiffintrack -n 100`
2. Verify .env configuration
3. Test components individually
4. Check GitHub issues

---

**Last Updated:** February 24, 2026
