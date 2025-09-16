#!/usr/bin/env python3
"""
Quick Deployment Alternatives for MedAgg Healthcare Voice Agent
Multiple deployment options to ensure success
"""

import subprocess
import sys
import os

def deploy_render():
    """Deploy to Render"""
    print("🚀 Deploying to Render...")
    print("1. Go to https://render.com")
    print("2. Connect your GitHub account")
    print("3. Create new Web Service")
    print("4. Connect repository: MONISHSHARAN/voice")
    print("5. Use these settings:")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: python app.py")
    print("   - Environment: Python 3")
    print("6. Add environment variables:")
    print("   - PORT: 8000")
    print("   - TWILIO_ACCOUNT_SID: AC33f397657e06dac328e5d5081eb4f9fd")
    print("   - TWILIO_AUTH_TOKEN: bbf7abc794d8f0eb9538350b501d033f")
    print("   - TWILIO_PHONE_NUMBER: +17752586467")
    print("7. Deploy!")
    print("✅ Render deployment ready!")

def deploy_railway():
    """Deploy to Railway"""
    print("🚀 Deploying to Railway...")
    print("1. Go to https://railway.app")
    print("2. Sign up with GitHub")
    print("3. Create new project from GitHub repo")
    print("4. Select: MONISHSHARAN/voice")
    print("5. Railway will auto-detect Python and deploy")
    print("6. Add environment variables in Railway dashboard:")
    print("   - PORT: 8000")
    print("   - TWILIO_ACCOUNT_SID: AC33f397657e06dac328e5d5081eb4f9fd")
    print("   - TWILIO_AUTH_TOKEN: bbf7abc794d8f0eb9538350b501d033f")
    print("   - TWILIO_PHONE_NUMBER: +17752586467")
    print("7. Deploy!")
    print("✅ Railway deployment ready!")

def deploy_heroku():
    """Deploy to Heroku"""
    print("🚀 Deploying to Heroku...")
    print("1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli")
    print("2. Run these commands:")
    print("   heroku login")
    print("   heroku create medagg-voice-agent")
    print("   git push heroku main")
    print("   heroku config:set TWILIO_ACCOUNT_SID=AC33f397657e06dac328e5d5081eb4f9fd")
    print("   heroku config:set TWILIO_AUTH_TOKEN=bbf7abc794d8f0eb9538350b501d033f")
    print("   heroku config:set TWILIO_PHONE_NUMBER=+17752586467")
    print("   heroku open")
    print("✅ Heroku deployment ready!")

def deploy_vercel():
    """Deploy to Vercel"""
    print("🚀 Deploying to Vercel...")
    print("1. Go to https://vercel.com")
    print("2. Import project from GitHub")
    print("3. Select: MONISHSHARAN/voice")
    print("4. Framework: Other")
    print("5. Build Command: pip install -r requirements.txt")
    print("6. Output Directory: .")
    print("7. Add environment variables:")
    print("   - TWILIO_ACCOUNT_SID: AC33f397657e06dac328e5d5081eb4f9fd")
    print("   - TWILIO_AUTH_TOKEN: bbf7abc794d8f0eb9538350b501d033f")
    print("   - TWILIO_PHONE_NUMBER: +17752586467")
    print("8. Deploy!")
    print("✅ Vercel deployment ready!")

def main():
    print("🏥 MedAgg Healthcare Voice Agent - Quick Deployment")
    print("=" * 60)
    print("Choose your deployment option:")
    print("1. Render (Recommended)")
    print("2. Railway (Fast)")
    print("3. Heroku (Classic)")
    print("4. Vercel (Modern)")
    print("5. All options")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        deploy_render()
    elif choice == "2":
        deploy_railway()
    elif choice == "3":
        deploy_heroku()
    elif choice == "4":
        deploy_vercel()
    elif choice == "5":
        print("\n" + "="*60)
        deploy_render()
        print("\n" + "="*60)
        deploy_railway()
        print("\n" + "="*60)
        deploy_heroku()
        print("\n" + "="*60)
        deploy_vercel()
    else:
        print("Invalid choice. Please run again.")
        return
    
    print("\n🎉 Deployment instructions complete!")
    print("📞 After deployment, configure Twilio webhooks:")
    print("   Voice URL: https://your-app-url.com/twiml")
    print("   HTTP Method: POST")
    print("🔗 Test your voice agent at: https://your-app-url.com/test")

if __name__ == "__main__":
    main()
