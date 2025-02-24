#!/usr/bin/env python3
"""
start_datasource_manager.py

This script initializes and runs the DataSourceManager.
It automatically adjusts sys.path so that the package is importable whether the script is run
from the repository root or from within the package folder.
The DataSourceManager publishes its registration on the "manager_registry" channel
periodically (every 5 seconds), so that any client (e.g. a PyQt frontend) can eventually
receive its network connection information.
"""

import os
import sys

# Determine the directory where this script resides.
script_dir = os.path.dirname(os.path.abspath(__file__))

# Check if the package folder "brainboost_data_source_package" exists in the current directory.
# If not, assume that the current directory is the package folder and add its parent.
if os.path.exists(os.path.join(script_dir, "brainboost_data_source_package")):
    # Running from the repository root.
    repo_root = script_dir
else:
    # Likely running from inside the package folder.
    repo_root = os.path.abspath(os.path.join(script_dir, os.pardir))

# Ensure that the repository root is in sys.path.
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Debug print (optional)
#print("sys.path:", sys.path)

# Now try to import DataSourceManager.
try:
    from brainboost_data_source_package.data_source_manager.DataSourceManager import DataSourceManager
except ModuleNotFoundError as e:
    print("Import failed even after sys.path adjustment:", e)
    sys.exit(1)

import redis
import json
import socket
import time
import threading
from brainboost_configuration_package.BBConfig import BBConfig

def get_local_ip():
    """
    Returns the local IP address of the machine.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        print(f"Error obtaining local IP address: {e}")
        ip = '127.0.0.1'
    return ip

def main():
    local_ip = get_local_ip()
    print(f"Local IP address determined: {local_ip}")
    
    redis_host = BBConfig.get('redis_server_ip')
    redis_port = BBConfig.get('redis_server_port')
    try:
        redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)
        redis_client.ping()
        print(f"Connected to Redis at {redis_host}:{redis_port}")
    except redis.ConnectionError as e:
        print(f"Failed to connect to Redis at {redis_host}:{redis_port}: {e}")
        sys.exit(1)
    
    command_channel = f"datasource_commands_{local_ip}"
    
    manager = DataSourceManager(command_channel=command_channel)
    
    manager_thread = threading.Thread(target=manager.start, daemon=True)
    manager_thread.start()
    print(f"DataSourceManager started and listening on channel: '{command_channel}'")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down DataSourceManager...")
        sys.exit(0)

if __name__ == "__main__":
    main()
