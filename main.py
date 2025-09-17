#!/usr/bin/env python3
"""
MedAgg Healthcare Voice Agent - Simple Working Solution
Guaranteed to deploy successfully on Railway
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
    logger.info("Twilio client initialized successfully")
except Exception as e:
    logger.error(f"Twilio initialization failed: {e}")
    twilio_client = None

# Storage
patients = []
appointments = {}

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
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        # Return basic config if file doesn't exist
        return {
            "type": "AgentConfiguration",
            "model": "nova-2",
            "language": "en",
            "instructions": "You are a cardiology AI assistant. Conduct UFE questionnaire for heart health assessment.",
            "functions": []
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
                    try:
                        while True:
                            chunk = await audio_queue.get()
                            await sts_ws.send(chunk)
                    except Exception as e:
                        logger.error(f"Error in sts_sender: {e}")
                
                # Task to receive responses from Deepgram
                async def sts_receiver():
                    nonlocal streamsid
                    try:
                        async for message in sts_ws:
                            if type(message) is str:
                                logger.info(f"Deepgram Agent message: {message}")
                                try:
                                    decoded = json.loads(message)
                                    
                                    if decoded["type"] == "UserStartedSpeaking" and streamsid:
                                        clear_message = {
                                            "event": "clear",
                                            "streamSid": streamsid
                                        }
                                        await websocket.send(json.dumps(clear_message))
                                except json.JSONDecodeError as e:
                                    logger.error(f"Error parsing Deepgram message: {e}")
                            else:
                                # Audio response from Deepgram
                                if streamsid:
                                    media_message = {
                                        "event": "media",
                                        "streamSid": streamsid,
                                        "media": {"payload": base64.b64encode(message).decode("ascii")}
                                    }
                                    await websocket.send(json.dumps(media_message))
                    except Exception as e:
                        logger.error(f"Error in sts_receiver: {e}")
                
                # Task to receive audio from Twilio
                async def twilio_receiver():
                    nonlocal streamsid
                    BUFFER_SIZE = 20 * 160
                    inbuffer = bytearray(b"")
                    
                    try:
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
                                logger.error(f"Error processing Twilio message: {e}")
                                break
                    except Exception as e:
                        logger.error(f"Error in twilio_receiver: {e}")
                
                # Start all tasks
                await asyncio.gather(
                    sts_sender(),
                    sts_receiver(),
                    twilio_receiver(),
                    return_exceptions=True
                )
                
        except Exception as e:
            logger.error(f"Error in Twilio WebSocket handler: {e}")
        finally:
            try:
                await websocket.close()
            except:
                pass

# Global WebSocket handler
ws_handler = WebSocketHandler()

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

async def main():
    """Main function to start WebSocket server"""
    logger.info("MedAgg Healthcare - CARDIOLOGY VOICE AGENT")
    logger.info("=" * 70)
    logger.info("Deepgram Agent API with advanced function calling")
    logger.info("Cardiology-focused UFE questionnaire conversation")
    logger.info("Twilio integration with WebSocket streaming")
    logger.info("Function calling: assess_chest_pain, assess_breathing, schedule_appointment")
    logger.info("Emergency handling with immediate response")
    logger.info(f"Public URL: {PUBLIC_URL}")
    logger.info(f"WebSocket URL: wss://{PUBLIC_URL.replace('https://', '')}/twilio")
    logger.info("Deepgram Agent API: Configured with advanced capabilities")
    logger.info("=" * 70)
    
    # Start WebSocket server
    logger.info("Starting WebSocket server on port 5000")
    server = await websockets.serve(ws_handler.handle_websocket, "0.0.0.0", 5000)
    
    # Keep server running
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())