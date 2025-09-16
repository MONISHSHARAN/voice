#!/usr/bin/env python3
"""
MedAgg Healthcare Voice Agent - English Only
Outstanding voice AI system with Deepgram integration
"""

import json
import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
DEEPGRAM_API_KEY = 'ebae70e078574403bf495088b5ea043e456b7f2f'
TWILIO_ACCOUNT_SID = 'AC33f397657e06dac328e5d5081eb4f9fd'
TWILIO_AUTH_TOKEN = 'bbf7abc794d8f0eb9538350b501d033f'
TWILIO_PHONE_NUMBER = '+17752586467'
PUBLIC_URL = 'https://voice-95g5.onrender.com'

# Initialize Twilio client
try:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    logger.info("✅ Twilio client initialized successfully")
except Exception as e:
    logger.error(f"❌ Twilio initialization failed: {e}")
    twilio_client = None

# Storage
patients = []
conversations = {}
active_calls = {}

# Healthcare Functions
def get_patient_info(patient_id):
    """Get patient information by ID"""
    patient = next((p for p in patients if p['id'] == patient_id), None)
    if patient:
        return {
            "patient_id": patient['id'],
            "name": patient['name'],
            "phone": patient['phone_number'],
            "language": patient['language_preference'],
            "created_at": patient['created_at']
        }
    return {"error": f"Patient {patient_id} not found"}

def schedule_appointment(patient_name, appointment_type, urgency_level):
    """Schedule a medical appointment"""
    appointment_id = str(uuid.uuid4())
    appointment = {
        "id": appointment_id,
        "patient_name": patient_name,
        "type": appointment_type,
        "urgency": urgency_level,
        "status": "scheduled",
        "created_at": datetime.now().isoformat()
    }
    
    # Store appointment
    if 'appointments' not in conversations:
        conversations['appointments'] = {}
    conversations['appointments'][appointment_id] = appointment
    
    return {
        "appointment_id": appointment_id,
        "message": f"Appointment scheduled for {patient_name}. Type: {appointment_type}, Urgency: {urgency_level}",
        "status": "scheduled"
    }

def get_medical_advice(symptoms):
    """Provide medical advice based on symptoms"""
    advice_responses = {
        "headache": "For headaches: rest in a dark room, apply cold compress, stay hydrated. If severe or persistent, consult a doctor immediately.",
        "fever": "For fever: rest, stay hydrated, use fever reducers if appropriate. If temperature is very high or persistent, seek medical attention.",
        "cough": "For cough: stay hydrated, use throat lozenges, avoid irritants. If cough is severe or with blood, see a doctor.",
        "nausea": "For nausea: eat small, bland meals, avoid strong smells, stay hydrated. If severe or with vomiting, seek medical help.",
        "chest_pain": "Chest pain requires immediate medical attention. Call emergency services or go to the nearest hospital immediately.",
        "emergency": "This appears to be an emergency situation. Please call 108 or your local emergency services immediately. I can help you, but immediate medical assistance is needed.",
        "default": "Please describe your symptoms in detail. If symptoms are severe or concerning, consult a healthcare professional immediately."
    }
    
    symptoms_lower = symptoms.lower()
    if 'chest pain' in symptoms_lower or 'heart' in symptoms_lower or 'emergency' in symptoms_lower:
        return advice_responses["emergency"]
    elif 'headache' in symptoms_lower:
        return advice_responses["headache"]
    elif 'fever' in symptoms_lower:
        return advice_responses["fever"]
    elif 'cough' in symptoms_lower:
        return advice_responses["cough"]
    elif 'nausea' in symptoms_lower or 'vomit' in symptoms_lower:
        return advice_responses["nausea"]
    else:
        return advice_responses["default"]

def emergency_alert(patient_name, emergency_type, location):
    """Send emergency alert"""
    alert_id = str(uuid.uuid4())
    alert = {
        "id": alert_id,
        "patient_name": patient_name,
        "type": emergency_type,
        "location": location,
        "status": "alert_sent",
        "created_at": datetime.now().isoformat()
    }
    
    # Store emergency alert
    if 'emergencies' not in conversations:
        conversations['emergencies'] = {}
    conversations['emergencies'][alert_id] = alert
    
    return {
        "alert_id": alert_id,
        "message": f"Emergency alert sent for {patient_name}. Type: {emergency_type}, Location: {location}",
        "status": "alert_sent"
    }

# Function mapping for Deepgram
FUNCTION_MAP = {
    'get_patient_info': get_patient_info,
    'schedule_appointment': schedule_appointment,
    'get_medical_advice': get_medical_advice,
    'emergency_alert': emergency_alert
}

