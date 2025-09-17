#!/usr/bin/env python3
"""
MedAgg Healthcare Voice Agent - App Entry Point
This file ensures compatibility with Render deployment
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main application
if __name__ == '__main__':
    try:
        # Import the Flask app from main.py
        from main import app, logger, PUBLIC_URL
        
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
        
        # Start Flask app
        logger.info("🌐 Starting Flask app on port 5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except ImportError as e:
        print(f"❌ Error: Could not import from main.py: {e}")
        print("Available files:", os.listdir('.'))
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)
