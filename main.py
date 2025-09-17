#!/usr/bin/env python3
"""
MedAgg Healthcare Voice Agent - Fixed for Railway Healthcheck
WebSocket server with HTTP healthcheck support
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
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

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

# Simple HTTP handler for healthcheck
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>MedAgg Healthcare - Voice Agent</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .status { padding: 20px; margin: 20px 0; border-radius: 5px; background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🏥 MedAgg Healthcare - Voice Agent</h1>
                    <div class="status">
                        <h3>✅ System Status: ONLINE</h3>
                        <p>Advanced Cardiology AI Voice Agent with Deepgram Agent API is active!</p>
                        <p><strong>WebSocket URL:</strong> wss://''' + PUBLIC_URL.replace('https://', '') + b'''/twilio</p>
                    </div>
                </div>
            </body>
            </html>
            ''')
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'healthy',
                'service': 'MedAgg Voice Agent',
                'websocket_url': f'wss://{PUBLIC_URL.replace("https://", "")}/twilio'
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/twiml':
            self.send_response(200)
            self.send_header('Content-type', 'text/xml')
            self.end_headers()
            twiml = self.get_twiml()
            self.wfile.write(twiml.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
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

def start_http_server():
    """Start HTTP server for healthcheck"""
    def run_http():
        try:
            server = HTTPServer(('0.0.0.0', 5000), HealthHandler)
            logger.info("HTTP server started on port 5000 for healthcheck")
            server.serve_forever()
        except Exception as e:
            logger.error(f"Error starting HTTP server: {e}")
    
    http_thread = threading.Thread(target=run_http, daemon=True)
    http_thread.start()
    return http_thread

def start_websocket_server():
    """Start WebSocket server"""
    def run_websocket():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Start WebSocket server on port 5001
            server = loop.run_until_complete(websockets.serve(ws_handler.handle_websocket, "0.0.0.0", 5001))
            logger.info("WebSocket server started on port 5001")
            loop.run_forever()
        except Exception as e:
            logger.error(f"Error starting WebSocket server: {e}")
    
    websocket_thread = threading.Thread(target=run_websocket, daemon=True)
    websocket_thread.start()
    return websocket_thread

def main():
    """Main function to start both servers"""
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
    
    # Start both servers
    try:
        start_http_server()  # Port 5000 for healthcheck
        start_websocket_server()  # Port 5001 for WebSocket
        
        # Keep main thread alive
        while True:
            pass
    except KeyboardInterrupt:
        logger.info("Shutting down servers...")
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == '__main__':
    main()