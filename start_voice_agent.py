#!/usr/bin/env python3
"""
Start both Flask app and WebSocket server for MedAgg Voice Agent
"""

import subprocess
import sys
import time
import os
import signal
import threading

def start_websocket_server():
    """Start the WebSocket server"""
    print("🚀 Starting WebSocket server...")
    try:
        process = subprocess.Popen([
            sys.executable, "websocket_server_fix.py"
        ])
        print("✅ WebSocket server started")
        return process
    except Exception as e:
        print(f"❌ Failed to start WebSocket server: {e}")
        return None

def start_flask_app():
    """Start the Flask app"""
    print("🚀 Starting Flask app...")
    try:
        process = subprocess.Popen([
            sys.executable, "app.py"
        ])
        print("✅ Flask app started")
        return process
    except Exception as e:
        print(f"❌ Failed to start Flask app: {e}")
        return None

def main():
    """Main function to start both servers"""
    print("🏥 MedAgg Healthcare - Starting Voice Agent")
    print("=" * 50)
    
    # Start WebSocket server
    ws_process = start_websocket_server()
    if not ws_process:
        print("❌ Cannot start without WebSocket server")
        return
    
    # Wait a moment for WebSocket to start
    time.sleep(2)
    
    # Start Flask app
    flask_process = start_flask_app()
    if not flask_process:
        print("❌ Cannot start without Flask app")
        ws_process.terminate()
        return
    
    print("\n🎉 Both servers started successfully!")
    print("🌐 Flask app: http://localhost:8000")
    print("🔗 WebSocket: ws://localhost:5000")
    print("\nPress Ctrl+C to stop both servers")
    
    try:
        # Wait for both processes
        while True:
            time.sleep(1)
            if ws_process.poll() is not None:
                print("❌ WebSocket server stopped")
                break
            if flask_process.poll() is not None:
                print("❌ Flask app stopped")
                break
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        ws_process.terminate()
        flask_process.terminate()
        print("✅ Servers stopped")

if __name__ == "__main__":
    main()
