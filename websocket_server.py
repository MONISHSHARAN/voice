#!/usr/bin/env python3
"""
WebSocket Server for MedAgg Healthcare Voice Agent
Runs separately from Flask app for production deployment
"""

import asyncio
import websockets
import logging
from main import twilio_handler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Start WebSocket server"""
    logger.info("🎤 Starting WebSocket server for Twilio media streaming")
    server = await websockets.serve(twilio_handler, "0.0.0.0", 5001)
    logger.info("🎤 WebSocket server started on port 5001")
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())