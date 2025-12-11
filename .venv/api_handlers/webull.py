import os 
import requests
from .base_provider import BaseProvider

WEBULL_API_KEY = os.getenv("WEBULL_API_KEY")
WEBULL_BASE_URL = "https://api.webull.com" # REPLACE

class WebullProvider(BaseProvider):
    def fetch_balance(self, account):
        """
        account contains:
        -account_identifier
        -api_provider
        -id
        """

        account_id = account["account_identifier"]

        try:
            response = requests.get(
                f"{WEBULL_BASE_URL}/account/balance",
                headers={"Authorization": f"Bearer {WEBULL_API_KEY}"},
                params={"account_id": account_id},
                timeout=5
            )

            if response.status_code != 200:
                print("WeBull API error", response.text)
                return None
            
            data = response.json()

            return float(data["total_asset"])
        
        except Exception as e:
            print("error contacting WeBull:", e)
            return None