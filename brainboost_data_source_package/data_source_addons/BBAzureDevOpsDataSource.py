import os
import subprocess
import requests
from urllib.parse import urljoin

from brainboost_data_source_package.data_source_abstract.BBDataSource import BBDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger
from brainboost_configuration_package.BBConfig import BBConfig


class BBAzureDevOpsDataSource(BBDataSource):
    def __init__(self, name=None, session=None, dependency_data_sources=[], subscribers=None, params=None):
        super().__init__(name=name, session=session, dependency_data_sources=dependency_data_sources, subscribers=subscribers, params=params)
        self.params = params

    def fetch(self):
        organization = self.params['organization']
        project = self.params['project']
        target_directory = self.params['target_directory']
        token = self.params['token']

        BBLogger.log(f"Starting fetch process for Azure DevOps organization '{organization}' and project '{project}' into directory '{target_directory}'.")

        if not os.path.exists(target_directory):
            try:
                os.makedirs(target_directory)
                BBLogger.log(f"Created directory: {target_directory}")
            except OSError as e:
                BBLogger.log(f"Failed to create directory '{target_directory}': {e}")
                raise

        headers = {
            'Authorization': f'Basic {token}'
        }
        url = f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories?api-version=6.0"

        BBLogger.log(f"Fetching repositories for Azure DevOps project '{project}'.")
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            error_msg = f"Failed to fetch repositories: HTTP {response.status_code}"
            BBLogger.log(error_msg)
            raise ConnectionError(error_msg)

        repos = response.json().get('value', [])
        if not repos:
            BBLogger.log(f"No repositories found for project '{project}'.")
            return

        BBLogger.log(f"Found {len(repos)} repositories. Starting cloning process.")

        for repo in repos:
            clone_url = repo.get('remoteUrl')
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

    # ------------------------------------------------------------------
    def get_icon(self):
        """Return the SVG code for the Azure DevOps icon."""
        return """
<svg fill="#000000" viewBox="0 0 24 24" role="img" xmlns="http://www.w3.org/2000/svg" data-darkreader-inline-fill="" style="--darkreader-inline-fill: #000000;">
  <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
  <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
  <g id="SVGRepo_iconCarrier">
    <title>Azure DevOps icon</title>
    <path d="M0 8.899l2.247-2.966 8.405-3.416V.045l7.37 5.393L2.966 8.36v8.224L0 15.73zm24-4.45v14.652L18.247 24l-9.303-3.056V24l-5.978-7.416 15.057 1.798V5.438z"></path>
  </g>
</svg>
        """

    def get_connection_data(self):
        """
        Return the connection type and required fields for Azure DevOps.
        """
        return {
            "connection_type": "AzureDevOps",
            "fields": ["organization", "project", "token", "target_directory"]
        }

import os
import subprocess
import time
from brainboost_data_source_package.data_source_abstract.BBDataSource import BBDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger


class BBAWSCodeCommitDataSource(BBDataSource):
    def __init__(self, name=None, session=None, dependency_data_sources=[], subscribers=None, params=None):
        super().__init__(name=name, session=session, dependency_data_sources=dependency_data_sources,
                         subscribers=subscribers, params=params)
        # Existing code…
        self._total_items = 0
        self._processed_items = 0
        self._total_processing_time = 0.0
        self._fetch_completed = False

    def fetch(self):
        start_time = time.time()
        region = self.params.get('region', '')
        target_directory = self.params.get('target_directory', '')
        access_key = self.params.get('access_key', '')
        secret_key = self.params.get('secret_key', '')
        BBLogger.log(f"Starting AWS CodeCommit fetch for region '{region}' into '{target_directory}'.")

        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
            BBLogger.log(f"Created directory {target_directory}")

        # Simulate obtaining repository names from AWS CodeCommit.
        repos = self._get_repositories()
        self._total_items = len(repos)
        BBLogger.log(f"Found {self._total_items} repositories.")

        for repo in repos:
            step_start = time.time()
            repo_name = repo  # In this dummy implementation, repo is just the name.
            clone_url = f"https://git-codecommit.{region}.amazonaws.com/v1/repos/{repo_name}"
            dest_path = os.path.join(target_directory, repo_name)
            if os.path.exists(dest_path) and os.listdir(dest_path):
                BBLogger.log(f"Repository {repo_name} already exists. Skipping clone.")
            else:
                try:
                    BBLogger.log(f"Cloning repository {repo_name} from {clone_url} ...")
                    subprocess.run(["git", "clone", clone_url, dest_path],
                                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except subprocess.CalledProcessError as e:
                    BBLogger.log(f"Error cloning {repo_name}: {e.stderr.decode()}", level="error")
            elapsed = time.time() - step_start
            self._total_processing_time += elapsed
            self._processed_items += 1
            if self.progress_callback:
                est_time = self.estimated_remaining_time()
                self.progress_callback(self.get_name(), self.total_to_process(), self.total_processed(), est_time)
        self._fetch_completed = True
        BBLogger.log("AWS CodeCommit fetch process completed.")

    def _get_repositories(self):
        # Dummy implementation: replace with actual AWS API calls.
        return ['Repo1', 'Repo2', 'Repo3']

    def get_icon(self):
        # Complete AWS CodeCommit icon (placeholder; replace with full original if needed)
        return """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20">
  <circle cx="10" cy="10" r="10" fill="#252F3E"/>
</svg>"""

    def get_connection_data(self):
        return {
            "connection_type": "AWS",
            "fields": ["region", "access_key", "secret_key", "target_directory"]
        }

