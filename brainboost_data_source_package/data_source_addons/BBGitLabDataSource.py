import os
import subprocess
import requests
from urllib.parse import urljoin

from brainboost_data_source_package.data_source_abstract.BBDataSource import BBDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger
from brainboost_configuration_package.BBConfig import BBConfig


class BBGitLabDataSource(BBDataSource):
    def __init__(self, name=None, session=None, dependency_data_sources=[], subscribers=None, params=None):
        # Passing parameters to the base class.
        super().__init__(name=name, session=session, dependency_data_sources=dependency_data_sources, subscribers=subscribers, params=params)
        self.params = params

    def fetch(self):
        username = self.params['username']
        target_directory = self.params['target_directory']
        token = self.params['token']

        BBLogger.log(f"Starting fetch process for GitLab user '{username}' into directory '{target_directory}'.")

        if not os.path.exists(target_directory):
            try:
                os.makedirs(target_directory)
                BBLogger.log(f"Created directory: {target_directory}")
            except OSError as e:
                BBLogger.log(f"Failed to create directory '{target_directory}': {e}")
                raise

        elif not os.path.isdir(target_directory):
            error_msg = f"Path '{target_directory}' is not a directory."
            BBLogger.log(error_msg)
            raise NotADirectoryError(error_msg)

        repos = self.get_repos(username, token)
        if not repos:
            BBLogger.log(f"No repositories found for user '{username}'.")
            return

        BBLogger.log(f"Found {len(repos)} repositories. Starting cloning process.")

        for repo in repos:
            clone_url = repo.get('http_url_to_repo')
            repo_name = repo.get('name', 'Unnamed Repository')
            if clone_url:
                self.clone_repo(clone_url, target_directory, repo_name)
            else:
                BBLogger.log(f"No clone URL found for repository '{repo_name}'. Skipping.")

        BBLogger.log("All repositories have been processed.")

    def get_repos(self, username, token):
        repos = []
        per_page = 100
        page = 1
        headers = {
            'Private-Token': token
        }

        while True:
            url = f"https://gitlab.com/api/v4/users/{username}/projects"
            params = {'per_page': per_page, 'page': page}
            BBLogger.log(f"Fetching page {page} of repositories for GitLab user '{username}'.")
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                page_repos = response.json()
                if not page_repos:
                    BBLogger.log("No more repositories found.")
                    break
                repos.extend(page_repos)
                page += 1
            elif response.status_code == 404:
                error_msg = f"User '{username}' not found on GitLab."
                BBLogger.log(error_msg)
                raise ValueError(error_msg)
            elif response.status_code == 403:
                error_msg = "Access forbidden. Check your token or permissions."
                BBLogger.log(error_msg)
                raise PermissionError(error_msg)
            else:
                error_msg = f"Failed to fetch repositories: HTTP {response.status_code}"
                BBLogger.log(error_msg)
                raise ConnectionError(error_msg)

        return repos

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
        """Return the SVG code for the GitLab icon."""
        return """
<svg viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
  <path fill="#FC6D26" d="M14.975 8.904L14.19 6.55l-1.552-4.67a.268.268 0 00-.255-.18.268.268 0 00-.254.18l-1.552 4.667H5.422L3.87 1.879a.267.267 0 00-.254-.179.267.267 0 00-.254.18l-1.55 4.667-.784 2.357a.515.515 0 00.193.583l6.78 4.812 6.778-4.812a.516.516 0 00.196-.583z"/>
  <path fill="#E24329" d="M8 14.296l2.578-7.75H5.423L8 14.296z"/>
</svg>
        """

    def get_connection_data(self):
        """
        Return the connection type and required fields for GitLab.
        """
        return {
            "connection_type": "GitLab",
            "fields": ["username", "token", "target_directory"]
        }

