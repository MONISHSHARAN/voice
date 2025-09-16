#!/usr/bin/env python3
"""
Configuration file for MedAgg Healthcare POC
Update these settings with your actual credentials
"""

# Email Configuration (Gmail SMTP)
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",  # Replace with your Gmail
    "sender_password": "your_app_password"   # Replace with your Gmail App Password
}

# Twilio Configuration (Get these from https://console.twilio.com/)
TWILIO_CONFIG = {
    "account_sid": "your_twilio_account_sid",
    "auth_token": "your_twilio_auth_token",
    "phone_number": "+1234567890"  # Your Twilio phone number
}

# Instructions for setup:
"""
1. EMAIL SETUP (Gmail):
   - Go to Gmail Settings > Security
   - Enable 2-Factor Authentication
   - Generate an App Password
   - Use the App Password in sender_password

2. TWILIO SETUP:
   - Sign up at https://www.twilio.com/
   - Get your Account SID and Auth Token from console
   - Buy a phone number from Twilio
   - Update the phone_number with your Twilio number

3. FOR TESTING WITHOUT REAL CALLS:
   - The system will simulate calls if Twilio is not configured
   - Email will be simulated if SMTP is not configured
"""


