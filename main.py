#!/usr/bin/env python3
"""
MedAgg Healthcare Voice Agent - Live Call Implementation
Based on working DeepgramVoiceAgent model with cardiology focus
"""

import asyncio
import base64
import json
import websockets
import os
import uuid
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Start, Stream
from dotenv import load_dotenv
from cardiology_functions import FUNCTION_MAP

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'medagg-secret-key'

# Configuration
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "ebae70e078574403bf495088b5ea043e456b7f2f")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "AC33f397657e06dac328e5d5081eb4f9fd")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "bbf7abc794d8f0eb9538350b501d033f")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+17752586467")
PUBLIC_URL = os.getenv("PUBLIC_URL", "https://voice-95g5.onrender.com")

# Initialize Twilio client
try:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    logger.info("✅ Twilio client initialized successfully")
except Exception as e:
    logger.error(f"❌ Twilio initialization failed: {e}")
    twilio_client = None

# Storage
patients = []
appointments = {}
active_calls = {}

def sts_connect():
    """Connect to Deepgram Agent API"""
    if not DEEPGRAM_API_KEY:
        raise Exception("DEEPGRAM_API_KEY not found")

    sts_ws = websockets.connect(
        "wss://agent.deepgram.com/v1/agent/converse",
        subprotocols=["token", DEEPGRAM_API_KEY]
    )
    return sts_ws

def load_config():
    """Load Deepgram Agent configuration for cardiology"""
    with open("config.json", "r") as f:
        return json.load(f)

async def handle_barge_in(decoded, twilio_ws, streamsid):
    """Handle user speaking interruption"""
    if decoded["type"] == "UserStartedSpeaking":
        clear_message = {
            "event": "clear",
            "streamSid": streamsid
        }
        await twilio_ws.send(json.dumps(clear_message))

def execute_function_call(func_name, arguments):
    """Execute function call"""
    if func_name in FUNCTION_MAP:
        result = FUNCTION_MAP[func_name](**arguments)
        logger.info(f"Function call result: {result}")
        return result
    else:
        result = {"error": f"Unknown function: {func_name}"}
        logger.error(result)
        return result

def create_function_call_response(func_id, func_name, result):
    """Create function call response"""
    return {
        "type": "FunctionCallResponse",
        "id": func_id,
        "name": func_name,
        "content": json.dumps(result)
    }

async def handle_function_call_request(decoded, sts_ws):
    """Handle function call requests from Deepgram Agent"""
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
    """Handle text messages from Deepgram Agent"""
    await handle_barge_in(decoded, twilio_ws, streamsid)

    if decoded["type"] == "FunctionCallRequest":
        await handle_function_call_request(decoded, sts_ws)

async def sts_sender(sts_ws, audio_queue):
    """Send audio to Deepgram Agent"""
    logger.info("sts_sender started")
    while True:
        chunk = await audio_queue.get()
        await sts_ws.send(chunk)

async def sts_receiver(sts_ws, twilio_ws, streamsid_queue):
    """Receive responses from Deepgram Agent"""
    logger.info("sts_receiver started")
    streamsid = await streamsid_queue.get()

    async for message in sts_ws:
        if type(message) is str:
            logger.info(f"Deepgram Agent message: {message}")
            decoded = json.loads(message)
            await handle_text_message(decoded, twilio_ws, sts_ws, streamsid)
            continue

        # Audio response from Deepgram
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
                logger.info("Call started - getting stream SID")
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
            logger.error(f"Error in twilio_receiver: {e}")
            break

async def twilio_handler(twilio_ws):
    """Main handler for Twilio WebSocket connection"""
    audio_queue = asyncio.Queue()
    streamsid_queue = asyncio.Queue()

    async with sts_connect() as sts_ws:
        config_message = load_config()
        await sts_ws.send(json.dumps(config_message))

        await asyncio.wait(
            [
                asyncio.ensure_future(sts_sender(sts_ws, audio_queue)),
                asyncio.ensure_future(sts_receiver(sts_ws, twilio_ws, streamsid_queue)),
                asyncio.ensure_future(twilio_receiver(twilio_ws, audio_queue, streamsid_queue)),
            ]
        )

        await twilio_ws.close()

