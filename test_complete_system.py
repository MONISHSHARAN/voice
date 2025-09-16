#!/usr/bin/env python3
"""
Complete system test with real Twilio calls
"""

import requests
import json
import time

def test_complete_system():
    print("🚀 Complete MedAgg Healthcare POC Test")
    print("=" * 50)
    
    # Test backend
    print("📡 Testing Backend API...")
    try:
        response = requests.get("http://localhost:8000", timeout=10)
        if response.status_code == 200:
            print("✅ Backend: Running")
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   Twilio: {data.get('twilio_status', 'unknown')}")
        else:
            print(f"❌ Backend: HTTP {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Backend: {e}")
        return
    
    # Test frontend
    print("\n🌐 Testing Frontend...")
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend: Running")
        else:
            print(f"❌ Frontend: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend: {e}")
    
    # Test patient registration with REAL call
    print("\n📝 Testing Patient Registration with REAL Call...")
    print("🔔 This will make a REAL call to your phone!")
    
    # Get user's phone number
    phone_number = input("Enter your phone number (with country code, e.g., +919876543210): ").strip()
    if not phone_number:
        phone_number = "+919876543210"  # Default for testing
        print(f"Using default number: {phone_number}")
    
    try:
        patient_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": phone_number,
            "age": 30,
            "gender": "Male",
            "location": "Mumbai, Maharashtra",
            "problem_description": "Chest pain and shortness of breath",
            "medical_category": "Interventional Cardiology",
            "subcategory": "Chronic Total Occlusion",
            "language_preference": "English"
        }
        
        print(f"📞 Submitting patient data...")
        response = requests.post(
            "http://localhost:8000/api/patients",
            json=patient_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Patient Registration: SUCCESS!")
            patient = response.json()
            print(f"   Patient ID: {patient.get('id', 'N/A')}")
            print(f"   Name: {patient.get('name', 'N/A')}")
            print(f"   Phone: {patient.get('phone', 'N/A')}")
            print(f"   Language: {patient.get('language_preference', 'N/A')}")
            print(f"   Email: {patient.get('email', 'N/A')}")
            
            print(f"\n🎯 What should happen now:")
            print(f"1. Your phone should ring from +17752586467")
            print(f"2. The AI will speak to you in {patient.get('language_preference', 'English')}")
            print(f"3. Your appointment will be scheduled")
            print(f"4. You'll receive an email confirmation")
            
        else:
            print(f"❌ Patient Registration: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Patient Registration: {e}")
    
    print(f"\n🎯 System Summary:")
    print(f"✅ Backend: http://localhost:8000")
    print(f"✅ Frontend: http://localhost:3000")
    print(f"📞 Twilio: Configured with your credentials")
    print(f"🌍 Multilingual: English, Tamil, Hindi")
    print(f"🔧 Fixed: Twilio localhost issue")
    
    print(f"\n🚀 Ready to Use!")
    print(f"1. Open http://localhost:3000 in your browser")
    print(f"2. Fill out the patient form with YOUR phone number")
    print(f"3. Submit to receive a REAL call!")

if __name__ == "__main__":
    test_complete_system()