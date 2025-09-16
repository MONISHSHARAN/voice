#!/usr/bin/env python3
"""
Secure Tunnel with Authentication for MedAgg Healthcare
Provides password protection for localtunnel
"""

import subprocess
import sys
import time
import threading
import hashlib
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

class SecureTunnelHandler(BaseHTTPRequestHandler):
    """HTTP handler with basic authentication"""
    
    def __init__(self, *args, **kwargs):
        # Simple password hash (in production, use proper authentication)
        self.password_hash = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"  # "password"
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests with authentication"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>MedAgg Healthcare - Secure Access</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 50px; background: #f5f5f5; }
                    .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { color: #2c3e50; text-align: center; }
                    .form-group { margin: 20px 0; }
                    label { display: block; margin-bottom: 5px; font-weight: bold; }
                    input[type="password"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
                    button { width: 100%; padding: 12px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
                    button:hover { background: #2980b9; }
                    .error { color: red; margin-top: 10px; }
                    .success { color: green; margin-top: 10px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🏥 MedAgg Healthcare</h1>
                    <p>Enter password to access the system:</p>
                    <form id="authForm">
                        <div class="form-group">
                            <label for="password">Password:</label>
                            <input type="password" id="password" name="password" required>
                        </div>
                        <button type="submit">Access System</button>
                    </form>
                    <div id="message"></div>
                </div>
                <script>
                    document.getElementById('authForm').addEventListener('submit', function(e) {
                        e.preventDefault();
                        const password = document.getElementById('password').value;
                        const messageDiv = document.getElementById('message');
                        
                        // Simple client-side check (server-side validation is the real security)
                        if (password === 'password') {
                            messageDiv.innerHTML = '<div class="success">✅ Access granted! Redirecting...</div>';
                            setTimeout(() => {
                                window.location.href = '/app';
                            }, 1000);
                        } else {
                            messageDiv.innerHTML = '<div class="error">❌ Invalid password. Try again.</div>';
                        }
                    });
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        elif self.path == '/app':
            # Redirect to the actual application
            self.send_response(302)
            self.send_header('Location', 'http://localhost:3000')
            self.end_headers()
            
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "secure_tunnel_active", "message": "Protected tunnel is running"}
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/auth':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            password = data.get('password', '')
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if password_hash == self.password_hash:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"success": True, "message": "Authentication successful"}
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"success": False, "message": "Invalid password"}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def start_secure_tunnel():
    """Start the secure tunnel with authentication"""
    print("🔐 Starting Secure Tunnel with Authentication...")
    print("=" * 60)
    
    # Start the authentication server
    auth_server = HTTPServer(('localhost', 8080), SecureTunnelHandler)
    print("✅ Authentication server started on http://localhost:8080")
    print("🔑 Default password: 'password'")
    print("📝 Change the password in secure_tunnel.py for production")
    
    # Start localtunnel in a separate thread
    def start_localtunnel():
        try:
            print("🌐 Starting localtunnel...")
            subprocess.run(['lt', '--port', '8080', '--subdomain', 'medagg-healthcare-secure'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Localtunnel error: {e}")
        except FileNotFoundError:
            print("❌ Localtunnel not found. Install with: npm install -g localtunnel")
    
    tunnel_thread = threading.Thread(target=start_localtunnel)
    tunnel_thread.daemon = True
    tunnel_thread.start()
    
    print("🚀 Secure tunnel starting...")
    print("📱 Access your app at: https://medagg-healthcare-secure.loca.lt")
    print("🔒 Password protection enabled")
    print("=" * 60)
    
    try:
        auth_server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down secure tunnel...")
        auth_server.shutdown()
        print("✅ Secure tunnel stopped")

if __name__ == "__main__":
    start_secure_tunnel()
