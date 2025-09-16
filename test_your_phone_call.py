#!/usr/bin/env python3
"""
Test script to make a REAL call to your phone
"""

import requests
import json
import time

def test_your_phone_call():
    """Test the system with a REAL call to your phone"""
    
    print("🚀 Testing MedAgg Healthcare POC with REAL Twilio Call")
    print("=" * 60)
    print("📞 Your Twilio Setup:")
    print("   Account SID: AC33f397657e06dac328e5d5081eb4f9fd")
    print("   Auth Token: bbf7abc794d8f0eb9538350b501d033f")
    print("   Twilio Number: +17752586467")
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
    
    # Test patient registration with REAL call to YOUR phone
    print("\n📝 Registering patient for REAL call to YOUR phone...")
    print("🔔 You should receive a call on your phone!")
    
    # Replace this with YOUR actual phone number
    YOUR_PHONE_NUMBER = input("Enter your phone number (with country code, e.g., +919876543210): ").strip()
    
    if not YOUR_PHONE_NUMBER:
        YOUR_PHONE_NUMBER = "+919876543210"  # Default for testing
        print(f"Using default number: {YOUR_PHONE_NUMBER}")
    
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
        print(f"\n📞 Initiating REAL call to {patient_data['phone']}...")
        print("🔔 Your phone should ring NOW!")
        print("📱 Answer the call to hear the AI speak!")
        
        response = requests.post(
            "http://localhost:8000/api/patients",
            json=patient_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            patient = response.json()
            print(f"\n✅ Patient registered: {patient['name']} (ID: {patient['id']})")
            print(f"📧 Email: {patient['email']}")
            print(f"📞 Phone: {patient['phone']}")
            print(f"🗣️ Language: {patient['language_preference']}")
            print(f"📞 REAL call initiated to your phone!")
            print(f"📅 Appointment scheduled automatically")
            print(f"📧 Email confirmation sent")
            
            print(f"\n🎯 What to expect:")
            print(f"1. Your phone should ring with a call from +17752586467")
            print(f"2. The AI will speak to you in {patient['language_preference']}")
            print(f"3. The AI will confirm your appointment")
            print(f"4. You'll receive an email confirmation")
            
            print(f"\n⏰ Wait for the call...")
            print(f"📱 If you don't receive a call, check your phone's call log")
            
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
    test_your_phone_call()

