#!/usr/bin/env python3
"""
MedAgg Healthcare Voice Agent - WebSocket Server Entry Point
Based on official Deepgram documentation
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the WebSocket server
if __name__ == '__main__':
    try:
        # Import the WebSocket server from server.py
        from server import main
        
        print("🏥 MedAgg Healthcare - CARDIOLOGY VOICE AGENT")
        print("=" * 70)
        print("🎤 Deepgram Agent API with advanced function calling")
        print("❤️ Cardiology-focused UFE questionnaire conversation")
        print("📞 Twilio integration with WebSocket streaming")
        print("🔧 Function calling: assess_chest_pain, assess_breathing, schedule_appointment")
        print("🚨 Emergency handling with immediate response")
        print("🌐 WebSocket Server: ws://0.0.0.0:5000")
        print("🔗 Twilio WebSocket URL: wss://voice-95g5.onrender.com/twilio")
        print("💰 Deepgram Agent API: ✅ Configured with advanced capabilities")
        print("=" * 70)
        
        # Start WebSocket server
        main()
        
    except ImportError as e:
        print(f"❌ Error: Could not import from server.py: {e}")
        print("Available files:", os.listdir('.'))
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting WebSocket server: {e}")
        sys.exit(1)