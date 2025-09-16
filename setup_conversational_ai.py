#!/usr/bin/env python3
"""
Setup script for MedAgg Healthcare Conversational AI
Installs required dependencies and configures the system
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    print("🚀 Setting up MedAgg Healthcare Conversational AI")
    print("=" * 60)
    
    # Required packages
    packages = [
        "twilio",
        "openai",
        "requests",
        "websockets",
        "asyncio"
    ]
    
    print("📦 Installing required packages...")
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Installation Summary:")
    print(f"✅ Successfully installed: {success_count}/{len(packages)} packages")
    
    if success_count == len(packages):
        print("\n🎉 All packages installed successfully!")
        print("\n📋 Next steps:")
        print("1. Set your OpenAI API key:")
        print("   export OPENAI_API_KEY='your-openai-api-key-here'")
        print("   or")
        print("   set OPENAI_API_KEY=your-openai-api-key-here  (Windows)")
        print("\n2. Run the conversational AI backend:")
        print("   python conversational_ai_backend.py")
        print("\n3. Start the frontend:")
        print("   python -m http.server 3000 --directory frontend")
        print("\n4. Open http://localhost:3000 in your browser")
        
        # Create a .env file template
        with open('.env.template', 'w') as f:
            f.write("""# MedAgg Healthcare Conversational AI Configuration
# Copy this file to .env and fill in your actual values

# Twilio Configuration (already configured)
TWILIO_ACCOUNT_SID=AC33f397657e06dac328e5d5081eb4f9fd
TWILIO_AUTH_TOKEN=bbf7abc794d8f0eb9538350b501d033f
TWILIO_PHONE_NUMBER=+17752586467

# OpenAI Configuration (REQUIRED - get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Customize AI behavior
AI_MODEL=gpt-4
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=500
""")
        
        print("\n📄 Created .env.template file with configuration template")
        print("   Copy it to .env and fill in your OpenAI API key")
        
    else:
        print(f"\n⚠️  Some packages failed to install. Please install them manually:")
        for i, package in enumerate(packages):
            if not install_package(package):
                print(f"   pip install {package}")

if __name__ == "__main__":
    main()
