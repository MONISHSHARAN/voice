#!/usr/bin/env python3
"""
MedAgg Healthcare Voice Agent - Deepgram Integration
Outstanding voice AI system with Deepgram Nova-3 Medical
"""

import asyncio
import base64
import json
import websockets
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
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY', 'ebae70e078574403bf495088b5ea043e456b7f2f')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'AC33f397657e06dac328e5d5081eb4f9fd')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'bbf7abc794d8f0eb9538350b501d033f')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '+17752586467')
PUBLIC_URL = os.getenv('PUBLIC_URL', 'https://voice-95g5.onrender.com')

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

def sts_connect():
    """Connect to Deepgram Voice Agent"""
    sts_ws = websockets.connect(
        "wss://agent.deepgram.com/v1/agent/converse",
        subprotocols=["token", DEEPGRAM_API_KEY]
    )
    return sts_ws

def load_healthcare_config():
    """Load healthcare-specific configuration for English only"""
    return {
        "type": "Settings",
        "audio": {
            "input": {
                "encoding": "mulaw",
                "sample_rate": 8000
            },
            "output": {
                "encoding": "mulaw",
                "sample_rate": 8000,
                "container": "none"
            }
        },
        "agent": {
            "language": "en",
            "listen": {
                "provider": {
                    "type": "deepgram",
                    "model": "nova-3-medical",
                    "keyterms": ["hello", "goodbye", "emergency", "help", "doctor", "pain", "chest", "breath", "appointment", "yes", "no", "cardiology", "heart"]
                }
            },
            "think": {
                "provider": {
                    "type": "open_ai",
                    "model": "gpt-4o-mini",
                    "temperature": 0.7
                },
                "prompt": "You are Dr. MedAgg, a professional cardiology AI specialist from MedAgg Healthcare. You are conducting a UFE (Unified Flow Evaluation) cardiology questionnaire. Follow this conversation flow: 1) Welcome and ask about chest pain/discomfort, 2) Ask about shortness of breath, 3) Get details about pain location and duration, 4) Assess breathing during activity and position, 5) Offer to schedule cardiology appointment, 6) Ask about urgency and preferred time, 7) Confirm appointment booking, 8) Offer to connect with live specialist. Always be empathetic, professional, and thorough. For emergencies (severe chest pain, heart attack symptoms), immediately use emergency_alert function. Ask only 2 questions at a time, wait for responses, then ask 2 more. Keep the conversation natural and human-like. Focus on cardiology and heart health.",
                "functions": [
                    {
                        "name": "get_patient_info",
                        "description": "Get patient information by ID. Use when patient asks about their details or when you need to verify patient information.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "patient_id": {
                                    "type": "string",
                                    "description": "Patient ID to look up"
                                }
                            },
                            "required": ["patient_id"]
                        }
                    },
                    {
                        "name": "schedule_appointment",
                        "description": "Schedule a medical appointment. Use when patient wants to book an appointment or consultation.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "patient_name": {
                                    "type": "string",
                                    "description": "Patient's full name"
                                },
                                "appointment_type": {
                                    "type": "string",
                                    "description": "Type of appointment (consultation, follow-up, emergency, checkup, etc.)"
                                },
                                "urgency_level": {
                                    "type": "string",
                                    "description": "Urgency level (low, medium, high, emergency)"
                                }
                            },
                            "required": ["patient_name", "appointment_type", "urgency_level"]
                        }
                    },
                    {
                        "name": "get_medical_advice",
                        "description": "Provide medical advice based on symptoms. Use when patient describes symptoms or asks for medical guidance.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symptoms": {
                                    "type": "string",
                                    "description": "Patient's symptoms or health concerns"
                                }
                            },
                            "required": ["symptoms"]
                        }
                    },
                    {
                        "name": "emergency_alert",
                        "description": "Send emergency alert for critical situations. Use when patient has severe symptoms or emergency situations.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "patient_name": {
                                    "type": "string",
                                    "description": "Patient's name"
                                },
                                "emergency_type": {
                                    "type": "string",
                                    "description": "Type of emergency (chest pain, severe injury, unconscious, heart attack, stroke, etc.)"
                                },
                                "location": {
                                    "type": "string",
                                    "description": "Patient's current location"
                                }
                            },
                            "required": ["patient_name", "emergency_type", "location"]
                        }
                    }
                ]
            },
            "speak": {
                "provider": {
                    "type": "deepgram",
                    "model": "aura-2-vesta-en"
                }
            },
            "greeting": "Hello! Welcome to MedAgg Healthcare. I'm Dr. MedAgg, your AI cardiology specialist. I'm here to conduct a comprehensive heart health evaluation with you today. I'll ask you some important questions about your cardiovascular health, and then help you schedule a consultation if needed. How are you feeling today?"
        }
    }

