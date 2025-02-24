import os
import subprocess
import requests
from urllib.parse import urljoin

from brainboost_data_source_package.data_source_abstract.BBDataSource import BBDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger
from brainboost_configuration_package.BBConfig import BBConfig


class BBSVNDataSource(BBDataSource):
    def __init__(self, name=None, session=None, dependency_data_sources=[], subscribers=None, params=None):
        super().__init__(name=name, session=session, dependency_data_sources=dependency_data_sources, subscribers=subscribers, params=params)
        self.params = params

    def fetch(self):
        repo_url = self.params['repo_url']
        target_directory = self.params['target_directory']

        BBLogger.log(f"Starting fetch process for SVN repository '{repo_url}' into directory '{target_directory}'.")

        if not os.path.exists(target_directory):
            try:
                os.makedirs(target_directory)
                BBLogger.log(f"Created directory: {target_directory}")
            except OSError as e:
                BBLogger.log(f"Failed to create directory '{target_directory}': {e}")
                raise

        try:
            subprocess.run(['svn', 'checkout', repo_url, target_directory], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            BBLogger.log("Successfully checked out SVN repository.")
        except subprocess.CalledProcessError as e:
            BBLogger.log(f"Error checking out SVN repository: {e.stderr.decode().strip()}")
        except Exception as e:
            BBLogger.log(f"Unexpected error checking out SVN repository: {e}")

    # ------------------------------------------------------------------
    def get_icon(self):
        """Return the SVG code for the SVN icon."""
        return """
<svg fill="#000000" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <path d="M493.331,69.485C318.286,103.59,150.203,144.593,0.5,204.047c0-44.854,0-89.707,0-134.562
    C164.774,69.485,329.057,69.485,493.331,69.485z M275.587,351.102C189.643,377.108,97.007,394.691,0.5,409.3c0-36.433,0-72.865,0-109.299
    c67.393-4.819,131.838-10.454,199.006-17.881c48.322-5.349,97.955-10.95,150.459-12.21c17.828-0.428,36.13-0.569,49.399,4.541
    c4.399,1.697,9.586,5.032,9.935,10.222c0.578,8.571-9.253,15.066-14.763,19.021c-6.745,4.836-14.155,8.604-21.292,11.922
    c-15.437,7.183-30.947,13.856-47.407,19.305C309.528,340.318,292.633,345.945,275.587,351.102z" />
</svg>
        """

    def get_connection_data(self):
        """
        Return the connection type and required fields for SVN.
        """
        return {
            "connection_type": "SVN",
            "fields": ["repo_url", "target_directory"]
        }

