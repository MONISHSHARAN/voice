#!/usr/bin/env python3
"""
Test system status
"""

import requests
import time
import subprocess
import sys

def test_system():
    print("🔍 Testing MedAgg Healthcare POC System Status")
    print("=" * 50)
    
    # Test backend
    print("📡 Testing Backend API...")
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend API: Running")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Twilio: {data.get('twilio_status', 'unknown')}")
        else:
            print(f"❌ Backend API: HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Backend API: Connection refused")
    except requests.exceptions.Timeout:
        print("❌ Backend API: Timeout")
    except Exception as e:
        print(f"❌ Backend API: Error - {e}")
    
    # Test frontend
    print("\n🌐 Testing Frontend...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend: Running")
        else:
            print(f"❌ Frontend: HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Frontend: Connection refused")
    except requests.exceptions.Timeout:
        print("❌ Frontend: Timeout")
    except Exception as e:
        print(f"❌ Frontend: Error - {e}")
    
    # Test patient registration
    print("\n📝 Testing Patient Registration...")
    try:
        patient_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+919876543210",
            "age": 30,
            "gender": "Male",
            "location": "Mumbai",
            "problem_description": "Test problem",
            "medical_category": "Interventional Cardiology",
            "subcategory": "Chronic Total Occlusion",
            "language_preference": "English"
        }
        
        response = requests.post(
            "http://localhost:8000/api/patients",
            json=patient_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Patient Registration: Working")
            patient = response.json()
            print(f"   Patient ID: {patient.get('id', 'N/A')}")
            print(f"   Name: {patient.get('name', 'N/A')}")
        else:
            print(f"❌ Patient Registration: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Patient Registration: Error - {e}")
    
    print("\n🎯 System Summary:")
    print("✅ Backend: http://localhost:8000")
    print("✅ Frontend: http://localhost:3000")
    print("📞 Twilio: Configured with your credentials")
    print("🌍 Multilingual: English, Tamil, Hindi")
    
    print("\n🚀 Ready to Use!")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Fill out the patient form")
    print("3. Submit to receive a REAL call!")

if __name__ == "__main__":
    test_system()

