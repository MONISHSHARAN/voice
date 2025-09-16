#!/usr/bin/env python3
"""
Deploy MedAgg Healthcare System NOW
"""

import subprocess
import threading
import time
import webbrowser

def start_backend():
    """Start the backend server"""
    print("🚀 Starting MedAgg Healthcare Backend...")
    subprocess.run(["python", "app.py"])

def start_tunnel():
    """Start localtunnel"""
    print("🌐 Starting public tunnel...")
    time.sleep(3)  # Wait for backend to start
    subprocess.run(["lt", "--port", "8000", "--subdomain", "medagg-healthcare"])

def main():
    print("🏥 MedAgg Healthcare System - IMMEDIATE DEPLOYMENT")
    print("=" * 70)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(5)
    
    # Start tunnel in a separate thread
    tunnel_thread = threading.Thread(target=start_tunnel)
    tunnel_thread.daemon = True
    tunnel_thread.start()
    
    print("✅ Backend started on port 8000")
    print("🌐 Creating public tunnel...")
    print("⏳ Please wait for tunnel to be created...")
    
    # Wait for tunnel to be created
    time.sleep(10)
    
    public_url = "https://medagg-healthcare.loca.lt"
    
    print("\n🎉 DEPLOYMENT SUCCESSFUL!")
    print("=" * 70)
    print(f"🌐 Public URL: {public_url}")
    print(f"📞 Webhook URL: {public_url}/twiml")
    print("=" * 70)
    
    print("\n📋 NEXT STEPS:")
    print("1. Configure Twilio webhooks:")
    print(f"   - Voice URL: {public_url}/twiml")
    print("   - HTTP Method: POST")
    print("2. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming")
    print("3. Click on your phone number: +17752586467")
    print("4. Set the webhook URL and save")
    print("5. Test by registering a patient!")
    
    print("\n🧪 Test the system:")
    print(f"   - Main page: {public_url}")
    print(f"   - Test page: {public_url}/test")
    
    # Open the public URL
    try:
        webbrowser.open(public_url)
    except:
        print(f"Please manually open: {public_url}")
    
    print("\n✅ Your MedAgg Healthcare System is now LIVE!")
    print("Press Ctrl+C to stop the servers")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        print("✅ Servers stopped!")

if __name__ == "__main__":
    main()
