
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the app
from app import start_heroku_backend

if __name__ == "__main__":
    start_heroku_backend()
