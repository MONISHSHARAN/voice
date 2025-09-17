#!/usr/bin/env python3
"""
MedAgg Healthcare Voice Agent - Production Entry Point
Handles both Flask app and WebSocket server for Render deployment
"""

import asyncio
import threading
import logging
from main import app, logger, PUBLIC_URL, twilio_handler
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO)

def start_websocket_server():
    """Start WebSocket server in background thread"""
    def run_websocket():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        server = loop.run_until_complete(websockets.serve(twilio_handler, "0.0.0.0", 5001))
        logger.info("🎤 WebSocket server started on port 5001")
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
    logger.info(f"🔗 WebSocket URL: wss://{PUBLIC_URL.replace('https://', '')}/stream")
    logger.info("💰 Deepgram Agent API: ✅ Configured with advanced capabilities")
    logger.info("=" * 70)
    
    # Start WebSocket server in background
    start_websocket_server()
    
    # Start Flask app
    logger.info("🌐 Starting Flask app on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=False)