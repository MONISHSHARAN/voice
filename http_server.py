#!/usr/bin/env python3
"""
MedAgg Healthcare Voice Agent - HTTP Server
Handles web requests and TwiML for Twilio
"""

import json
import os
import uuid
import logging
from datetime import datetime
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "AC33f397657e06dac328e5d5081eb4f9fd")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "bbf7abc794d8f0eb9538350b501d033f")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+17752586467")
PUBLIC_URL = os.getenv("PUBLIC_URL", "https://medagg-voice-agent-production.up.railway.app")

# Initialize Twilio client
try:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    logger.info("Twilio client initialized successfully")
except Exception as e:
    logger.error(f"Twilio initialization failed: {e}")
    twilio_client = None

# Storage
patients = []
appointments = {}

class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(self.get_home_page().encode())
            elif self.path == '/test':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(self.get_test_page().encode())
            elif self.path == '/appointments':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'appointments': appointments,
                    'patients': patients,
                    'active_calls': 0
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            logger.error(f"Error in GET request: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_POST(self):
        try:
            if self.path == '/twiml':
                self.send_response(200)
                self.send_header('Content-type', 'text/xml')
                self.end_headers()
                twiml = self.get_twiml()
                self.wfile.write(twiml.encode())
            elif self.path == '/register-patient':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                patient_data = json.loads(post_data.decode('utf-8'))
                
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
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            logger.error(f"Error in POST request: {e}")
            self.send_response(500)
            self.end_headers()
    
    def get_home_page(self):
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>MedAgg Healthcare - Cardiology Voice Agent</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .status {{ padding: 20px; margin: 20px 0; border-radius: 5px; }}
                .online {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                .info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
                .button {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 5px; }}
                .feature {{ background: #e8f5e8; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #28a745; }}
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
                    <p><strong>Public URL:</strong> {PUBLIC_URL}</p>
                    <p><strong>WebSocket URL:</strong> wss://{PUBLIC_URL.replace('https://', '')}/twilio</p>
                    <p><strong>Deepgram Agent API:</strong> ✅ Configured with advanced function calling</p>
                    <p><strong>Language:</strong> English (optimized for medical conversations)</p>
                </div>
                
                <div class="info">
                    <h3>📞 Twilio Setup</h3>
                    <p>Configure your Twilio phone number webhooks:</p>
                    <div style="background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 3px; font-family: monospace;">
                        Voice URL: {PUBLIC_URL}/twiml<br>
                        HTTP Method: POST
                    </div>
                    <a href="https://console.twilio.com/us1/develop/phone-numbers/manage/incoming" target="_blank" class="button">Configure Twilio Webhooks</a>
                </div>
                
                <div class="info">
                    <h3>🧪 Test the System</h3>
                    <p>Test the advanced cardiology voice agent:</p>
                    <a href="{PUBLIC_URL}/test" target="_blank" class="button">Test Patient Registration</a>
                    <a href="{PUBLIC_URL}/appointments" target="_blank" class="button">View Appointments</a>
                </div>
            </div>
        </body>
        </html>
        '''
    
    def get_test_page(self):
        return f'''
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
                <h1>🏥 MedAgg Healthcare - Cardiology Voice Agent Test</h1>
                <form id="patientForm">
                    <div class="form-group">
                        <label for="name">Full Name:</label>
                        <input type="text" id="name" name="name" required>
                    </div>
                    <div class="form-group">
                        <label for="phone">Phone Number (Indian):</label>
                        <input type="tel" id="phone" name="phone_number" pattern="^(\\+91|91)?[6-9]\\d{{9}}$" required>
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
                                    <p><strong>Voice Agent:</strong> Cardiology AI with Deepgram Agent API</p>
                                    <p>You will receive a call with comprehensive cardiology evaluation and appointment booking!</p>
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
    
    def get_twiml(self):
        try:
            logger.info("Creating TwiML for Deepgram Agent Voice Agent")
            
            response = VoiceResponse()
            
            # Use proper TwiML syntax for streaming
            response.say("This call may be monitored or recorded.", language="en")
            connect = response.connect()
            stream = connect.stream(url=f"wss://{PUBLIC_URL.replace('https://', '')}/twilio")
            
            twiml = str(response)
            logger.info("TwiML created successfully")
            
            return twiml
            
        except Exception as e:
            logger.error(f"Error creating TwiML: {e}")
            response = VoiceResponse()
            response.say("Hello! This is MedAgg Healthcare. I'm here to help you with your health concerns.", voice='alice')
            response.hangup()
            return str(response)

def make_twilio_call(patient):
    """Make Twilio call"""
    try:
        if not twilio_client:
            logger.error("Twilio client not initialized")
            return False
            
        # Create TwiML URL
        twiml_url = f"{PUBLIC_URL}/twiml"
        
        logger.info(f"Making call to {patient['phone_number']} for {patient['name']}")
        logger.info(f"TwiML URL: {twiml_url}")
        logger.info(f"Using Twilio Account: {TWILIO_ACCOUNT_SID}")
        
        # Check if phone number is verified for trial accounts
        if patient['phone_number'].startswith('+91'):
            logger.warning("Indian number detected. Trial accounts may need verification.")
        
        # Use Twilio client to make the call
        call = twilio_client.calls.create(
            url=twiml_url,
            to=patient['phone_number'],
            from_=TWILIO_PHONE_NUMBER
        )
        
        logger.info(f"Call initiated successfully!")
        logger.info(f"Call SID: {call.sid}")
        
        return True
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error making call: {error_msg}")
        
        if "401" in error_msg or "Authenticate" in error_msg:
            logger.error("Authentication failed. Check Twilio credentials.")
        elif "unverified" in error_msg.lower():
            logger.error("Phone number needs verification for trial accounts.")
        elif "not a valid phone number" in error_msg.lower():
            logger.error("Invalid phone number format.")
        
        return False

def main():
    """Main function to start HTTP server"""
    logger.info("MedAgg Healthcare - HTTP Server")
    logger.info("=" * 50)
    logger.info("Starting HTTP server on port 5001")
    logger.info(f"Public URL: {PUBLIC_URL}")
    logger.info("=" * 50)
    
    try:
        server = HTTPServer(('0.0.0.0', 5001), WebHandler)
        logger.info("HTTP server started on port 5001")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Error starting HTTP server: {e}")

if __name__ == '__main__':
    main()
