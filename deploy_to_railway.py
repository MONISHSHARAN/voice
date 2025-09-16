#!/usr/bin/env python3
"""
Deploy MedAgg Healthcare System to Railway
"""

import subprocess
import os
import json
import time

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def main():
    print("🚀 Deploying MedAgg Healthcare System to Railway")
    print("=" * 60)
    
    # Check if Railway CLI is installed
    print("🔍 Checking Railway CLI...")
    railway_check = run_command("railway --version", "Checking Railway CLI")
    if not railway_check:
        print("❌ Railway CLI not found. Please install it first:")
        print("   npm install -g @railway/cli")
        print("   or visit: https://docs.railway.app/develop/cli")
        return
    
    # Login to Railway
    print("\n🔐 Logging into Railway...")
    login_result = run_command("railway login", "Railway login")
    if not login_result:
        print("❌ Failed to login to Railway")
        return
    
    # Create new project
    print("\n📦 Creating Railway project...")
    project_result = run_command("railway init", "Creating Railway project")
    if not project_result:
        print("❌ Failed to create Railway project")
        return
    
    # Deploy the application
    print("\n🚀 Deploying application...")
    deploy_result = run_command("railway up", "Deploying to Railway")
    if not deploy_result:
        print("❌ Failed to deploy to Railway")
        return
    
    # Get the public URL
    print("\n🔗 Getting public URL...")
    url_result = run_command("railway domain", "Getting public URL")
    if url_result:
        public_url = url_result.strip()
        print(f"✅ Your MedAgg Healthcare System is deployed!")
        print(f"🌐 Public URL: {public_url}")
        print(f"📞 Webhook URL: {public_url}/twiml")
        
        # Update the backend with the public URL
        print("\n🔧 Updating backend with public URL...")
        try:
            with open('deployed_backend.py', 'r') as f:
                content = f.read()
            
            # Replace the placeholder URL
            content = content.replace(
                "PUBLIC_URL = os.getenv('RAILWAY_PUBLIC_DOMAIN', 'https://medagg-healthcare-production.up.railway.app')",
                f"PUBLIC_URL = '{public_url}'"
            )
            
            with open('deployed_backend.py', 'w') as f:
                f.write(content)
            
            print("✅ Backend updated with public URL!")
            
        except Exception as e:
            print(f"⚠️  Could not update backend automatically: {e}")
            print(f"   Please manually update deployed_backend.py with: {public_url}")
        
        print("\n🎉 Deployment completed successfully!")
        print("=" * 60)
        print("📋 Next Steps:")
        print("1. Configure your Twilio phone number webhooks:")
        print(f"   - Voice URL: {public_url}/twiml")
        print("   - HTTP Method: POST")
        print("2. Test the system by registering a patient")
        print("3. The AI will call the patient and have a conversation")
        print("=" * 60)
        
    else:
        print("❌ Could not get public URL")

if __name__ == "__main__":
    main()
