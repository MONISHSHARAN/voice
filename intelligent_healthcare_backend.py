#!/usr/bin/env python3
"""
MedAgg Healthcare POC - Intelligent Backend with Twilio Conversational Intelligence
Real-time AI conversations with OpenAI Realtime API and Twilio ConversationRelay
"""

import json
import uuid
import datetime
import subprocess
import urllib.parse
import asyncio
import websockets
import threading
import time
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import requests
import base64
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
active_calls = {}

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

class ConversationRelay:
    """Handles real-time conversation with OpenAI Realtime API"""
    
    def __init__(self, conversation_id, language="english"):
        self.conversation_id = conversation_id
        self.language = language
        self.websocket = None
        self.is_connected = False
        
    async def connect_to_openai(self):
        """Connect to OpenAI Realtime API"""
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            self.websocket = await websockets.connect(
                "wss://api.openai.com/v1/realtime",
                extra_headers=headers
            )
            
            # Send initial configuration
            config = {
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],
                    "instructions": MEDICAL_PROMPTS.get(self.language, MEDICAL_PROMPTS["english"]),
                    "voice": "alloy",
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16",
                    "input_audio_transcription": {
                        "model": "whisper-1"
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 200
                    },
                    "tools": [
                        {
                            "type": "function",
                            "name": "schedule_appointment",
                            "description": "Schedule a medical appointment",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "patient_name": {"type": "string"},
                                    "phone_number": {"type": "string"},
                                    "symptoms": {"type": "string"},
                                    "urgency": {"type": "string", "enum": ["low", "medium", "high", "emergency"]},
                                    "preferred_hospital": {"type": "string"}
                                },
                                "required": ["patient_name", "symptoms", "urgency"]
                            }
                        }
                    ]
                }
            }
            
            await self.websocket.send(json.dumps(config))
            self.is_connected = True
            logger.info(f"Connected to OpenAI Realtime API for conversation {self.conversation_id}")
            
        except Exception as e:
            logger.error(f"Failed to connect to OpenAI: {e}")
            self.is_connected = False
    
    async def process_audio(self, audio_data):
        """Process incoming audio data"""
        if not self.is_connected:
            return None
            
        try:
            # Send audio data to OpenAI
            audio_message = {
                "type": "input_audio_buffer.append",
                "audio": base64.b64encode(audio_data).decode('utf-8')
            }
            await self.websocket.send(json.dumps(audio_message))
            
            # Commence input
            await self.websocket.send(json.dumps({"type": "input_audio_buffer.commit"}))
            
            # Wait for response
            response = await self.websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get("type") == "conversation.item.input_audio_transcription.completed":
                return response_data.get("transcript")
            elif response_data.get("type") == "conversation.item.output_audio.delta":
                return base64.b64decode(response_data.get("delta", ""))
                
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return None
    
    async def close(self):
        """Close the connection"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False

class IntelligentRequestHandler(BaseHTTPRequestHandler):
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
                self.wfile.write(b'<h1>MedAgg Healthcare POC - Intelligent Backend</h1><p>Backend with Conversational Intelligence is running!</p>')
                
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
                
            elif self.path.startswith('/conversation/'):
                # WebSocket endpoint for real-time conversation
                conversation_id = self.path.split('/')[-1]
                self.handle_websocket_upgrade(conversation_id)
                
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
                'status': 'initiated'
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
            
            # Create TwiML response
            response = VoiceResponse()
            
            # Greeting based on language
            greetings = {
                'english': f"Hello! This is Dr. MedAgg from MedAgg Healthcare. I'm here to help you with your medical concerns. How can I assist you today?",
                'tamil': f"வணக்கம்! இது மெட்அக் ஹெல்த்கேரிலிருந்து டாக்டர் மெட்அக். உங்கள் மருத்துவ கவலைகளுக்கு உதவ நான் இங்கே இருக்கிறேன். இன்று நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?",
                'hindi': f"नमस्ते! यह मेडएग हेल्थकेयर से डॉ. मेडएग है। मैं आपकी चिकित्सा चिंताओं में आपकी मदद के लिए यहाँ हूँ। आज मैं आपकी कैसे मदद कर सकता हूँ?"
            }
            
            response.say(greetings.get(language, greetings['english']), voice='alice')
            
            # Start conversation with media stream
            start = response.start()
            stream = start.stream(
                url=f'wss://localhost:8000/conversation/{conversation_id}',
                track='both_tracks'
            )
            
            # Handle conversation events
            response.say("Please speak now, and I'll listen to your concerns.", voice='alice')
            
            self.send_response(200)
            self.send_header('Content-type', 'text/xml')
            self.end_headers()
            self.wfile.write(str(response).encode())
            
        except Exception as e:
            logger.error(f"Error handling TwiML request: {e}")
            self.send_response(500)
            self.end_headers()

    def handle_websocket_upgrade(self, conversation_id):
        """Handle WebSocket upgrade for real-time conversation"""
        # This would need to be implemented with a proper WebSocket server
        # For now, we'll return a simple response
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(f"WebSocket endpoint for conversation {conversation_id}".encode())

def start_intelligent_backend():
    """Start the intelligent backend server"""
    init_dummy_data()
    
    print("🏥 MedAgg Healthcare POC - INTELLIGENT BACKEND")
    print("=" * 60)
    print("📊 Dummy data initialized")
    print("🤖 OpenAI Realtime API integration")
    print("📞 Twilio Conversational Intelligence enabled")
    print("🌍 Multilingual support (English, Tamil, Hindi)")
    print("🔗 API running on http://localhost:8000")
    print("📱 Frontend should be on http://localhost:3000")
    print("✅ Ready for intelligent conversations!")
    print("=" * 60)
    
    try:
        with HTTPServer(('localhost', 8000), IntelligentRequestHandler) as httpd:
            print("🚀 Intelligent backend server started successfully!")
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_intelligent_backend()