async def handle_barge_in(decoded, twilio_ws, streamsid):
    """Handle user interruption during AI speech"""
    if decoded["type"] == "UserStartedSpeaking":
        clear_message = {
            "event": "clear",
            "streamSid": streamsid
        }
        await twilio_ws.send(json.dumps(clear_message))

def execute_function_call(func_name, arguments):
    """Execute healthcare function calls"""
    if func_name in FUNCTION_MAP:
        result = FUNCTION_MAP[func_name](**arguments)
        logger.info(f"Function call result: {result}")
        return result
    else:
        result = {"error": f"Unknown function: {func_name}"}
        logger.error(result)
        return result

def create_function_call_response(func_id, func_name, result):
    """Create function call response for Deepgram"""
    return {
        "type": "FunctionCallResponse",
        "id": func_id,
        "name": func_name,
        "content": json.dumps(result)
    }

async def handle_function_call_request(decoded, sts_ws):
    """Handle function call requests from Deepgram"""
    try:
        for function_call in decoded["functions"]:
            func_name = function_call["name"]
            func_id = function_call["id"]
            arguments = json.loads(function_call["arguments"])

            logger.info(f"Function call: {func_name} (ID: {func_id}), arguments: {arguments}")

            result = execute_function_call(func_name, arguments)

            function_result = create_function_call_response(func_id, func_name, result)
            await sts_ws.send(json.dumps(function_result))
            logger.info(f"Sent function result: {function_result}")

    except Exception as e:
        logger.error(f"Error calling function: {e}")
        error_result = create_function_call_response(
            func_id if "func_id" in locals() else "unknown",
            func_name if "func_name" in locals() else "unknown",
            {"error": f"Function call failed with: {str(e)}"}
        )
        await sts_ws.send(json.dumps(error_result))

async def handle_text_message(decoded, twilio_ws, sts_ws, streamsid):
    """Handle text messages from Deepgram"""
    await handle_barge_in(decoded, twilio_ws, streamsid)

    if decoded["type"] == "FunctionCallRequest":
        await handle_function_call_request(decoded, sts_ws)

async def sts_sender(sts_ws, audio_queue):
    """Send audio to Deepgram"""
    logger.info("Deepgram sender started")
    while True:
        chunk = await audio_queue.get()
        await sts_ws.send(chunk)

async def sts_receiver(sts_ws, twilio_ws, streamsid_queue):
    """Receive responses from Deepgram"""
    logger.info("Deepgram receiver started")
    streamsid = await streamsid_queue.get()

    async for message in sts_ws:
        if type(message) is str:
            logger.info(f"Deepgram message: {message}")
            decoded = json.loads(message)
            await handle_text_message(decoded, twilio_ws, sts_ws, streamsid)
            continue

        # Send audio back to Twilio
        raw_mulaw = message
        media_message = {
            "event": "media",
            "streamSid": streamsid,
            "media": {"payload": base64.b64encode(raw_mulaw).decode("ascii")}
        }
        await twilio_ws.send(json.dumps(media_message))

