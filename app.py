#!/usr/bin/env python3
"""
MedAgg Healthcare POC - Heroku Deployment
Production-ready backend for Heroku deployment
"""

import json
import uuid
import datetime
import urllib.parse
import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Twilio Configuration
TWILIO_ACCOUNT_SID = "AC33f397657e06dac328e5d5081eb4f9fd"
TWILIO_AUTH_TOKEN = "bbf7abc794d8f0eb9538350b501d033f"
TWILIO_PHONE_NUMBER = "+17752586467"

# Get public URL from Heroku
PUBLIC_URL = os.getenv('HEROKU_APP_NAME', 'medagg-healthcare')
if not PUBLIC_URL.startswith('http'):
    PUBLIC_URL = f"https://{PUBLIC_URL}.herokuapp.com"

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
            action=f'{PUBLIC_URL}/process-speech?conversation_id={conversation_id}&language={language}',
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

class HerokuAIHandler(BaseHTTPRequestHandler):
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
                html_content = f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>MedAgg Healthcare POC - Production</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                        .status {{ padding: 20px; margin: 20px 0; border-radius: 5px; }}
                        .online {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                        .info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
                        .endpoint {{ background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 3px; font-family: monospace; }}
                        .button {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 5px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🏥 MedAgg Healthcare POC - Production Backend</h1>
                        <div class="status online">
                            <h3>✅ System Status: ONLINE</h3>
                            <p>Conversational AI backend is running successfully on Heroku!</p>
                        </div>
                        <div class="info">
                            <h3>🌐 Public URL Information</h3>
                            <p><strong>Public URL:</strong> {PUBLIC_URL}</p>
                            <p><strong>Webhook URL:</strong> {PUBLIC_URL}/twiml</p>
                        </div>
                        <div class="info">
                            <h3>📞 Twilio Configuration</h3>
                            <p>Configure your Twilio phone number webhooks:</p>
                            <div class="endpoint">Voice URL: {PUBLIC_URL}/twiml</div>
                            <div class="endpoint">HTTP Method: POST</div>
                            <a href="https://console.twilio.com/us1/develop/phone-numbers/manage/incoming" target="_blank" class="button">Configure Twilio Webhooks</a>
                        </div>
                        <div class="info">
                            <h3>🔗 API Endpoints</h3>
                            <div class="endpoint">GET {PUBLIC_URL}/ai/status - AI Status</div>
                            <div class="endpoint">GET {PUBLIC_URL}/patients - Patient List</div>
                            <div class="endpoint">GET {PUBLIC_URL}/hospitals - Hospital List</div>
                            <div class="endpoint">POST {PUBLIC_URL}/register-patient - Register Patient</div>
                        </div>
                        <div class="info">
                            <h3>🧪 Test the System</h3>
                            <p>Test the conversational AI by registering a patient:</p>
                            <a href="{PUBLIC_URL}/test" target="_blank" class="button">Test Patient Registration</a>
                        </div>
                    </div>
                </body>
                </html>
                '''
                self.wfile.write(html_content.encode())
                
            elif self.path == '/test':
                # Test page for patient registration
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                test_html = f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>MedAgg Healthcare - Test Page</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                        .form-group {{ margin: 15px 0; }}
                        label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                        input, select {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                        button {{ background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
                        .result {{ margin-top: 20px; padding: 15px; border-radius: 5px; }}
                        .success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                        .error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🏥 MedAgg Healthcare - Test Patient Registration</h1>
                        <form id="patientForm">
                            <div class="form-group">
                                <label for="name">Full Name:</label>
                                <input type="text" id="name" name="name" required>
                            </div>
                            <div class="form-group">
                                <label for="phone">Phone Number (Indian):</label>
                                <input type="tel" id="phone" name="phone_number" pattern="^(\+91|91)?[6-9]\d{{9}}$" required>
                                <small>Format: +91XXXXXXXXXX or 91XXXXXXXXXX</small>
                            </div>
                            <div class="form-group">
                                <label for="email">Email:</label>
                                <input type="email" id="email" name="email" required>
                            </div>
                            <div class="form-group">
                                <label for="age">Age:</label>
                                <input type="number" id="age" name="age" min="1" max="120" required>
                            </div>
                            <div class="form-group">
                                <label for="location">Location:</label>
                                <input type="text" id="location" name="location" required>
                            </div>
                            <div class="form-group">
                                <label for="language">Language Preference:</label>
                                <select id="language" name="language_preference" required>
                                    <option value="English">English</option>
                                    <option value="Tamil">தமிழ் (Tamil)</option>
                                    <option value="Hindi">हिन्दी (Hindi)</option>
                                </select>
                            </div>
                            <button type="submit">Register & Get AI Call</button>
                        </form>
                        <div id="result"></div>
                    </div>
                    <script>
                        document.getElementById('patientForm').addEventListener('submit', async function(e) {{
                            e.preventDefault();
                            
                            const formData = new FormData(this);
                            const data = Object.fromEntries(formData);
                            
                            try {{
                                const response = await fetch('{PUBLIC_URL}/register-patient', {{
                                    method: 'POST',
                                    headers: {{
                                        'Content-Type': 'application/json',
                                    }},
                                    body: JSON.stringify(data)
                                }});
                                
                                const result = await response.json();
                                
                                if (result.success) {{
                                    document.getElementById('result').innerHTML = `
                                        <div class="result success">
                                            <h3>✅ Registration Successful!</h3>
                                            <p><strong>Patient ID:</strong> ${{result.patient_id}}</p>
                                            <p><strong>Call Status:</strong> ${{result.call_initiated ? 'Initiated' : 'Failed'}}</p>
                                            <p><strong>Webhook URL:</strong> ${{result.webhook_url}}</p>
                                            <p>You should receive a call shortly with AI conversation!</p>
                                        </div>
                                    `;
                                }} else {{
                                    document.getElementById('result').innerHTML = `
                                        <div class="result error">
                                            <h3>❌ Registration Failed</h3>
                                            <p>${{result.error}}</p>
                                        </div>
                                    `;
                                }}
                            }} catch (error) {{
                                document.getElementById('result').innerHTML = `
                                    <div class="result error">
                                        <h3>❌ Error</h3>
                                        <p>${{error.message}}</p>
                                    </div>
                                `;
                            }}
                        }});
                    </script>
                </body>
                </html>
                '''
                self.wfile.write(test_html.encode())
                
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
                    "conversations": len(conversations),
                    "public_url": PUBLIC_URL,
                    "webhook_url": f"{PUBLIC_URL}/twiml"
                }
                self.wfile.write(json.dumps(status).encode())
                
            elif self.path == '/twiml':
                # TwiML endpoint for Twilio calls
                self.handle_twiml_request()
                
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
                
                # Make Twilio call using the public URL
                call_success = self.make_twilio_call_with_public_url(patient)
                
                response = {
                    'success': True,
                    'patient_id': patient['id'],
                    'message': 'Patient registered successfully',
                    'call_initiated': call_success,
                    'public_url': PUBLIC_URL,
                    'webhook_url': f"{PUBLIC_URL}/twiml"
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
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

    def make_twilio_call_with_public_url(self, patient):
        """Make Twilio call using public URL"""
        try:
            conversation_id = str(uuid.uuid4())
            language = patient['language_preference'].lower()
            
            # Create TwiML URL using public URL
            twiml_url = f"{PUBLIC_URL}/twiml?conversation_id={conversation_id}&language={language}"
            
            print(f"📞 Making AI call to {patient['phone_number']} for {patient['name']} in {language}")
            print(f"🔗 TwiML URL: {twiml_url}")
            
            # Use Twilio client to make the call
            call = twilio_client.calls.create(
                url=twiml_url,
                to=patient['phone_number'],
                from_=TWILIO_PHONE_NUMBER
            )
            
            print(f"✅ AI call initiated successfully!")
            print(f"📋 Call SID: {call.sid}")
            
            # Store conversation info
            conversations[conversation_id] = {
                'patient': patient,
                'language': language,
                'status': 'initiated',
                'call_sid': call.sid,
                'messages': []
            }
            
            return True
                
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
                action=f'{PUBLIC_URL}/process-speech?conversation_id={conversation_id}&language={language}',
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

def start_heroku_backend():
    """Start the Heroku backend server"""
    init_dummy_data()
    
    print("🏥 MedAgg Healthcare POC - HEROKU DEPLOYMENT")
    print("=" * 70)
    print("📊 Dummy data initialized")
    print("🤖 Conversational AI enabled")
    print("📞 Twilio integration with public webhooks")
    print("🌍 Multilingual support (English, Tamil, Hindi)")
    print("💬 Real-time AI conversations")
    print(f"🌐 Public URL: {PUBLIC_URL}")
    print(f"📞 Webhook URL: {PUBLIC_URL}/twiml")
    print("=" * 70)
    
    try:
        port = int(os.getenv('PORT', 8000))
        with HTTPServer(('0.0.0.0', port), HerokuAIHandler) as httpd:
            print(f"🚀 Heroku backend server started on port {port}!")
            print("Press Ctrl+C to stop the server")
            httpd.serve_forever()
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        print("✅ Server stopped successfully!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_heroku_backend()
