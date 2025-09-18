#!/usr/bin/env python3
"""
MedAgg Healthcare Voice Agent - Deepgram Agent API Implementation
Advanced cardiology AI with nova-3-medical and aura-2-vesta-en models
"""

import asyncio
import base64
import json
import os
import logging
import websockets
from dotenv import load_dotenv
from cardiology_functions import FUNCTION_MAP

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
PUBLIC_URL = os.getenv("PUBLIC_URL", "https://web-production-39bb.up.railway.app")

# --- Deepgram Agent API Connection and Handlers ---
def sts_connect():
    """Connect to Deepgram Agent API"""
    if not DEEPGRAM_API_KEY:
        raise Exception("DEEPGRAM_API_KEY not found")

    return websockets.connect(
        "wss://agent.deepgram.com/v1/agent/converse",
        subprotocols=["token", DEEPGRAM_API_KEY]
    )

def load_config():
    """Load Deepgram Agent configuration for cardiology"""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("config.json not found. Ensure it's in the same directory.")
        raise
    except json.JSONDecodeError:
        logger.error("Error decoding config.json. Check file format.")
        raise

async def handle_barge_in(decoded, twilio_ws, streamsid):
    """Handle user speaking interruption"""
    if decoded["type"] == "UserStartedSpeaking":
        clear_message = {
            "event": "clear",
            "streamSid": streamsid
        }
        await twilio_ws.send(json.dumps(clear_message))
        logger.info(f"Sent clear message for stream {streamsid} (barge-in)")

def execute_function_call(func_name, arguments):
    """Execute function call"""
    if func_name in FUNCTION_MAP:
        try:
            result = FUNCTION_MAP[func_name](**arguments)
            logger.info(f"Function call result for {func_name}: {result}")
            return result
        except Exception as e:
            logger.error(f"Error executing function {func_name} with args {arguments}: {e}")
            return {"error": f"Function '{func_name}' failed with: {str(e)}"}
    else:
        result = {"error": f"Unknown function: {func_name}"}
        logger.error(result)
        return result

def create_function_call_response(func_id, func_name, result):
    """Create function call response"""
    return {
        "type": "FunctionCallResponse",
        "id": func_id,
        "name": func_name,
        "content": json.dumps(result)
    }

async def handle_function_call_request(decoded, sts_ws):
    """Handle function call requests from Deepgram Agent"""
    try:
        for function_call in decoded["functions"]:
            func_name = function_call["name"]
            func_id = function_call["id"]
            arguments = json.loads(function_call["arguments"])

            logger.info(f"Function call: {func_name} (ID: {func_id}), arguments: {arguments}")

            result = execute_function_call(func_name, arguments)

            function_result = create_function_call_response(func_id, func_name, result)
            await sts_ws.send(json.dumps(function_result))
            logger.info(f"Sent function result: {function_result}")

    except Exception as e:
        logger.error(f"Error handling function call request: {e}")
        func_id = decoded.get("functions", [{}])[0].get("id", "unknown")
        func_name = decoded.get("functions", [{}])[0].get("name", "unknown")
        error_result = create_function_call_response(
            func_id,
            func_name,
            {"error": f"Function call failed with: {str(e)}"}
        )
        await sts_ws.send(json.dumps(error_result))

async def handle_text_message(decoded, twilio_ws, sts_ws, streamsid):
    """Handle text messages from Deepgram Agent"""
    await handle_barge_in(decoded, twilio_ws, streamsid)

    if decoded["type"] == "FunctionCallRequest":
        await handle_function_call_request(decoded, sts_ws)
    elif decoded["type"] == "AgentSpeaking":
        logger.info(f"Agent speaking: {decoded.get('text', 'No text')}")
    elif decoded["type"] == "AgentStoppedSpeaking":
        logger.info("Agent stopped speaking.")
    elif decoded["type"] == "UtteranceEnd":
        logger.info("Utterance ended.")
    elif decoded["type"] == "Error":
        logger.error(f"Deepgram Agent Error: {decoded.get('message', 'Unknown error')}")
    else:
        logger.debug(f"Unhandled Deepgram Agent message type: {decoded['type']}")

async def sts_sender(sts_ws, audio_queue):
    """Send audio to Deepgram Agent"""
    logger.info("sts_sender started")
    try:
        while True:
            chunk = await audio_queue.get()
            await sts_ws.send(chunk)
    except websockets.exceptions.ConnectionClosedOK:
        logger.info("STS sender: WebSocket connection closed normally.")
    except Exception as e:
        logger.error(f"Error in sts_sender: {e}")

