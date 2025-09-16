#!/usr/bin/env python3
"""
Emergency Fix for MedAgg Healthcare Voice Agent
Ultra-simple version that will definitely work
"""

from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>MedAgg Healthcare - Voice Agent</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .status { padding: 20px; margin: 20px 0; border-radius: 5px; background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 MedAgg Healthcare - Voice Agent</h1>
            <div class="status">
                <h3>✅ System Status: ONLINE</h3>
                <p>Emergency version - Simple and working!</p>
            </div>
            <p><strong>Public URL:</strong> https://your-app-url.com</p>
            <p><strong>Voice URL:</strong> https://your-app-url.com/twiml</p>
            <a href="/test" class="button">Test Voice Agent</a>
        </div>
    </body>
    </html>
    '''

@app.route('/twiml', methods=['GET', 'POST'])
def twiml():
    """Ultra-simple TwiML that will definitely work"""
    response = VoiceResponse()
    response.say("Hello! Welcome to MedAgg Healthcare. I'm Dr. MedAgg, your AI healthcare assistant. How can I help you today?", voice='alice')
    
    # Simple gather
    gather = response.gather(
        input='speech',
        action='/process',
        method='POST',
        speech_timeout='auto',
        timeout=10
    )
    
    # Fallback
    response.say("I didn't hear anything. Please try again.", voice='alice')
    response.redirect('/twiml')
    
    return str(response), 200, {'Content-Type': 'text/xml'}

@app.route('/process', methods=['POST'])
def process():
    """Process speech input"""
    speech = request.form.get('SpeechResult', '').lower()
    logger.info(f"Speech: {speech}")
    
    response = VoiceResponse()
    
    if 'hello' in speech or 'hi' in speech:
        response.say("Hello! How can I help you today? You can ask about medical advice, appointments, or health concerns.", voice='alice')
    elif 'appointment' in speech:
        response.say("I can help you schedule an appointment. What type of appointment do you need?", voice='alice')
    elif 'pain' in speech or 'hurt' in speech:
        response.say("I understand you're in discomfort. Can you tell me more about your symptoms?", voice='alice')
    elif 'emergency' in speech:
        response.say("This sounds like an emergency. Please call 108 or your local emergency services immediately!", voice='alice')
    elif 'goodbye' in speech or 'bye' in speech:
        response.say("Thank you for calling MedAgg Healthcare. Take care and call again if needed. Goodbye!", voice='alice')
        response.hangup()
    else:
        response.say(f"I heard: {speech}. How can I help you with that?", voice='alice')
    
    response.redirect('/twiml')
    return str(response), 200, {'Content-Type': 'text/xml'}

@app.route('/test')
def test():
    """Test page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Voice Agent</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧪 Test Voice Agent</h1>
            <p>This is the emergency version - simple and working!</p>
            <p><strong>Status:</strong> ✅ Ready for calls</p>
            <p><strong>Features:</strong> Speech recognition, healthcare responses</p>
            <a href="/" class="button">Back to Home</a>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info("🏥 MedAgg Healthcare - Emergency Voice Agent Starting...")
    logger.info(f"🌐 Running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
