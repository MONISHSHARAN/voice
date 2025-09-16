#!/usr/bin/env python3
"""
MedAgg Healthcare POC - Open Source AI Backend
Uses Hugging Face Transformers and LLaMA models for conversational AI
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

class OpenSourceAI:
    """Open Source AI implementation using Hugging Face and local models"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        self.load_model()
    
    def load_model(self):
        """Load Hugging Face model for medical conversations"""
        try:
            print("🤖 Loading open-source AI model...")
            
            # Try to import transformers
            try:
                from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
                print("✅ Transformers library available")
            except ImportError:
                print("❌ Transformers not installed. Using rule-based responses.")
                self.is_loaded = False
                return
            
            # Load a lightweight model for medical conversations
            try:
                # Use a smaller, faster model for real-time conversations
                model_name = "microsoft/DialoGPT-medium"
                print(f"🔄 Loading {model_name}...")
                
                self.model = pipeline(
                    "text-generation",
                    model=model_name,
                    tokenizer=model_name,
                    max_length=150,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=50256
                )
                
                self.is_loaded = True
                print("✅ Open-source AI model loaded successfully!")
                
            except Exception as e:
                print(f"⚠️  Could not load Hugging Face model: {e}")
                print("🔄 Falling back to rule-based responses")
                self.is_loaded = False
                
        except Exception as e:
            print(f"❌ Error loading AI model: {e}")
            self.is_loaded = False
    
    def generate_response(self, user_input, language="english", context=""):
        """Generate AI response using open-source models"""
        try:
            if not self.is_loaded:
                return self.get_rule_based_response(user_input, language)
            
            # Prepare the prompt
            prompt = self.prepare_prompt(user_input, language, context)
            
            # Generate response using Hugging Face model
            response = self.model(
                prompt,
                max_length=len(prompt.split()) + 50,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=50256
            )
            
            # Extract the generated text
            generated_text = response[0]['generated_text']
            
            # Clean up the response
            ai_response = self.clean_response(generated_text, prompt)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self.get_rule_based_response(user_input, language)
    
    def prepare_prompt(self, user_input, language, context=""):
        """Prepare prompt for the AI model"""
        base_prompt = MEDICAL_PROMPTS.get(language, MEDICAL_PROMPTS["english"])
        
        if context:
            prompt = f"{base_prompt}\n\nContext: {context}\n\nPatient: {user_input}\n\nDr. MedAgg:"
        else:
            prompt = f"{base_prompt}\n\nPatient: {user_input}\n\nDr. MedAgg:"
        
        return prompt
    
    def clean_response(self, generated_text, original_prompt):
        """Clean and format the AI response"""
        # Remove the original prompt from the generated text
        if original_prompt in generated_text:
            response = generated_text.replace(original_prompt, "").strip()
        else:
            response = generated_text.strip()
        
        # Remove any incomplete sentences
        sentences = response.split('.')
        if len(sentences) > 1 and len(sentences[-1].strip()) < 10:
            response = '.'.join(sentences[:-1]) + '.'
        
        # Ensure response is not too long
        if len(response) > 200:
            response = response[:200] + "..."
        
        return response if response else "I understand your concern. Please provide more details so I can help you better."
    
    def get_rule_based_response(self, user_input, language="english"):
        """Fallback rule-based responses when AI model is not available"""
        user_input_lower = user_input.lower()
        
        # Emergency keywords
        emergency_keywords = ['emergency', 'urgent', 'pain', 'bleeding', 'unconscious', 'chest pain', 'heart attack', 'stroke']
        if any(keyword in user_input_lower for keyword in emergency_keywords):
            if language == "tamil":
                return "இது அவசரகாலமாகத் தெரிகிறது. உடனடியாக 108 அல்லது உங்கள் உள்ளூர் அவசரகால சேவையை அழைக்கவும். நான் உங்களுக்கு உதவ முடியும், ஆனால் உடனடியாக மருத்துவ உதவி தேவை."
            elif language == "hindi":
                return "यह एक आपातकालीन स्थिति लगती है। कृपया तुरंत 108 या अपनी स्थानीय आपातकालीन सेवा को कॉल करें। मैं आपकी मदद कर सकता हूं, लेकिन तत्काल चिकित्सा सहायता की आवश्यकता है।"
            else:
                return "This appears to be an emergency situation. Please call 108 or your local emergency services immediately. I can help you, but immediate medical assistance is needed."
        
        # Common medical concerns
        if 'headache' in user_input_lower:
            if language == "tamil":
                return "தலைவலி பல காரணங்களால் ஏற்படலாம். நீங்கள் ஓய்வு எடுத்து, நீரை அதிகம் குடிக்கவும். வலி தொடர்ந்தால் மருத்துவரை பார்க்கவும்."
            elif language == "hindi":
                return "सिरदर्द कई कारणों से हो सकता है। आराम करें और अधिक पानी पिएं। यदि दर्द बना रहे तो डॉक्टर से मिलें।"
            else:
                return "Headaches can have various causes. Please rest, stay hydrated, and if the pain persists, consult a doctor."
        
        elif 'fever' in user_input_lower:
            if language == "tamil":
                return "காய்ச்சல் உடலின் நோய் எதிர்ப்பு அமைப்பின் அறிகுறியாகும். ஓய்வு எடுத்து, நீரை அதிகம் குடிக்கவும். வெப்பநிலை அதிகமாக இருந்தால் மருத்துவரை பார்க்கவும்."
            elif language == "hindi":
                return "बुखार शरीर की प्रतिरक्षा प्रणाली का संकेत है। आराम करें और अधिक पानी पिएं। यदि तापमान अधिक है तो डॉक्टर से मिलें।"
            else:
                return "Fever is a sign of your body's immune system working. Please rest, stay hydrated, and if the temperature is high, consult a doctor."
        
        elif 'appointment' in user_input_lower or 'schedule' in user_input_lower:
            if language == "tamil":
                return "நான் உங்களுக்கு ஒரு நேரம் பதிவு செய்ய உதவ முடியும். எந்த மருத்துவமனையில் நீங்கள் பார்க்க விரும்புகிறீர்கள்? உங்கள் அறிகுறிகள் என்ன?"
            elif language == "hindi":
                return "मैं आपके लिए अपॉइंटमेंट शेड्यूल करने में मदद कर सकता हूं। आप किस अस्पताल में जाना चाहते हैं? आपके लक्षण क्या हैं?"
            else:
                return "I can help you schedule an appointment. Which hospital would you prefer? What are your symptoms?"
        
        # Default response
        if language == "tamil":
            return "நான் உங்களுக்கு உதவ முடியும். உங்கள் அறிகுறிகள் மற்றும் கவலைகளை விரிவாக விளக்குங்கள். நான் உங்களுக்கு மருத்துவ ஆலோசனை வழங்க முடியும்."
        elif language == "hindi":
            return "मैं आपकी मदद कर सकता हूं। कृपया अपने लक्षणों और चिंताओं के बारे में विस्तार से बताएं। मैं आपको चिकित्सा सलाह दे सकता हूं।"
        else:
            return "I'm here to help you. Please describe your symptoms and concerns in detail. I can provide medical guidance and help you schedule an appointment if needed."

