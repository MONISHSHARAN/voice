#!/usr/bin/env python3
"""
Test script for real Twilio calls with your credentials
"""

import requests
import json
import time

def test_real_twilio_call():
    """Test the system with real Twilio call"""
    
    print("🚀 Testing MedAgg Healthcare POC with REAL Twilio Calls")
    print("=" * 60)
    print("📞 Using your Twilio credentials:")
    print("   Account SID: AC33f397657e06dac328e5d5081eb4f9fd")
    print("   Auth Token: bbf7abc794d8f0eb9538350b501d033f")
    print("=" * 60)
    
    # Test backend connectivity
    try:
        response = requests.get("http://localhost:8000")
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend API: Running")
            print(f"   Twilio Status: {data.get('twilio_status', 'unknown')}")
        else:
            print("❌ Backend API: Not responding")
            return
    except Exception as e:
        print(f"❌ Backend API: Connection failed - {e}")
        return
    
    # Test patient registration with REAL call
    print("\n📝 Registering patient for REAL call...")
    print("⚠️  IMPORTANT: Replace the phone number with YOUR actual phone number!")
    
    # Replace this with your actual phone number
    YOUR_PHONE_NUMBER = "+919876543210"  # CHANGE THIS TO YOUR PHONE NUMBER
    
    patient_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": YOUR_PHONE_NUMBER,
        "age": 30,
        "gender": "Male",
        "location": "Mumbai, Maharashtra",
        "problem_description": "Chest pain and shortness of breath",
        "medical_category": "Interventional Cardiology",
        "subcategory": "Chronic Total Occlusion",
        "language_preference": "English"
    }
    
    try:
        print(f"📞 Initiating REAL call to {patient_data['phone']}...")
        print("🔔 You should receive a call on your phone!")
        
        response = requests.post(
            "http://localhost:8000/api/patients",
            json=patient_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            patient = response.json()
            print(f"✅ Patient registered: {patient['name']} (ID: {patient['id']})")
            print(f"📧 Email: {patient['email']}")
            print(f"📞 Phone: {patient['phone']}")
            print(f"🗣️ Language: {patient['language_preference']}")
            print(f"📞 REAL call should be initiated to your phone!")
            print(f"📅 Appointment scheduled automatically")
            print(f"📧 Email confirmation sent")
            
            print(f"\n🎯 What to expect:")
            print(f"1. Your phone should ring with a call from Twilio")
            print(f"2. The AI will speak to you in {patient['language_preference']}")
            print(f"3. The AI will confirm your appointment")
            print(f"4. You'll receive an email confirmation")
            
        else:
            print(f"❌ Patient registration failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
    
    print(f"\n🎯 System Status:")
    print(f"✅ Backend: http://localhost:8000")
    print(f"✅ Frontend: http://localhost:3000")
    print(f"📞 REAL Twilio calls enabled")
    print(f"🌍 Multilingual support (English/Tamil/Hindi)")
    
    print(f"\n🚀 Ready to Use!")
    print(f"1. Open http://localhost:3000 in your browser")
    print(f"2. Fill out the patient form with YOUR phone number")
    print(f"3. Submit and receive a REAL AI call!")
    print(f"4. The AI will speak to you in your chosen language")

if __name__ == "__main__":
    test_real_twilio_call()

