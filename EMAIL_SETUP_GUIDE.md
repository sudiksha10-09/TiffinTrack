# Email Configuration Guide for TiffinTrack

## Overview
TiffinTrack uses email to send payment reminders, notifications, and other communications to customers. This guide will help you set up email functionality.

## Why Email Configuration is Needed

Email is used for:
- 📧 Payment reminders to customers with unpaid bills
- 🔔 Order confirmations
- 📝 Account notifications
- 💳 Payment receipts
- 🎉 Welcome emails

---

## Quick Setup (Recommended: Gmail)

### Step 1: Get Gmail App Password

1. **Go to your Google Account:**
   - Visit: https://myaccount.google.com/
   - Sign in with your Gmail account

2. **Enable 2-Step Verification:**
   - Go to Security → 2-Step Verification
   - Follow the steps to enable it (required for app passwords)

3. **Create App Password:**
   - Go to Security → App passwords
   - Select app: "Mail"
   - Select device: "Other (Custom name)"
   - Enter: "TiffinTrack"
   - Click "Generate"
   - **Copy the 16-character password** (you'll need this)

### Step 2: Update .env File

Add these lines to your `.env` file:

```bash
# Email Configuration (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SENDER_EMAIL=your-email@gmail.com
SENDER_NAME=TiffinTrack
```

**Replace:**
- `your-email@gmail.com` → Your actual Gmail address
- `your-16-char-app-password` → The app password you generated

### Step 3: Restart Application

```bash
# On AWS
sudo systemctl restart tiffintrack

# Locally
# Stop and restart your Flask app
```

### Step 4: Test

1. Go to Bill Management
2. Click "Send Reminders"
3. Check if emails are sent successfully

---

## Alternative Email Providers

### Option 1: Gmail (Recommended)
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
SENDER_NAME=TiffinTrack
```

**Pros:**
- ✅ Free
- ✅ Reliable
- ✅ Easy to set up
- ✅ 500 emails/day limit

**Cons:**
- ❌ Requires 2FA and app password
- ❌ Daily sending limit

---

### Option 2: SendGrid (Best for Production)
```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SENDER_EMAIL=noreply@yourdomain.com
SENDER_NAME=TiffinTrack
```

**Setup:**
1. Sign up at https://sendgrid.com (Free tier: 100 emails/day)
2. Verify your sender email
3. Create API key
4. Use "apikey" as username and API key as password

**Pros:**
- ✅ Professional
- ✅ Better deliverability
- ✅ Email analytics
- ✅ No daily limits (paid plans)

**Cons:**
- ❌ Requires account setup
- ❌ Free tier limited to 100/day

---

### Option 3: Mailgun
```bash
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=your-mailgun-password
SENDER_EMAIL=noreply@yourdomain.com
SENDER_NAME=TiffinTrack
```

**Setup:**
1. Sign up at https://mailgun.com
2. Add and verify your domain
3. Get SMTP credentials from dashboard

**Pros:**
- ✅ Reliable
- ✅ Good for high volume
- ✅ Detailed analytics

---

### Option 4: Outlook/Office 365
```bash
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
SENDER_EMAIL=your-email@outlook.com
SENDER_NAME=TiffinTrack
```

**Pros:**
- ✅ Free with Outlook account
- ✅ Professional

**Cons:**
- ❌ Lower sending limits
- ❌ May require app password

---

### Option 5: Custom SMTP Server
```bash
SMTP_SERVER=mail.yourdomain.com
SMTP_PORT=587
SMTP_USERNAME=noreply@yourdomain.com
SMTP_PASSWORD=your-password
SENDER_EMAIL=noreply@yourdomain.com
SENDER_NAME=TiffinTrack
```

**Use if:**
- You have your own email server
- Your hosting provides SMTP
- You have a custom domain

---

## Complete .env Configuration

Here's a complete example with all email settings:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# Flask
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# Stripe
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_key

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
SENDER_NAME=TiffinTrack

# Optional: Email Settings
SMTP_USE_TLS=True
SMTP_TIMEOUT=30

# Application
UPLOAD_FOLDER=static/uploads/dishes
MAX_CONTENT_LENGTH=16777216
```

---

## Testing Email Configuration

### Method 1: Using Admin Panel

1. Login as admin
2. Go to Bill Management
3. Click "Send Reminders"
4. Check the response message

**Success:** "Successfully sent X reminder(s)!"
**Failure:** "Email service is not configured..."

### Method 2: Using Python Console

```bash
# On your server
cd ~/TiffinTrack
source venv/bin/activate
python3

# In Python console
from app import app, send_email
with app.app_context():
    success, error = send_email(
        "test@example.com",
        "Test Email",
        "<h1>Test</h1>",
        "Test"
    )
    print(f"Success: {success}, Error: {error}")
```

### Method 3: Test Email Endpoint

Add this temporary route to test:

```python
@app.route("/test-email")
def test_email():
    if not session.get("is_admin"):
        return "Unauthorized", 401
    
    success, error = send_email(
        session.get("user_email", "admin@example.com"),
        "TiffinTrack Test Email",
        "<h1>Email Configuration Test</h1><p>If you receive this, email is working!</p>",
        "Email Configuration Test - If you receive this, email is working!"
    )
    
    if success:
        return "✅ Email sent successfully! Check your inbox."
    else:
        return f"❌ Failed to send email: {error}"
```

---

## Troubleshooting

### Error: "Email service is not configured"

**Cause:** Missing SMTP settings in .env

**Fix:**
1. Check if .env file exists
2. Verify all SMTP_* variables are set
3. Restart application

### Error: "Authentication failed"

**Cause:** Wrong username or password

**Fix:**
1. **Gmail:** Use app password, not regular password
2. **Other:** Verify credentials are correct
3. Check for typos in .env file

### Error: "Connection timeout"

**Cause:** Firewall or wrong SMTP server

**Fix:**
1. Check SMTP_SERVER is correct
2. Verify SMTP_PORT (usually 587 or 465)
3. Check firewall allows outbound SMTP
4. Try different port (587 vs 465)

### Error: "Sender address rejected"

**Cause:** Email not verified or wrong sender

**Fix:**
1. Verify sender email with provider
2. Use verified email as SENDER_EMAIL
3. Check SPF/DKIM records (for custom domains)

### Emails Going to Spam

**Fix:**
1. Use professional email service (SendGrid, Mailgun)
2. Set up SPF, DKIM, DMARC records
3. Use verified sender domain
4. Avoid spam trigger words
5. Include unsubscribe link

---

## Security Best Practices

### 1. Never Commit .env File
```bash
# Make sure .env is in .gitignore
echo ".env" >> .gitignore
```

### 2. Use App Passwords
- Never use your main email password
- Use app-specific passwords
- Rotate passwords regularly

### 3. Limit Permissions
- Use dedicated email account for app
- Don't use personal email
- Set up separate account: noreply@yourdomain.com

### 4. Monitor Usage
- Check email sending logs
- Watch for unusual activity
- Set up alerts for failures

---

## Production Recommendations

### For Small Scale (< 100 customers)
- ✅ **Gmail** with app password
- Free and reliable
- Easy to set up

### For Medium Scale (100-1000 customers)
- ✅ **SendGrid** free tier
- Better deliverability
- Email analytics
- Professional appearance

### For Large Scale (1000+ customers)
- ✅ **SendGrid** or **Mailgun** paid plan
- High volume support
- Dedicated IP
- Advanced features
- Better support

---

## Email Templates

TiffinTrack includes professional email templates for:

### 1. Payment Reminders
- Customer name personalization
- Bill details (period, amount, days)
- Direct payment link
- Professional branding

### 2. Welcome Emails (Future)
- Account confirmation
- Getting started guide
- Support information

### 3. Payment Receipts (Future)
- Transaction details
- Invoice PDF
- Payment method

---

## Monitoring Email Delivery

### Check Logs
```bash
# On AWS
sudo journalctl -u tiffintrack -f | grep -i email

# Look for:
# ✅ "Email sent successfully"
# ❌ "Error sending email"
```

### Track Metrics
- Emails sent
- Emails failed
- Bounce rate
- Open rate (with SendGrid/Mailgun)

---

## FAQ

### Q: Do I need a custom domain?
**A:** No, Gmail works fine. Custom domain is better for professional appearance.

### Q: How many emails can I send?
**A:** 
- Gmail: 500/day
- SendGrid Free: 100/day
- SendGrid Paid: Unlimited
- Mailgun: Based on plan

### Q: Will emails go to spam?
**A:** 
- Gmail: Sometimes
- Professional services: Rarely
- Custom domain with SPF/DKIM: Almost never

### Q: Can I use free email services?
**A:** Yes, Gmail and Outlook work great for small scale.

### Q: What if email fails?
**A:** The app will show an error message and log the failure. Customers won't be affected.

### Q: Can I disable email?
**A:** Yes, just don't configure SMTP settings. The app will work without email, but reminders won't be sent.

---

## Quick Reference

### Gmail Setup (5 minutes)
1. Enable 2FA on Google Account
2. Generate App Password
3. Add to .env:
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your@gmail.com
   SMTP_PASSWORD=app-password
   SENDER_EMAIL=your@gmail.com
   SENDER_NAME=TiffinTrack
   ```
4. Restart app
5. Test with "Send Reminders"

### SendGrid Setup (10 minutes)
1. Sign up at sendgrid.com
2. Verify sender email
3. Create API key
4. Add to .env:
   ```
   SMTP_SERVER=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_USERNAME=apikey
   SMTP_PASSWORD=your-api-key
   SENDER_EMAIL=noreply@yourdomain.com
   SENDER_NAME=TiffinTrack
   ```
5. Restart app
6. Test

---

## Support

If you need help:
1. Check error messages in logs
2. Verify .env configuration
3. Test with simple email first
4. Check provider documentation
5. Ensure firewall allows SMTP

---

**Last Updated:** February 24, 2026
**Status:** Production Ready
**Recommended:** Gmail for testing, SendGrid for production
