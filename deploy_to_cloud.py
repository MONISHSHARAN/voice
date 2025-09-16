#!/usr/bin/env python3
"""
Deploy MedAgg Healthcare System to Cloud
"""

import webbrowser
import time

def main():
    print("🚀 CLOUD DEPLOYMENT - MedAgg Healthcare System")
    print("=" * 70)
    
    print("🎯 RECOMMENDED: Deploy to Render.com (Free & Easy)")
    print("=" * 70)
    print("1. Go to: https://render.com/")
    print("2. Sign up with GitHub")
    print("3. Click 'New +' → 'Web Service'")
    print("4. Connect your GitHub repository")
    print("5. Select this repository")
    print("6. Render will auto-detect Python")
    print("7. Set these environment variables:")
    print("   - TWILIO_ACCOUNT_SID: AC33f397657e06dac328e5d5081eb4f9fd")
    print("   - TWILIO_AUTH_TOKEN: bbf7abc794d8f0eb9538350b501d033f")
    print("   - TWILIO_PHONE_NUMBER: +17752586467")
    print("8. Click 'Deploy'")
    print("9. You'll get a URL like: https://medagg-healthcare.onrender.com")
    print("=" * 70)
    
    print("\n🌐 Opening Render.com...")
    try:
        webbrowser.open("https://render.com/")
    except:
        print("Please manually open: https://render.com/")
    
    print("\n📋 AFTER DEPLOYMENT:")
    print("1. Get your public URL (e.g., https://medagg-healthcare.onrender.com)")
    print("2. Configure Twilio webhooks:")
    print("   - Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming")
    print("   - Click on your phone number: +17752586467")
    print("   - Set Voice URL to: https://your-app-url.com/twiml")
    print("   - Set HTTP Method to: POST")
    print("   - Save configuration")
    print("3. Test by registering a patient!")
    
    print("\n✅ Your system is ready for cloud deployment!")

if __name__ == "__main__":
    main()
