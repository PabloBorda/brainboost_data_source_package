import os
import subprocess
import requests
from urllib.parse import urljoin

from brainboost_data_source_package.data_source_abstract.BBDataSource import BBDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger
from brainboost_configuration_package.BBConfig import BBConfig


class BBRationalTeamConcertDataSource(BBDataSource):
    def __init__(self, name=None, session=None, dependency_data_sources=[], subscribers=None, params=None):
        super().__init__(name=name, session=session, dependency_data_sources=dependency_data_sources, subscribers=subscribers, params=params)
        self.params = params

    def fetch(self):
        server_url = self.params['server_url']
        project_area = self.params['project_area']
        repository_workspace = self.params['repository_workspace']
        target_directory = self.params['target_directory']
        username = self.params['username']
        password = self.params['password']

        BBLogger.log(f"Starting fetch process for RTC workspace '{repository_workspace}' from server '{server_url}' into directory '{target_directory}'.")

        if not os.path.exists(target_directory):
            try:
                os.makedirs(target_directory)
                BBLogger.log(f"Created directory: {target_directory}")
            except OSError as e:
                BBLogger.log(f"Failed to create directory '{target_directory}': {e}")
                raise

        try:
            BBLogger.log("Authenticating with RTC server.")
            auth_command = [
                'lscm', 'login', '-r', server_url, '-u', username, '-P', password
            ]
            subprocess.run(auth_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            BBLogger.log(f"Loading workspace '{repository_workspace}' into '{target_directory}'.")
            load_command = [
                'lscm', 'load', repository_workspace, '-d', target_directory
            ]
            subprocess.run(load_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            BBLogger.log(f"Successfully loaded workspace '{repository_workspace}' into '{target_directory}'.")
        except subprocess.CalledProcessError as e:
            BBLogger.log(f"Error during RTC operations: {e.stderr.decode().strip()}")
        except Exception as e:
            BBLogger.log(f"Unexpected error during RTC operations: {e}")

    # ------------------------------------------------------------------
    def get_icon(self):
        """Return the SVG code for the RTC icon."""
        return """
<svg viewBox="0 0 24 24" fill="none" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="10" stroke="#16335B" stroke-width="2" fill="none"/>
  <text x="50%" y="50%" font-size="5" fill="#16335B" text-anchor="middle" alignment-baseline="middle">RTC</text>
</svg>
        """

    def get_connection_data(self):
        """
        Return the connection type and required fields for Rational Team Concert.
        """
        return {
            "connection_type": "RationalTeamConcert",
            "fields": ["server_url", "project_area", "repository_workspace", "username", "password", "target_directory"]
        }

