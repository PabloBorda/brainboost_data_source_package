import requests
import json

def get_bybit_p2p_opportunities(base_currency="USDT", trade_type="SELL", fiat_currency="USD"):
    """
    Fetches P2P opportunities from Bybit's public API.

    Args:
        base_currency (str): The cryptocurrency you want to buy/sell (e.g., USDT, BTC, ETH).
        trade_type (str): Trade type, either "BUY" or "SELL".
        fiat_currency (str): The fiat currency to filter by (e.g., USD, EUR).

    Returns:
        list: A list of P2P trading opportunities.
    """
    url = "https://api2.bybit.com/spot/api/otc/item/list"

    params = {
        "userId": "",
        "tokenId": base_currency,
        "currencyId": fiat_currency,
        "side": trade_type.upper(),
        "size": 10,  # Number of results per page
        "page": 1    # Starting page
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if data.get("ret_code") == 0:
            p2p_opportunities = data.get("result", {}).get("items", [])
            return p2p_opportunities
        else:
            print(f"Error from API: {data.get('ret_msg')}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed: {e}")
        return []


def display_p2p_opportunities(opportunities):
    """
    Displays P2P opportunities in a readable format.

    Args:
        opportunities (list): A list of P2P trading opportunities.
    """
    if not opportunities:
        print("No opportunities found.")
        return

    print("P2P Opportunities:\n")
    for opp in opportunities:
        print(f"Trader: {opp.get('nickname', 'N/A')}")
        print(f"Price: {opp.get('price', 'N/A')} {opp.get('currency', 'N/A')}")
        print(f"Quantity Available: {opp.get('quantity', 'N/A')} {opp.get('token', 'N/A')}")
        print(f"Payment Methods: {', '.join([pm.get('name', 'N/A') for pm in opp.get('payMethods', [])])}")
        print("-" * 40)


if __name__ == "__main__":
    base_currency = input("Enter the cryptocurrency (e.g., USDT, BTC): ").upper()
    trade_type = input("Enter trade type (BUY or SELL): ").upper()
    fiat_currency = input("Enter fiat currency (e.g., USD, EUR): ").upper()

    print("\nFetching P2P opportunities...\n")

    opportunities = get_bybit_p2p_opportunities(base_currency, trade_type, fiat_currency)
    display_p2p_opportunities(opportunities)

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

