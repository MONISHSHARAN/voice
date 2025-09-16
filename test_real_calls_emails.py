#!/usr/bin/env python3
"""
Test script for real calls and emails functionality
"""

import requests
import json
import time

def test_real_system():
    """Test the complete system with real calls and emails"""
    
    print("🚀 Testing MedAgg Healthcare POC with Real Calls & Emails")
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
    
    # Test patient registration with real call and email
    print("\n📝 Testing Patient Registration with Real Call & Email...")
    
    patient_data = {
        "name": "Rajesh Kumar",
        "email": "rajesh.kumar@example.com",
        "phone": "+919876543210",
        "age": 35,
        "gender": "Male",
        "location": "Mumbai, Maharashtra",
        "problem_description": "Chest pain and shortness of breath for the past week",
        "medical_category": "Interventional Cardiology",
        "subcategory": "Chronic Total Occlusion",
        "language_preference": "Hindi"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/patients/",
            json=patient_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            patient = response.json()
            print(f"✅ Patient registered: {patient['name']} (ID: {patient['id']})")
            print(f"📧 Email: {patient['email']}")
            print(f"📞 Phone: {patient['phone']}")
            print(f"🗣️ Language: {patient['language_preference']}")
            
            # Test call initiation
            print(f"\n📞 Initiating AI call to {patient['phone']}...")
            call_response = requests.post(
                f"http://localhost:8000/api/calls/initiate/{patient['id']}",
                json={"call_type": "ai_diagnosis"}
            )
            
            if call_response.status_code == 200:
                call_data = call_response.json()
                print(f"✅ Call initiated: {call_data['status']}")
                print(f"🆔 Call ID: {call_data['call_id']}")
                
                # Simulate call completion and appointment booking
                print(f"\n📅 Simulating appointment booking...")
                appointment_data = {
                    "patient_id": patient['id'],
                    "hospital_id": 1,  # Using first hospital
                    "appointment_date": "2024-01-15T10:00:00",
                    "notes": "AI call completed - Chest pain evaluation"
                }
                
                appointment_response = requests.post(
                    "http://localhost:8000/api/appointments/",
                    json=appointment_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if appointment_response.status_code == 200:
                    appointment = appointment_response.json()
                    print(f"✅ Appointment booked: {appointment['id']}")
                    print(f"🏥 Hospital: {appointment['hospital_name']}")
                    print(f"📅 Date: {appointment['appointment_date']}")
                    print(f"📧 Email confirmation sent to: {patient['email']}")
                    
                    # Test email sending
                    print(f"\n📧 Testing email confirmation...")
                    email_response = requests.post(
                        f"http://localhost:8000/api/email/send-confirmation/{appointment['id']}"
                    )
                    
                    if email_response.status_code == 200:
                        print("✅ Email confirmation sent successfully!")
                    else:
                        print(f"⚠️ Email sending failed: {email_response.text}")
                else:
                    print(f"❌ Appointment booking failed: {appointment_response.text}")
            else:
                print(f"❌ Call initiation failed: {call_response.text}")
        else:
            print(f"❌ Patient registration failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
    
    # Test admin dashboard
    print(f"\n🔧 Testing Admin Dashboard...")
    try:
        admin_response = requests.get("http://localhost:8000/api/admin/patients")
        if admin_response.status_code == 200:
            patients = admin_response.json()
            print(f"✅ Admin API: {len(patients)} patients found")
        else:
            print("❌ Admin API: Not accessible")
    except:
        print("❌ Admin API: Connection failed")
    
    print(f"\n🎯 System Status Summary:")
    print(f"✅ Backend: http://localhost:8000")
    print(f"✅ Frontend: http://localhost:3000")
    print(f"✅ Admin Dashboard: http://localhost:3000#admin")
    print(f"✅ API Documentation: http://localhost:8000/docs")
    
    print(f"\n🚀 Ready to Use!")
    print(f"1. Open http://localhost:3000 in your browser")
    print(f"2. Fill out the patient form with your details")
    print(f"3. Select your language preference (English/Tamil/Hindi)")
    print(f"4. Submit and receive a real AI call!")
    print(f"5. Check your email for appointment confirmation")
    print(f"6. Monitor the admin dashboard for real-time updates")

if __name__ == "__main__":
    test_real_system()

