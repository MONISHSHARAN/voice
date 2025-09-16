#!/usr/bin/env python3
"""
Test the MedAgg Healthcare app locally
"""

import requests
import json

def test_app():
    """Test the app endpoints"""
    base_url = "https://voice-95g5.onrender.com"
    
    print("🧪 Testing MedAgg Healthcare App")
    print("=" * 50)
    
    # Test 1: Home page
    print("1. Testing home page...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Home page working")
        else:
            print("   ❌ Home page failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: TwiML endpoint
    print("\n2. Testing TwiML endpoint...")
    try:
        response = requests.get(f"{base_url}/twiml?language=english", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        if response.status_code == 200 and 'text/xml' in response.headers.get('content-type', ''):
            print("   ✅ TwiML endpoint working")
            print(f"   TwiML preview: {response.text[:100]}...")
        else:
            print("   ❌ TwiML endpoint failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Test page
    print("\n3. Testing test page...")
    try:
        response = requests.get(f"{base_url}/test", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Test page working")
        else:
            print("   ❌ Test page failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Conversations endpoint
    print("\n4. Testing conversations endpoint...")
    try:
        response = requests.get(f"{base_url}/conversations", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Conversations endpoint working")
        else:
            print("   ❌ Conversations endpoint failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🎯 Test Summary:")
    print("If all tests show ✅, your app is working!")
    print("If any show ❌, check the Render deployment logs.")

if __name__ == "__main__":
    test_app()