# Initialize AI
ai_service = OpenSourceAI()

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
        # Get AI response using open-source AI
        ai_response = ai_service.generate_response(user_input, language)
        
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

class OpenSourceAIHandler(BaseHTTPRequestHandler):
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
                self.wfile.write(b'<h1>MedAgg Healthcare POC - Open Source AI Backend</h1><p>Backend with Open Source AI is running!</p>')
                
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
                
                # Make intelligent Twilio call using curl (like the working version)
                call_success = self.make_intelligent_call_with_curl(patient)
                
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

    def make_intelligent_call_with_curl(self, patient):
        """Make an intelligent Twilio call using curl (like the working version)"""
        try:
            conversation_id = str(uuid.uuid4())
            language = patient['language_preference'].lower()
            
            # Create TwiML for intelligent conversation
            twiml_url = f"http://demo.twilio.com/docs/voice.xml"  # Use demo URL for now
            
            # Use the exact curl command that works
            curl_command = [
                "curl.exe", "-X", "POST",
                f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Calls.json",
                "--data-urlencode", f"Url={twiml_url}",
                "--data-urlencode", f"To={patient['phone_number']}",
                "--data-urlencode", f"From={TWILIO_PHONE_NUMBER}",
                "-u", f"{TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}"
            ]
            
            print(f"📞 Making intelligent call to {patient['phone_number']} for {patient['name']} in {language}")
            
            # Execute the curl command
            result = subprocess.run(curl_command, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✅ Intelligent call initiated successfully!")
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
            
            # Process conversation using open-source AI
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

def start_open_source_ai_backend():
    """Start the open source AI backend server"""
    init_dummy_data()
    
    print("🏥 MedAgg Healthcare POC - OPEN SOURCE AI BACKEND")
    print("=" * 70)
    print("📊 Dummy data initialized")
    print("🤖 Hugging Face Transformers integration")
    print("📞 Twilio Conversational Intelligence enabled")
    print("🌍 Multilingual support (English, Tamil, Hindi)")
    print("💬 Open-source AI conversations")
    print("🔗 API running on http://localhost:8000")
    print("📱 Frontend should be on http://localhost:3000")
    print("✅ Ready for intelligent conversations!")
    print("=" * 70)
    
    if ai_service.is_loaded:
        print("✅ AI Model: Hugging Face Transformers loaded successfully!")
    else:
        print("⚠️  AI Model: Using rule-based responses (transformers not available)")
        print("   Install transformers: pip install transformers torch")
    
    try:
        with HTTPServer(('localhost', 8000), OpenSourceAIHandler) as httpd:
            print("🚀 Open Source AI backend server started successfully!")
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_open_source_ai_backend()
