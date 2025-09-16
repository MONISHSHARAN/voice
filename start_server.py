#!/usr/bin/env python3
"""
Startup script for MedAgg Healthcare Voice Agent
Runs both Flask app and WebSocket server
"""

import os
import subprocess
import threading
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_flask_app():
    """Run the Flask application"""
    logger.info("🚀 Starting Flask application...")
    try:
        subprocess.run(["python", "app.py"], check=True)
    except Exception as e:
        logger.error(f"❌ Flask app failed: {e}")

def run_websocket_server():
    """Run the WebSocket server"""
    logger.info("🚀 Starting WebSocket server...")
    try:
        subprocess.run(["python", "websocket_server.py"], check=True)
    except Exception as e:
        logger.error(f"❌ WebSocket server failed: {e}")

def main():
    """Start both servers"""
    logger.info("🏥 MedAgg Healthcare Voice Agent - Starting Complete System")
    logger.info("=" * 70)
    
    # Start WebSocket server in background thread
    websocket_thread = threading.Thread(target=run_websocket_server, daemon=True)
    websocket_thread.start()
    
    # Wait a moment for WebSocket server to start
    time.sleep(2)
    
    # Start Flask app (this will block)
    run_flask_app()

if __name__ == '__main__':
    main()
