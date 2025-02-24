#!/usr/bin/env python3
"""
start_datasource_manager.py

This script initializes and runs the DataSourceManager.
It automatically adds the parent directory (the project root) to sys.path so that 
the 'brainboost_data_source_package' is always importable, regardless of the working directory.
The DataSourceManager publishes its registration on the "manager_registry" channel
periodically (every 5 seconds), so that any client (e.g. a PyQt frontend) can eventually
receive its network connection information.
"""

import os
import sys

# Determine the current directory of this script.
current_dir = os.path.dirname(os.path.abspath(__file__))
# Compute the parent directory (project root) which should contain the package.
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
# Add the project root to sys.path if it isn't already present.
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import redis
import json
import socket
import time
import threading
from brainboost_configuration_package.BBConfig import BBConfig
from brainboost_data_source_package.data_source_manager.DataSourceManager import DataSourceManager

def get_local_ip():
    """
    Returns the local IP address of the machine.
    """
    try:
        # Connect to a dummy external address to get the local IP.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        print(f"Error obtaining local IP address: {e}")
        ip = '127.0.0.1'  # Fallback to localhost.
    return ip

def main():
    # Determine the local IP address.
    local_ip = get_local_ip()
    print(f"Local IP address determined: {local_ip}")
    
    # Initialize Redis connection.
    redis_host = BBConfig.get('redis_server_ip')
    redis_port = BBConfig.get('redis_server_port')
    try:
        redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)
        redis_client.ping()
        print(f"Connected to Redis at {redis_host}:{redis_port}")
    except redis.ConnectionError as e:
        print(f"Failed to connect to Redis at {redis_host}:{redis_port}: {e}")
        sys.exit(1)
    
    # Create a unique command channel based on the local IP.
    command_channel = f"datasource_commands_{local_ip}"
    
    # Instantiate the DataSourceManager with the specified command channel.
    manager = DataSourceManager(command_channel=command_channel)
    
    # Start the DataSourceManager in a separate daemon thread so that it listens for commands.
    manager_thread = threading.Thread(target=manager.start, daemon=True)
    manager_thread.start()
    print(f"DataSourceManager started and listening on channel: '{command_channel}'")
    
    try:
        # Keep the main thread alive so that the manager can run continuously.
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down DataSourceManager...")
        sys.exit(0)

if __name__ == "__main__":
    main()
