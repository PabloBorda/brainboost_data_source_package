import subprocess
import threading
import sys
from brainboost_configuration_package.BBConfig import BBConfig

# ... (rest of your DataSourceManager code)

class DataSourceManager:
    def __init__(self, redis_host=None, redis_port=None,
                 command_channel_prefix='datasource_commands', command_channel=None):
        
        if redis_host==None:
            redis_host = BBConfig.get('redis_server_ip')
        if redis_port==None:
            redis_port = BBConfig.get('redis_server_port')
        # ... your existing initialization ...
        self.running_processes = {}

    def stream_reader(self, stream, prefix):
        """
        Reads from the given stream line by line and prints each line with a prefix.
        """
        for line in iter(stream.readline, b''):
            # Decode the line if needed and strip newlines.
            text = line.decode('utf-8', errors='replace').rstrip()
            if text:
                print(f"[{prefix}] {text}")
        stream.close()

    def start_data_source(self, datasource, params):
        """
        Launches a new process for the specified data source.
        The process is launched using the current Python interpreter and the
        separate launcher script (datasource_launcher.py). Its output (stdout and stderr)
        is piped to our console, with each line prefixed with the datasource name.
        Stores process information internally.
        """
        # Build the command:
        launcher_script = os.path.join(os.path.dirname(__file__), "..", "datasource_launcher.py")
        if not os.path.exists(launcher_script):
            raise Exception(f"Launcher script not found at {launcher_script}")
        # Convert params to a JSON string.
        params_json = json.dumps(params)
        cmd = [
            sys.executable,
            launcher_script,
            "--datasource", datasource,
            "--params", params_json
        ]
        print(f"Starting data source process with command: {' '.join(cmd)}")
        # Launch the process and capture stdout and stderr.
        process = subprocess.Popen(
            cmd,
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Store process information.
        self.running_processes[process.pid] = {
            "process": process,
            "datasource": datasource,
            "params": params
        }
        # Create threads to read stdout and stderr.
        prefix = datasource
        threading.Thread(target=self.stream_reader, args=(process.stdout, prefix), daemon=True).start()
        threading.Thread(target=self.stream_reader, args=(process.stderr, prefix), daemon=True).start()
        return {"pid": process.pid, "datasource": datasource}
