#!/usr/bin/env python3
"""
Deploy MedAgg Healthcare System to Railway (Simple Method)
"""

import subprocess
import os
import json
import time
import webbrowser

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
    
    # Create a simple deployment package
    print("📦 Creating deployment package...")
    
    # Create a simple start script
    with open('start.py', 'w') as f:
        f.write('''
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the app
from app import start_heroku_backend

if __name__ == "__main__":
    start_heroku_backend()
''')
    
    print("✅ Deployment package created!")
    
    # Instructions for manual deployment
    print("\n📋 MANUAL DEPLOYMENT INSTRUCTIONS:")
    print("=" * 60)
    print("1. Go to https://railway.app/")
    print("2. Sign up/Login with GitHub")
    print("3. Click 'New Project'")
    print("4. Select 'Deploy from GitHub repo'")
    print("5. Connect your GitHub account")
    print("6. Select this repository")
    print("7. Railway will automatically detect Python and deploy")
    print("8. Once deployed, you'll get a public URL like:")
    print("   https://your-app-name.up.railway.app")
    print("=" * 60)
    
    # Create a GitHub repository setup script
    print("\n🔧 Setting up for GitHub deployment...")
    
    # Initialize git if not already done
    if not os.path.exists('.git'):
        run_command("git init", "Initializing git repository")
        run_command("git add .", "Adding files to git")
        run_command('git commit -m "Initial commit - MedAgg Healthcare System"', "Creating initial commit")
    
    print("✅ Git repository ready!")
    print("\n📋 NEXT STEPS:")
    print("1. Push to GitHub:")
    print("   - Create a new repository on GitHub")
    print("   - Run: git remote add origin <your-github-repo-url>")
    print("   - Run: git push -u origin main")
    print("2. Deploy to Railway:")
    print("   - Follow the manual instructions above")
    print("3. Configure Twilio webhooks with the Railway URL")
    
    # Open Railway in browser
    print("\n🌐 Opening Railway in your browser...")
    try:
        webbrowser.open("https://railway.app/")
    except:
        print("Please manually open: https://railway.app/")

if __name__ == "__main__":
    main()
