from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def fetch_p2p_offers():
    # Configure Selenium options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Initialize WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to Binance P2P
        driver.get("https://p2p.binance.com/en/trade/BTC_USDT")
        
        # Wait for the page to load
        time.sleep(5)  # Adjust as necessary

        # Example: Extract offer elements
        offers = driver.find_elements(By.CLASS_NAME, "css-1sv7ku3")  # Update with actual class names
        
        for offer in offers:
            try:
                seller = offer.find_element(By.CLASS_NAME, "css-1gw9lzm").text  # Update class name
                price = offer.find_element(By.CLASS_NAME, "css-1uvkrz3").text  # Update class name
                min_amt = offer.find_element(By.CLASS_NAME, "css-1w0m5x8").text  # Update class name
                max_amt = offer.find_element(By.CLASS_NAME, "css-1w0m5x8").text  # Update class name
                payment_methods = [pm.text for pm in offer.find_elements(By.CLASS_NAME, "css-1pm6sv3")]  # Update class name
                
                print(f"Seller: {seller}, Price: {price}, Min: {min_amt}, Max: {max_amt}, Payment Methods: {payment_methods}")
            except Exception as e:
                print(f"Error extracting offer details: {e}")
        
    except Exception as e:
        print(f"Error navigating to Binance P2P: {e}")
    finally:
        driver.quit()


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


