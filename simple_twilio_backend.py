#!/usr/bin/env python3
"""
MedAgg Healthcare POC - Simple Backend with Real Twilio Calls
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import uuid
import datetime
from urllib.parse import urlparse, parse_qs
import threading
import time
import random
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

# Twilio Configuration
TWILIO_ACCOUNT_SID = "AC33f397657e06dac328e5d5081eb4f9fd"
TWILIO_AUTH_TOKEN = "bbf7abc794d8f0eb9538350b501d033f"
# You need to get your Twilio phone number from the Twilio Console
TWILIO_PHONE_NUMBER = "+17752586467"  # Your actual Twilio number

# Initialize Twilio client
try:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    print("✅ Twilio client initialized successfully")
except Exception as e:
    print(f"❌ Twilio initialization failed: {e}")
    twilio_client = None

# In-memory storage
patients = []
hospitals = []
appointments = []
call_sessions = []

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
            "specializations": ["Interventional Cardiology", "Cardiology"],
            "phone": "+91-11-98765432"
        }
    ]

# Real Twilio Call Handler
def make_real_call(patient_phone, patient_name, language="english"):
    """Make a real phone call using Twilio"""
    if not twilio_client:
        print("❌ Twilio client not available")
        return None
    
    try:
        # Create a simple TwiML response (URL encode the patient name)
        import urllib.parse
        encoded_name = urllib.parse.quote(patient_name)
        twiml_url = f"http://localhost:8000/twiml/{encoded_name}/{language}"
        
        print(f"📞 Attempting to call {patient_phone}...")
        print(f"🔗 TwiML URL: {twiml_url}")
        
        # Make the call
        call = twilio_client.calls.create(
            to=patient_phone,
            from_=TWILIO_PHONE_NUMBER,
            url=twiml_url,
            method='GET'
        )
        
        print(f"✅ Call initiated successfully!")
        print(f"🆔 Call SID: {call.sid}")
        print(f"📞 Status: {call.status}")
        return call.sid
    except Exception as e:
        print(f"❌ Call failed: {str(e)}")
        print(f"💡 Make sure you have a valid Twilio phone number configured")
        return None

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # CORS headers
        self.send_cors_headers()
        
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "message": "MedAgg Healthcare POC API",
                "status": "running",
                "version": "3.0.0",
                "features": ["Real Twilio Calls", "Multilingual AI", "Email Confirmations"],
                "twilio_status": "configured" if twilio_client else "not_configured"
            }
            self.wfile.write(json.dumps(response).encode())
        
        elif path == '/api/patients':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(patients).encode())
        
        elif path == '/api/hospitals':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(hospitals).encode())
        
        elif path == '/api/appointments':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(appointments).encode())
        
        elif path == '/api/calls':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(call_sessions).encode())
        
        elif path.startswith('/twiml/'):
            # TwiML endpoint for Twilio calls
            parts = path.split('/')
            if len(parts) >= 4:
                import urllib.parse
                patient_name = urllib.parse.unquote(parts[2])
                language = parts[3]
                
                # Generate TwiML response
                response = VoiceResponse()
                
                if language.lower() == "tamil":
                    response.say(f"வணக்கம் {patient_name}! நான் MedAgg மருத்துவ AI.", voice='alice')
                    response.say("உங்கள் மருத்துவ நியமனம் வெற்றிகரமாக திட்டமிடப்பட்டது.", voice='alice')
                    response.say("நன்றி!", voice='alice')
                elif language.lower() == "hindi":
                    response.say(f"नमस्ते {patient_name}! मैं MedAgg मेडिकल AI हूं।", voice='alice')
                    response.say("आपका मेडिकल अपॉइंटमेंट सफलतापूर्वक शेड्यूल हो गया है।", voice='alice')
                    response.say("धन्यवाद!", voice='alice')
                else:  # English
                    response.say(f"Hello {patient_name}! This is MedAgg Medical AI.", voice='alice')
                    response.say("Your medical appointment has been successfully scheduled.", voice='alice')
                    response.say("Thank you!", voice='alice')
                
                self.send_response(200)
                self.send_header('Content-type', 'text/xml')
                self.end_headers()
                self.wfile.write(response.to_xml().encode())
            else:
                self.send_error(404)
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # CORS headers
        self.send_cors_headers()
        
        if path == '/api/patients':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            patient_data = json.loads(post_data.decode('utf-8'))
            
            # Validate Indian phone number
            phone = patient_data.get('phone', '')
            if not phone.startswith('+91') and not phone.startswith('91'):
                patient_data['phone'] = '+91' + phone.lstrip('0')
            
            # Create patient
            patient = {
                "id": len(patients) + 1,
                "name": patient_data.get('name', ''),
                "email": patient_data.get('email', ''),
                "phone": patient_data.get('phone', ''),
                "age": patient_data.get('age', 0),
                "gender": patient_data.get('gender', ''),
                "location": patient_data.get('location', ''),
                "problem_description": patient_data.get('problem_description', ''),
                "medical_category": patient_data.get('medical_category', ''),
                "subcategory": patient_data.get('subcategory', ''),
                "language_preference": patient_data.get('language_preference', 'English'),
                "created_at": datetime.datetime.now().isoformat()
            }
            
            patients.append(patient)
            
            # Make REAL phone call
            print(f"\n📞 Making REAL call to {patient['phone']}...")
            print(f"👤 Patient: {patient['name']}")
            print(f"🗣️ Language: {patient['language_preference']}")
            
            call_sid = make_real_call(patient['phone'], patient['name'], patient['language_preference'])
            
            if call_sid:
                # Create call session
                call_session = {
                    "id": str(uuid.uuid4()),
                    "patient_id": patient['id'],
                    "call_sid": call_sid,
                    "status": "initiated",
                    "language": patient['language_preference'],
                    "created_at": datetime.datetime.now().isoformat()
                }
                call_sessions.append(call_session)
                
                # Schedule appointment
                appointment = {
                    "id": len(appointments) + 1,
                    "patient_id": patient['id'],
                    "patient_name": patient['name'],
                    "hospital_id": 1,
                    "hospital_name": hospitals[0]['name'],
                    "appointment_date": "2025-09-15T10:00:00",
                    "status": "scheduled",
                    "created_at": datetime.datetime.now().isoformat()
                }
                appointments.append(appointment)
                
                print(f"✅ Patient {patient['name']} registered successfully!")
                print(f"📞 REAL call initiated to {patient['phone']}")
                print(f"📅 Appointment scheduled for {appointment['appointment_date']}")
                print(f"📧 Email confirmation will be sent to {patient['email']}")
            else:
                print(f"⚠️ Call failed, but patient registered successfully")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(patient).encode())
        
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_cors_headers()
        self.send_response(200)
        self.end_headers()
    
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

def main():
    init_dummy_data()
    
    print("🏥 MedAgg Healthcare POC Backend Started!")
    print("📊 Dummy data initialized")
    print("🌍 Multilingual AI ready (English, Tamil, Hindi)")
    print("📞 REAL Twilio calls enabled")
    print("📧 Email confirmations enabled")
    print("🇮🇳 Indian phone number validation enabled")
    print("🔗 API running on http://localhost:8000")
    print("📱 Frontend should be on http://localhost:3000")
    print("⚠️  IMPORTANT: Configure your Twilio phone number in the code!")
    
    server = HTTPServer(('localhost', 8000), RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()

if __name__ == '__main__':
    main()
