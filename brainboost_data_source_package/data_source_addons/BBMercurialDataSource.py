import os
import subprocess
import requests
from urllib.parse import urljoin

from brainboost_data_source_package.data_source_abstract.BBDataSource import BBDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger
from brainboost_configuration_package.BBConfig import BBConfig


class BBMercurialDataSource(BBDataSource):
    def __init__(self, name=None, session=None, dependency_data_sources=[], subscribers=None, params=None):
        super().__init__(name=name, session=session, dependency_data_sources=dependency_data_sources, subscribers=subscribers, params=params)
        self.params = params

    def fetch(self):
        repo_url = self.params['repo_url']
        target_directory = self.params['target_directory']

        BBLogger.log(f"Starting fetch process for Mercurial repository '{repo_url}' into directory '{target_directory}'.")

        if not os.path.exists(target_directory):
            try:
                os.makedirs(target_directory)
                BBLogger.log(f"Created directory: {target_directory}")
            except OSError as e:
                BBLogger.log(f"Failed to create directory '{target_directory}': {e}")
                raise

        try:
            subprocess.run(['hg', 'clone', repo_url, target_directory], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            BBLogger.log("Successfully cloned Mercurial repository.")
        except subprocess.CalledProcessError as e:
            BBLogger.log(f"Error cloning Mercurial repository: {e.stderr.decode().strip()}")
        except Exception as e:
            BBLogger.log(f"Unexpected error cloning Mercurial repository: {e}")
    
    # ------------------------------------------------------------------
    def get_icon(self):
        """Return the SVG code for the Mercurial icon."""
        return """
<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" fill="#000000" data-darkreader-inline-fill=""
     style="--darkreader-inline-fill: #000000;">
  <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
  <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
  <g id="SVGRepo_iconCarrier">
    <title>file_type_mercurial</title>
    <path d="M28.042,23.172c4.989-8.3-1.054-21.751-12.1-20.384C5.955,4.022,5.794,14.53,14.593,17.026
      c7.614,2.162,1.573,6.992,1.749,10.208s6.62,4.382,11.7-4.063" 
      style="fill: rgb(27, 27, 27); --darkreader-inline-fill: #d7d3ce;" 
      data-darkreader-inline-fill=""></path>
    <circle cx="9.784" cy="24.257" r="4.332" 
      style="fill: rgb(27, 27, 27); --darkreader-inline-fill: #d7d3ce;" 
      data-darkreader-inline-fill=""></circle>
    <circle cx="4.835" cy="15.099" r="2.835" 
      style="fill: rgb(27, 27, 27); --darkreader-inline-fill: #d7d3ce;" 
      data-darkreader-inline-fill=""></circle>
    <path d="M28.231,22.835c4.989-8.3-1.054-21.751-12.1-20.384C6.144,3.686,5.983,14.194,14.781,16.69
      c7.614,2.162,1.573,6.992,1.749,10.208s6.62,4.382,11.7-4.063" 
      style="fill: rgb(191, 191, 191); --darkreader-inline-fill: #c0bab2;" 
      data-darkreader-inline-fill=""></path>
    <circle cx="9.972" cy="23.921" r="4.332" 
      style="fill: rgb(191, 191, 191); --darkreader-inline-fill: #c0bab2;" 
      data-darkreader-inline-fill=""></circle>
    <circle cx="5.023" cy="14.762" r="2.835" 
      style="fill: rgb(191, 191, 191); --darkreader-inline-fill: #c0bab2;" 
      data-darkreader-inline-fill=""></circle>
    <path d="M17.811,28.168a.669.669,0,0,1,.635-.994,7,7,0,0,0,3.7-.746c3.247-1.841,8.244-10.7,5.731-16.285
      A12.77,12.77,0,0,0,25.049,5.7c-.236-.249-.1-.236.059-.152a10.08,10.08,0,0,1,2.857,3.676,
      14.578,14.578,0,0,1,1.1,10.279c-.494,1.817-2.2,5.928-4.691,7.706s-5.424,2.8-6.563.955
      M15.548,16.673c-1.7-.5-3.894-1.208-5.163-2.867A8.088,8.088,0,0,1,8.854,10.49c-.043-.27-.08-.5,0-.558
      a21.882,21.882,0,0,0,1.688,2.723,6.487,6.487,0,0,0,3.526,2.256,12.383,12.383,0,0,1,3.867,1.37
      c.739.629.8,1.989.552,2.142s-.759-1.1-2.938-1.749
      m-8.155,10.4c3.369,3.121,8.439-1.166,6.207-4.954-.251-.425-.576-.749-.469-.423
      .714,2.178.054,3.9-1.176,4.788a4.063,4.063,0,0,1-4.192.328c-.39-.2-.551.092-.37.261
      m-3.93-10.16c.018.2.292.458.722.576a2.969,2.969,0,0,0,2.55-.413,2.759,2.759,0,0,0,
      .81-3.452c-.172-.308-.4-.533-.218-.041A2.68,2.68,0,0,1,6.148,16.53a2.439,2.439,0,0,1-2.1.164
      c-.391-.119-.6.016-.58.223"></path>
  </g>
</svg>
        """

    def get_connection_data(self):
        """
        Return the connection type and required fields for Mercurial.
        """
        return {
            "connection_type": "Mercurial",
            "fields": ["repo_url", "target_directory"]
        }

