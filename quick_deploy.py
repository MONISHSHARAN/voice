#!/usr/bin/env python3
"""
Quick Deploy MedAgg Healthcare System
"""

import subprocess
import os
import webbrowser
import time

def main():
    print("🚀 QUICK DEPLOY - MedAgg Healthcare System")
    print("=" * 60)
    
    # Create a simple deployment package
    print("📦 Preparing deployment package...")
    
    # Create requirements.txt
    with open('requirements.txt', 'w') as f:
        f.write('''twilio==9.8.0
requests==2.31.0
gunicorn==21.2.0''')
    
    # Create runtime.txt
    with open('runtime.txt', 'w') as f:
        f.write('python-3.12.0')
    
    # Create a simple start script
    with open('start.py', 'w') as f:
        f.write('''
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the app
from app import start_heroku_backend

if __name__ == "__main__":
    start_heroku_backend()
''')
    
    print("✅ Deployment package created!")
    
    # Instructions for immediate deployment
    print("\n🎯 IMMEDIATE DEPLOYMENT OPTIONS:")
    print("=" * 60)
    print("OPTION 1: Render (Recommended - Easiest)")
    print("1. Go to https://render.com/")
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
    print("=" * 60)
    
    print("\nOPTION 2: Railway (Alternative)")
    print("1. Go to https://railway.app/")
    print("2. Sign up with GitHub")
    print("3. Click 'New Project' → 'Deploy from GitHub repo'")
    print("4. Select this repository")
    print("5. Railway will auto-deploy")
    print("6. You'll get a URL like: https://medagg-healthcare.up.railway.app")
    print("=" * 60)
    
    print("\nOPTION 3: Heroku (If you have CLI)")
    print("1. Install Heroku CLI from https://devcenter.heroku.com/articles/heroku-cli")
    print("2. Run: heroku login")
    print("3. Run: heroku create medagg-healthcare")
    print("4. Run: git push heroku main")
    print("5. You'll get a URL like: https://medagg-healthcare.herokuapp.com")
    print("=" * 60)
    
    # Open deployment services
    print("\n🌐 Opening deployment services...")
    try:
        webbrowser.open("https://render.com/")
        time.sleep(2)
        webbrowser.open("https://railway.app/")
    except:
        print("Please manually open: https://render.com/ and https://railway.app/")
    
    print("\n📋 AFTER DEPLOYMENT:")
    print("1. Get your public URL (e.g., https://medagg-healthcare.onrender.com)")
    print("2. Configure Twilio webhooks:")
    print("   - Go to https://console.twilio.com/us1/develop/phone-numbers/manage/incoming")
    print("   - Click on your phone number: +17752586467")
    print("   - Set Voice URL to: https://your-app-url.com/twiml")
    print("   - Set HTTP Method to: POST")
    print("   - Save configuration")
    print("3. Test by registering a patient!")
    
    print("\n✅ Your system is ready for deployment!")

if __name__ == "__main__":
    main()
