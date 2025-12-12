import requests


class BaseService:
    """
    A base service class to handle external API requests.
    It takes in a base URL and an optional API key for authorization.
    Provides methods to make GET and POST requests.
    ```
    always wrap in a try-except block when calling methods to handle external api specific errors.
    """

    def __init__(
            self, 
            base_url: str, 
            api_key: str=None,
        ):
        self.base_url = base_url
        self.api_key = api_key    


    def get_headers(self) -> dict:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers


    def post(self, endpoint: str, data: dict, timeout: int=15):
        url = f"{self.base_url}/{endpoint}"
        headers = self.get_headers()
        try:
            response = requests.post(
                url, headers=headers, json=data, timeout=timeout
            )
        except requests.RequestException as e:
            raise       
        return response


    def get(self, endpoint: str, params: dict=None, timeout: int=15):
        url = f"{self.base_url}/{endpoint}"
        headers = self.get_headers()
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
        except requests.RequestException as e:
            raise      
        return response


    def delete(self, endpoint: str, timeout: int=15):
        url = f"{self.base_url}/{endpoint}"
        headers = self.get_headers()
        try:
            response = requests.delete(url, headers=headers, timeout=timeout)
        except requests.RequestException as e:
            raise      
        return response