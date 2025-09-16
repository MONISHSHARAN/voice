#!/usr/bin/env python3
"""
MedAgg Healthcare POC - Simple Working Backend
Uses direct Twilio curl commands for calls
"""

import json
import uuid
import datetime
import threading
import time
import random
import subprocess
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver

# Twilio Configuration
TWILIO_ACCOUNT_SID = "AC33f397657e06dac328e5d5081eb4f9fd"
TWILIO_AUTH_TOKEN = "bbf7abc794d8f0eb9538350b501d033f"
TWILIO_PHONE_NUMBER = "+17752586467"

# In-memory storage
patients = []
hospitals = []
appointments = []

# Initialize dummy data
def init_dummy_data():
    global hospitals
    hospitals = [
        {
            "id": 1,
            "name": "Apollo Hospital",
            "location": "Mumbai, Maharashtra",
            "specializations": ["Interventional Cardiology", "General Medicine"],
            "phone": "+91-22-12345678"
        },
        {
            "id": 2,
            "name": "Fortis Healthcare",
            "location": "Delhi, NCR",
            "specializations": ["Neurology", "Orthopedics"],
            "phone": "+91-11-98765432"
        },
        {
            "id": 3,
            "name": "Manipal Hospital",
            "location": "Bangalore, Karnataka",
            "specializations": ["Cardiology", "Oncology"],
            "phone": "+91-80-55555555"
        }
    ]

def make_twilio_call(patient_name, phone_number, language="English"):
    """Make a Twilio call using curl command"""
    try:
        # Create TwiML URL with patient info
        twiml_url = f"http://demo.twilio.com/docs/voice.xml"
        
        # Use the exact curl command you provided
        curl_command = [
            "curl.exe", "-X", "POST",
            f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Calls.json",
            "--data-urlencode", f"Url={twiml_url}",
            "--data-urlencode", f"To={phone_number}",
            "--data-urlencode", f"From={TWILIO_PHONE_NUMBER}",
            "-u", f"{TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}"
        ]
        
        print(f"📞 Making call to {phone_number} for {patient_name} in {language}")
        print(f"🔧 Command: {' '.join(curl_command)}")
        
        # Execute the curl command
        result = subprocess.run(curl_command, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ Call initiated successfully!")
            print(f"📋 Response: {result.stdout}")
            return True
        else:
            print(f"❌ Call failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error making call: {e}")
        return False

class RequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>MedAgg Healthcare POC Backend</h1><p>Backend is running!</p>')
        elif self.path == '/hospitals':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(hospitals).encode())
        elif self.path == '/patients':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(patients).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/register-patient':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                patient_data = json.loads(post_data.decode('utf-8'))
                
                # Validate Indian phone number
                phone = patient_data.get('phone_number', '')
                if not phone.startswith('+91') and not phone.startswith('91'):
                    phone = '+91' + phone.lstrip('0')
                
                # Create patient
                patient = {
                    'id': str(uuid.uuid4()),
                    'name': patient_data.get('name', ''),
                    'phone_number': phone,
                    'email': patient_data.get('email', ''),
                    'age': patient_data.get('age', 0),
                    'location': patient_data.get('location', ''),
                    'language_preference': patient_data.get('language_preference', 'English'),
                    'created_at': datetime.datetime.now().isoformat()
                }
                
                patients.append(patient)
                
                # Make Twilio call
                call_success = make_twilio_call(
                    patient['name'], 
                    patient['phone_number'], 
                    patient['language_preference']
                )
                
                response = {
                    'success': True,
                    'patient_id': patient['id'],
                    'message': 'Patient registered successfully',
                    'call_initiated': call_success
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                error_response = {
                    'success': False,
                    'error': str(e)
                }
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_backend():
    """Start the backend server"""
    init_dummy_data()
    
    print("🏥 MedAgg Healthcare POC Backend - SIMPLE VERSION")
    print("=" * 50)
    print("📊 Dummy data initialized")
    print("📞 Twilio calls using curl commands")
    print("🔗 API running on http://localhost:8000")
    print("📱 Frontend should be on http://localhost:3000")
    print("✅ Ready for testing!")
    print("=" * 50)
    
    try:
        with HTTPServer(('localhost', 8000), RequestHandler) as httpd:
            print("🚀 Backend server started successfully!")
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_backend()
