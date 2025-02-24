import os
import subprocess
import requests
from urllib.parse import urljoin

from brainboost_data_source_package.data_source_abstract.BBDataSource import BBDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger
from brainboost_configuration_package.BBConfig import BBConfig


class BBGoogleCloudSourceDataSource(BBDataSource):
    def __init__(self, name=None, session=None, dependency_data_sources=[], subscribers=None, params=None):
        super().__init__(name=name, session=session, dependency_data_sources=dependency_data_sources, subscribers=subscribers, params=params)
        self.params = params

    def fetch(self):
        project_id = self.params['project_id']
        target_directory = self.params['target_directory']
        token = self.params['token']

        BBLogger.log(f"Starting fetch process for Google Cloud Source project '{project_id}' into directory '{target_directory}'.")

        if not os.path.exists(target_directory):
            try:
                os.makedirs(target_directory)
                BBLogger.log(f"Created directory: {target_directory}")
            except OSError as e:
                BBLogger.log(f"Failed to create directory '{target_directory}': {e}")
                raise

        headers = {
            'Authorization': f'Bearer {token}'
        }
        url = f"https://source.developers.google.com/projects/{project_id}/repos"

        BBLogger.log(f"Fetching repositories for Google Cloud Source project '{project_id}'.")
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            error_msg = f"Failed to fetch repositories: HTTP {response.status_code}"
            BBLogger.log(error_msg)
            raise ConnectionError(error_msg)

        repos = response.json().get('repos', [])
        if not repos:
            BBLogger.log(f"No repositories found for project '{project_id}'.")
            return

        BBLogger.log(f"Found {len(repos)} repositories. Starting cloning process.")

        for repo in repos:
            clone_url = repo.get('url')
            repo_name = repo.get('name', 'Unnamed Repository')
            if clone_url:
                self.clone_repo(clone_url, target_directory, repo_name)
            else:
                BBLogger.log(f"No clone URL found for repository '{repo_name}'. Skipping.")

        BBLogger.log("All repositories have been processed.")

    def clone_repo(self, repo_clone_url, target_directory, repo_name):
        try:
            BBLogger.log(f"Cloning repository '{repo_name}' from {repo_clone_url}...")
            subprocess.run(['git', 'clone', repo_clone_url], cwd=target_directory, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            BBLogger.log(f"Successfully cloned '{repo_name}'.")
        except subprocess.CalledProcessError as e:
            BBLogger.log(f"Error cloning '{repo_name}': {e.stderr.decode().strip()}")
        except Exception as e:
            BBLogger.log(f"Unexpected error cloning '{repo_name}': {e}")

    # ------------------ New Methods ------------------
    def get_icon(self):
        """Return the SVG code for the Google Cloud Source icon."""
        return """
<svg viewBox="0 0 24 24" fill="none" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 2L2 12h3v5h14v-5h3L12 2z" fill="#4285F4"/>
  <text x="50%" y="70%" font-size="5" fill="white" text-anchor="middle" alignment-baseline="middle">GCS</text>
</svg>
        """

    def get_connection_data(self):
        """
        Return the connection type and required fields for Google Cloud Source.
        """
        return {
            "connection_type": "GoogleCloudSource",
            "fields": ["project_id", "token", "target_directory"]
        }

