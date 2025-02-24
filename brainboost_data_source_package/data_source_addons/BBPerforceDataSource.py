import os
import subprocess
import requests
from urllib.parse import urljoin

from brainboost_data_source_package.data_source_abstract.BBDataSource import BBDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger
from brainboost_configuration_package.BBConfig import BBConfig


class BBPerforceDataSource(BBDataSource):
    def __init__(self, name=None, session=None, dependency_data_sources=[], subscribers=None, params=None):
        super().__init__(name=name, session=session, dependency_data_sources=dependency_data_sources, subscribers=subscribers, params=params)
        self.params = params

    def fetch(self):
        server = self.params['server']
        user = self.params['user']
        password = self.params['password']
        target_directory = self.params['target_directory']

        BBLogger.log(f"Starting fetch process for Perforce server '{server}' into directory '{target_directory}'.")

        if not os.path.exists(target_directory):
            try:
                os.makedirs(target_directory)
                BBLogger.log(f"Created directory: {target_directory}")
            except OSError as e:
                BBLogger.log(f"Failed to create directory '{target_directory}': {e}")
                raise

        try:
            os.environ['P4PORT'] = server
            os.environ['P4USER'] = user
            os.environ['P4PASSWD'] = password

            BBLogger.log(f"Fetching repositories for Perforce server '{server}'.")
            subprocess.run(['p4', 'sync'], cwd=target_directory, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            BBLogger.log("Successfully synchronized Perforce workspace.")
        except subprocess.CalledProcessError as e:
            BBLogger.log(f"Error syncing Perforce workspace: {e.stderr.decode().strip()}")
        except Exception as e:
            BBLogger.log(f"Unexpected error syncing Perforce workspace: {e}")

    # ------------------------------------------------------------------
    def get_icon(self):
        """Return the SVG code for the Perforce icon."""
        return """
<svg viewBox="0 0 24 24" fill="none" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
  <rect width="24" height="24" fill="#0060FF"/>
  <text x="50%" y="50%" font-size="10" fill="white" text-anchor="middle" alignment-baseline="middle">P4</text>
</svg>
        """

    def get_connection_data(self):
        """
        Return the connection type and required fields for Perforce.
        """
        return {
            "connection_type": "Perforce",
            "fields": ["server", "user", "password", "target_directory"]
        }


