#!/usr/bin/env python3
"""
Deploy MedAgg Healthcare System to Heroku
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
    print("🚀 Deploying MedAgg Healthcare System to Heroku")
    print("=" * 60)
    
    # Check if Heroku CLI is installed
    print("🔍 Checking Heroku CLI...")
    heroku_check = run_command("heroku --version", "Checking Heroku CLI")
    if not heroku_check:
        print("❌ Heroku CLI not found. Please install it first:")
        print("   Visit: https://devcenter.heroku.com/articles/heroku-cli")
        return
    
    # Login to Heroku
    print("\n🔐 Logging into Heroku...")
    login_result = run_command("heroku login", "Heroku login")
    if not login_result:
        print("❌ Failed to login to Heroku")
        return
    
    # Create new app
    app_name = "medagg-healthcare-" + str(int(time.time()))[-6:]
    print(f"\n📦 Creating Heroku app: {app_name}...")
    create_result = run_command(f"heroku create {app_name}", f"Creating Heroku app {app_name}")
    if not create_result:
        print("❌ Failed to create Heroku app")
        return
    
    # Set environment variables
    print("\n🔧 Setting environment variables...")
    env_vars = [
        f"heroku config:set HEROKU_APP_NAME={app_name} -a {app_name}",
        f"heroku config:set TWILIO_ACCOUNT_SID=AC33f397657e06dac328e5d5081eb4f9fd -a {app_name}",
        f"heroku config:set TWILIO_AUTH_TOKEN=bbf7abc794d8f0eb9538350b501d033f -a {app_name}",
        f"heroku config:set TWILIO_PHONE_NUMBER=+17752586467 -a {app_name}"
    ]
    
    for env_var in env_vars:
        run_command(env_var, f"Setting environment variable")
    
    # Deploy the application
    print("\n🚀 Deploying application...")
    deploy_result = run_command(f"git add . && git commit -m 'Deploy MedAgg Healthcare System' && git push heroku main", "Deploying to Heroku")
    if not deploy_result:
        print("❌ Failed to deploy to Heroku")
        return
    
    # Get the app URL
    public_url = f"https://{app_name}.herokuapp.com"
    print(f"\n✅ Your MedAgg Healthcare System is deployed!")
    print(f"🌐 Public URL: {public_url}")
    print(f"📞 Webhook URL: {public_url}/twiml")
    
    print("\n🎉 Deployment completed successfully!")
    print("=" * 60)
    print("📋 Next Steps:")
    print("1. Configure your Twilio phone number webhooks:")
    print(f"   - Voice URL: {public_url}/twiml")
    print("   - HTTP Method: POST")
    print("2. Test the system by visiting:")
    print(f"   - Main page: {public_url}")
    print(f"   - Test page: {public_url}/test")
    print("3. Register a patient to test the AI conversation")
    print("=" * 60)
    
    # Update the app.py with the correct URL
    print("\n🔧 Updating app.py with correct URL...")
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Replace the placeholder URL
        content = content.replace(
            "PUBLIC_URL = os.getenv('HEROKU_APP_NAME', 'medagg-healthcare')",
            f"PUBLIC_URL = '{public_url}'"
        )
        
        with open('app.py', 'w') as f:
            f.write(content)
        
        print("✅ app.py updated with correct URL!")
        
    except Exception as e:
        print(f"⚠️  Could not update app.py automatically: {e}")
        print(f"   Please manually update app.py with: {public_url}")

if __name__ == "__main__":
    main()
