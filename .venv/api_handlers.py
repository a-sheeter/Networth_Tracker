import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FINANCIAL_API_KEY")
API_SECRET = os.getenv("FINANCIAL_API_SECRET")
API_BASE_URL = os.getenv("API_BASE_URL")  # add to your .env

def get_balance_from_provider(provider, identifier):

    if provider == "example_provider":
        return fetch_example_provider_balance(identifier)
    
    # Add more providers as needed
    return None

def fetch_example_provider_balance(identifier):

    url = f"{API_BASE_URL}/accounts/{identifier}/balance"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "X-API-SECRET": API_SECRET
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return None
        
        data = response.json()

        return float(data.get("balance"))
    
    except requests.RequestException:
        return None