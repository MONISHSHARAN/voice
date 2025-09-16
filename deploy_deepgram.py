#!/usr/bin/env python3
"""
Deploy MedAgg Healthcare with Deepgram Voice Agent
"""

import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_deepgram.txt"], check=True)
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def setup_environment():
    """Setup environment variables"""
    print("🔧 Setting up environment...")
    
    env_vars = {
        'DEEPGRAM_API_KEY': 'your_deepgram_api_key_here',
        'TWILIO_ACCOUNT_SID': 'AC33f397657e06dac328e5d5081eb4f9fd',
        'TWILIO_AUTH_TOKEN': 'bbf7abc794d8f0eb9538350b501d033f',
        'TWILIO_PHONE_NUMBER': '+17752586467',
        'RENDER_EXTERNAL_URL': 'https://voice-95g5.onrender.com'
    }
    
    print("Environment variables needed:")
    for key, value in env_vars.items():
        print(f"  {key}={value}")
    
    return True

def test_deepgram_connection():
    """Test Deepgram connection"""
    print("🧪 Testing Deepgram connection...")
    try:
        import requests
        
        # Test with a simple audio file
        test_audio = b"test audio data"
        
        response = requests.post(
            'https://api.deepgram.com/v1/listen',
            headers={'Authorization': f'Token {os.getenv("DEEPGRAM_API_KEY", "test")}'},
            data=test_audio,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Deepgram connection test passed")
            return True
        else:
            print(f"⚠️ Deepgram connection test returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️ Deepgram connection test failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("🏥 MedAgg Healthcare - Deepgram Voice Agent Deployment")
    print("=" * 60)
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        return False
    
    # Setup environment
    setup_environment()
    
    # Test Deepgram connection
    test_deepgram_connection()
    
    print("\n🚀 Deployment Steps:")
    print("1. Get Deepgram API key from: https://console.deepgram.com/")
    print("2. Set DEEPGRAM_API_KEY environment variable")
    print("3. Deploy to Render with: python deepgram_voice_agent.py")
    print("4. Configure Twilio webhook to: https://voice-95g5.onrender.com/twiml")
    print("5. Test the system!")
    
    print("\n✅ Deepgram Voice Agent is ready for deployment!")
    return True

if __name__ == "__main__":
    main()
