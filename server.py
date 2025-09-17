#!/usr/bin/env python3
"""
MedAgg Healthcare Voice Agent - Standalone WebSocket Server
Based on official Deepgram documentation: https://developers.deepgram.com/docs/twilio-and-deepgram-voice-agent
"""

import asyncio
import base64
import json
import sys
import websockets
import ssl
import os
from dotenv import load_dotenv
from cardiology_functions import FUNCTION_MAP

load_dotenv()

def sts_connect():
    """Connect to Deepgram Agent API - Based on official documentation"""
    api_key = os.getenv('DEEPGRAM_API_KEY')
    if not api_key:
        raise ValueError("DEEPGRAM_API_KEY environment variable is not set")
    
    sts_ws = websockets.connect(
        "wss://agent.deepgram.com/v1/agent/converse",
        subprotocols=["token", api_key]
    )
    return sts_ws

def load_config():
    """Load Deepgram Agent configuration for cardiology"""
    with open("config.json", "r") as f:
        return json.load(f)

async def twilio_handler(twilio_ws):
    """Main handler for Twilio WebSocket connection - Based on official documentation"""
    audio_queue = asyncio.Queue()
    streamsid_queue = asyncio.Queue()

    async with sts_connect() as sts_ws:
        # Send configuration to Deepgram Agent
        config_message = load_config()
        await sts_ws.send(json.dumps(config_message))

        # Start all async tasks
        await asyncio.wait(
            [
                asyncio.ensure_future(sts_sender(sts_ws, audio_queue)),
                asyncio.ensure_future(sts_receiver(sts_ws, twilio_ws, streamsid_queue)),
                asyncio.ensure_future(twilio_receiver(twilio_ws, audio_queue, streamsid_queue)),
            ]
        )

        await twilio_ws.close()

async def sts_sender(sts_ws, audio_queue):
    """Send audio to Deepgram Agent - Based on official documentation"""
    print("sts_sender started")
    while True:
        chunk = await audio_queue.get()
        await sts_ws.send(chunk)

async def sts_receiver(sts_ws, twilio_ws, streamsid_queue):
    """Receive responses from Deepgram Agent - Based on official documentation"""
    print("sts_receiver started")
    # Wait for stream SID from Twilio
    streamsid = await streamsid_queue.get()
    
    async for message in sts_ws:
        if type(message) is str:
            print(message)
            # Handle barge-in
            decoded = json.loads(message)
            if decoded['type'] == 'UserStartedSpeaking':
                clear_message = {
                    "event": "clear",
                    "streamSid": streamsid
                }
                await twilio_ws.send(json.dumps(clear_message))
            continue

        # Audio response from Deepgram - convert to Twilio format
        raw_mulaw = message
        
        # Construct Twilio media message
        media_message = {
            "event": "media",
            "streamSid": streamsid,
            "media": {"payload": base64.b64encode(raw_mulaw).decode("ascii")}
        }
        
        # Send TTS audio to Twilio
        await twilio_ws.send(json.dumps(media_message))

async def twilio_receiver(twilio_ws, audio_queue, streamsid_queue):
    """Receive audio from Twilio - Based on official documentation"""
    print("twilio_receiver started")
    # Twilio sends 160 byte messages (20ms of audio each)
    # Buffer 20 messages = 0.4 seconds for better throughput
    BUFFER_SIZE = 20 * 160
    inbuffer = bytearray(b"")
    
    async for message in twilio_ws:
        try:
            data = json.loads(message)
            
            if data["event"] == "start":
                print("got our streamsid")
                start = data["start"]
                streamsid = start["streamSid"]
                streamsid_queue.put_nowait(streamsid)
            elif data["event"] == "connected":
                continue
            elif data["event"] == "media":
                media = data["media"]
                chunk = base64.b64decode(media["payload"])
                if media["track"] == "inbound":
                    inbuffer.extend(chunk)
            elif data["event"] == "stop":
                break
            
            # Send buffered audio to Deepgram
            while len(inbuffer) >= BUFFER_SIZE:
                chunk = inbuffer[:BUFFER_SIZE]
                audio_queue.put_nowait(chunk)
                inbuffer = inbuffer[BUFFER_SIZE:]
        except Exception as e:
            print(f"Error in twilio_receiver: {e}")
            break

async def router(websocket, path):
    """Route WebSocket connections - Based on official documentation"""
    print(f"Incoming connection on path: {path}")
    if path == "/twilio":
        print("Starting Twilio handler")
        await twilio_handler(websocket)

def main():
    """Main function to start WebSocket server"""
    # Use this if not using ssl
    server = websockets.serve(router, "0.0.0.0", 5000)
    print("Server starting on ws://0.0.0.0:5000")
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    sys.exit(main() or 0)
