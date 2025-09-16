#!/usr/bin/env python3
"""
WebSocket Server for Twilio-Deepgram Integration
Handles the /stream endpoint for real-time audio streaming
"""

import asyncio
import base64
import json
import websockets
import os
import uuid
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY', 'ebae70e078574403bf495088b5ea043e456b7f2f')
PUBLIC_URL = os.getenv('PUBLIC_URL', 'https://voice-95g5.onrender.com')

# Storage for conversations
conversations = {}

def get_ai_response(transcript, language="english"):
    """Get AI response based on transcript using rule-based system"""
    try:
        # Simple rule-based responses for cardiology questionnaire
        transcript_lower = transcript.lower()
        
        # Cardiology UFE Questionnaire Flow
        if any(word in transcript_lower for word in ["hello", "hi", "hey", "start", "yes", "okay", "ok"]):
            return "Hello! Welcome to MedAgg Healthcare. I'm Dr. MedAgg, your AI cardiology specialist. I'm here to conduct a comprehensive heart health evaluation with you today. First, do you experience any chest pain or discomfort?"
        
        elif any(word in transcript_lower for word in ["yes", "chest pain", "discomfort", "pain", "hurt", "ache"]):
            return "I understand you're experiencing chest discomfort. Can you describe the pain? Is it sharp, dull, or burning? And how long have you had this pain?"
        
        elif any(word in transcript_lower for word in ["no", "no pain", "no discomfort", "none", "nothing"]):
            return "That's good to hear. Now, do you experience any shortness of breath, especially during physical activity or when lying down?"
        
        elif any(word in transcript_lower for word in ["breath", "breathing", "shortness", "difficulty", "trouble", "hard"]):
            return "I see you have breathing concerns. Does this happen during rest, activity, or both? And have you noticed any swelling in your legs or ankles?"
        
        elif any(word in transcript_lower for word in ["appointment", "book", "schedule", "see doctor", "consultation"]):
            return "I'd be happy to help you schedule an appointment. What type of consultation would you like - a general cardiology checkup, follow-up, or emergency consultation? And what's your preferred urgency level - low, medium, or high?"
        
        elif any(word in transcript_lower for word in ["emergency", "urgent", "severe", "heart attack", "critical"]):
            return "This sounds like it could be an emergency. I'm going to alert our emergency team immediately. Please stay calm and if you're experiencing severe chest pain, call 108 or go to the nearest hospital right now. Can you tell me your current location?"
        
        elif any(word in transcript_lower for word in ["thank", "thanks", "goodbye", "bye", "end", "done"]):
            return "You're very welcome! Thank you for calling MedAgg Healthcare. If you need any further assistance or want to schedule an appointment, please call us back. Take care and stay healthy!"
        
        elif any(word in transcript_lower for word in ["sharp", "dull", "burning", "stabbing", "pressure"]):
            return "Thank you for describing the pain. Now, does this pain radiate to your arm, neck, or jaw? And does it get worse with activity or stress?"
        
        elif any(word in transcript_lower for word in ["radiate", "arm", "neck", "jaw", "shoulder"]):
            return "I understand. Now, have you experienced any dizziness, nausea, or sweating along with these symptoms? And when did you first notice these symptoms?"
        
        elif any(word in transcript_lower for word in ["dizziness", "nausea", "sweating", "sweat", "dizzy"]):
            return "Thank you for that information. Based on your symptoms, I recommend scheduling an appointment with our cardiology team. Would you like me to book an appointment for you? What's your preferred time - morning, afternoon, or evening?"
        
        elif any(word in transcript_lower for word in ["morning", "afternoon", "evening", "time", "schedule"]):
            return "Perfect! I'll schedule your cardiology consultation. Can you please provide your full name and phone number for the appointment booking?"
        
        elif any(word in transcript_lower for word in ["name", "phone", "number", "contact"]):
            return "Thank you for providing your information. Your appointment has been scheduled. You'll receive a confirmation call shortly. Is there anything else you'd like to discuss about your heart health?"
        
        else:
            return "I understand. Can you tell me more about your symptoms? Are you experiencing any chest pain, shortness of breath, or other cardiovascular concerns?"
    
    except Exception as e:
        logger.error(f"Error getting AI response: {e}")
        return "I'm sorry, I didn't catch that. Could you please repeat your response?"

async def handle_audio_stream(websocket, path):
    """Handle real-time audio streaming with Deepgram"""
    call_sid = None
    conversation_id = str(uuid.uuid4())
    language = "english"
    
    try:
        logger.info(f"🎤 New WebSocket connection established on path: {path}")
        
        # Connect to Deepgram
        deepgram_url = f"wss://api.deepgram.com/v1/listen?access_token={DEEPGRAM_API_KEY}&model=nova-2&language={language}&smart_format=true&interim_results=true"
        
        async with websockets.connect(deepgram_url) as deepgram_ws:
            logger.info("🔗 Connected to Deepgram")
            
            async def forward_audio():
                """Forward audio from Twilio to Deepgram"""
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        event = data.get('event')
                        
                        if event == 'start':
                            call_sid = data.get('start', {}).get('callSid')
                            logger.info(f"📞 Call started: {call_sid}")
                            
                        elif event == 'media':
                            media = data.get('media', {})
                            if media.get('track') == 'inbound':
                                audio_data = base64.b64decode(media.get('payload', ''))
                                await deepgram_ws.send(audio_data)
                                
                        elif event == 'stop':
                            logger.info("🛑 Call stopped")
                            break
                            
                    except Exception as e:
                        logger.error(f"Error forwarding audio: {e}")
                        break
            
            async def receive_transcription():
                """Receive transcription from Deepgram"""
                async for message in deepgram_ws:
                    try:
                        data = json.loads(message)
                        if 'channel' in data and 'alternatives' in data['channel']:
                            result = data['channel']['alternatives'][0]
                            transcript = result.get('transcript', '')
                            is_final = result.get('is_final', False)
                            
                            if transcript and is_final:
                                logger.info(f"🎯 Transcript: {transcript}")
                                
                                # Get AI response
                                ai_response = get_ai_response(transcript, language)
                                logger.info(f"🤖 AI Response: {ai_response}")
                                
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
                                
                                # Send AI response back to Twilio using proper TwiML
                                from twilio.twiml.voice_response import VoiceResponse
                                
                                twiml_response = VoiceResponse()
                                twiml_response.say(ai_response, voice='alice')
                                
                                # Send the TwiML response
                                response_data = {
                                    'event': 'twiml',
                                    'twiml': str(twiml_response)
                                }
                                await websocket.send(json.dumps(response_data))
                                
                    except Exception as e:
                        logger.error(f"Error receiving transcription: {e}")
                        break
            
            # Start both tasks
            await asyncio.gather(
                forward_audio(),
                receive_transcription()
            )
            
    except Exception as e:
        logger.error(f"Error in audio stream handler: {e}")

async def main():
    """Start the WebSocket server"""
    logger.info("🚀 Starting WebSocket server for Twilio-Deepgram integration")
    logger.info(f"🌐 Public URL: {PUBLIC_URL}")
    logger.info(f"🔗 WebSocket URL: wss://{PUBLIC_URL.replace('https://', '')}/stream")
    
    # Start WebSocket server on port 5000
    server = await websockets.serve(handle_audio_stream, "0.0.0.0", 5000)
    logger.info("✅ WebSocket server started on port 5000")
    
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())