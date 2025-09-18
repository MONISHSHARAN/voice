#!/usr/bin/env python3
"""
Test healthcheck endpoint
"""

import requests
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_healthcheck():
    """Test healthcheck endpoint"""
    try:
        # Test local healthcheck
        response = requests.get("http://localhost:5000/health", timeout=10)
        logger.info(f"Healthcheck status: {response.status_code}")
        logger.info(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Healthcheck test failed: {e}")
        return False

def test_main_page():
    """Test main page"""
    try:
        response = requests.get("http://localhost:5000/", timeout=10)
        logger.info(f"Main page status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Main page test failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("Testing healthcheck endpoints...")
    
    # Wait a moment for server to start
    time.sleep(5)
    
    health_ok = test_healthcheck()
    main_ok = test_main_page()
    
    if health_ok and main_ok:
        logger.info("✅ All tests passed!")
    else:
        logger.error("❌ Some tests failed!")
