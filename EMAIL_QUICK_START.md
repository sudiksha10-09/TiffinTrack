# Email Setup - Quick Start (5 Minutes)

## Gmail Setup (Easiest)

### Step 1: Get App Password (2 minutes)
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification" (if not already enabled)
3. Go to "App passwords"
4. Select "Mail" and "Other (Custom name)"
5. Enter "TiffinTrack"
6. Click "Generate"
7. **Copy the 16-character password**

### Step 2: Update .env (1 minute)
Add these lines to your `.env` file:

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
SENDER_EMAIL=your-email@gmail.com
SENDER_NAME=TiffinTrack
```

Replace:
- `your-email@gmail.com` with your Gmail
- `abcd efgh ijkl mnop` with the app password (remove spaces)

### Step 3: Restart App (1 minute)
```bash
# On AWS
sudo systemctl restart tiffintrack

# Locally
# Stop and restart Flask
```

### Step 4: Test (1 minute)
```bash
# Option 1: Use test script
python3 test_email.py

# Option 2: Use admin panel
# Login → Bill Management → Send Reminders
```

## Done! ✅

Your email is now configured. You can send payment reminders to customers.

---

## Troubleshooting

### "Authentication failed"
- ❌ Using regular password
- ✅ Use App Password from Google

### "Email not configured"
- Check .env file exists
- Verify all SMTP_* variables are set
- Restart application

### Email goes to spam
- Normal for first few emails
- Ask recipients to mark as "Not Spam"
- Consider using SendGrid for production

---

## For Production

Use SendGrid (100 free emails/day):

1. Sign up: https://sendgrid.com
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

**Need more help?** See EMAIL_SETUP_GUIDE.md for detailed instructions.
