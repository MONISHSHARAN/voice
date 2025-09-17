#!/usr/bin/env python3
"""
MedAgg Healthcare Voice Agent - Production Entry Point
Based on Deepgram Official Documentation
https://developers.deepgram.com/docs/twilio-and-deepgram-voice-agent
"""

import asyncio
import threading
import logging
import websockets
from main import app, logger, PUBLIC_URL, router

# Configure logging
logging.basicConfig(level=logging.INFO)

def start_websocket_server():
    """Start WebSocket server in background thread - Based on official documentation"""
    def run_websocket():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # Based on documentation - use localhost for development, 0.0.0.0 for production
        server = loop.run_until_complete(websockets.serve(router, "0.0.0.0", 5000))
        logger.info("🎤 WebSocket server started on port 5000")
        loop.run_forever()
    
    websocket_thread = threading.Thread(target=run_websocket, daemon=True)
    websocket_thread.start()
    return websocket_thread

if __name__ == '__main__':
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
    
    # Start WebSocket server in background
    start_websocket_server()
    
    # Start Flask app
    logger.info("🌐 Starting Flask app on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=False)