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
        logger.info("Starting Flask HTTP server...")
        subprocess.run([sys.executable, "flask_server.py"], check=True)
    except Exception as e:
        logger.error(f"Error running HTTP server: {e}")

def main():
    """Main function"""
    logger.info("🏥 MedAgg Healthcare - Starting Voice Agent")
    logger.info("=" * 50)
    
    # Start HTTP server first (for healthcheck)
    logger.info("Starting HTTP server for healthcheck...")
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    # Wait for HTTP server to start
    time.sleep(3)
    
    # Start WebSocket server in background
    logger.info("Starting WebSocket server...")
    ws_thread = threading.Thread(target=run_websocket_server, daemon=True)
    ws_thread.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Shutting down...")

if __name__ == "__main__":
    main()