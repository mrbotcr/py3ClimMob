import abc
import requests

class BaseAPIClient(abc.ABC):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Api-key {self.api_key}"
        }

    def get(self, endpoint: str, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {**self.headers, **kwargs.pop("headers", {})}
        return requests.get(url, headers=headers, **kwargs).json()

    @abc.abstractmethod
    def post(self, endpoint: str, data=None, **kwargs):
        pass
