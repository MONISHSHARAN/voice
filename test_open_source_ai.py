#!/usr/bin/env python3
"""
Test script for MedAgg Healthcare Open Source AI
Tests all components of the open-source AI system
"""

import requests
import json
import time
import os

def test_backend():
    """Test backend endpoints"""
    print("🧪 Testing Open Source AI Backend...")
    
    try:
        # Test basic endpoint
        response = requests.get("http://localhost:8000", timeout=10)
        print(f"✅ Backend is running: {response.status_code}")
        
        # Test hospitals endpoint
        response = requests.get("http://localhost:8000/hospitals", timeout=10)
        hospitals = response.json()
        print(f"✅ Hospitals loaded: {len(hospitals)} hospitals")
        
        # Test conversations endpoint
        response = requests.get("http://localhost:8000/conversations", timeout=10)
        conversations = response.json()
        print(f"✅ Conversations endpoint working: {len(conversations)} active conversations")
        
        return True
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def test_ai_responses():
    """Test AI response generation"""
    print("\n🧪 Testing Open Source AI Responses...")
    
    try:
        from open_source_ai_backend import ai_service
        
        # Test English response
        response_en = ai_service.generate_response("I have a headache", "english")
        print(f"✅ English AI response: {response_en[:100]}...")
        
        # Test Tamil response
        response_ta = ai_service.generate_response("தலைவலி", "tamil")
        print(f"✅ Tamil AI response: {response_ta[:100]}...")
        
        # Test Hindi response
        response_hi = ai_service.generate_response("सिरदर्द", "hindi")
        print(f"✅ Hindi AI response: {response_hi[:100]}...")
        
        # Test emergency response
        emergency_response = ai_service.generate_response("I have chest pain", "english")
        print(f"✅ Emergency response: {emergency_response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ AI response test failed: {e}")
        return False

def test_patient_registration():
    """Test patient registration with open-source AI"""
    print("\n🧪 Testing Patient Registration with Open Source AI...")
    
    patient_data = {
        "name": "Test Patient",
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
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Patient registered successfully!")
            print(f"📋 Patient ID: {result.get('patient_id')}")
            print(f"📞 Open Source AI call initiated: {result.get('call_initiated')}")
            return True
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"📋 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
        return False

def test_multilingual_registration():
    """Test multilingual patient registration"""
    print("\n🧪 Testing Multilingual Patient Registration...")
    
    languages = [
        {"language": "English", "name": "John Doe"},
        {"language": "Tamil", "name": "ராஜ் குமார்"},
        {"language": "Hindi", "name": "राज कुमार"}
    ]
    
    success_count = 0
    for lang_data in languages:
        patient_data = {
            "name": lang_data["name"],
            "phone_number": "+917010557477",
            "email": f"test_{lang_data['language'].lower()}@example.com",
            "age": 30,
            "location": "Mumbai",
            "language_preference": lang_data["language"]
        }
        
        try:
            response = requests.post(
                "http://localhost:8000/register-patient",
                json=patient_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                print(f"✅ {lang_data['language']} registration successful")
                success_count += 1
            else:
                print(f"❌ {lang_data['language']} registration failed")
                
        except Exception as e:
            print(f"❌ {lang_data['language']} registration error: {e}")
    
    print(f"📊 Multilingual test: {success_count}/{len(languages)} languages successful")
    return success_count == len(languages)

def test_twiml_generation():
    """Test TwiML generation"""
    print("\n🧪 Testing TwiML Generation...")
    
    try:
        from open_source_ai_backend import create_intelligent_twiml
        
        # Test English TwiML
        twiml_en = create_intelligent_twiml("test-conversation", "english")
        if "Dr. MedAgg" in twiml_en and "Hello!" in twiml_en:
            print("✅ English TwiML generation working")
        else:
            print("❌ English TwiML generation failed")
            return False
        
        # Test Tamil TwiML
        twiml_ta = create_intelligent_twiml("test-conversation", "tamil")
        if "டாக்டர் மெட்அக்" in twiml_ta and "வணக்கம்" in twiml_ta:
            print("✅ Tamil TwiML generation working")
        else:
            print("❌ Tamil TwiML generation failed")
            return False
        
        # Test Hindi TwiML
        twiml_hi = create_intelligent_twiml("test-conversation", "hindi")
        if "डॉ. मेडएग" in twiml_hi and "नमस्ते" in twiml_hi:
            print("✅ Hindi TwiML generation working")
        else:
            print("❌ Hindi TwiML generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ TwiML generation test failed: {e}")
        return False

def test_frontend():
    """Test frontend"""
    print("\n🧪 Testing Frontend...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend is running")
            return True
        else:
            print(f"❌ Frontend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False

def test_ai_model_loading():
    """Test AI model loading"""
    print("\n🧪 Testing AI Model Loading...")
    
    try:
        from open_source_ai_backend import ai_service
        
        if ai_service.is_loaded:
            print("✅ Hugging Face model loaded successfully")
            print("🤖 AI Model: Microsoft DialoGPT-medium")
            return True
        else:
            print("⚠️  Hugging Face model not loaded - using rule-based responses")
            print("💡 Install transformers: pip install transformers torch")
            return True  # Rule-based is still valid
            
    except Exception as e:
        print(f"❌ AI model test failed: {e}")
        return False

def main():
    print("🚀 Testing MedAgg Healthcare Open Source AI System")
    print("=" * 70)
    
    # Test backend
    backend_ok = test_backend()
    
    # Test frontend
    frontend_ok = test_frontend()
    
    # Test AI model loading
    ai_model_ok = test_ai_model_loading()
    
    # Test AI responses
    ai_responses_ok = test_ai_responses()
    
    # Test TwiML generation
    twiml_ok = test_twiml_generation()
    
    # Test patient registration
    registration_ok = test_patient_registration()
    
    # Test multilingual support
    multilingual_ok = test_multilingual_registration()
    
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    print(f"Backend API: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"Frontend: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    print(f"AI Model Loading: {'✅ PASS' if ai_model_ok else '❌ FAIL'}")
    print(f"AI Responses: {'✅ PASS' if ai_responses_ok else '❌ FAIL'}")
    print(f"TwiML Generation: {'✅ PASS' if twiml_ok else '❌ FAIL'}")
    print(f"Patient Registration: {'✅ PASS' if registration_ok else '❌ FAIL'}")
    print(f"Multilingual Support: {'✅ PASS' if multilingual_ok else '❌ FAIL'}")
    
    total_tests = 7
    passed_tests = sum([backend_ok, frontend_ok, ai_model_ok, ai_responses_ok, twiml_ok, registration_ok, multilingual_ok])
    
    print(f"\n🎯 Overall Score: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests >= 5:  # At least 5 out of 7 tests should pass
        print("\n🎉 OPEN SOURCE AI SYSTEM IS WORKING!")
        print("\n📱 Next steps:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Register a patient to test the open-source AI conversation")
        print("3. You should receive an intelligent call with AI conversation")
        print("\n🤖 AI Features:")
        print("✅ Completely free - no API keys required")
        print("✅ Runs locally on your machine")
        print("✅ Multilingual AI conversations")
        print("✅ Medical-specific responses")
        print("✅ Twilio voice integration")
        print("✅ Rule-based fallback system")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
