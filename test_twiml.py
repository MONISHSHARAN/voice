#!/usr/bin/env python3
"""
Test TwiML generation for voice recognition
"""

import requests
import json

def test_twiml_endpoint():
    """Test the TwiML endpoint"""
    url = "https://voice-95g5.onrender.com/twiml"
    
    print("🧪 Testing TwiML Endpoint...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print("\nTwiML Response:")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
        
        if response.status_code == 200 and 'text/xml' in response.headers.get('content-type', ''):
            print("✅ TwiML endpoint is working correctly!")
            return True
        else:
            print("❌ TwiML endpoint has issues")
            return False
            
    except Exception as e:
        print(f"❌ Error testing TwiML: {e}")
        return False

def test_speech_processing():
    """Test speech processing endpoint"""
    url = "https://voice-95g5.onrender.com/process-speech"
    
    print("\n🧪 Testing Speech Processing Endpoint...")
    print(f"URL: {url}")
    
    test_data = {
        'conversation_id': 'test-123',
        'language': 'english',
        'SpeechResult': 'I have a headache'
    }
    
    try:
        response = requests.post(url, data=test_data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print("\nTwiML Response:")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
        
        if response.status_code == 200 and 'text/xml' in response.headers.get('content-type', ''):
            print("✅ Speech processing endpoint is working correctly!")
            return True
        else:
            print("❌ Speech processing endpoint has issues")
            return False
            
    except Exception as e:
        print(f"❌ Error testing speech processing: {e}")
        return False

if __name__ == "__main__":
    print("🏥 MedAgg Healthcare - TwiML Test")
    print("=" * 50)
    
    # Test TwiML endpoint
    twiml_ok = test_twiml_endpoint()
    
    # Test speech processing
    speech_ok = test_speech_processing()
    
    print("\n📊 Test Results:")
    print(f"TwiML Endpoint: {'✅ PASS' if twiml_ok else '❌ FAIL'}")
    print(f"Speech Processing: {'✅ PASS' if speech_ok else '❌ FAIL'}")
    
    if twiml_ok and speech_ok:
        print("\n🎉 All tests passed! Your voice recognition system is ready!")
    else:
        print("\n⚠️ Some tests failed. Check the deployment logs.")
