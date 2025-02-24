import os
import subprocess
import requests
from urllib.parse import urljoin

from brainboost_data_source_package.data_source_abstract.BBDataSource import BBDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger
from brainboost_configuration_package.BBConfig import BBConfig


class BBPlasticSCMDataSource(BBDataSource):
    def __init__(self, name=None, session=None, dependency_data_sources=[], subscribers=None, params=None):
        super().__init__(name=name, session=session, dependency_data_sources=dependency_data_sources, subscribers=subscribers, params=params)
        self.params = params

    def fetch(self):
        server_url = self.params['server_url']
        repository_name = self.params['repository_name']
        target_directory = self.params['target_directory']
        username = self.params['username']
        password = self.params['password']

        BBLogger.log(f"Starting fetch process for Plastic SCM repository '{repository_name}' from server '{server_url}' into directory '{target_directory}'.")

        if not os.path.exists(target_directory):
            try:
                os.makedirs(target_directory)
                BBLogger.log(f"Created directory: {target_directory}")
            except OSError as e:
                BBLogger.log(f"Failed to create directory '{target_directory}': {e}")
                raise

        try:
            BBLogger.log("Authenticating with Plastic SCM server.")
            auth_command = [
                'cm', 'authenticate', f'--server={server_url}', f'--user={username}', f'--password={password}'
            ]
            subprocess.run(auth_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            BBLogger.log(f"Cloning Plastic SCM repository '{repository_name}'.")
            clone_command = [
                'cm', 'clone', f'{server_url}/{repository_name}', target_directory
            ]
            subprocess.run(clone_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            BBLogger.log(f"Successfully cloned repository '{repository_name}' into '{target_directory}'.")
        except subprocess.CalledProcessError as e:
            BBLogger.log(f"Error during Plastic SCM operations: {e.stderr.decode().strip()}")
        except Exception as e:
            BBLogger.log(f"Unexpected error during Plastic SCM operations: {e}")

    # ------------------------------------------------------------------
    def get_icon(self):
        """Return the SVG code for the Plastic SCM icon."""
        return """
<svg viewBox="0 0 24 24" fill="none" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="10" fill="#556677"/>
  <text x="50%" y="50%" font-size="5" fill="white" text-anchor="middle" alignment-baseline="middle">Plastic</text>
</svg>
        """

    def get_connection_data(self):
        """
        Return the connection type and required fields for Plastic SCM.
        """
        return {
            "connection_type": "PlasticSCM",
            "fields": ["server_url", "repository_name", "username", "password", "target_directory"]
        }


