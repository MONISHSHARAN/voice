#!/usr/bin/env python3
"""
MedAgg Healthcare POC - Conversational AI Backend
Implements Twilio Conversational Intelligence with real-time AI conversations
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

# OpenAI Configuration (you'll need to add your OpenAI API key)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")

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

# Medical AI Prompts for different languages
MEDICAL_PROMPTS = {
    "english": """You are Dr. MedAgg, an intelligent medical assistant for MedAgg Healthcare. 
    You help patients with:
    - Initial symptom assessment
    - Medical advice and guidance
    - Appointment scheduling
    - Emergency triage
    - General health information
    
    Always be professional, empathetic, and clear. If it's an emergency, advise calling emergency services immediately.
    Keep responses concise and helpful.""",
    
    "tamil": """நீங்கள் டாக்டர் மெட்அக், மெட்அக் ஹெல்த்கேர் அமைப்பின் புத்திசாலி மருத்துவ உதவியாளர்.
    நீங்கள் நோயாளிகளுக்கு உதவுகிறீர்கள்:
    - ஆரம்ப அறிகுறி மதிப்பீடு
    - மருத்துவ ஆலோசனை மற்றும் வழிகாட்டுதல்
    - நேரம் பதிவு செய்தல்
    - அவசரகால மருத்துவ மதிப்பீடு
    - பொது சுகாதார தகவல்கள்
    
    எப்போதும் தொழில்முறை, இரக்கமுள்ள மற்றும் தெளிவாக இருங்கள். அவசரகாலமாக இருந்தால், உடனடியாக அவசரகால சேவைகளை அழைக்குமாறு அறிவுறுத்துங்கள்.""",
    
    "hindi": """आप डॉ. मेडएग हैं, मेडएग हेल्थकेयर के लिए एक बुद्धिमान चिकित्सा सहायक।
    आप रोगियों की मदद करते हैं:
    - प्रारंभिक लक्षण मूल्यांकन
    - चिकित्सा सलाह और मार्गदर्शन
    - अपॉइंटमेंट शेड्यूलिंग
    - आपातकालीन ट्रायेज
    - सामान्य स्वास्थ्य जानकारी
    
    हमेशा पेशेवर, सहानुभूतिपूर्ण और स्पष्ट रहें। यदि यह आपातकाल है, तो तुरंत आपातकालीन सेवाओं को कॉल करने की सलाह दें।"""
}

def call_openai_api(prompt, language="english"):
    """Call OpenAI API for medical conversation"""
    try:
        if OPENAI_API_KEY == "your-openai-api-key-here":
            # Return a mock response if no API key is provided
            return f"Hello! This is Dr. MedAgg from MedAgg Healthcare. I'm here to help you with your medical concerns. How can I assist you today? (Note: OpenAI API key not configured)"
        
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": MEDICAL_PROMPTS.get(language, MEDICAL_PROMPTS["english"])
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again later."
            
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        return "I'm sorry, I'm having trouble processing your request right now. Please try again later."

def create_intelligent_twiml(conversation_id, language="english"):
    """Create intelligent TwiML for conversational AI"""
    try:
        response = VoiceResponse()
        
        # Greeting based on language
        greetings = {
            'english': f"Hello! This is Dr. MedAgg from MedAgg Healthcare. I'm here to help you with your medical concerns. How can I assist you today?",
            'tamil': f"வணக்கம்! இது மெட்அக் ஹெல்த்கேரிலிருந்து டாக்டர் மெட்அக். உங்கள் மருத்துவ கவலைகளுக்கு உதவ நான் இங்கே இருக்கிறேன். இன்று நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?",
            'hindi': f"नमस्ते! यह मेडएग हेल्थकेयर से डॉ. मेडएग है। मैं आपकी चिकित्सा चिंताओं में आपकी मदद के लिए यहाँ हूँ। आज मैं आपकी कैसे मदद कर सकता हूँ?"
        }
        
        # Initial greeting
        response.say(greetings.get(language, greetings['english']), voice='alice')
        
        # Gather user input
        gather = response.gather(
            num_digits=1,
            action=f'/process-input?conversation_id={conversation_id}&language={language}',
            method='POST',
            timeout=10
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

def process_conversation_input(conversation_id, user_input, language="english"):
    """Process user input and generate AI response"""
    try:
        # Get AI response
        ai_response = call_openai_api(user_input, language)
        
        # Store conversation
        if conversation_id not in conversations:
            conversations[conversation_id] = {
                'messages': [],
                'language': language,
                'created_at': datetime.datetime.now()
            }
        
        conversations[conversation_id]['messages'].append({
            'user': user_input,
            'ai': ai_response,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
        return ai_response
        
    except Exception as e:
        logger.error(f"Error processing conversation: {e}")
        return "I'm sorry, I'm having trouble processing your request right now. Please try again later."

class ConversationalAIHandler(BaseHTTPRequestHandler):
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
                self.wfile.write(b'<h1>MedAgg Healthcare POC - Conversational AI Backend</h1><p>Backend with Conversational Intelligence is running!</p>')
                
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
                
                # Make intelligent Twilio call
                call_success = self.make_intelligent_call(patient)
                
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
                
            elif self.path.startswith('/process-input'):
                # Process user input from Twilio
                self.handle_input_processing()
                
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

    def make_intelligent_call(self, patient):
        """Make an intelligent Twilio call with Conversational Intelligence"""
        try:
            conversation_id = str(uuid.uuid4())
            language = patient['language_preference'].lower()
            
            # Create TwiML for intelligent conversation
            twiml_url = f"http://localhost:8000/twiml?conversation_id={conversation_id}&language={language}"
            
            # Use Twilio client to make the call
            call = twilio_client.calls.create(
                url=twiml_url,
                to=patient['phone_number'],
                from_=TWILIO_PHONE_NUMBER
            )
            
            # Store conversation info
            conversations[conversation_id] = {
                'patient': patient,
                'call_sid': call.sid,
                'language': language,
                'status': 'initiated',
                'messages': []
            }
            
            logger.info(f"Intelligent call initiated for {patient['name']} - Call SID: {call.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error making intelligent call: {e}")
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
            
            # Create intelligent TwiML
            twiml = create_intelligent_twiml(conversation_id, language)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/xml')
            self.end_headers()
            self.wfile.write(twiml.encode())
            
        except Exception as e:
            logger.error(f"Error handling TwiML request: {e}")
            self.send_response(500)
            self.end_headers()

    def handle_input_processing(self):
        """Handle user input processing from Twilio"""
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
            
            # Process conversation
            ai_response = process_conversation_input(conversation_id, user_input, language)
            
            # Create TwiML response
            response = VoiceResponse()
            response.say(ai_response, voice='alice')
            
            # Continue conversation
            gather = response.gather(
                num_digits=1,
                action=f'/process-input?conversation_id={conversation_id}&language={language}',
                method='POST',
                timeout=10
            )
            
            response.say("Thank you for calling MedAgg Healthcare. Have a great day!", voice='alice')
            response.hangup()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/xml')
            self.end_headers()
            self.wfile.write(str(response).encode())
            
        except Exception as e:
            logger.error(f"Error handling input processing: {e}")
            self.send_response(500)
            self.end_headers()

def start_conversational_ai_backend():
    """Start the conversational AI backend server"""
    init_dummy_data()
    
    print("🏥 MedAgg Healthcare POC - CONVERSATIONAL AI BACKEND")
    print("=" * 70)
    print("📊 Dummy data initialized")
    print("🤖 OpenAI GPT-4 integration")
    print("📞 Twilio Conversational Intelligence enabled")
    print("🌍 Multilingual support (English, Tamil, Hindi)")
    print("💬 Real-time conversation processing")
    print("🔗 API running on http://localhost:8000")
    print("📱 Frontend should be on http://localhost:3000")
    print("✅ Ready for intelligent conversations!")
    print("=" * 70)
    
    if OPENAI_API_KEY == "your-openai-api-key-here":
        print("⚠️  WARNING: OpenAI API key not configured. Using mock responses.")
        print("   Set OPENAI_API_KEY environment variable for real AI responses.")
    
    try:
        with HTTPServer(('localhost', 8000), ConversationalAIHandler) as httpd:
            print("🚀 Conversational AI backend server started successfully!")
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_conversational_ai_backend()