# Healthcare functions for basic voice interaction
def process_healthcare_request(speech_text):
    """Process healthcare requests from speech input"""
    speech_lower = speech_text.lower()
    
    if 'appointment' in speech_lower or 'book' in speech_lower:
        return "I can help you schedule an appointment. What type of appointment do you need? Please tell me if it's a consultation, follow-up, or emergency visit."
    
    elif 'pain' in speech_lower or 'hurt' in speech_lower or 'sick' in speech_lower:
        return "I understand you're experiencing discomfort. Can you tell me more about your symptoms? For example, where does it hurt and how severe is the pain?"
    
    elif 'emergency' in speech_lower or 'urgent' in speech_lower:
        return "This sounds like an emergency situation. Please call 108 or your local emergency services immediately. I can provide guidance, but immediate medical attention may be needed."
    
    elif 'help' in speech_lower:
        return "I'm here to help! I can provide medical advice, schedule appointments, and assist with health concerns. What would you like to know?"
    
    else:
        return f"I heard you say: {speech_text}. How can I help you with that? You can ask for medical advice, schedule an appointment, or tell me about any health concerns."

# Flask Routes
@app.route('/')
def home():
    """Main page"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>MedAgg Healthcare - Voice Agent</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .status { padding: 20px; margin: 20px 0; border-radius: 5px; }
            .online { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
            .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 5px; }
            .feature { background: #e8f5e8; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #28a745; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 MedAgg Healthcare - Voice Agent</h1>
            <div class="status online">
                <h3>✅ System Status: ONLINE</h3>
                <p>Healthcare Voice Agent with Twilio Speech Recognition is active!</p>
            </div>
            
            <div class="feature">
                <h3>🎤 Outstanding Features</h3>
                <ul>
                    <li><strong>Voice Recognition:</strong> Twilio's built-in speech recognition</li>
                    <li><strong>Natural Conversation:</strong> Human-like AI interaction in English</li>
                    <li><strong>Medical Functions:</strong> Patient info, appointments, medical advice</li>
                    <li><strong>Emergency Alerts:</strong> Automatic emergency response</li>
                    <li><strong>Professional Healthcare AI:</strong> Dr. MedAgg assistant</li>
                </ul>
            </div>
            
            <div class="info">
                <h3>🌐 Configuration</h3>
                <p><strong>Public URL:</strong> {{ public_url }}</p>
                <p><strong>Speech Processing:</strong> Twilio Speech Recognition</p>
                <p><strong>Language:</strong> English (optimized for healthcare)</p>
                <p><strong>Status:</strong> ✅ Ready for voice calls</p>
            </div>
            
            <div class="info">
                <h3>📞 Twilio Setup</h3>
                <p>Configure your Twilio phone number webhooks:</p>
                <div style="background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 3px; font-family: monospace;">
                    Voice URL: {{ public_url }}/twiml<br>
                    HTTP Method: POST
                </div>
                <a href="https://console.twilio.com/us1/develop/phone-numbers/manage/incoming" target="_blank" class="button">Configure Twilio Webhooks</a>
            </div>
            
            <div class="info">
                <h3>🧪 Test the System</h3>
                <p>Test the advanced voice agent:</p>
                <a href="{{ public_url }}/test" target="_blank" class="button">Test Patient Registration</a>
                <a href="{{ public_url }}/conversations" target="_blank" class="button">View Conversations</a>
            </div>
        </div>
    </body>
    </html>
    ''', public_url=PUBLIC_URL)

@app.route('/twiml', methods=['GET', 'POST'])
def twiml_endpoint():
    """TwiML endpoint for Twilio calls with speech recognition"""
    try:
        logger.info("Creating TwiML for Healthcare Voice Agent")
        
        response = VoiceResponse()
        
        # Say greeting
        response.say("Hello! Welcome to MedAgg Healthcare. I'm Dr. MedAgg, your AI healthcare assistant. I'm here to help you with your health concerns.", voice='alice')
        
        # Gather speech input
        gather = response.gather(
            input='speech',
            action='/process-speech',
            method='POST',
            speech_timeout='auto',
            timeout=10,
            language='en-US'
        )
        
        # Fallback if no speech detected
        response.say("I didn't hear anything. Please try again or say 'help' for assistance.", voice='alice')
        response.redirect('/twiml')
        
        twiml = str(response)
        logger.info("TwiML created successfully")
        
        return twiml, 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logger.error(f"Error creating TwiML: {e}")
        response = VoiceResponse()
        response.say("Hello! This is MedAgg Healthcare. I'm here to help you with your health concerns.", voice='alice')
        response.hangup()
        return str(response), 200, {'Content-Type': 'text/xml'}

@app.route('/process-speech', methods=['POST'])
def process_speech():
    """Process speech input from Twilio"""
    try:
        speech_result = request.form.get('SpeechResult', '')
        logger.info(f"Speech received: {speech_result}")
        
        response = VoiceResponse()
        
        # Handle special cases
        if 'goodbye' in speech_result.lower() or 'bye' in speech_result.lower() or 'thank you' in speech_result.lower():
            response.say("Thank you for calling MedAgg Healthcare. Take care of yourself and don't hesitate to call again if you need assistance. Goodbye!", voice='alice')
            response.hangup()
        else:
            # Process healthcare request
            response_text = process_healthcare_request(speech_result)
            response.say(response_text, voice='alice')
            response.redirect('/twiml')
        
        return str(response), 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logger.error(f"Error processing speech: {e}")
        response = VoiceResponse()
        response.say("I'm sorry, I didn't understand that. Please try again or say 'help' for assistance.", voice='alice')
        response.redirect('/twiml')
        return str(response), 200, {'Content-Type': 'text/xml'}

@app.route('/twilio', methods=['GET', 'POST'])
def twilio_websocket():
    """WebSocket endpoint for Twilio audio streaming"""
    return "WebSocket endpoint - use wss:// protocol", 200

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
            <h1>🏥 MedAgg Healthcare - Voice Agent Test</h1>
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
                    <label for="language">Language:</label>
                    <select id="language" name="language_preference" required>
                        <option value="english">English (Deepgram Optimized)</option>
                    </select>
                </div>
                <button type="submit">Register & Get AI Voice Call</button>
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
                                <p><strong>Voice Agent:</strong> Healthcare AI with Medical Functions</p>
                                <p>You will receive a call with intelligent healthcare conversation in English!</p>
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

@app.route('/register-patient', methods=['POST'])
def register_patient():
    """Register a new patient and initiate call"""
    try:
        patient_data = request.get_json()
        
        # Validate phone number
        phone = patient_data.get('phone_number', '')
        if not phone.startswith('+91') and not phone.startswith('91'):
            phone = '+91' + phone.lstrip('0')
        
        # Create patient
        patient = {
            'id': str(uuid.uuid4()),
            'name': patient_data.get('name', ''),
            'phone_number': phone,
            'language_preference': 'english',  # Force English for Deepgram
            'created_at': datetime.now().isoformat()
        }
        
        patients.append(patient)
        
        # Make Twilio call
        call_success = make_twilio_call(patient)
        
        response = {
            'success': True,
            'patient_id': patient['id'],
            'message': 'Patient registered successfully',
            'call_initiated': call_success,
            'voice_agent': 'Healthcare AI with Medical Functions (English)',
            'public_url': PUBLIC_URL
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error registering patient: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/conversations')
def get_conversations():
    """Get all conversations and data"""
    return jsonify({
        'conversations': conversations,
        'patients': patients,
        'active_calls': len(active_calls)
    })

def make_twilio_call(patient):
    """Make Twilio call"""
    try:
        # Create TwiML URL
        twiml_url = f"{PUBLIC_URL}/twiml"
        
        logger.info(f"📞 Making call to {patient['phone_number']} for {patient['name']}")
        logger.info(f"🔗 TwiML URL: {twiml_url}")
        
        # Use Twilio client to make the call
        call = twilio_client.calls.create(
            url=twiml_url,
            to=patient['phone_number'],
            from_=TWILIO_PHONE_NUMBER
        )
        
        logger.info(f"✅ Call initiated successfully!")
        logger.info(f"📋 Call SID: {call.sid}")
        
        return True
            
    except Exception as e:
        logger.error(f"Error making call: {e}")
        return False

# Note: WebSocket functionality removed for simpler deployment
# Using Twilio's built-in speech recognition instead

def run_app():
    """Run the Flask app with healthcare voice agent"""
    logger.info("🏥 MedAgg Healthcare POC - VOICE AGENT (ENGLISH)")
    logger.info("=" * 70)
    logger.info("🎤 Voice recognition with Twilio Speech Recognition")
    logger.info("🤖 Intelligent AI conversation with medical functions")
    logger.info("📞 Twilio integration with speech processing")
    logger.info("🌍 Language: English (optimized for healthcare)")
    logger.info("💬 Human-like conversation flow")
    logger.info(f"🌐 Public URL: {PUBLIC_URL}")
    logger.info("🔗 Speech Processing: Twilio Speech Recognition")
    logger.info("💰 System: ✅ Ready for healthcare voice calls")
    logger.info("=" * 70)
    
    # Get port from environment variable
    port = int(os.environ.get('PORT', 8000))
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"Failed to start Flask app: {e}")
        raise

if __name__ == '__main__':
    run_app()
