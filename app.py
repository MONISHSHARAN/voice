#!/usr/bin/env python3
"""
MedAgg Healthcare Voice Agent - App Entry Point
This file ensures compatibility with Render deployment
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main application
if __name__ == '__main__':
    try:
        from main import main
        import asyncio
        asyncio.run(main())
    except ImportError:
        print("❌ Error: Could not import main.py")
        print("Available files:", os.listdir('.'))
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)
