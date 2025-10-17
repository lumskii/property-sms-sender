#!/usr/bin/env python3
"""
Simple test script to verify the master agent is working
"""

import sys
import os
sys.path.append('/workspaces/property-sms-sender/master-agent')

from master_agent import MasterAgent
import threading
import time

def run_server():
    print("Starting Master Agent server...")
    agent = MasterAgent()
    try:
        agent.app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    print("Testing Master Agent...")
    
    # Start server in background
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(3)
    
    # Test API endpoints
    import requests
    try:
        response = requests.get('http://localhost:5000/api/status', timeout=5)
        print(f"✓ API Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"✗ API Error: {e}")
    
    print("Server is running. Access at http://localhost:5000")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping server...")
        sys.exit(0)