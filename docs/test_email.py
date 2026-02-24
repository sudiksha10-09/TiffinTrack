#!/usr/bin/env python3
"""
Test Email Configuration
Run this script to test if your email settings are working correctly
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_config():
    """Test email configuration"""
    
    print("🔧 TiffinTrack Email Configuration Test")
    print("=" * 50)
    print()
    
    # Check if environment variables are set
    required_vars = [
        'SMTP_SERVER',
        'SMTP_PORT',
        'SMTP_USERNAME',
        'SMTP_PASSWORD',
        'SENDER_EMAIL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask password
            if 'PASSWORD' in var:
                display_value = '*' * len(value)
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    print()
    
    if missing_vars:
        print(f"❌ Missing required variables: {', '.join(missing_vars)}")
        print()
        print("Please set these in your .env file:")
        print()
        for var in missing_vars:
            print(f"  {var}=your-value-here")
        print()
        print("See EMAIL_SETUP_GUIDE.md for detailed instructions")
        return False
    
    print("✅ All required variables are set!")
    print()
    
    # Test email sending
    print("📧 Testing email sending...")
    print()
    
    try:
        from app import app, send_email
        
        with app.app_context():
            # Get test email address
            test_email = input("Enter email address to send test email to: ").strip()
            
            if not test_email:
                print("❌ No email address provided")
                return False
            
            print(f"Sending test email to {test_email}...")
            
            success, error = send_email(
                test_email,
                "TiffinTrack Email Configuration Test",
                """
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #ff6b35;">✅ Email Configuration Successful!</h2>
                    <p>If you're reading this, your TiffinTrack email configuration is working correctly.</p>
                    <p><strong>Configuration Details:</strong></p>
                    <ul>
                        <li>SMTP Server: {}</li>
                        <li>SMTP Port: {}</li>
                        <li>Sender: {}</li>
                    </ul>
                    <p>You can now send payment reminders and notifications to your customers!</p>
                    <hr>
                    <p style="font-size: 12px; color: #666;">
                        TiffinTrack - Fresh, Healthy Meals Delivered Daily
                    </p>
                </body>
                </html>
                """.format(
                    os.getenv('SMTP_SERVER'),
                    os.getenv('SMTP_PORT'),
                    os.getenv('SENDER_EMAIL')
                ),
                f"""
                Email Configuration Successful!
                
                If you're reading this, your TiffinTrack email configuration is working correctly.
                
                Configuration Details:
                - SMTP Server: {os.getenv('SMTP_SERVER')}
                - SMTP Port: {os.getenv('SMTP_PORT')}
                - Sender: {os.getenv('SENDER_EMAIL')}
                
                You can now send payment reminders and notifications to your customers!
                
                TiffinTrack - Fresh, Healthy Meals Delivered Daily
                """
            )
            
            if success:
                print()
                print("✅ Test email sent successfully!")
                print(f"📬 Check your inbox at {test_email}")
                print()
                print("If you don't see the email:")
                print("1. Check your spam/junk folder")
                print("2. Wait a few minutes (email can be delayed)")
                print("3. Verify the email address is correct")
                print()
                return True
            else:
                print()
                print(f"❌ Failed to send test email: {error}")
                print()
                print("Common issues:")
                print("1. Wrong SMTP credentials")
                print("2. Gmail: Need to use App Password (not regular password)")
                print("3. Firewall blocking SMTP port")
                print("4. SMTP server address incorrect")
                print()
                print("See EMAIL_SETUP_GUIDE.md for troubleshooting")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Make sure you're running this from the TiffinTrack directory")
        return False

if __name__ == "__main__":
    try:
        success = test_email_config()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled")
        sys.exit(1)
