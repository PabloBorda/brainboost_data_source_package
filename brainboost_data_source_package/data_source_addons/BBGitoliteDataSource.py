import os
import subprocess

from brainboost_data_source_package.data_source_abstract.BBDataSource import BBDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger
from brainboost_configuration_package.BBConfig import BBConfig


class BBGitoliteDataSource(BBDataSource):
    def __init__(self, name=None, session=None, dependency_data_sources=[], subscribers=None, params=None):
        super().__init__(name=name, session=session, dependency_data_sources=dependency_data_sources, subscribers=subscribers, params=params)
        self.params = params

    def fetch(self):
        repo_name = self.params['repo_name']
        gitolite_user = self.params['gitolite_user']
        gitolite_host = self.params['gitolite_host']
        target_directory = self.params['target_directory']

        BBLogger.log(f"Starting fetch process for Gitolite repository '{repo_name}' from host '{gitolite_host}' into directory '{target_directory}'.")

        if not os.path.exists(target_directory):
            try:
                os.makedirs(target_directory)
                BBLogger.log(f"Created directory: {target_directory}")
            except OSError as e:
                BBLogger.log(f"Failed to create directory '{target_directory}': {e}")
                raise

        try:
            clone_url = f"ssh://{gitolite_user}@{gitolite_host}/{repo_name}.git"
            BBLogger.log(f"Cloning Gitolite repository '{repo_name}' from '{clone_url}'.")
            subprocess.run(['git', 'clone', clone_url], cwd=target_directory, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            BBLogger.log("Successfully cloned Gitolite repository.")
        except subprocess.CalledProcessError as e:
            BBLogger.log(f"Error cloning Gitolite repository: {e.stderr.decode().strip()}")
        except Exception as e:
            BBLogger.log(f"Unexpected error cloning Gitolite repository: {e}")

    # ------------------ New Methods ------------------
    def get_icon(self):
        """Return the SVG code for the Gitolite icon."""
        return """
<svg viewBox="0 0 24 24" fill="none" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
  <rect width="24" height="24" fill="#E84E31"/>
  <text x="50%" y="50%" font-size="6" fill="white" text-anchor="middle" alignment-baseline="middle">GLT</text>
</svg>
        """

    def get_connection_data(self):
        """
        Return the connection type and required fields for Gitolite.
        """
        return {
            "connection_type": "Gitolite",
            "fields": ["repo_name", "gitolite_user", "gitolite_host", "target_directory"]
        }

