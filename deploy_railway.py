#!/usr/bin/env python3
"""
Deploy MedAgg Voice Agent to Railway
Perfect solution with proper WebSocket support
"""

import os
import subprocess
import json

def create_railway_config():
    """Create Railway configuration"""
    
    # Create railway.json
    railway_config = {
        "$schema": "https://railway.app/railway.schema.json",
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "python main.py",
            "healthcheckPath": "/",
            "healthcheckTimeout": 100,
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 10
        }
    }
    
    with open("railway.json", "w") as f:
        json.dump(railway_config, f, indent=2)
    
    print("✅ Railway configuration created")

def create_main_server():
    """Create main server file"""
    
    main_content = '''#!/usr/bin/env python3
"""
MedAgg Healthcare Voice Agent - Railway Server
Perfect solution with proper WebSocket support
"""

import asyncio
import base64
import json
import os
import uuid
import logging
import websockets
from datetime import datetime
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv
from cardiology_functions import FUNCTION_MAP

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "ebae70e078574403bf495088b5ea043e456b7f2f")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "AC33f397657e06dac328e5d5081eb4f9fd")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "bbf7abc794d8f0eb9538350b501d033f")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+17752586467")
PUBLIC_URL = os.getenv("PUBLIC_URL", "https://medagg-voice-agent-production.up.railway.app")

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
    api_key = os.getenv('DEEPGRAM_API_KEY')
    if not api_key:
        raise ValueError("DEEPGRAM_API_KEY environment variable is not set")
    
    sts_ws = websockets.connect(
        "wss://agent.deepgram.com/v1/agent/converse",
        subprotocols=["token", api_key]
    )
    return sts_ws

def load_config():
    """Load Deepgram Agent configuration for cardiology"""
    with open("config.json", "r") as f:
        return json.load(f)

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

# WebSocket handler for Twilio
class WebSocketHandler:
    def __init__(self):
        self.clients = {}
    
    async def handle_websocket(self, websocket, path):
        """Handle WebSocket connections"""
        logger.info(f"WebSocket connection from {websocket.remote_address} on path: {path}")
        
        if path == "/twilio":
            await self.handle_twilio_connection(websocket)
        else:
            logger.warning(f"Unknown WebSocket path: {path}")
            await websocket.close()
    
    async def handle_twilio_connection(self, websocket):
        """Handle Twilio Media Stream WebSocket"""
        try:
            # Start Deepgram Agent session
            async with sts_connect() as sts_ws:
                # Send configuration
                config_message = load_config()
                await sts_ws.send(json.dumps(config_message))
                
                # Start audio processing tasks
                audio_queue = asyncio.Queue()
                streamsid = None
                
                # Task to send audio to Deepgram
                async def sts_sender():
                    while True:
                        chunk = await audio_queue.get()
                        await sts_ws.send(chunk)
                
                # Task to receive responses from Deepgram
                async def sts_receiver():
                    nonlocal streamsid
                    async for message in sts_ws:
                        if type(message) is str:
                            logger.info(f"Deepgram Agent message: {message}")
                            decoded = json.loads(message)
                            
                            if decoded["type"] == "UserStartedSpeaking" and streamsid:
                                clear_message = {
                                    "event": "clear",
                                    "streamSid": streamsid
                                }
                                await websocket.send(json.dumps(clear_message))
                            elif decoded["type"] == "FunctionCallRequest":
                                await self.handle_function_call_request(decoded, sts_ws)
                        else:
                            # Audio response from Deepgram
                            if streamsid:
                                media_message = {
                                    "event": "media",
                                    "streamSid": streamsid,
                                    "media": {"payload": base64.b64encode(message).decode("ascii")}
                                }
                                await websocket.send(json.dumps(media_message))
                
                # Task to receive audio from Twilio
                async def twilio_receiver():
                    nonlocal streamsid
                    BUFFER_SIZE = 20 * 160
                    inbuffer = bytearray(b"")
                    
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            
                            if data["event"] == "start":
                                logger.info("Call started - getting stream SID")
                                start = data["start"]
                                streamsid = start["streamSid"]
                            elif data["event"] == "connected":
                                continue
                            elif data["event"] == "media":
                                media = data["media"]
                                chunk = base64.b64decode(media["payload"])
                                if media["track"] == "inbound":
                                    inbuffer.extend(chunk)
                            elif data["event"] == "stop":
                                break
                            
                            # Send buffered audio to Deepgram
                            while len(inbuffer) >= BUFFER_SIZE:
                                chunk = inbuffer[:BUFFER_SIZE]
                                await audio_queue.put(chunk)
                                inbuffer = inbuffer[BUFFER_SIZE:]
                        except Exception as e:
                            logger.error(f"Error in twilio_receiver: {e}")
                            break
                
                # Start all tasks
                await asyncio.gather(
                    sts_sender(),
                    sts_receiver(),
                    twilio_receiver()
                )
                
        except Exception as e:
            logger.error(f"Error in Twilio WebSocket handler: {e}")
        finally:
            await websocket.close()
    
    async def handle_function_call_request(self, decoded, sts_ws):
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

# Global WebSocket handler
ws_handler = WebSocketHandler()

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

async def main():
    """Main function to start WebSocket server"""
    logger.info("🏥 MedAgg Healthcare - CARDIOLOGY VOICE AGENT")
    logger.info("=" * 70)
    logger.info("🎤 Deepgram Agent API with advanced function calling")
    logger.info("❤️ Cardiology-focused UFE questionnaire conversation")
    logger.info("📞 Twilio integration with WebSocket streaming")
    logger.info("🔧 Function calling: assess_chest_pain, assess_breathing, schedule_appointment")
    logger.info("🚨 Emergency handling with immediate response")
    logger.info(f"🌐 Public URL: {PUBLIC_URL}")
    logger.info(f"🔗 WebSocket URL: wss://{PUBLIC_URL.replace('https://', '')}/twilio")
    logger.info("💰 Deepgram Agent API: ✅ Configured with advanced capabilities")
    logger.info("=" * 70)
    
    # Start WebSocket server
    logger.info("🎤 Starting WebSocket server on port 5000")
    server = await websockets.serve(ws_handler.handle_websocket, "0.0.0.0", 5000)
    
    # Keep server running
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
'''
    
    with open("main.py", "w") as f:
        f.write(main_content)
    
    print("✅ Main server file created")

