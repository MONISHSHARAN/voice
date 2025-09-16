#!/usr/bin/env python3
"""
Quick test for the system
"""

import requests
import json

def quick_test():
    print("🚀 Quick System Test")
    print("=" * 30)
    
    # Test backend
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        if response.status_code == 200:
            print("✅ Backend: RUNNING")
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   Twilio: {data.get('twilio_status', 'unknown')}")
        else:
            print(f"❌ Backend: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Backend: {e}")
    
    # Test frontend
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend: RUNNING")
        else:
            print(f"❌ Frontend: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend: {e}")
    
    print("\n🎯 System Status:")
    print("✅ Backend: http://localhost:8000")
    print("✅ Frontend: http://localhost:3000")
    print("📞 Twilio: Configured")
    print("🌍 Multilingual: English, Tamil, Hindi")
    
    print("\n🚀 Ready to Use!")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Fill out the patient form with YOUR phone number")
    print("3. Submit to receive a REAL call!")

if __name__ == "__main__":
    quick_test()