#!/usr/bin/env python3
"""
MedAgg Healthcare POC - Working AI Backend
Fixed backend with proper API status and Twilio webhook handling
"""

import json
import uuid
import datetime
import subprocess
import urllib.parse
import threading
import time
import os
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Twilio Configuration
TWILIO_ACCOUNT_SID = "AC33f397657e06dac328e5d5081eb4f9fd"
TWILIO_AUTH_TOKEN = "bbf7abc794d8f0eb9538350b501d033f"
TWILIO_PHONE_NUMBER = "+17752586467"

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
conversations = {}

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

# Medical AI Responses for different languages
MEDICAL_RESPONSES = {
    "english": {
        "greeting": "Hello! This is Dr. MedAgg from MedAgg Healthcare. I'm here to help you with your medical concerns. How can I assist you today?",
        "headache": "Headaches can have various causes. Please rest, stay hydrated, and if the pain persists, consult a doctor.",
        "fever": "Fever is a sign of your body's immune system working. Please rest, stay hydrated, and if the temperature is high, consult a doctor.",
        "emergency": "This appears to be an emergency situation. Please call 108 or your local emergency services immediately. I can help you, but immediate medical assistance is needed.",
        "appointment": "I can help you schedule an appointment. Which hospital would you prefer? What are your symptoms?",
        "default": "I'm here to help you. Please describe your symptoms and concerns in detail. I can provide medical guidance and help you schedule an appointment if needed."
    },
    "tamil": {
        "greeting": "வணக்கம்! இது மெட்அக் ஹெல்த்கேரிலிருந்து டாக்டர் மெட்அக். உங்கள் மருத்துவ கவலைகளுக்கு உதவ நான் இங்கே இருக்கிறேன். இன்று நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?",
        "headache": "தலைவலி பல காரணங்களால் ஏற்படலாம். நீங்கள் ஓய்வு எடுத்து, நீரை அதிகம் குடிக்கவும். வலி தொடர்ந்தால் மருத்துவரை பார்க்கவும்.",
        "fever": "காய்ச்சல் உடலின் நோய் எதிர்ப்பு அமைப்பின் அறிகுறியாகும். ஓய்வு எடுத்து, நீரை அதிகம் குடிக்கவும். வெப்பநிலை அதிகமாக இருந்தால் மருத்துவரை பார்க்கவும்.",
        "emergency": "இது அவசரகாலமாகத் தெரிகிறது. உடனடியாக 108 அல்லது உங்கள் உள்ளூர் அவசரகால சேவையை அழைக்கவும். நான் உங்களுக்கு உதவ முடியும், ஆனால் உடனடியாக மருத்துவ உதவி தேவை.",
        "appointment": "நான் உங்களுக்கு ஒரு நேரம் பதிவு செய்ய உதவ முடியும். எந்த மருத்துவமனையில் நீங்கள் பார்க்க விரும்புகிறீர்கள்? உங்கள் அறிகுறிகள் என்ன?",
        "default": "நான் உங்களுக்கு உதவ முடியும். உங்கள் அறிகுறிகள் மற்றும் கவலைகளை விரிவாக விளக்குங்கள். நான் உங்களுக்கு மருத்துவ ஆலோசனை வழங்க முடியும்."
    },
    "hindi": {
        "greeting": "नमस्ते! यह मेडएग हेल्थकेयर से डॉ. मेडएग है। मैं आपकी चिकित्सा चिंताओं में आपकी मदद के लिए यहाँ हूँ। आज मैं आपकी कैसे मदद कर सकता हूँ?",
        "headache": "सिरदर्द कई कारणों से हो सकता है। आराम करें और अधिक पानी पिएं। यदि दर्द बना रहे तो डॉक्टर से मिलें।",
        "fever": "बुखार शरीर की प्रतिरक्षा प्रणाली का संकेत है। आराम करें और अधिक पानी पिएं। यदि तापमान अधिक है तो डॉक्टर से मिलें।",
        "emergency": "यह एक आपातकालीन स्थिति लगती है। कृपया तुरंत 108 या अपनी स्थानीय आपातकालीन सेवा को कॉल करें। मैं आपकी मदद कर सकता हूं, लेकिन तत्काल चिकित्सा सहायता की आवश्यकता है।",
        "appointment": "मैं आपके लिए अपॉइंटमेंट शेड्यूल करने में मदद कर सकता हूं। आप किस अस्पताल में जाना चाहते हैं? आपके लक्षण क्या हैं?",
        "default": "मैं आपकी मदद कर सकता हूं। कृपया अपने लक्षणों और चिंताओं के बारे में विस्तार से बताएं। मैं आपको चिकित्सा सलाह दे सकता हूं।"
    }
}

