#!/usr/bin/env python3
"""
Simple Email Test - Debug email configuration issues
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("EMAIL CONFIGURATION TEST")
print("=" * 60)
print()

# Check environment variables
print("1. Checking Environment Variables:")
print("-" * 60)

required_vars = {
    'SMTP_SERVER': os.getenv('SMTP_SERVER'),
    'SMTP_PORT': os.getenv('SMTP_PORT'),
    'SMTP_USERNAME': os.getenv('SMTP_USERNAME'),
    'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD'),
    'SENDER_EMAIL': os.getenv('SENDER_EMAIL'),
}

all_set = True
for var, value in required_vars.items():
    if value:
        if 'PASSWORD' in var:
            display = '*' * 16
        else:
            display = value
        print(f"✅ {var:20} = {display}")
    else:
        print(f"❌ {var:20} = NOT SET")
        all_set = False

print()

if not all_set:
    print("❌ ERROR: Some required variables are not set!")
    print()
    print("Please add these to your .env file:")
    print()
    print("SMTP_SERVER=smtp.gmail.com")
    print("SMTP_PORT=587")
    print("SMTP_USERNAME=your-email@gmail.com")
    print("SMTP_PASSWORD=your-app-password")
    print("SENDER_EMAIL=your-email@gmail.com")
    print()
    print("See docs/SETUP.md for detailed instructions")
    exit(1)

print("✅ All required variables are set!")
print()

# Test email sending
print("2. Testing Email Sending:")
print("-" * 60)

try:
    from app import app, send_email, is_email_configured
    
    with app.app_context():
        # Check if configured
        if not is_email_configured():
            print("❌ Email is not configured in the app")
            print("   Check that app.py is reading the correct variables")
            exit(1)
        
        print("✅ Email is configured in the app")
        print()
        
        # Get test email
        test_to = input("Enter email address to send test to (or press Enter to skip): ").strip()
        
        if not test_to:
            print("⏭️  Skipping email send test")
            exit(0)
        
        print(f"📧 Sending test email to {test_to}...")
        print()
        
        success, error = send_email(
            test_to,
            "TiffinTrack Email Test",
            """
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #ff6b35;">✅ Email Configuration Successful!</h2>
                <p>If you're reading this, your TiffinTrack email configuration is working correctly.</p>
                <p><strong>Configuration:</strong></p>
                <ul>
                    <li>SMTP Server: {}</li>
                    <li>SMTP Port: {}</li>
                    <li>Sender: {}</li>
                </ul>
                <p>You can now send payment reminders to your customers!</p>
            </body>
            </html>
            """.format(
                os.getenv('SMTP_SERVER'),
                os.getenv('SMTP_PORT'),
                os.getenv('SENDER_EMAIL')
            ),
            f"Email Test - Configuration successful! Server: {os.getenv('SMTP_SERVER')}, Port: {os.getenv('SMTP_PORT')}"
        )
        
        if success:
            print("✅ Email sent successfully!")
            print(f"📬 Check your inbox at {test_to}")
            print()
            print("If you don't see it:")
            print("  1. Check spam/junk folder")
            print("  2. Wait a few minutes")
            print("  3. Verify email address is correct")
        else:
            print(f"❌ Failed to send email!")
            print(f"   Error: {error}")
            print()
            print("Common issues:")
            print("  1. Gmail: Need App Password (not regular password)")
            print("  2. Wrong SMTP credentials")
            print("  3. Firewall blocking SMTP port")
            print("  4. SMTP server address incorrect")
            
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
