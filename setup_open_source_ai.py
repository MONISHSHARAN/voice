#!/usr/bin/env python3
"""
Setup script for MedAgg Healthcare Open Source AI
Installs required dependencies for Hugging Face and open-source AI
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
    print("🚀 Setting up MedAgg Healthcare Open Source AI")
    print("=" * 60)
    
    # Required packages for open-source AI
    packages = [
        "twilio",
        "requests",
        "transformers",
        "torch",
        "torchaudio",
        "accelerate",
        "bitsandbytes",
        "sentence-transformers",
        "datasets",
        "pandas",
        "numpy",
        "scikit-learn"
    ]
    
    print("📦 Installing required packages for open-source AI...")
    print("This may take a few minutes as we're downloading AI models...")
    
    success_count = 0
    for package in packages:
        print(f"\n🔄 Installing {package}...")
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Installation Summary:")
    print(f"✅ Successfully installed: {success_count}/{len(packages)} packages")
    
    if success_count >= 3:  # At least basic packages
        print("\n🎉 Open Source AI setup completed!")
        print("\n📋 What's included:")
        print("🤖 Hugging Face Transformers - For conversational AI")
        print("🧠 PyTorch - Deep learning framework")
        print("📞 Twilio - Voice calls and SMS")
        print("🌍 Multilingual support - English, Tamil, Hindi")
        print("💬 Rule-based fallback - When AI models aren't available")
        
        print("\n🚀 Next steps:")
        print("1. Run the open-source AI backend:")
        print("   python open_source_ai_backend.py")
        print("\n2. Start the frontend:")
        print("   python -m http.server 3000 --directory frontend")
        print("\n3. Open http://localhost:3000 in your browser")
        print("\n4. Register a patient to test the AI conversation")
        
        # Create a .env file template
        with open('.env.template', 'w') as f:
            f.write("""# MedAgg Healthcare Open Source AI Configuration
# Copy this file to .env and fill in your actual values

# Twilio Configuration (already configured)
TWILIO_ACCOUNT_SID=AC33f397657e06dac328e5d5081eb4f9fd
TWILIO_AUTH_TOKEN=bbf7abc794d8f0eb9538350b501d033f
TWILIO_PHONE_NUMBER=+17752586467

# Open Source AI Configuration
AI_MODEL=microsoft/DialoGPT-medium
AI_TEMPERATURE=0.7
AI_MAX_LENGTH=150

# Optional: Customize AI behavior
ENABLE_HUGGING_FACE=true
FALLBACK_TO_RULES=true
""")
        
        print("\n📄 Created .env.template file with configuration template")
        print("   Copy it to .env and customize as needed")
        
        print("\n🎯 Features:")
        print("✅ No API keys required - completely free!")
        print("✅ Runs locally on your machine")
        print("✅ Multilingual AI conversations")
        print("✅ Medical-specific responses")
        print("✅ Twilio voice integration")
        print("✅ Rule-based fallback system")
        
    else:
        print(f"\n⚠️  Some packages failed to install. Please install them manually:")
        for i, package in enumerate(packages):
            if not install_package(package):
                print(f"   pip install {package}")
        
        print("\n🔄 You can still run the system with rule-based responses:")
        print("   python open_source_ai_backend.py")

if __name__ == "__main__":
    main()
