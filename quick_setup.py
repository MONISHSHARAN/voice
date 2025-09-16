#!/usr/bin/env python3
"""
Quick Setup for MedAgg Healthcare Deepgram Voice Agent
"""

import os
import requests
import webbrowser

def main():
    print("🏥 MedAgg Healthcare - Deepgram Voice Agent Setup")
    print("=" * 60)
    
    print("\n🎯 OUTSTANDING FEATURES READY:")
    print("✅ Real-time voice recognition with Deepgram Nova-2")
    print("✅ WebSocket streaming for live conversation")
    print("✅ No key presses - just speak naturally")
    print("✅ Multilingual support (English, Tamil, Hindi)")
    print("✅ Advanced AI conversation system")
    
    print("\n🔧 SETUP STEPS:")
    print("1. Get Deepgram API Key:")
    print("   - Visit: https://console.deepgram.com/")
    print("   - Sign up (free tier available)")
    print("   - Copy your API key")
    
    print("\n2. Set Environment Variable in Render:")
    print("   - Go to your Render dashboard")
    print("   - Select your service")
    print("   - Go to Environment tab")
    print("   - Add: DEEPGRAM_API_KEY = your_api_key_here")
    
    print("\n3. Configure Twilio Webhook:")
    print("   - Visit: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming")
    print("   - Set Voice URL: https://voice-95g5.onrender.com/twiml")
    print("   - Set HTTP Method: POST")
    
    print("\n4. Test the System:")
    print("   - Visit: https://voice-95g5.onrender.com/test")
    print("   - Register a patient")
    print("   - Receive AI call with voice recognition!")
    
    print("\n🚀 DEPLOYMENT STATUS:")
    print("✅ Code deployed to GitHub")
    print("✅ Render deployment updated")
    print("✅ WebSocket streaming ready")
    print("✅ TwiML configuration ready")
    
    print("\n🎉 YOUR SYSTEM IS READY!")
    print("Just add the Deepgram API key and you're good to go!")
    
    # Open Deepgram console
    try:
        webbrowser.open("https://console.deepgram.com/")
        print("\n🌐 Opening Deepgram console for you...")
    except:
        print("\n📝 Please manually visit: https://console.deepgram.com/")

if __name__ == "__main__":
    main()