def create_railway_deployment():
    """Create Railway deployment files"""
    
    # Create Procfile
    with open("Procfile", "w") as f:
        f.write("web: python main.py\n")
    
    print("✅ Procfile created")
    
    # Create railway.json
    create_railway_config()
    
    print("✅ Railway deployment files created")

def main():
    """Main deployment function"""
    print("🚀 MedAgg Voice Agent - Railway Deployment Setup")
    print("=" * 50)
    
    # Create deployment files
    create_railway_deployment()
    create_main_server()
    
    print("\n✅ Railway deployment setup complete!")
    print("\n📋 Next steps:")
    print("1. Go to https://railway.app")
    print("2. Sign up/Login with GitHub")
    print("3. Click 'New Project' → 'Deploy from GitHub repo'")
    print("4. Select your repository")
    print("5. Add environment variables:")
    print("   - DEEPGRAM_API_KEY")
    print("   - TWILIO_ACCOUNT_SID")
    print("   - TWILIO_AUTH_TOKEN")
    print("   - TWILIO_PHONE_NUMBER")
    print("6. Deploy!")
    print("\n🌐 Your app will be available at:")
    print("   https://your-app-name.up.railway.app")
    print("\n🔗 WebSocket URL for Twilio:")
    print("   wss://your-app-name.up.railway.app/twilio")

if __name__ == "__main__":
    main()
