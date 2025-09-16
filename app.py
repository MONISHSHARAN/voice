#!/usr/bin/env python3
"""
MedAgg Healthcare POC - Render Deployment
Production-ready Flask app for Render deployment
"""

import json
import uuid
import datetime
import urllib.parse
import os
import logging
from flask import Flask, request, jsonify, render_template_string
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'AC33f397657e06dac328e5d5081eb4f9fd')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'bbf7abc794d8f0eb9538350b501d033f')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '+17752586467')

# Get public URL from Render
PUBLIC_URL = os.getenv('RENDER_EXTERNAL_URL', 'https://voice-95g5.onrender.com')

# Initialize Twilio client
try:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    logger.info("✅ Twilio client initialized successfully")
except Exception as e:
    logger.error(f"❌ Twilio initialization failed: {e}")
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

# Flask Routes
@app.route('/')
def home():
    """Main page"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>MedAgg Healthcare POC - Production</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .status { padding: 20px; margin: 20px 0; border-radius: 5px; }
            .online { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
            .endpoint { background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 3px; font-family: monospace; }
            .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 MedAgg Healthcare POC - Production Backend</h1>
            <div class="status online">
                <h3>✅ System Status: ONLINE</h3>
                <p>Conversational AI backend is running successfully on Render!</p>
            </div>
            <div class="info">
                <h3>🌐 Public URL Information</h3>
                <p><strong>Public URL:</strong> {{ public_url }}</p>
                <p><strong>Webhook URL:</strong> {{ public_url }}/twiml</p>
            </div>
            <div class="info">
                <h3>📞 Twilio Configuration</h3>
                <p>Configure your Twilio phone number webhooks:</p>
                <div class="endpoint">Voice URL: {{ public_url }}/twiml</div>
                <div class="endpoint">HTTP Method: POST</div>
                <a href="https://console.twilio.com/us1/develop/phone-numbers/manage/incoming" target="_blank" class="button">Configure Twilio Webhooks</a>
            </div>
            <div class="info">
                <h3>🔗 API Endpoints</h3>
                <div class="endpoint">GET {{ public_url }}/ai/status - AI Status</div>
                <div class="endpoint">GET {{ public_url }}/patients - Patient List</div>
                <div class="endpoint">GET {{ public_url }}/hospitals - Hospital List</div>
                <div class="endpoint">POST {{ public_url }}/register-patient - Register Patient</div>
            </div>
            <div class="info">
                <h3>🧪 Test the System</h3>
                <p>Test the conversational AI by registering a patient:</p>
                <a href="{{ public_url }}/test" target="_blank" class="button">Test Patient Registration</a>
            </div>
        </div>
    </body>
    </html>
    ''', public_url=PUBLIC_URL)

@app.route('/test')
def test_page():
    """Test page for patient registration"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>MedAgg Healthcare - Test Page</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            .result { margin-top: 20px; padding: 15px; border-radius: 5px; }
            .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
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
                    <input type="tel" id="phone" name="phone_number" pattern="^(\+91|91)?[6-9]\d{9}$" required>
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
            document.getElementById('patientForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const data = Object.fromEntries(formData);
                
                try {
                    const response = await fetch('{{ public_url }}/register-patient', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        document.getElementById('result').innerHTML = `
                            <div class="result success">
                                <h3>✅ Registration Successful!</h3>
                                <p><strong>Patient ID:</strong> ${result.patient_id}</p>
                                <p><strong>Call Status:</strong> ${result.call_initiated ? 'Initiated' : 'Failed'}</p>
                                <p><strong>Webhook URL:</strong> ${result.webhook_url}</p>
                                <p>You should receive a call shortly with AI conversation!</p>
                            </div>
                        `;
                    } else {
                        document.getElementById('result').innerHTML = `
                            <div class="result error">
                                <h3>❌ Registration Failed</h3>
                                <p>${result.error}</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result error">
                            <h3>❌ Error</h3>
                            <p>${error.message}</p>
                        </div>
                    `;
                }
            });
        </script>
    </body>
    </html>
    ''', public_url=PUBLIC_URL)

@app.route('/hospitals')
def get_hospitals():
    """Get list of hospitals"""
    return jsonify(hospitals)

@app.route('/patients')
def get_patients():
    """Get list of patients"""
    return jsonify(patients)

@app.route('/conversations')
def get_conversations():
    """Get list of conversations"""
    return jsonify(conversations)

@app.route('/ai/status')
def ai_status():
    """AI status endpoint for frontend"""
    status = {
        "status": "ready",
        "model": "rule-based",
        "languages": ["english", "tamil", "hindi"],
        "conversations": len(conversations),
        "public_url": PUBLIC_URL,
        "webhook_url": f"{PUBLIC_URL}/twiml"
    }
    return jsonify(status)

@app.route('/twiml')
def twiml_endpoint():
    """TwiML endpoint for Twilio calls"""
    try:
        # Parse query parameters
        conversation_id = request.args.get('conversation_id')
        language = request.args.get('language', 'english')
        
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Create conversational TwiML
        twiml = create_conversational_twiml(conversation_id, language)
        
        return twiml, 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logger.error(f"Error handling TwiML request: {e}")
        response = VoiceResponse()
        response.say("Sorry, there was an error processing your request.")
        response.hangup()
        return str(response), 200, {'Content-Type': 'text/xml'}

@app.route('/register-patient', methods=['POST'])
def register_patient():
    """Register a new patient"""
    try:
        patient_data = request.get_json()
        
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
        call_success = make_twilio_call_with_public_url(patient)
        
        response = {
            'success': True,
            'patient_id': patient['id'],
            'message': 'Patient registered successfully',
            'call_initiated': call_success,
            'public_url': PUBLIC_URL,
            'webhook_url': f"{PUBLIC_URL}/twiml"
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error registering patient: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/process-speech', methods=['POST'])
def process_speech():
    """Process speech input from Twilio"""
    try:
        conversation_id = request.form.get('conversation_id')
        language = request.form.get('language', 'english')
        user_input = request.form.get('SpeechResult', '')
        
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
        
        return str(response), 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logger.error(f"Error handling speech processing: {e}")
        response = VoiceResponse()
        response.say("Thank you for calling MedAgg Healthcare.")
        response.hangup()
        return str(response), 200, {'Content-Type': 'text/xml'}

def make_twilio_call_with_public_url(patient):
    """Make Twilio call using public URL"""
    try:
        conversation_id = str(uuid.uuid4())
        language = patient['language_preference'].lower()
        
        # Create TwiML URL using public URL
        twiml_url = f"{PUBLIC_URL}/twiml?conversation_id={conversation_id}&language={language}"
        
        logger.info(f"📞 Making AI call to {patient['phone_number']} for {patient['name']} in {language}")
        logger.info(f"🔗 TwiML URL: {twiml_url}")
        
        # Use Twilio client to make the call
        call = twilio_client.calls.create(
            url=twiml_url,
            to=patient['phone_number'],
            from_=TWILIO_PHONE_NUMBER
        )
        
        logger.info(f"✅ AI call initiated successfully!")
        logger.info(f"📋 Call SID: {call.sid}")
        
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

if __name__ == '__main__':
    # Initialize dummy data
    init_dummy_data()
    
    logger.info("🏥 MedAgg Healthcare POC - RENDER DEPLOYMENT")
    logger.info("=" * 70)
    logger.info("📊 Dummy data initialized")
    logger.info("🤖 Conversational AI enabled")
    logger.info("📞 Twilio integration with public webhooks")
    logger.info("🌍 Multilingual support (English, Tamil, Hindi)")
    logger.info("💬 Real-time AI conversations")
    logger.info(f"🌐 Public URL: {PUBLIC_URL}")
    logger.info(f"📞 Webhook URL: {PUBLIC_URL}/twiml")
    logger.info("=" * 70)
    
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)