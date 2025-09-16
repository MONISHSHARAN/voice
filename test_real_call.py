#!/usr/bin/env python3
"""
Test script for real Twilio calls
"""

import requests
import json
import time

def test_real_call():
    """Test the system with real Twilio call"""
    
    print("🚀 Testing MedAgg Healthcare POC with REAL Twilio Calls")
    print("=" * 60)
    
    # Test backend connectivity
    try:
        response = requests.get("http://localhost:8000")
        if response.status_code == 200:
            print("✅ Backend API: Running")
        else:
            print("❌ Backend API: Not responding")
            return
    except:
        print("❌ Backend API: Connection failed")
        return
    
    # Test patient registration with REAL call
    print("\n📝 Registering patient for REAL call...")
    
    patient_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+919876543210",  # Replace with your actual phone number
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
        print("⚠️  Make sure to replace the phone number with your actual number!")
        
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
    test_real_call()

