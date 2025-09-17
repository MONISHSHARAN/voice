#!/usr/bin/env python3
"""
MedAgg Healthcare Voice Agent - Startup Script
Runs both HTTP and WebSocket servers
"""

import subprocess
import sys
import time
import logging
import threading
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_websocket_server():
    """Run WebSocket server"""
    try:
        logger.info("Starting WebSocket server...")
        subprocess.run([sys.executable, "main.py"], check=True)
    except Exception as e:
        logger.error(f"Error running WebSocket server: {e}")

def run_http_server():
    """Run HTTP server"""
    try:
        logger.info("Starting HTTP server...")
        subprocess.run([sys.executable, "http_server.py"], check=True)
    except Exception as e:
        logger.error(f"Error running HTTP server: {e}")

def main():
    """Main function"""
    logger.info("🏥 MedAgg Healthcare - Starting Voice Agent")
    logger.info("=" * 50)
    
    # Start WebSocket server in background
    ws_thread = threading.Thread(target=run_websocket_server, daemon=True)
    ws_thread.start()
    
    # Wait a moment for WebSocket server to start
    time.sleep(2)
    
    # Start HTTP server in foreground
    run_http_server()

if __name__ == "__main__":
    main()