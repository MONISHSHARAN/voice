#!/usr/bin/env python3
"""
Startup script for MedAgg Healthcare Voice Agent
"""

import subprocess
import sys
import os

def main():
    """Start the application"""
    print("🏥 Starting MedAgg Healthcare Voice Agent...")
    
    # Check if main.py exists
    if not os.path.exists('main.py'):
        print("❌ Error: main.py not found!")
        sys.exit(1)
    
    # Start the application
    try:
        subprocess.run([sys.executable, 'main.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()