#!/usr/bin/env python3
"""
WebSocket Server for Real-time Conversations
Handles Twilio Media Streams and OpenAI Realtime API integration
"""

import asyncio
import websockets
import json
import base64
import logging
import uuid
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI Configuration
OPENAI_API_KEY = "your-openai-api-key-here"  # Replace with your actual API key

class ConversationManager:
    """Manages real-time conversations between Twilio and OpenAI"""
    
    def __init__(self):
        self.active_conversations = {}
        self.openai_connections = {}
    
    async def handle_twilio_connection(self, websocket, path):
        """Handle incoming Twilio Media Stream connection"""
        try:
            conversation_id = path.split('/')[-1]
            logger.info(f"New Twilio connection for conversation {conversation_id}")
            
            # Store the Twilio connection
            self.active_conversations[conversation_id] = {
                'twilio_ws': websocket,
                'openai_ws': None,
                'status': 'connected',
                'created_at': datetime.now()
            }
            
            # Connect to OpenAI Realtime API
            await self.connect_to_openai(conversation_id)
            
            # Handle messages from Twilio
            async for message in websocket:
                await self.handle_twilio_message(conversation_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Twilio connection closed for conversation {conversation_id}")
        except Exception as e:
            logger.error(f"Error in Twilio connection: {e}")
        finally:
            # Clean up
            if conversation_id in self.active_conversations:
                del self.active_conversations[conversation_id]
            if conversation_id in self.openai_connections:
                del self.openai_connections[conversation_id]
    
    async def connect_to_openai(self, conversation_id):
        """Connect to OpenAI Realtime API"""
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            openai_ws = await websockets.connect(
                "wss://api.openai.com/v1/realtime",
                extra_headers=headers
            )
            
            # Store OpenAI connection
            self.openai_connections[conversation_id] = openai_ws
            self.active_conversations[conversation_id]['openai_ws'] = openai_ws
            
            # Send initial configuration
            config = {
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],
                    "instructions": self.get_medical_prompt(),
                    "voice": "alloy",
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16",
                    "input_audio_transcription": {
                        "model": "whisper-1"
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 200
                    },
                    "tools": [
                        {
                            "type": "function",
                            "name": "schedule_appointment",
                            "description": "Schedule a medical appointment",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "patient_name": {"type": "string"},
                                    "phone_number": {"type": "string"},
                                    "symptoms": {"type": "string"},
                                    "urgency": {"type": "string", "enum": ["low", "medium", "high", "emergency"]},
                                    "preferred_hospital": {"type": "string"}
                                },
                                "required": ["patient_name", "symptoms", "urgency"]
                            }
                        }
                    ]
                }
            }
            
            await openai_ws.send(json.dumps(config))
            logger.info(f"Connected to OpenAI for conversation {conversation_id}")
            
            # Start listening for OpenAI responses
            asyncio.create_task(self.handle_openai_messages(conversation_id))
            
        except Exception as e:
            logger.error(f"Failed to connect to OpenAI: {e}")
    
    async def handle_twilio_message(self, conversation_id, message):
        """Handle incoming message from Twilio Media Stream"""
        try:
            data = json.loads(message)
            
            if data.get('event') == 'media':
                # Forward audio data to OpenAI
                audio_data = data.get('media', {}).get('payload', '')
                if audio_data and conversation_id in self.openai_connections:
                    openai_ws = self.openai_connections[conversation_id]
                    
                    # Send audio to OpenAI
                    audio_message = {
                        "type": "input_audio_buffer.append",
                        "audio": audio_data
                    }
                    await openai_ws.send(json.dumps(audio_message))
                    
                    # Commit the audio buffer
                    await openai_ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
                    
        except Exception as e:
            logger.error(f"Error handling Twilio message: {e}")
    
    async def handle_openai_messages(self, conversation_id):
        """Handle messages from OpenAI Realtime API"""
        try:
            if conversation_id not in self.openai_connections:
                return
                
            openai_ws = self.openai_connections[conversation_id]
            twilio_ws = self.active_conversations[conversation_id]['twilio_ws']
            
            async for message in openai_ws:
                data = json.loads(message)
                
                if data.get('type') == 'conversation.item.output_audio.delta':
                    # Forward audio response to Twilio
                    audio_data = data.get('delta', '')
                    if audio_data:
                        twilio_message = {
                            "event": "media",
                            "streamSid": "your-stream-sid",  # This should come from Twilio
                            "media": {
                                "payload": audio_data
                            }
                        }
                        await twilio_ws.send(json.dumps(twilio_message))
                
                elif data.get('type') == 'conversation.item.input_audio_transcription.completed':
                    # Log transcription
                    transcript = data.get('transcript', '')
                    logger.info(f"Transcription: {transcript}")
                
                elif data.get('type') == 'conversation.item.tool_call':
                    # Handle tool calls (e.g., appointment scheduling)
                    await self.handle_tool_call(conversation_id, data)
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"OpenAI connection closed for conversation {conversation_id}")
        except Exception as e:
            logger.error(f"Error handling OpenAI messages: {e}")
    
    async def handle_tool_call(self, conversation_id, data):
        """Handle tool calls from OpenAI"""
        try:
            tool_call = data.get('tool_call', {})
            function_name = tool_call.get('function', {}).get('name')
            parameters = tool_call.get('function', {}).get('parameters', {})
            
            if function_name == 'schedule_appointment':
                # Schedule appointment logic
                result = await self.schedule_appointment(parameters)
                
                # Send result back to OpenAI
                if conversation_id in self.openai_connections:
                    openai_ws = self.openai_connections[conversation_id]
                    response = {
                        "type": "conversation.item.tool_result",
                        "tool_call_id": tool_call.get('id'),
                        "content": result
                    }
                    await openai_ws.send(json.dumps(response))
                    
        except Exception as e:
            logger.error(f"Error handling tool call: {e}")
    
    async def schedule_appointment(self, parameters):
        """Schedule a medical appointment"""
        try:
            # This would integrate with your appointment system
            patient_name = parameters.get('patient_name', 'Unknown')
            symptoms = parameters.get('symptoms', '')
            urgency = parameters.get('urgency', 'medium')
            
            # For now, return a simple response
            return f"Appointment scheduled for {patient_name}. Symptoms: {symptoms}. Urgency: {urgency}. You will receive a confirmation call shortly."
            
        except Exception as e:
            logger.error(f"Error scheduling appointment: {e}")
            return "I'm sorry, there was an error scheduling your appointment. Please try again."
    
    def get_medical_prompt(self):
        """Get medical AI prompt"""
        return """You are Dr. MedAgg, an intelligent medical assistant for MedAgg Healthcare. 
        You help patients with:
        - Initial symptom assessment
        - Medical advice and guidance
        - Appointment scheduling
        - Emergency triage
        - General health information
        
        Always be professional, empathetic, and clear. If it's an emergency, advise calling emergency services immediately.
        Keep responses concise and helpful. You can schedule appointments using the schedule_appointment tool."""

async def start_websocket_server():
    """Start the WebSocket server"""
    conversation_manager = ConversationManager()
    
    print("🌐 Starting WebSocket Server for Real-time Conversations")
    print("=" * 60)
    print("🔗 WebSocket server running on ws://localhost:8765")
    print("🤖 OpenAI Realtime API integration ready")
    print("📞 Twilio Media Streams support enabled")
    print("✅ Ready for intelligent conversations!")
    print("=" * 60)
    
    async with websockets.serve(
        conversation_manager.handle_twilio_connection,
        "localhost",
        8765,
        subprotocols=["twilio"]
    ):
        logger.info("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(start_websocket_server())
