#!/usr/bin/env python3
"""
Test the simple working system
"""

import requests
import json
import time

def test_backend():
    """Test backend endpoints"""
    print("🧪 Testing Backend...")
    
    try:
        # Test basic endpoint
        response = requests.get("http://localhost:8000", timeout=5)
        print(f"✅ Backend is running: {response.status_code}")
        
        # Test hospitals endpoint
        response = requests.get("http://localhost:8000/hospitals", timeout=5)
        hospitals = response.json()
        print(f"✅ Hospitals loaded: {len(hospitals)} hospitals")
        
        return True
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def test_patient_registration():
    """Test patient registration with call"""
    print("\n🧪 Testing Patient Registration...")
    
    patient_data = {
        "name": "Test User",
        "phone_number": "+917010557477",  # Your test number
        "email": "test@example.com",
        "age": 30,
        "location": "Mumbai",
        "language_preference": "English"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/register-patient",
            json=patient_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Patient registered successfully!")
            print(f"📋 Patient ID: {result.get('patient_id')}")
            print(f"📞 Call initiated: {result.get('call_initiated')}")
            return True
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"📋 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
        return False

def test_frontend():
    """Test frontend"""
    print("\n🧪 Testing Frontend...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running")
            return True
        else:
            print(f"❌ Frontend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False

def main():
    print("🚀 Testing Simple MedAgg Healthcare System")
    print("=" * 50)
    
    # Test backend
    backend_ok = test_backend()
    
    # Test frontend
    frontend_ok = test_frontend()
    
    if backend_ok and frontend_ok:
        print("\n✅ All systems are running!")
        print("🌐 Open http://localhost:3000 in your browser")
        print("📞 Register a patient to test the call system")
        
        # Test patient registration
        test_patient_registration()
    else:
        print("\n❌ Some systems are not working properly")

if __name__ == "__main__":
    main()
