#!/usr/bin/env python3
"""
Setup script for MedAgg Healthcare POC with real calls and emails
"""

import os
import json

def setup_configuration():
    print("🏥 MedAgg Healthcare POC - Real Calls & Email Setup")
    print("=" * 55)
    
    print("\n📧 EMAIL CONFIGURATION:")
    print("1. Go to Gmail Settings > Security")
    print("2. Enable 2-Factor Authentication")
    print("3. Generate an App Password")
    print("4. Use the App Password below")
    
    email = input("\nEnter your Gmail address: ")
    app_password = input("Enter your Gmail App Password: ")
    
    print("\n📞 TWILIO CONFIGURATION:")
    print("1. Sign up at https://www.twilio.com/")
    print("2. Get your Account SID and Auth Token from console")
    print("3. Buy a phone number from Twilio")
    print("4. Enter the details below")
    
    account_sid = input("\nEnter Twilio Account SID: ")
    auth_token = input("Enter Twilio Auth Token: ")
    twilio_phone = input("Enter your Twilio phone number (+1234567890): ")
    
    # Create configuration
    config = {
        "email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": email,
            "sender_password": app_password
        },
        "twilio": {
            "account_sid": account_sid,
            "auth_token": auth_token,
            "phone_number": twilio_phone
        }
    }
    
    # Save configuration
    with open('real_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n✅ Configuration saved to real_config.json")
    print("\n🚀 You can now run the system with real calls and emails!")
    print("   python backend_server_with_calls.py")

def test_configuration():
    """Test the configuration"""
    try:
        with open('real_config.json', 'r') as f:
            config = json.load(f)
        
        print("\n🧪 Testing Configuration...")
        
        # Test email
        try:
            import smtplib
            server = smtplib.SMTP(config['email']['smtp_server'], config['email']['smtp_port'])
            server.starttls()
            server.login(config['email']['sender_email'], config['email']['sender_password'])
            server.quit()
            print("✅ Email configuration: Working")
        except Exception as e:
            print(f"❌ Email configuration: Failed - {e}")
        
        # Test Twilio
        try:
            from twilio.rest import Client
            client = Client(config['twilio']['account_sid'], config['twilio']['auth_token'])
            account = client.api.accounts(config['twilio']['account_sid']).fetch()
            print("✅ Twilio configuration: Working")
        except Exception as e:
            print(f"❌ Twilio configuration: Failed - {e}")
            
    except FileNotFoundError:
        print("❌ Configuration file not found. Run setup first.")
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Setup configuration")
    print("2. Test configuration")
    
    choice = input("\nEnter choice (1 or 2): ")
    
    if choice == "1":
        setup_configuration()
    elif choice == "2":
        test_configuration()
    else:
        print("Invalid choice. Please run again.")