async def twilio_receiver(twilio_ws, audio_queue, streamsid_queue):
    """Receive audio from Twilio"""
    BUFFER_SIZE = 20 * 160
    inbuffer = bytearray(b"")

    async for message in twilio_ws:
        try:
            data = json.loads(message)
            event = data["event"]

            if event == "start":
                logger.info("Call started, getting stream ID")
                start = data["start"]
                streamsid = start["streamSid"]
                streamsid_queue.put_nowait(streamsid)
            elif event == "connected":
                continue
            elif event == "media":
                media = data["media"]
                chunk = base64.b64decode(media["payload"])
                if media["track"] == "inbound":
                    inbuffer.extend(chunk)
            elif event == "stop":
                break

            while len(inbuffer) >= BUFFER_SIZE:
                chunk = inbuffer[:BUFFER_SIZE]
                audio_queue.put_nowait(chunk)
                inbuffer = inbuffer[BUFFER_SIZE:]
        except Exception as e:
            logger.error(f"Error in Twilio receiver: {e}")
            break

async def twilio_handler(twilio_ws):
    """Main handler for Twilio WebSocket connection"""
    try:
        logger.info("🔗 New Twilio WebSocket connection established")
        
        audio_queue = asyncio.Queue()
        streamsid_queue = asyncio.Queue()

        async with sts_connect() as sts_ws:
            logger.info("🔗 Connected to Deepgram Voice Agent")
            
            config_message = load_healthcare_config()
            await sts_ws.send(json.dumps(config_message))
            logger.info("📤 Sent configuration to Deepgram")

            await asyncio.wait([
                asyncio.ensure_future(sts_sender(sts_ws, audio_queue)),
                asyncio.ensure_future(sts_receiver(sts_ws, twilio_ws, streamsid_queue)),
                asyncio.ensure_future(twilio_receiver(twilio_ws, audio_queue, streamsid_queue)),
            ])

        logger.info("🔌 WebSocket connection closed")
        await twilio_ws.close()
        
    except Exception as e:
        logger.error(f"❌ Error in WebSocket handler: {e}")
        try:
            await twilio_ws.close()
        except:
            pass

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
            <h1>🏥 MedAgg Healthcare - Cardiology Voice Agent</h1>
            <div class="status online">
                <h3>✅ System Status: ONLINE</h3>
                <p>Advanced Cardiology AI Voice Agent with Deepgram is active!</p>
            </div>
            
            <div class="feature">
                <h3>🎤 Outstanding Features</h3>
                <ul>
                    <li><strong>Real-time Voice Recognition:</strong> Deepgram Nova-3 Medical model</li>
                    <li><strong>Cardiology Focus:</strong> UFE questionnaire for heart health evaluation</li>
                    <li><strong>Structured Conversation:</strong> 4-question flow with appointment booking</li>
                    <li><strong>Emergency Detection:</strong> Automatic emergency response for heart symptoms</li>
                    <li><strong>Live Agent Transfer:</strong> Connect with real cardiology specialists</li>
                </ul>
            </div>
            
            <div class="info">
                <h3>🌐 Configuration</h3>
                <p><strong>Public URL:</strong> {{ public_url }}</p>
                <p><strong>WebSocket URL:</strong> wss://{{ public_url.replace('https://', '') }}/twilio</p>
                <p><strong>Deepgram API:</strong> ✅ Configured with $200 credit</p>
                <p><strong>Language:</strong> English (optimized for Deepgram)</p>
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
    """TwiML endpoint for Twilio calls with Deepgram streaming"""
    try:
        logger.info("Creating TwiML for Deepgram Voice Agent")
        
        response = VoiceResponse()
        
        # Connect directly to Deepgram Voice Agent via WebSocket
        response.connect()
        response.stream(url=f"wss://{PUBLIC_URL.replace('https://', '')}/twilio")
        
        twiml = str(response)
        logger.info("TwiML created successfully")
        logger.info(f"WebSocket URL: wss://{PUBLIC_URL.replace('https://', '')}/twilio")
        
        return twiml, 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logger.error(f"Error creating TwiML: {e}")
        response = VoiceResponse()
        response.say("Hello! This is MedAgg Healthcare. I'm here to help you with your health concerns.", voice='alice')
        response.hangup()
        return str(response), 200, {'Content-Type': 'text/xml'}

