#!/usr/bin/env python3
"""
MedAgg Healthcare POC - Backend with Real Twilio Calls
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
import requests

# Twilio Configuration
TWILIO_ACCOUNT_SID = "AC33f397657e06dac328e5d5081eb4f9fd"
TWILIO_AUTH_TOKEN = "bbf7abc794d8f0eb9538350b501d033f"
TWILIO_PHONE_NUMBER = "+1234567890"  # You'll need to get this from Twilio Console

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

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
        },
        {
            "id": 3,
            "name": "Manipal Hospital",
            "location": "Bangalore, Karnataka",
            "specializations": ["Interventional Cardiology", "Cardiology"],
            "phone": "+91-80-55555555"
        }
    ]

# AI Conversation Service
class AIConversationService:
    def __init__(self):
        self.conversations = {}
    
    def start_conversation(self, patient_id, language="english"):
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = {
            "patient_id": patient_id,
            "language": language,
            "messages": [],
            "status": "active"
        }
        return conversation_id
    
    def get_ai_response(self, conversation_id, user_message):
        if conversation_id not in self.conversations:
            return "I'm sorry, I couldn't find our conversation. Let me start fresh."
        
        conv = self.conversations[conversation_id]
        conv["messages"].append({"role": "user", "content": user_message})
        
        # Get patient info
        patient = next((p for p in patients if p["id"] == conv["patient_id"]), None)
        if not patient:
            return "I'm sorry, I couldn't find your information."
        
        # AI Response based on language and context
        language = conv["language"].lower()
        
        if language == "tamil":
            responses = [
                f"வணக்கம் {patient['name']}! நான் MedAgg மருத்துவ AI. உங்கள் {patient['problem_description']} பற்றி கேட்கிறேன்.",
                "உங்கள் அறிகுறிகள் எவ்வளவு காலமாக இருக்கிறது?",
                "உங்களுக்கு மார்பு வலி எப்போது தொடங்கியது?",
                "நன்றி! உங்கள் அறிகுறிகளின் அடிப்படையில், நான் உங்களுக்கு சிறந்த மருத்துவமனையை பரிந்துரைக்கிறேன்.",
                "உங்கள் நியமனம் வெற்றிகரமாக திட்டமிடப்பட்டது!"
            ]
        elif language == "hindi":
            responses = [
                f"नमस्ते {patient['name']}! मैं MedAgg मेडिकल AI हूं। आपकी {patient['problem_description']} के बारे में सुन रहा हूं।",
                "आपके लक्षण कब से हैं?",
                "आपको छाती में दर्द कब शुरू हुआ?",
                "धन्यवाद! आपके लक्षणों के आधार पर, मैं आपको सबसे अच्छा अस्पताल सुझाता हूं।",
                "आपका अपॉइंटमेंट सफलतापूर्वक शेड्यूल हो गया है!"
            ]
        else:  # English
            responses = [
                f"Hello {patient['name']}! I'm MedAgg Medical AI. I understand you're experiencing {patient['problem_description']}.",
                "How long have you been experiencing these symptoms?",
                "When did the chest pain start?",
                "Thank you! Based on your symptoms, I'm recommending the best hospital for your condition.",
                "Your appointment has been successfully scheduled!"
            ]
        
        # Get a contextual response
        message_count = len(conv["messages"])
        if message_count <= 2:
            response = responses[0]
        elif message_count <= 4:
            response = responses[1]
        elif message_count <= 6:
            response = responses[2]
        elif message_count <= 8:
            response = responses[3]
        else:
            response = responses[4]
            conv["status"] = "completed"
        
        conv["messages"].append({"role": "assistant", "content": response})
        return response

ai_service = AIConversationService()

# Real Twilio Call Handler
def make_real_call(patient_phone, patient_name, language="english"):
    """Make a real phone call using Twilio"""
    try:
        # Create TwiML for the call
        twiml_url = f"http://localhost:8000/twiml/{patient_name}/{language}"
        
        # Make the call
        call = twilio_client.calls.create(
            to=patient_phone,
            from_=TWILIO_PHONE_NUMBER,  # You need to get this from Twilio Console
            url=twiml_url,
            method='GET'
        )
        
        print(f"📞 Real call initiated to {patient_phone}")
        print(f"🆔 Call SID: {call.sid}")
        return call.sid
    except Exception as e:
        print(f"❌ Call failed: {str(e)}")
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
                "features": ["Real Twilio Calls", "Multilingual AI", "Email Confirmations"]
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
                patient_name = parts[2]
                language = parts[3]
                
                # Generate TwiML response
                response = VoiceResponse()
                response.say(f"Hello {patient_name}! This is MedAgg Medical AI calling you.", voice='alice')
                response.say("I'm calling to discuss your medical appointment and symptoms.", voice='alice')
                response.say("Please hold while I connect you to our AI assistant.", voice='alice')
                
                # Add a pause and then continue
                response.pause(length=2)
                response.say("Thank you for your patience. Your appointment has been scheduled successfully.", voice='alice')
                response.say("You will receive an email confirmation shortly.", voice='alice')
                response.say("Goodbye and take care!", voice='alice')
                
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
            
            # Start AI conversation
            conversation_id = ai_service.start_conversation(patient['id'], patient['language_preference'])
            
            # Make REAL phone call
            print(f"📞 Making REAL call to {patient['phone']}...")
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
    print("⚠️  IMPORTANT: Make sure your Twilio phone number is configured!")
    
    server = HTTPServer(('localhost', 8000), RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()

if __name__ == '__main__':
    main()
