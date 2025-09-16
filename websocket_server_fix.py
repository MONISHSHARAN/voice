#!/usr/bin/env python3
"""
Standalone WebSocket Server for Twilio-Deepgram Integration
This ensures the WebSocket connection works properly
"""

import asyncio
import websockets
import json
import base64
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DEEPGRAM_API_KEY = 'ebae70e078574403bf495088b5ea043e456b7f2f'
PUBLIC_URL = 'https://voice-95g5.onrender.com'

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

async def sts_connect():
    """Connect to Deepgram Voice Agent"""
    sts_ws = websockets.connect(
        "wss://agent.deepgram.com/v1/agent/converse",
        subprotocols=["token", DEEPGRAM_API_KEY]
    )
    return sts_ws

async def handle_barge_in(decoded, twilio_ws, streamsid):
    """Handle user interruption during AI speech"""
    if decoded["type"] == "UserStartedSpeaking":
        clear_message = {
            "event": "clear",
            "streamSid": streamsid
        }
        await twilio_ws.send(json.dumps(clear_message))

async def sts_sender(sts_ws, audio_queue):
    """Send audio to Deepgram"""
    logger.info("🎤 Deepgram sender started")
    while True:
        try:
            chunk = await audio_queue.get()
            await sts_ws.send(chunk)
        except Exception as e:
            logger.error(f"Error in sts_sender: {e}")
            break

async def sts_receiver(sts_ws, twilio_ws, streamsid_queue):
    """Receive responses from Deepgram"""
    logger.info("🎧 Deepgram receiver started")
    streamsid = await streamsid_queue.get()

    async for message in sts_ws:
        try:
            if type(message) is str:
                logger.info(f"📝 Deepgram message: {message}")
                decoded = json.loads(message)
                await handle_barge_in(decoded, twilio_ws, streamsid)
                continue

            # Send audio back to Twilio
            raw_mulaw = message
            media_message = {
                "event": "media",
                "streamSid": streamsid,
                "media": {"payload": base64.b64encode(raw_mulaw).decode("ascii")}
            }
            await twilio_ws.send(json.dumps(media_message))
        except Exception as e:
            logger.error(f"Error in sts_receiver: {e}")
            break

async def twilio_receiver(twilio_ws, audio_queue, streamsid_queue):
    """Receive audio from Twilio"""
    BUFFER_SIZE = 20 * 160
    inbuffer = bytearray(b"")

    async for message in twilio_ws:
        try:
            data = json.loads(message)
            event = data["event"]

            if event == "start":
                logger.info("🎬 Call started, getting stream ID")
                start = data["start"]
                streamsid = start["streamSid"]
                streamsid_queue.put_nowait(streamsid)
            elif event == "connected":
                logger.info("🔗 Call connected")
                continue
            elif event == "media":
                media = data["media"]
                chunk = base64.b64decode(media["payload"])
                if media["track"] == "inbound":
                    inbuffer.extend(chunk)
            elif event == "stop":
                logger.info("🛑 Call stopped")
                break

            while len(inbuffer) >= BUFFER_SIZE:
                chunk = inbuffer[:BUFFER_SIZE]
                audio_queue.put_nowait(chunk)
                inbuffer = inbuffer[BUFFER_SIZE:]
        except Exception as e:
            logger.error(f"Error in Twilio receiver: {e}")
            break

async def twilio_handler(twilio_ws, path):
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

async def main():
    """Start the WebSocket server"""
    logger.info("🚀 Starting WebSocket server for Twilio-Deepgram integration")
    logger.info(f"🌐 Public URL: {PUBLIC_URL}")
    logger.info(f"🔗 WebSocket URL: wss://{PUBLIC_URL.replace('https://', '')}/twilio")
    
    server = await websockets.serve(twilio_handler, "0.0.0.0", 5000)
    logger.info("✅ WebSocket server started on port 5000")
    
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