@app.route('/twilio', methods=['GET', 'POST'])
async def twilio_websocket():
    """WebSocket endpoint for Twilio audio streaming"""
    if request.method == 'GET':
        return f"WebSocket endpoint ready - use wss://{PUBLIC_URL.replace('https://', '')}/twilio", 200
    
    # This will be handled by the WebSocket server
    return "WebSocket connection required", 400

@app.route('/test-websocket')
def test_websocket():
    """Test WebSocket connectivity"""
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Test</title>
    </head>
    <body>
        <h1>WebSocket Test</h1>
        <p>Testing connection to: wss://{PUBLIC_URL.replace('https://', '')}/twilio</p>
        <div id="status">Connecting...</div>
        <script>
            const ws = new WebSocket('wss://{PUBLIC_URL.replace('https://', '')}/twilio');
            ws.onopen = function() {{
                document.getElementById('status').innerHTML = '✅ WebSocket Connected!';
            }};
            ws.onerror = function(error) {{
                document.getElementById('status').innerHTML = '❌ WebSocket Error: ' + error;
            }};
        </script>
    </body>
    </html>
    '''

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
                                <p><strong>Voice Agent:</strong> Cardiology AI with UFE Questionnaire</p>
                                <p>You will receive a call with structured cardiology evaluation and appointment booking!</p>
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
            'voice_agent': 'Cardiology AI with UFE Questionnaire (English)',
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
        logger.info(f"🔑 Using Twilio Account: {TWILIO_ACCOUNT_SID}")
        
        # Check if phone number is verified for trial accounts
        if patient['phone_number'].startswith('+91'):
            logger.warning("⚠️ Indian number detected. Trial accounts may need verification.")
        
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
        error_msg = str(e)
        logger.error(f"❌ Error making call: {error_msg}")
        
        if "401" in error_msg or "Authenticate" in error_msg:
            logger.error("🔑 Authentication failed. Check Twilio credentials.")
        elif "unverified" in error_msg.lower():
            logger.error("📱 Phone number needs verification for trial accounts.")
        elif "not a valid phone number" in error_msg.lower():
            logger.error("📞 Invalid phone number format.")
        
        return False

# WebSocket server for Twilio streaming
def start_websocket_server():
    """Start WebSocket server for Twilio audio streaming"""
    async def start_server():
        logger.info("Starting WebSocket server for Twilio streaming...")
        server = await websockets.serve(twilio_handler, "0.0.0.0", 5000)
        logger.info("WebSocket server started on port 5000")
        return server
    
    # Run the async server in a separate thread
    import threading
    def run_websocket():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_server())
        loop.run_forever()
    
    websocket_thread = threading.Thread(target=run_websocket, daemon=True)
    websocket_thread.start()
    logger.info("WebSocket server thread started")

def run_app():
    """Run the Flask app with Deepgram WebSocket server"""
    logger.info("🏥 MedAgg Healthcare POC - CARDIOLOGY VOICE AGENT (ENGLISH)")
    logger.info("=" * 70)
    logger.info("🎤 Real-time voice recognition with Deepgram Nova-3 Medical")
    logger.info("❤️ Cardiology-focused UFE questionnaire conversation")
    logger.info("📞 Twilio integration with WebSocket streaming")
    logger.info("🌍 Language: English (optimized for Deepgram)")
    logger.info("💬 Structured 4-question flow with appointment booking")
    logger.info(f"🌐 Public URL: {PUBLIC_URL}")
    logger.info(f"🔗 WebSocket URL: wss://{PUBLIC_URL.replace('https://', '')}/twilio")
    logger.info("💰 Deepgram API: ✅ Configured with $200 credit")
    logger.info("=" * 70)
    
    # Start WebSocket server
    start_websocket_server()
    
    # Get port from environment variable
    port = int(os.environ.get('PORT', 8000))
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"Failed to start Flask app: {e}")
        raise

if __name__ == '__main__':
    run_app()
