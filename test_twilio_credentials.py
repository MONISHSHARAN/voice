#!/usr/bin/env python3
"""
Quick test for Twilio credentials and phone number verification
"""

from twilio.rest import Client
import os

# Configuration
TWILIO_ACCOUNT_SID = 'AC33f397657e06dac328e5d5081eb4f9fd'
TWILIO_AUTH_TOKEN = 'bbf7abc794d8f0eb9538350b501d033f'
TWILIO_PHONE_NUMBER = '+17752586467'

def test_twilio_credentials():
    """Test Twilio credentials and account status"""
    try:
        print("🔍 Testing Twilio credentials...")
        
        # Initialize client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Get account info
        account = client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
        print(f"✅ Account Status: {account.status}")
        print(f"📧 Account Name: {account.friendly_name}")
        print(f"💰 Account Type: {account.type}")
        
        # Check phone numbers
        incoming_phone_numbers = client.incoming_phone_numbers.list()
        print(f"📞 Available Phone Numbers: {len(incoming_phone_numbers)}")
        
        for number in incoming_phone_numbers:
            print(f"   - {number.phone_number} ({number.friendly_name})")
        
        # Test making a call to a verified number
        print("\n🧪 Testing call capability...")
        print("⚠️ Note: Trial accounts can only call verified numbers")
        print("📱 To verify a number, go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verify_phone_number(phone_number):
    """Verify a phone number for trial accounts"""
    try:
        print(f"📱 Verifying phone number: {phone_number}")
        print("🔗 Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
        print("📝 Add your phone number there to enable calling")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🏥 MedAgg Healthcare - Twilio Credentials Test")
    print("=" * 50)
    
    # Test credentials
    if test_twilio_credentials():
        print("\n✅ Twilio credentials are working!")
        print("\n📋 Next steps:")
        print("1. Verify your phone number in Twilio console")
        print("2. Make sure your Twilio account is active")
        print("3. Check if you have sufficient credits")
    else:
        print("\n❌ Twilio credentials failed!")
        print("🔧 Check your Account SID and Auth Token")
    
    print("\n🔗 Twilio Console: https://console.twilio.com/")
    print("📞 Verified Numbers: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
