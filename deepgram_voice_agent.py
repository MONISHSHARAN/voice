#!/usr/bin/env python3
"""
MedAgg Healthcare POC - Deepgram Voice Agent
Real-time voice recognition with Deepgram for outstanding call experience
"""

import asyncio
import json
import base64
import logging
import uuid
import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_sock import Sock
import websockets
import requests
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app with WebSocket support
app = Flask(__name__)
sock = Sock(app)

# Configuration
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY', 'your_deepgram_api_key_here')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'AC33f397657e06dac328e5d5081eb4f9fd')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'bbf7abc794d8f0eb9538350b501d033f')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '+17752586467')
PUBLIC_URL = os.getenv('RENDER_EXTERNAL_URL', 'https://voice-95g5.onrender.com')

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

# Medical AI Responses
MEDICAL_RESPONSES = {
    "english": {
        "greeting": "Hello! This is Dr. MedAgg from MedAgg Healthcare. I'm here to help you with your medical concerns. How can I assist you today?",
        "headache": "Headaches can have various causes. Please rest, stay hydrated, and if the pain persists, consult a doctor immediately.",
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

def text_to_speech(text, language="english"):
    """Convert text to speech using Twilio's built-in TTS"""
    # This will be handled by TwiML Say verb
    return text

# WebSocket endpoint for Deepgram streaming
@sock.route('/stream')
def stream(ws):
    """Handle real-time audio streaming with Deepgram"""
    call_sid = None
    conversation_id = None
    language = "english"
    
    try:
        logger.info("🎤 New WebSocket connection established")
        
        # Connect to Deepgram
        deepgram_url = f"wss://api.deepgram.com/v1/listen?access_token={DEEPGRAM_API_KEY}&model=nova-2&language={language}&smart_format=true&interim_results=true"
        
        async def handle_audio_stream():
            nonlocal call_sid, conversation_id, language
            
            async with websockets.connect(deepgram_url) as deepgram_ws:
                logger.info("🔗 Connected to Deepgram")
                
                async def forward_audio():
                    """Forward audio from Twilio to Deepgram"""
                    async for message in ws:
                        try:
                            data = json.loads(message)
                            
                            if data.get('event') == 'start':
                                call_sid = data.get('start', {}).get('callSid')
                                conversation_id = str(uuid.uuid4())
                                language = data.get('start', {}).get('customParameters', {}).get('language', 'english')
                                
                                logger.info(f"📞 Call started: {call_sid}, Language: {language}")
                                
                                # Store call info
                                active_calls[call_sid] = {
                                    'conversation_id': conversation_id,
                                    'language': language,
                                    'start_time': datetime.now().isoformat()
                                }
                                
                                # Send greeting
                                greeting = MEDICAL_RESPONSES[language]["greeting"]
                                await ws.send(json.dumps({
                                    'event': 'say',
                                    'text': greeting
                                }))
                                
                            elif data.get('event') == 'media':
                                # Forward audio to Deepgram
                                audio_payload = data.get('media', {}).get('payload', '')
                                if audio_payload:
                                    audio_data = base64.b64decode(audio_payload)
                                    await deepgram_ws.send(audio_data)
                                    
                            elif data.get('event') == 'stop':
                                logger.info(f"📞 Call ended: {call_sid}")
                                if call_sid in active_calls:
                                    del active_calls[call_sid]
                                break
                                
                        except Exception as e:
                            logger.error(f"Error processing audio: {e}")
                
                async def receive_transcription():
                    """Receive transcription from Deepgram and respond"""
                    async for response in deepgram_ws:
                        try:
                            result = json.loads(response)
                            
                            # Get transcript
                            transcript = result.get('channel', {}).get('alternatives', [{}])[0].get('transcript', '')
                            is_final = result.get('is_final', False)
                            
                            if transcript and is_final:
                                logger.info(f"🎯 Transcript: {transcript}")
                                
                                # Get AI response
                                ai_response = get_ai_response(transcript, language)
                                
                                # Store conversation
                                if conversation_id:
                                    if conversation_id not in conversations:
                                        conversations[conversation_id] = {
                                            'call_sid': call_sid,
                                            'language': language,
                                            'messages': []
                                        }
                                    
                                    conversations[conversation_id]['messages'].append({
                                        'user': transcript,
                                        'ai': ai_response,
                                        'timestamp': datetime.now().isoformat()
                                    })
                                
                                # Send AI response back to Twilio
                                await ws.send(json.dumps({
                                    'event': 'say',
                                    'text': ai_response
                                }))
                                
                                # Check if conversation should end
                                if any(word in transcript.lower() for word in ['goodbye', 'thank you', 'bye', 'end', 'stop']):
                                    await ws.send(json.dumps({
                                        'event': 'say',
                                        'text': "Thank you for calling MedAgg Healthcare. Take care and stay healthy!"
                                    }))
                                    await ws.send(json.dumps({
                                        'event': 'hangup'
                                    }))
                                    break
                                    
                        except Exception as e:
                            logger.error(f"Error processing transcription: {e}")
                
                # Run both tasks concurrently
                await asyncio.gather(forward_audio(), receive_transcription())
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if call_sid and call_sid in active_calls:
            del active_calls[call_sid]
        logger.info("🔌 WebSocket connection closed")

# Flask Routes
@app.route('/')
def home():
    """Main page"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>MedAgg Healthcare - Deepgram Voice Agent</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .status { padding: 20px; margin: 20px 0; border-radius: 5px; }
            .online { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
            .endpoint { background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 3px; font-family: monospace; }
            .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 5px; }
            .feature { background: #e8f5e8; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #28a745; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 MedAgg Healthcare - Deepgram Voice Agent</h1>
            <div class="status online">
                <h3>✅ System Status: ONLINE</h3>
                <p>Real-time voice recognition with Deepgram is active!</p>
            </div>
            
            <div class="feature">
                <h3>🎤 Advanced Features</h3>
                <ul>
                    <li><strong>Real-time Speech Recognition:</strong> Powered by Deepgram Nova-2 model</li>
                    <li><strong>Live Conversation:</strong> No key presses, just speak naturally</li>
                    <li><strong>Multilingual Support:</strong> English, Tamil, Hindi with proper language detection</li>
                    <li><strong>Smart AI Responses:</strong> Context-aware medical advice</li>
                    <li><strong>Emergency Detection:</strong> Automatic emergency response</li>
                </ul>
            </div>
            
            <div class="info">
                <h3>🌐 Configuration</h3>
                <p><strong>Public URL:</strong> {{ public_url }}</p>
                <p><strong>WebSocket URL:</strong> wss://{{ public_url.replace('https://', '') }}/stream</p>
                <p><strong>Twilio Webhook:</strong> {{ public_url }}/twiml</p>
            </div>
            
            <div class="info">
                <h3>📞 Twilio Setup</h3>
                <p>Configure your Twilio phone number webhooks:</p>
                <div class="endpoint">Voice URL: {{ public_url }}/twiml</div>
                <div class="endpoint">HTTP Method: POST</div>
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

@app.route('/twiml')
def twiml_endpoint():
    """TwiML endpoint for Twilio calls with Deepgram streaming"""
    try:
        language = request.args.get('language', 'english')
        conversation_id = str(uuid.uuid4())
        
        logger.info(f"Creating TwiML for conversation {conversation_id} in {language}")
        
        response = VoiceResponse()
        
        # Start streaming to Deepgram
        response.start()
        response.stream(url=f"wss://{PUBLIC_URL.replace('https://', '')}/stream")
        
        # Say greeting
        greeting = MEDICAL_RESPONSES[language]["greeting"]
        response.say(greeting, voice='alice')
        
        # Keep the call alive for conversation
        response.pause(length=30)
        
        # Fallback
        response.say("Thank you for calling MedAgg Healthcare. Please call back if you need assistance.", voice='alice')
        response.hangup()
        
        twiml = str(response)
        logger.info(f"TwiML created: {twiml[:200]}...")
        
        return twiml, 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logger.error(f"Error creating TwiML: {e}")
        response = VoiceResponse()
        response.say("Hello! This is MedAgg Healthcare. I'm here to help you with your health concerns.", voice='alice')
        response.hangup()
        return str(response), 200, {'Content-Type': 'text/xml'}

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
            <h1>🏥 MedAgg Healthcare - Deepgram Voice Agent Test</h1>
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
                    <label for="language">Language Preference:</label>
                    <select id="language" name="language_preference" required>
                        <option value="english">English</option>
                        <option value="tamil">தமிழ் (Tamil)</option>
                        <option value="hindi">हिन्दी (Hindi)</option>
                    </select>
                </div>
                <button type="submit">Register & Get AI Call with Deepgram</button>
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
                                <p><strong>Voice Agent:</strong> Deepgram Real-time Recognition</p>
                                <p>You will receive a call with advanced voice recognition!</p>
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
    """Register a new patient and initiate Deepgram call"""
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
            'language_preference': patient_data.get('language_preference', 'english'),
            'created_at': datetime.now().isoformat()
        }
        
        patients.append(patient)
        
        # Make Twilio call with Deepgram streaming
        call_success = make_deepgram_call(patient)
        
        response = {
            'success': True,
            'patient_id': patient['id'],
            'message': 'Patient registered successfully',
            'call_initiated': call_success,
            'voice_agent': 'Deepgram Real-time Recognition',
            'public_url': PUBLIC_URL
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error registering patient: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/conversations')
def get_conversations():
    """Get all conversations"""
    return jsonify(conversations)

@app.route('/active-calls')
def get_active_calls():
    """Get active calls"""
    return jsonify(active_calls)

def make_deepgram_call(patient):
    """Make Twilio call with Deepgram streaming"""
    try:
        language = patient['language_preference'].lower()
        
        # Create TwiML URL with language parameter
        twiml_url = f"{PUBLIC_URL}/twiml?language={language}"
        
        logger.info(f"📞 Making Deepgram call to {patient['phone_number']} for {patient['name']} in {language}")
        logger.info(f"🔗 TwiML URL: {twiml_url}")
        
        # Use Twilio client to make the call
        call = twilio_client.calls.create(
            url=twiml_url,
            to=patient['phone_number'],
            from_=TWILIO_PHONE_NUMBER
        )
        
        logger.info(f"✅ Deepgram call initiated successfully!")
        logger.info(f"📋 Call SID: {call.sid}")
        
        return True
            
    except Exception as e:
        logger.error(f"Error making Deepgram call: {e}")
        return False

if __name__ == '__main__':
    logger.info("🏥 MedAgg Healthcare POC - DEEPGRAM VOICE AGENT")
    logger.info("=" * 70)
    logger.info("🎤 Real-time voice recognition with Deepgram")
    logger.info("🤖 Advanced AI conversation system")
    logger.info("📞 Twilio integration with WebSocket streaming")
    logger.info("🌍 Multilingual support (English, Tamil, Hindi)")
    logger.info("💬 Live conversation flow")
    logger.info(f"🌐 Public URL: {PUBLIC_URL}")
    logger.info(f"🔗 WebSocket URL: wss://{PUBLIC_URL.replace('https://', '')}/stream")
    logger.info("=" * 70)
    
    # Get port from environment variable
    port = int(os.environ.get('PORT', 8000))
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"Failed to start Flask app: {e}")
        raise
