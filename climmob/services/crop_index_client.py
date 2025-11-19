from climmob.services.base_api_client import BaseAPIClient

class CropIndexAPIClient(BaseAPIClient):
    def __init__(self, api_key: str, base_url: str):
        super().__init__(api_key, base_url)
        self.resource = "germplasm"

    def get_tech_by_id(self, germplasm_id: str):
        """GET /germplasm/:id"""
        endpoint = f"{self.resource}/{germplasm_id}"
        return self.get(endpoint)

    def search(self, **params):
        """GET /germplasm?q=..."""
        return self.get(self.resource, params=params)

    def post(self, endpoint: str, data=None, **kwargs):
        raise NotImplementedError("Crop Index API only supports GET requests.")