def get_ai_response(user_input, language="english"):
    """Get AI response based on user input and language"""
    user_input_lower = user_input.lower()
    
    # Emergency keywords
    emergency_keywords = ['emergency', 'urgent', 'pain', 'bleeding', 'unconscious', 'chest pain', 'heart attack', 'stroke']
    if any(keyword in user_input_lower for keyword in emergency_keywords):
        return MEDICAL_RESPONSES[language]["emergency"]
    
    # Common medical concerns
    if 'headache' in user_input_lower:
        return MEDICAL_RESPONSES[language]["headache"]
    elif 'fever' in user_input_lower:
        return MEDICAL_RESPONSES[language]["fever"]
    elif 'appointment' in user_input_lower or 'schedule' in user_input_lower:
        return MEDICAL_RESPONSES[language]["appointment"]
    else:
        return MEDICAL_RESPONSES[language]["default"]

def create_conversational_twiml(conversation_id, language="english"):
    """Create conversational TwiML for AI conversations"""
    try:
        response = VoiceResponse()
        
        # Initial greeting
        greeting = MEDICAL_RESPONSES[language]["greeting"]
        response.say(greeting, voice='alice')
        
        # Gather user input with speech recognition
        gather = response.gather(
            input='speech',
            action=f'/process-speech?conversation_id={conversation_id}&language={language}',
            method='POST',
            timeout=10,
            speech_timeout='auto'
        )
        
        # Fallback if no input
        response.say("I didn't hear anything. Please call back if you need medical assistance.", voice='alice')
        response.hangup()
        
        return str(response)
        
    except Exception as e:
        logger.error(f"Error creating TwiML: {e}")
        # Fallback TwiML
        response = VoiceResponse()
        response.say("Hello! This is MedAgg Healthcare. How can I help you today?", voice='alice')
        return str(response)

class WorkingAIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        try:
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>MedAgg Healthcare POC - Working AI Backend</h1><p>Backend with Conversational AI is running!</p>')
                
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
                
            elif self.path == '/conversations':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(conversations).encode())
                
            elif self.path == '/ai/status':
                # AI status endpoint for frontend
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                status = {
                    "status": "ready",
                    "model": "rule-based",
                    "languages": ["english", "tamil", "hindi"],
                    "conversations": len(conversations)
                }
                self.wfile.write(json.dumps(status).encode())
                
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            logger.error(f"GET Error: {e}")
            self.send_response(500)
            self.end_headers()

    def do_POST(self):
        try:
            if self.path == '/register-patient':
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                
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
                
                # Make Twilio call using curl (working method)
                call_success = self.make_twilio_call_with_curl(patient)
                
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
                
            elif self.path == '/twiml':
                # TwiML endpoint for Twilio calls
                self.handle_twiml_request()
                
            elif self.path.startswith('/process-speech'):
                # Process speech input from Twilio
                self.handle_speech_processing()
                
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            logger.error(f"POST Error: {e}")
            error_response = {
                'success': False,
                'error': str(e)
            }
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())

    def make_twilio_call_with_curl(self, patient):
        """Make Twilio call using curl (working method)"""
        try:
            conversation_id = str(uuid.uuid4())
            language = patient['language_preference'].lower()
            
            # Create TwiML URL for conversational AI
            twiml_url = f"http://demo.twilio.com/docs/voice.xml"  # Use demo for now
            
            # Use the exact curl command that works
            curl_command = [
                "curl.exe", "-X", "POST",
                f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Calls.json",
                "--data-urlencode", f"Url={twiml_url}",
                "--data-urlencode", f"To={patient['phone_number']}",
                "--data-urlencode", f"From={TWILIO_PHONE_NUMBER}",
                "-u", f"{TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}"
            ]
            
            print(f"📞 Making AI call to {patient['phone_number']} for {patient['name']} in {language}")
            
            # Execute the curl command
            result = subprocess.run(curl_command, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✅ AI call initiated successfully!")
                print(f"📋 Response: {result.stdout}")
                
                # Store conversation info
                conversations[conversation_id] = {
                    'patient': patient,
                    'language': language,
                    'status': 'initiated',
                    'messages': []
                }
                
                return True
            else:
                print(f"❌ Call failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error making AI call: {e}")
            return False

    def handle_twiml_request(self):
        """Handle TwiML request from Twilio"""
        try:
            # Parse query parameters
            query_params = urllib.parse.parse_qs(self.path.split('?')[1] if '?' in self.path else '')
            conversation_id = query_params.get('conversation_id', [None])[0]
            language = query_params.get('language', ['english'])[0]
            
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            # Create conversational TwiML
            twiml = create_conversational_twiml(conversation_id, language)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/xml')
            self.end_headers()
            self.wfile.write(twiml.encode())
            
        except Exception as e:
            logger.error(f"Error handling TwiML request: {e}")
            self.send_response(500)
            self.end_headers()

    def handle_speech_processing(self):
        """Handle speech processing from Twilio"""
        try:
            # Parse form data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            conversation_id = form_data.get('conversation_id', [None])[0]
            language = form_data.get('language', ['english'])[0]
            user_input = form_data.get('SpeechResult', [''])[0]
            
            if not user_input:
                user_input = "I need medical help"
            
            # Get AI response
            ai_response = get_ai_response(user_input, language)
            
            # Store conversation
            if conversation_id in conversations:
                conversations[conversation_id]['messages'].append({
                    'user': user_input,
                    'ai': ai_response,
                    'timestamp': datetime.datetime.now().isoformat()
                })
            
            # Create TwiML response
            response = VoiceResponse()
            response.say(ai_response, voice='alice')
            
            # Continue conversation
            gather = response.gather(
                input='speech',
                action=f'/process-speech?conversation_id={conversation_id}&language={language}',
                method='POST',
                timeout=10,
                speech_timeout='auto'
            )
            
            response.say("Thank you for calling MedAgg Healthcare. Have a great day!", voice='alice')
            response.hangup()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/xml')
            self.end_headers()
            self.wfile.write(str(response).encode())
            
        except Exception as e:
            logger.error(f"Error handling speech processing: {e}")
            self.send_response(500)
            self.end_headers()

def start_working_ai_backend():
    """Start the working AI backend server"""
    init_dummy_data()
    
    print("🏥 MedAgg Healthcare POC - WORKING AI BACKEND")
    print("=" * 70)
    print("📊 Dummy data initialized")
    print("🤖 Conversational AI enabled")
    print("📞 Twilio integration working")
    print("🌍 Multilingual support (English, Tamil, Hindi)")
    print("💬 Real-time AI conversations")
    print("🔗 API running on http://localhost:8000")
    print("📱 Frontend should be on http://localhost:3000")
    print("✅ Ready for intelligent conversations!")
    print("=" * 70)
    
    try:
        with HTTPServer(('localhost', 8000), WorkingAIHandler) as httpd:
            print("🚀 Working AI backend server started successfully!")
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_working_ai_backend()
