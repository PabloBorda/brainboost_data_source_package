#!/usr/bin/env python3
"""
DataSourceManager.py

Loads data source classes from built‐in and additional locations,
listens for commands over Redis, and provides proxy methods including:
  - get_data_source_names()
  - create_data_source()
  - get_data_source_info()
  - start_data_source()  <-- New command that launches a data source process

It also publishes registration messages to the "manager_registry" channel
periodically (every 5 seconds), so that any client (e.g. a PyQt frontend) can
receive its network connection information.
"""

import importlib
import pkgutil
import os
import sys
import importlib.util
import json
import redis
import threading
import time
import socket
import subprocess

from brainboost_data_source_package.data_source_abstract.BBDataSource import BBDataSource
from brainboost_data_source_package.data_source_abstract.BBRealTimeDataSource import BBRealTimeDataSource
from brainboost_configuration_package.BBConfig import BBConfig


class DataSourceManager:
    def __init__(self, redis_host=None, redis_port=None,
                 command_channel_prefix='datasource_commands', command_channel=None):
        if redis_host is None:
            redis_host = BBConfig.get('redis_server_ip')
        if redis_port is None:
            redis_port = BBConfig.get('redis_server_port')
        self.data_source_classes = {}
        self.load_data_sources()
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=0)
        self.local_ip = self.get_local_ip()
        if command_channel is not None:
            self.command_channel = command_channel
        else:
            self.command_channel = f"{command_channel_prefix}_{self.local_ip}"
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(self.command_channel)
        print(f"DataSourceManager initialized and subscribed to '{self.command_channel}' channel.")
        self.start_registration_publisher()
        # Dictionary to keep track of launched processes.
        self.running_processes = {}

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception as e:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def start_registration_publisher(self):
        def publisher():
            while True:
                manager_info = {
                    "ip": self.local_ip,
                    "command_channel": self.command_channel,
                    "timestamp": time.time()
                }
                self.redis.publish("manager_registry", json.dumps(manager_info))
                print(f"Published registration: {manager_info}")
                time.sleep(5)
        threading.Thread(target=publisher, daemon=True).start()

    def start(self):
        print("DataSourceManager started and listening for commands...")
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    command = json.loads(message['data'])
                except Exception as e:
                    print(f"Error decoding command: {e}")
                    continue
                threading.Thread(target=self.handle_command, args=(command,), daemon=True).start()
                print(f"Listening on channel: '{self.command_channel}'")

    def handle_command(self, command):
        request_id = command.get('request_id')
        method = command.get('method')
        params = command.get('params', {})
        response_channel = command.get('response_channel')
        print(f"Received command: {method} with params: {params} and request_id: {request_id}")
        if hasattr(self, method):
            try:
                result = getattr(self, method)(**params)
            except Exception as e:
                result = {"error": str(e)}
        else:
            result = {"error": f"Method '{method}' not found in DataSourceManager."}
        response = {"request_id": request_id, "result": result}
        self.redis.publish(response_channel, json.dumps(response))
        print(f"Published response for request_id: {request_id} to channel: {response_channel}")

    def stream_reader(self, stream, prefix):
        for line in iter(stream.readline, b''):
            text = line.decode('utf-8', errors='replace').rstrip()
            if text:
                print(f"[{prefix}] {text}")
        stream.close()

    def start_data_source(self, datasource, params):
        # Compute the project root. Since this file is in .../data_source_manager/,
        # we go two levels up.
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        launcher_script = os.path.join(project_root, "datasource_launcher.py")
        if not os.path.exists(launcher_script):
            raise Exception(f"Launcher script not found at {launcher_script}")
        
        # Determine and ensure the target directory exists.
        target_directory = params.get("target_directory")
        if not target_directory:
            default_dir = os.path.join(project_root, "data", datasource)
            os.makedirs(default_dir, exist_ok=True)
            params["target_directory"] = default_dir
        else:
            if not os.path.exists(target_directory):
                os.makedirs(target_directory, exist_ok=True)
        
        # Add client's redis listener information to params (if not already provided)
        if "client_ip" not in params:
            params["client_ip"] = BBConfig.get('redis_server_ip')
        # Remove client_port from params (we no longer need it)
        
        # Convert the parameters dictionary to a JSON string.
        params_json = json.dumps(params)
        cmd = [
            sys.executable,
            launcher_script,
            "--datasource", datasource,
            "--params", params_json,
            "--client_ip", params["client_ip"]
            # Removed the "--client_port" argument.
        ]
        print(f"Starting data source process with command: {' '.join(cmd)}")
        
        # Launch the process from the project root directory.
        process = subprocess.Popen(
            cmd,
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Store process information.
        self.running_processes[process.pid] = {
            "process": process,
            "datasource": datasource,
            "params": params
        }
        
        prefix = datasource
        threading.Thread(target=self.stream_reader, args=(process.stdout, prefix), daemon=True).start()
        threading.Thread(target=self.stream_reader, args=(process.stderr, prefix), daemon=True).start()
        
        return {"pid": process.pid, "datasource": datasource}

    def load_data_sources(self):
        # Load from built-in package.
        built_in_package = "brainboost_data_source_package.data_source_addons"
        try:
            package = importlib.import_module(built_in_package)
        except Exception as e:
            print(f"Error importing built-in package '{built_in_package}': {e}")
            package = None
        if package:
            for loader, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
                full_module_name = f"{built_in_package}.{module_name}"
                try:
                    module = importlib.import_module(full_module_name)
                except Exception as e:
                    print(f"Error importing module '{full_module_name}': {e}")
                    continue
                self._process_module(module, "built-in")
        # Load from additional path.
        additional_path = BBConfig.get('additional_data_sources_path')
        if additional_path and os.path.isdir(additional_path):
            if additional_path not in sys.path:
                sys.path.insert(0, additional_path)
            for filename in os.listdir(additional_path):
                if filename.endswith(".py") and not filename.startswith("__"):
                    module_path = os.path.join(additional_path, filename)
                    module_name = os.path.splitext(filename)[0]
                    try:
                        spec = importlib.util.spec_from_file_location(module_name, module_path)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                    except Exception as e:
                        print(f"Error importing module from '{module_path}': {e}")
                        continue
                    self._process_module(module, "additional")
        else:
            print(f"No valid additional path found: {additional_path}")

    def _process_module(self, module, source):
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                (issubclass(attr, BBDataSource) or issubclass(attr, BBRealTimeDataSource)) and 
                attr not in (BBDataSource, BBRealTimeDataSource)):
                self.data_source_classes[attr.__name__] = {"class": attr, "source": source}
                print(f"Loaded data source class '{attr.__name__}' from {source}.")

    def get_data_source_names(self):
        print("Getting list of data source names")
        return list(self.data_source_classes.keys())

    def create_data_source(self, name, **kwargs):
        if name not in self.data_source_classes:
            raise Exception(f"Data source '{name}' not found.")
        ds_class = self.data_source_classes[name]["class"]
        try:
            instance = ds_class(params=kwargs.get("params", {}))
            return instance
        except Exception as e:
            raise Exception(f"Error instantiating {name}: {e}")

    def get_data_source_info(self, name, **kwargs):
        instance = self.create_data_source(name, params={})
        try:
            info = {
                "name": instance.get_data_source_type_name(),
                "icon": instance.get_icon(),
                "connection_data": instance.get_connection_data()
            }
            return info
        except Exception as e:
            raise Exception(f"Error getting info for {name}: {e}")


if __name__ == "__main__":
    redis_host = BBConfig.get('redis_server_ip')
    redis_port = BBConfig.get('redis_server_port')
    command_channel = None  # or e.g., "datasource_commands_192.168.0.85"
    manager = DataSourceManager(command_channel=command_channel)
    manager.start()
