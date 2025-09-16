#!/usr/bin/env python3
"""
Quick Status Check for MedAgg Healthcare POC
"""

import requests
import time

def check_status():
    print("🏥 MedAgg Healthcare POC - Status Check")
    print("=" * 40)
    
    # Check Frontend
    try:
        response = requests.get("http://localhost:3000/", timeout=5)
        print("✅ Frontend: Running on http://localhost:3000")
    except:
        print("❌ Frontend: Not accessible")
    
    # Check Backend
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print("✅ Backend API: Running on http://localhost:8000")
    except:
        print("❌ Backend API: Not accessible")
    
    # Check API Docs
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        print("✅ API Documentation: Available at http://localhost:8000/docs")
    except:
        print("❌ API Documentation: Not accessible")
    
    print("\n🌐 URLs to Open:")
    print("• Main Application: http://localhost:3000")
    print("• Admin Dashboard: http://localhost:3000#admin")
    print("• API Documentation: http://localhost:8000/docs")
    
    print("\n🎯 Ready to Test!")
    print("1. Fill out the patient form")
    print("2. Select your language preference")
    print("3. Submit and experience the AI call")

if __name__ == "__main__":
    check_status()