# Flask Routes
@app.route('/')
def home():
    """Main page"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>MedAgg Healthcare - Cardiology Voice Agent</title>
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
                <p>Advanced Cardiology AI Voice Agent with Deepgram Agent API is active!</p>
            </div>
            
            <div class="feature">
                <h3>🎤 Outstanding Features</h3>
                <ul>
                    <li><strong>Deepgram Agent API:</strong> Advanced conversational AI with function calling</li>
                    <li><strong>Cardiology Focus:</strong> UFE questionnaire for comprehensive heart health evaluation</li>
                    <li><strong>Structured Assessment:</strong> Chest pain, breathing, and symptom evaluation</li>
                    <li><strong>Emergency Detection:</strong> Automatic emergency response for critical symptoms</li>
                    <li><strong>Appointment Booking:</strong> Integrated scheduling system</li>
                    <li><strong>Real-time Processing:</strong> Live audio streaming and response</li>
                </ul>
            </div>
            
            <div class="info">
                <h3>🌐 Configuration</h3>
                <p><strong>Public URL:</strong> {{ public_url }}</p>
                <p><strong>WebSocket URL:</strong> wss://voice-95g5.onrender.com/stream</p>
                <p><strong>Deepgram Agent API:</strong> ✅ Configured with advanced function calling</p>
                <p><strong>Language:</strong> English (optimized for medical conversations)</p>
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
                <p>Test the advanced cardiology voice agent:</p>
                <a href="{{ public_url }}/test" target="_blank" class="button">Test Patient Registration</a>
                <a href="{{ public_url }}/appointments" target="_blank" class="button">View Appointments</a>
            </div>
        </div>
    </body>
    </html>
    ''', public_url=PUBLIC_URL)

@app.route('/twiml', methods=['GET', 'POST'])
def twiml_endpoint():
    """TwiML endpoint for Twilio calls with Deepgram Agent streaming"""
    try:
        logger.info("Creating TwiML for Deepgram Agent Voice Agent")
        
        response = VoiceResponse()
        
        # Start streaming to Deepgram Agent using proper TwiML syntax
        start = Start()
        stream = Stream(url=f"wss://{PUBLIC_URL.replace('https://', '')}/stream")
        start.append(stream)
        response.append(start)
        
        # Keep the call alive for conversation
        response.pause(length=300)  # 5 minutes
        
        # Fallback message
        response.say("Thank you for calling MedAgg Healthcare. Please call back if you need assistance.", voice='alice')
        response.hangup()
        
        twiml = str(response)
        logger.info("TwiML created successfully")
        
        return twiml, 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logger.error(f"Error creating TwiML: {e}")
        response = VoiceResponse()
        response.say("Hello! This is MedAgg Healthcare. I'm here to help you with your health concerns.", voice='alice')
        response.hangup()
        return str(response), 200, {'Content-Type': 'text/xml'}

@app.route('/stream')
async def stream_endpoint():
    """WebSocket endpoint for Twilio media streaming"""
    return await websockets.serve(twilio_handler, "0.0.0.0", 5001)

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
            <h1>🏥 MedAgg Healthcare - Cardiology Voice Agent Test</h1>
            <form id="patientForm">
                <div class="form-group">
                    <label for="name">Full Name:</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="phone">Phone Number (Indian):</label>
                    <input type="tel" id="phone" name="phone_number" pattern="^(\\+91|91)?[6-9]\\d{9}$" required>
                    <small>Format: +91XXXXXXXXXX or 91XXXXXXXXXX</small>
                </div>
                <div class="form-group">
                    <label for="urgency">Urgency Level:</label>
                    <select id="urgency" name="urgency" required>
                        <option value="low">Low - Routine Checkup</option>
                        <option value="medium">Medium - Follow-up</option>
                        <option value="high">High - Urgent Consultation</option>
                        <option value="emergency">Emergency - Critical Symptoms</option>
                    </select>
                </div>
                <button type="submit">Register & Get Cardiology AI Call</button>
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
                                <p><strong>Voice Agent:</strong> Cardiology AI with Deepgram Agent API</p>
                                <p>You will receive a call with comprehensive cardiology evaluation and appointment booking!</p>
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
            'urgency': patient_data.get('urgency', 'medium'),
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
            'voice_agent': 'Cardiology AI with Deepgram Agent API',
            'public_url': PUBLIC_URL
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error registering patient: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/appointments')
def get_appointments():
    """Get all appointments"""
    return jsonify({
        'appointments': appointments,
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
            logger.error(" Invalid phone number format.")
        
        return False

if __name__ == '__main__':
    logger.info("🏥 MedAgg Healthcare - CARDIOLOGY VOICE AGENT")
    logger.info("=" * 70)
    logger.info("🎤 Deepgram Agent API with advanced function calling")
    logger.info("❤️ Cardiology-focused UFE questionnaire conversation")
    logger.info("📞 Twilio integration with WebSocket streaming")
    logger.info("🔧 Function calling: assess_chest_pain, assess_breathing, schedule_appointment")
    logger.info("🚨 Emergency handling with immediate response")
    logger.info(f"🌐 Public URL: {PUBLIC_URL}")
    logger.info(f"🔗 WebSocket URL: wss://{PUBLIC_URL.replace('https://', '')}/stream")
    logger.info("💰 Deepgram Agent API: ✅ Configured with advanced capabilities")
    logger.info("=" * 70)
    
    # Start WebSocket server in background
    import threading
    def run_websocket():
        asyncio.run(websockets.serve(twilio_handler, "0.0.0.0", 5001))
    
    websocket_thread = threading.Thread(target=run_websocket, daemon=True)
    websocket_thread.start()
    logger.info("🎤 WebSocket server started on port 5001")
    
    # Start Flask app
    logger.info("🌐 Starting Flask app on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=False)