import os
import subprocess

from brainboost_data_source_package.data_source_abstract.BBDataSource import BBDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger
from brainboost_configuration_package.BBConfig import BBConfig


class BBBazaarDataSource(BBDataSource):
    def __init__(self, name=None, session=None, dependency_data_sources=[], subscribers=None, params=None):
        super().__init__(name=name, session=session, dependency_data_sources=dependency_data_sources, subscribers=subscribers, params=params)
        self.params = params

    def fetch(self):
        repo_url = self.params['repo_url']
        target_directory = self.params['target_directory']

        BBLogger.log(f"Starting fetch process for Bazaar repository '{repo_url}' into directory '{target_directory}'.")

        if not os.path.exists(target_directory):
            try:
                os.makedirs(target_directory)
                BBLogger.log(f"Created directory: {target_directory}")
            except OSError as e:
                BBLogger.log(f"Failed to create directory '{target_directory}': {e}")
                raise

        try:
            BBLogger.log(f"Cloning Bazaar repository from '{repo_url}'.")
            subprocess.run(['bzr', 'branch', repo_url, target_directory], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            BBLogger.log("Successfully cloned Bazaar repository.")
        except subprocess.CalledProcessError as e:
            BBLogger.log(f"Error cloning Bazaar repository: {e.stderr.decode().strip()}")
        except Exception as e:
            BBLogger.log(f"Unexpected error cloning Bazaar repository: {e}")

    # ------------------------------------------------------------------
    def get_icon(self):
        """Return the SVG code for the Bazaar icon."""
        return """
<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" fill="#000000" data-darkreader-inline-fill="" style="--darkreader-inline-fill: #000000;">
  <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
  <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
  <g id="SVGRepo_iconCarrier">
    <title>file_type_bazaar</title>
    <path d="M23.418,8.449C17.727,2.634,16.918,2,16.17,2s-1.576.659-7.416,6.706c-6.364,6.59-7.034,7.359-6.18,8.7.235.37,6.168,6.374,6.228,6.435C14.477,29.586,15.2,30,15.72,30c.219,0,.492,0,2.8-2.155,1.276-1.192,2.922-2.812,4.636-4.563s3.3-3.433,4.466-4.736c2.1-2.352,2.1-2.625,2.1-2.845C29.725,15.245,29.26,14.42,23.418,8.449Z" style="fill: rgb(252, 233, 79); --darkreader-inline-fill: #fce952;" data-darkreader-inline-fill=""></path>
    <path d="M19.315,18.638c-1.455-2.081-2.193-4.1-1.969-4.683.084-.219.516-.344,1.184-.344.126,0,1.237-.01,1.237-.375,0-.6-3.321-5.565-3.78-5.656-.324-.061-1.03.759-2.1,2.446l-.036.057c-1.44,2.271-1.875,2.957-1.685,3.3.122.222.447.225.984.225h1.085v4.877a40.929,40.929,0,0,0,.219,5.251h0a3.532,3.532,0,0,0,1.475.219H17.25v-1.88a7.71,7.71,0,0,1,.152-1.87,3.448,3.448,0,0,1,1.1.822c.833.813,1.166,1.063,1.632.677C20.9,21.074,20.659,20.56,19.315,18.638Z" style="fill: rgb(196, 160, 0); --darkreader-inline-fill: #ffdc43;" data-darkreader-inline-fill=""></path>
    <path d="M14.093,23.224a38.676,38.676,0,0,1-.186-5.173V13.064H12.759c-1.391,0-1.4.019.783-3.417.985-1.554,1.727-2.449,1.986-2.4.4.08,3.692,5.021,3.692,5.549,0,.146-.507.266-1.127.266-.738,0-1.182.143-1.286.414-.264.688.635,2.858,1.982,4.785,1.38,1.975,1.5,2.375.839,2.92-.365.3-.6.2-1.486-.671-.58-.566-1.14-.943-1.246-.837a6.159,6.159,0,0,0-.192,1.963V23.41H15.492A3.487,3.487,0,0,1,14.093,23.224Z" style="fill: rgb(85, 87, 83); --darkreader-inline-fill: #b2aca2;" data-darkreader-inline-fill=""></path>
    <path d="M16.813,23.52H15.492a3.533,3.533,0,0,1-1.475-.219h0a40.93,40.93,0,0,1-.218-5.251V13.173H12.735c-.56,0-.883,0-1.007-.225-.19-.345.245-1.031,1.685-3.3l.036-.057c1.07-1.687,1.776-2.507,2.1-2.446.459.091,3.78,5.06,3.78,5.656,0,.365-1.11.375-1.237.375-.669,0-1.1.125-1.184.344-.223.582.515,2.6,1.969,4.683,1.343,1.922,1.58,2.435.819,3.067-.466.387-.8.137-1.632-.677a3.447,3.447,0,0,0-1.1-.822,7.708,7.708,0,0,0-.152,1.87Zm-2.633-.367a4.035,4.035,0,0,0,1.311.149h1.1V21.639a6.117,6.117,0,0,1,.224-2.04c.25-.25,1.134.577,1.4.836.939.917,1.069.889,1.339.665.563-.467.55-.757-.859-2.773-1.377-1.971-2.272-4.163-1.994-4.887.123-.322.59-.485,1.389-.485a1.938,1.938,0,0,0,1.023-.176A26.993,26.993,0,0,0,15.5,7.355c-.121-.022-.667.456-1.868,2.35l-.036.057c-1.2,1.9-1.805,2.848-1.678,3.08.062.112.4.11.815.112h1.281v5.1A46.7,46.7,0,0,0,14.18,23.153Z" style="fill: rgb(46, 52, 54); --darkreader-inline-fill: #c8c4bd;" data-darkreader-inline-fill=""></path>
  </g>
</svg>
        """

    def get_connection_data(self):
        """
        Return the connection type and required fields for Bazaar.
        """
        return {
            "connection_type": "Bazaar",
            "fields": ["username","repo_url", "target_directory"]
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

 