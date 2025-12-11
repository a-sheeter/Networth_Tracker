from .webull import WebullProvider

# Map provider name in your database to provider class
PROVIDER_MAP = {
    "webull": WebullProvider(),
}

def get_balance_for_account(account):
    provider_name = account["api_provider"]

    if provider_name not in PROVIDER_MAP:
        print(f"No provider found for {provider_name}")
        return None
    
    provider = PROVIDER_MAP[provider_name]
    return provider.fetch_balance(account)