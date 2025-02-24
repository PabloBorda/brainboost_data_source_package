import os
import subprocess

from brainboost_data_source_package.data_source_abstract.BBDataSource import BBDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger
from brainboost_configuration_package.BBConfig import BBConfig


class BBTeamFoundationDataSource(BBDataSource):
    def __init__(self, name=None, session=None, dependency_data_sources=[], subscribers=None, params=None):
        super().__init__(name=name, session=session, dependency_data_sources=dependency_data_sources, subscribers=subscribers, params=params)
        self.params = params

    def fetch(self):
        collection_url = self.params['collection_url']
        repo_name = self.params['repo_name']
        target_directory = self.params['target_directory']
        username = self.params['username']
        password = self.params['password']

        BBLogger.log(f"Starting fetch process for TFS repository '{repo_name}' from '{collection_url}' into directory '{target_directory}'.")

        if not os.path.exists(target_directory):
            try:
                os.makedirs(target_directory)
                BBLogger.log(f"Created directory: {target_directory}")
            except OSError as e:
                BBLogger.log(f"Failed to create directory '{target_directory}': {e}")
                raise

        try:
            BBLogger.log("Configuring TFS credentials.")
            auth_command = [
                'git', 'credential', 'approve'
            ]
            credential_data = f"url={collection_url}\nusername={username}\npassword={password}\n"
            subprocess.run(auth_command, input=credential_data.encode(), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            repo_url = f"{collection_url}/{repo_name}.git"
            BBLogger.log(f"Cloning TFS repository '{repo_name}' from '{repo_url}'.")
            subprocess.run(['git', 'clone', repo_url], cwd=target_directory, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            BBLogger.log("Successfully cloned TFS repository.")
        except subprocess.CalledProcessError as e:
            BBLogger.log(f"Error cloning TFS repository: {e.stderr.decode().strip()}")
        except Exception as e:
            BBLogger.log(f"Unexpected error cloning TFS repository: {e}")

    # ------------------------------------------------------------------
    def get_icon(self):
        """Return the SVG code for the Team Foundation (TFS) icon."""
        return """<svg viewBox="0 0 256 256" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" preserveAspectRatio="xMidYMid" fill="#000000"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <defs> <linearGradient x1="49.9999997%" y1="0.00244053108%" x2="49.9999997%" y2="99.999641%" id="linearGradient-1"> <stop stop-color="#FFFFFF" offset="0%"> </stop> <stop stop-color="#FFFFFF" stop-opacity="0" offset="100%"> </stop> </linearGradient> </defs> <g> <path d="M36.9866667,200.406215 C33.9280235,203.019746 29.6590738,203.689992 25.9466667,202.139549 L6.56,194.006215 C2.60661593,192.357112 0.0232284231,188.503034 0,184.219549 L0,70.4595487 C0.0232284231,66.1760633 2.60661593,62.3219852 6.56,60.6728821 L25.9466667,52.6728821 C29.6590738,51.122439 33.9280235,51.7926847 36.9866667,54.4062154 L41.3333333,58.0062154 C39.5360867,56.7141841 37.1664204,56.5381696 35.1980103,57.5504947 C33.2296003,58.5628199 31.9944221,60.5927545 32,62.8062154 L32,191.872882 C31.9944221,194.086343 33.2296003,196.116278 35.1980103,197.128603 C37.1664204,198.140928 39.5360867,197.964913 41.3333333,196.672882 L36.9866667,200.406215 Z" fill="#52218A" fill-rule="nonzero"> </path> <path d="M6.56,194.006215 C2.60661593,192.357112 0.0232284231,188.503034 0,184.219549 L0,183.339549 C0.0268934047,185.858586 1.58492217,188.107394 3.9339112,189.017627 C6.28290023,189.927861 8.94941357,189.316063 10.6666667,187.472882 L176,4.67288206 C180.797767,-0.101060222 188.080373,-1.3397438 194.186667,1.57954873 L246.933333,26.9662154 C252.477775,29.6321062 256.002663,35.2408256 256,41.3928821 L256,42.0062154 C255.996628,38.1026642 253.745578,34.5500434 250.217325,32.8799659 C246.689073,31.2098885 242.514491,31.7209739 239.493333,34.1928821 L41.3333333,196.672882 L36.9866667,200.406215 C33.9280235,203.019746 29.6590738,203.689992 25.9466667,202.139549 L6.56,194.006215 Z" fill="#6C33AF" fill-rule="nonzero"> </path> <path d="M6.56,60.6728821 C2.60661593,62.3219852 0.0232284231,66.1760633 0,70.4595487 L0,71.3395487 C0.0268934047,68.8205111 1.58492217,66.5717033 3.9339112,65.6614701 C6.28290023,64.7512369 8.94941357,65.3630345 10.6666667,67.2062154 L176,250.006215 C180.797767,254.780158 188.080373,256.018841 194.186667,253.099549 L246.933333,227.712882 C252.477775,225.046991 256.002663,219.438272 256,213.286215 L256,212.672882 C255.996628,216.576433 253.745578,220.129054 250.217325,221.799132 C246.689073,223.469209 242.514491,222.958124 239.493333,220.486215 L41.3333333,58.0062154 L36.9866667,54.2728821 C33.9010187,51.7044121 29.634528,51.0860801 25.9466667,52.6728821 L6.56,60.6728821 Z" fill="#854CC7" fill-rule="nonzero"> </path> <path d="M194.186667,253.099549 C188.080373,256.018841 180.797767,254.780158 176,250.006215 C178.687118,252.67399 182.713996,253.466025 186.211298,252.014645 C189.7086,250.563265 191.991405,247.152711 192,243.366215 L192,11.3662154 C192.012965,7.57001396 189.738069,4.13973417 186.235938,2.67467621 C182.733808,1.20961825 178.694002,1.99824786 176,4.67288206 C180.797767,-0.101060222 188.080373,-1.3397438 194.186667,1.57954873 L246.933333,26.9395487 C252.477775,29.6054395 256.002663,35.214159 256,41.3662154 L256,213.312882 C256.002663,219.464938 252.477775,225.073658 246.933333,227.739549 L194.186667,253.099549 Z" fill="#B179F1" fill-rule="nonzero"> </path> <path d="M183.706667,254.272882 C187.232219,255.077301 190.926299,254.663714 194.186667,253.099549 L246.933333,227.739549 C252.477775,225.073658 256.002663,219.464938 256,213.312882 L256,41.3662154 C256.002663,35.214159 252.477775,29.6054395 246.933333,26.9395487 L194.186667,1.57954873 C190.454554,-0.214455828 186.172257,-0.491658077 182.24,0.806215393 C179.888439,1.59407912 177.752219,2.9178052 176,4.67288206 L90.9866667,98.6995487 L41.3333333,58.0062154 L36.9866667,54.2728821 C34.3333065,52.0042454 30.7377412,51.1775642 27.36,52.0595487 C26.8727028,52.1672022 26.3987371,52.3281717 25.9466667,52.5395487 L6.56,60.6728821 C2.86046907,62.2004243 0.327434334,65.670476 0,69.6595487 C0,69.9262154 0,70.1928821 0,70.4595487 L0,184.219549 C0,184.486215 0,184.752882 0,185.019549 C0.327434334,189.008621 2.86046907,192.478673 6.56,194.006215 L25.9466667,202.006215 C26.3987371,202.217592 26.8727028,202.378562 27.36,202.486215 C30.7377412,203.3682 34.3333065,202.541519 36.9866667,200.272882 L41.3333333,196.672882 L90.9866667,155.979549 L176,250.006215 C178.119066,252.121513 180.789161,253.599766 183.706667,254.272882 L183.706667,254.272882 Z M192,73.1528821 L125.893333,127.339549 L192,181.526215 L192,73.1528821 Z M32,90.7262154 L65.0933333,127.339549 L32,163.952882 L32,90.7262154 Z" fill-opacity="0.25" fill="url(#linearGradient-1)"> </path> </g> </g></svg>"""

    def get_connection_data(self):
        """
        Return the connection type and required fields for Team Foundation.
        """
        return {
            "connection_type": "TeamFoundation",
            "fields": ["collection_url", "repo_name", "username", "password", "target_directory"]
        }


