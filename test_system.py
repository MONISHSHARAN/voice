#!/usr/bin/env python3
"""
Test script for MedAgg Healthcare POC
This script tests the system functionality including the multilingual AI
"""

import asyncio
import json
import requests
import time
from datetime import datetime

def test_backend_api():
    """Test if the backend API is running"""
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is running!")
            return True
        else:
            print(f"❌ Backend API returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend API is not running: {e}")
        return False

def test_patient_creation():
    """Test creating a patient and triggering AI call"""
    try:
        # Test patient data
        patient_data = {
            "name": "Test Patient",
            "gender": "male",
            "phone_number": "+1234567890",
            "age": 35,
            "location": "New York, NY",
            "language_preference": "english",
            "problem_description": "I have been experiencing chest pain for the past few days. It's a sharp pain that comes and goes, especially when I'm stressed or after physical activity.",
            "medical_category": "interventional_cardiology",
            "sub_category": "chronic_total_occlusion"
        }
        
        print("📝 Creating test patient...")
        response = requests.post("http://localhost:8000/api/patients", json=patient_data, timeout=10)
        
        if response.status_code == 200:
            patient = response.json()
            print(f"✅ Patient created successfully! ID: {patient['id']}")
            print(f"   Name: {patient['name']}")
            print(f"   Language: {patient['language_preference']}")
            print(f"   Phone: {patient['phone_number']}")
            return patient
        else:
            print(f"❌ Failed to create patient: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating patient: {e}")
        return None

def test_multilingual_patient():
    """Test creating a patient with different language preferences"""
    languages = [
        {"lang": "english", "name": "John Smith", "problem": "I have chest pain and shortness of breath"},
        {"lang": "tamil", "name": "ராஜா குமார்", "problem": "எனக்கு மார்பு வலி மற்றும் மூச்சுத் திணறல் இருக்கிறது"},
        {"lang": "hindi", "name": "राम शर्मा", "problem": "मुझे छाती में दर्द और सांस की तकलीफ है"}
    ]
    
    for lang_data in languages:
        try:
            patient_data = {
                "name": lang_data["name"],
                "gender": "male",
                "phone_number": f"+123456789{hash(lang_data['lang']) % 10}",
                "age": 30,
                "location": "New York, NY",
                "language_preference": lang_data["lang"],
                "problem_description": lang_data["problem"],
                "medical_category": "interventional_cardiology",
                "sub_category": "radiofrequency_ablation"
            }
            
            print(f"🌍 Creating {lang_data['lang']} patient: {lang_data['name']}")
            response = requests.post("http://localhost:8000/api/patients", json=patient_data, timeout=10)
            
            if response.status_code == 200:
                patient = response.json()
                print(f"✅ {lang_data['lang'].title()} patient created! ID: {patient['id']}")
            else:
                print(f"❌ Failed to create {lang_data['lang']} patient: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating {lang_data['lang']} patient: {e}")

def test_admin_dashboard():
    """Test admin dashboard endpoints"""
    try:
        print("🔧 Testing admin dashboard...")
        
        # Test system overview
        response = requests.get("http://localhost:8000/api/admin/analytics/overview", timeout=5)
        if response.status_code == 200:
            overview = response.json()
            print("✅ Admin overview accessible")
            print(f"   Total patients: {overview.get('patients', {}).get('total', 0)}")
            print(f"   Total hospitals: {overview.get('hospitals', {}).get('total', 0)}")
        else:
            print(f"❌ Admin overview failed: {response.status_code}")
        
        # Test patients list
        response = requests.get("http://localhost:8000/api/admin/patients?limit=10", timeout=5)
        if response.status_code == 200:
            patients = response.json()
            print(f"✅ Patients list accessible: {len(patients)} patients")
        else:
            print(f"❌ Patients list failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing admin dashboard: {e}")

def test_ai_simulation():
    """Simulate AI call process"""
    try:
        print("🤖 Simulating AI call process...")
        
        # This would normally be triggered by the patient creation
        # For testing, we'll simulate the conversation
        print("📞 AI would call the patient now...")
        print("🗣️  AI: Hello! This is MedAgg calling. I received your request for interventional cardiology consultation.")
        print("👤 Patient: Yes, I have chest pain.")
        print("🗣️  AI: I understand you're experiencing chest pain. Can you describe the pain in more detail?")
        print("👤 Patient: It's a sharp pain that comes and goes.")
        print("🗣️  AI: How long have you been experiencing these symptoms?")
        print("👤 Patient: About 3 days now.")
        print("🗣️  AI: Based on your symptoms, I recommend immediate consultation with a cardiologist.")
        print("📅 AI: I'll schedule an appointment for you with the best available specialist.")
        print("✅ Appointment scheduled! You'll receive a confirmation email shortly.")
        
    except Exception as e:
        print(f"❌ Error in AI simulation: {e}")

def main():
    """Main test function"""
    print("🏥 MedAgg Healthcare POC - System Test")
    print("=" * 50)
    
    # Test 1: Backend API
    print("\n1. Testing Backend API...")
    if not test_backend_api():
        print("❌ Backend API is not running. Please start it first:")
        print("   cd backend")
        print("   python main.py")
        return
    
    # Test 2: Patient Creation
    print("\n2. Testing Patient Creation...")
    patient = test_patient_creation()
    if not patient:
        print("❌ Patient creation failed. Check backend logs.")
        return
    
    # Test 3: Multilingual Patients
    print("\n3. Testing Multilingual Patient Creation...")
    test_multilingual_patient()
    
    # Test 4: Admin Dashboard
    print("\n4. Testing Admin Dashboard...")
    test_admin_dashboard()
    
    # Test 5: AI Simulation
    print("\n5. Simulating AI Call Process...")
    test_ai_simulation()
    
    print("\n" + "=" * 50)
    print("🎉 System Test Completed!")
    print("\n📋 Next Steps:")
    print("1. Open http://localhost:3000 in your browser (if frontend is running)")
    print("2. Fill out the patient form to test the full experience")
    print("3. Check the admin dashboard at http://localhost:3000/admin")
    print("4. Monitor the backend logs for AI call processing")
    
    print(f"\n🔗 Test Patient ID: {patient['id'] if patient else 'N/A'}")
    print("📞 The AI call simulation shows what would happen when a patient submits the form.")

if __name__ == "__main__":
    main()


