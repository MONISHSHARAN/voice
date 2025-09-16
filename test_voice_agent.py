#!/usr/bin/env python3
"""
Test script for MedAgg Voice Agent
"""

import requests
import json
import time

def test_flask_app():
    """Test if Flask app is running"""
    try:
        response = requests.get("https://voice-95g5.onrender.com/", timeout=10)
        if response.status_code == 200:
            print("✅ Flask app is running")
            return True
        else:
            print(f"❌ Flask app returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_websocket_endpoint():
    """Test if WebSocket endpoint is accessible"""
    try:
        response = requests.get("https://voice-95g5.onrender.com/twilio", timeout=10)
        if response.status_code == 200:
            print("✅ WebSocket endpoint is accessible")
            return True
        else:
            print(f"❌ WebSocket endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ WebSocket endpoint test failed: {e}")
        return False

def test_twiml_endpoint():
    """Test if TwiML endpoint is working"""
    try:
        response = requests.get("https://voice-95g5.onrender.com/twiml", timeout=10)
        if response.status_code == 200 and "stream" in response.text:
            print("✅ TwiML endpoint is working")
            return True
        else:
            print(f"❌ TwiML endpoint issue: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ TwiML endpoint test failed: {e}")
        return False

def test_patient_registration():
    """Test patient registration"""
    try:
        data = {
            "name": "Test Patient",
            "phone_number": "+919876543210",
            "language_preference": "english"
        }
        response = requests.post(
            "https://voice-95g5.onrender.com/register-patient",
            json=data,
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Patient registration working")
                return True
            else:
                print(f"❌ Patient registration failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Patient registration returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Patient registration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 MedAgg Voice Agent - System Test")
    print("=" * 40)
    
    tests = [
        ("Flask App", test_flask_app),
        ("WebSocket Endpoint", test_websocket_endpoint),
        ("TwiML Endpoint", test_twiml_endpoint),
        ("Patient Registration", test_patient_registration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        time.sleep(1)
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Voice agent is working!")
    else:
        print("⚠️ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()
