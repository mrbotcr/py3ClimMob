from climmob.services.crop_index_client import CropIndexAPIClient


def includeme(config):
    """Register all external API clients and make them injectable."""
    settings = config.get_settings()

    api_key = settings.get("crop_index.api_key")
    base_url = settings.get("crop_index.base_url")

    # Instantiate clients once (stateless clients are safe to reuse)
    crop_index_client = CropIndexAPIClient(api_key, base_url)

    # Register in the app registry
    config.registry.crop_index_api = crop_index_client

    # data = request.crop_index_api.get_by_id(item_id)

    # Add as request property for convenient per-request access
    config.add_request_method(
        lambda req: config.registry.crop_index_api, name="crop_index_api", reify=True
    )
