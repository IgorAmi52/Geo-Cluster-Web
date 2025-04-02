import requests


class ApiService:
    def __init__(self, base_url, api_key=None):
        """Initialize the API service with a base URL and optional API key."""
        self.base_url = base_url
        self.api_key = api_key

    def get(self, endpoint, params=None):
        """Send a GET request to the specified endpoint."""
        if not self.base_url:
            raise ValueError("Base URL is not configured.")

        url = f"{self.base_url}{endpoint}"
        params = params or {}
        if self.api_key:
            params["api_key"] = self.api_key  # Add API key if available

        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def uses_api_key(self):
        """Check if the API service uses an API key."""
        return True if self.api_key is not None else False