async def sts_receiver(sts_ws, twilio_ws, streamsid_queue):
    """Receive responses from Deepgram Agent"""
    logger.info("sts_receiver started")
    streamsid = await streamsid_queue.get()

    try:
        async for message in sts_ws:
            if isinstance(message, str):
                logger.info(f"Deepgram Agent message: {message}")
                decoded = json.loads(message)
                await handle_text_message(decoded, twilio_ws, sts_ws, streamsid)
                continue

            # Audio response from Deepgram
            raw_mulaw = message

            media_message = {
                "event": "media",
                "streamSid": streamsid,
                "media": {"payload": base64.b64encode(raw_mulaw).decode("ascii")},
            }

            await twilio_ws.send(json.dumps(media_message))
    except websockets.exceptions.ConnectionClosedOK:
        logger.info("STS receiver: WebSocket connection closed normally.")
    except Exception as e:
        logger.error(f"Error in sts_receiver: {e}")

async def twilio_receiver(twilio_ws, audio_queue, streamsid_queue):
    """Receive audio from Twilio"""
    BUFFER_SIZE = 20 * 160  # 20 messages * 160 bytes/message = 0.4 seconds of audio
    inbuffer = bytearray(b"")

    logger.info("twilio_receiver started")
    try:
        async for message in twilio_ws:
            data = json.loads(message)
            event = data.get("event")

            if event == "start":
                logger.info(f"Twilio Call started: {data.get('streamSid')}")
                streamsid = data["start"]["streamSid"]
                streamsid_queue.put_nowait(streamsid)
            elif event == "connected":
                logger.info("Twilio WebSocket connected.")
                continue
            elif event == "media":
                media = data["media"]
                chunk = base64.b64decode(media["payload"])
                if media["track"] == "inbound":
                    inbuffer.extend(chunk)
            elif event == "stop":
                logger.info(f"Twilio Call stopped: {data.get('streamSid')}")
                break

            while len(inbuffer) >= BUFFER_SIZE:
                chunk = inbuffer[:BUFFER_SIZE]
                audio_queue.put_nowait(chunk)
                inbuffer = inbuffer[BUFFER_SIZE:]
    except websockets.exceptions.ConnectionClosedOK:
        logger.info("Twilio receiver: WebSocket connection closed normally.")
    except Exception as e:
        logger.error(f"Error in twilio_receiver: {e}")

async def twilio_handler(websocket, path):
    """Main handler for Twilio WebSocket connection"""
    logger.info(f"Incoming WebSocket connection on path: {path}")
    if path == "/twilio":
        audio_queue = asyncio.Queue()
        streamsid_queue = asyncio.Queue()

        try:
            async with sts_connect() as sts_ws:
                logger.info("✅ Connected to Deepgram Agent API")
                
                config_message = load_config()
                await sts_ws.send(json.dumps(config_message))
                logger.info("✅ Deepgram Agent config sent (nova-3-medical + aura-2-vesta-en)")

                await asyncio.gather(
                    sts_sender(sts_ws, audio_queue),
                    sts_receiver(sts_ws, websocket, streamsid_queue),
                    twilio_receiver(websocket, audio_queue, streamsid_queue),
                )
        except websockets.exceptions.ConnectionClosed as e:
            logger.info(f"Deepgram Agent connection closed: {e}")
        except Exception as e:
            logger.error(f"Error in twilio_handler: {e}")
        finally:
            logger.info("Twilio handler finished.")
    else:
        logger.warning(f"Unhandled WebSocket path: {path}")
        await websocket.close(code=1000, reason="Invalid path")

async def start_websocket_server():
    """Starts the WebSocket server on port 5001"""
    logger.info("Starting WebSocket server on 0.0.0.0:5001")
    server = await websockets.serve(twilio_handler, "0.0.0.0", 5001)
    await server.wait_closed()

if __name__ == "__main__":
    logger.info("MedAgg Healthcare Voice Agent - WebSocket Server Starting...")
    logger.info("Using Deepgram Agent API with nova-3-medical and aura-2-vesta-en")
    logger.info("Advanced function calling for cardiology evaluation")
    asyncio.run(start_websocket_server())