#!/usr/bin/env python3
"""
Quick GitHub Deployment Script for MedAgg Healthcare
"""

import subprocess
import os
import sys

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return None

def main():
    print("🚀 QUICK GITHUB DEPLOYMENT - MedAgg Healthcare")
    print("=" * 60)
    
    # Step 1: Initialize Git
    if not os.path.exists('.git'):
        run_command('git init', 'Initializing Git repository')
    else:
        print("✅ Git repository already exists")
    
    # Step 2: Add all files
    run_command('git add .', 'Adding all files to Git')
    
    # Step 3: Commit
    run_command('git commit -m "Initial commit: MedAgg Healthcare POC with Conversational AI"', 'Committing files')
    
    # Step 4: Create GitHub repository (you'll need to do this manually)
    print("\n📋 MANUAL STEPS REQUIRED:")
    print("1. Go to https://github.com/new")
    print("2. Create a new repository named 'medagg-healthcare'")
    print("3. Copy the repository URL")
    print("4. Run these commands:")
    print("   git remote add origin https://github.com/YOUR_USERNAME/medagg-healthcare.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    
    print("\n🌐 RENDER DEPLOYMENT:")
    print("1. Go to https://render.com")
    print("2. Connect your GitHub account")
    print("3. Select 'medagg-healthcare' repository")
    print("4. Use these settings:")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: python app.py")
    print("   - Environment Variables:")
    print("     TWILIO_ACCOUNT_SID=AC33f397657e06dac328e5d5081eb4f9fd")
    print("     TWILIO_AUTH_TOKEN=bbf7abc794d8f0eb9538350b501d033f")
    print("     TWILIO_PHONE_NUMBER=+17752586467")
    print("     PORT=8000")
    
    print("\n🔧 TUNNEL PASSWORD SOLUTION:")
    print("Your tunnel password is: 'password'")
    print("To change it, edit the password_hash in secure_tunnel.py")
    
    print("\n✅ READY FOR DEPLOYMENT!")
    print("=" * 60)

if __name__ == "__main__":
    main()