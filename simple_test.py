#!/usr/bin/env python3
"""
Simple test to check if HTTP server starts
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from flask_server import app
    print("✅ Flask server imported successfully")
    
    # Test if we can create the app
    print("✅ Flask app created successfully")
    
    # Test the health endpoint
    with app.test_client() as client:
        response = client.get('/health')
        print(f"✅ Health endpoint status: {response.status_code}")
        print(f"✅ Health response: {response.get_json()}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()