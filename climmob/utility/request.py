import json


def get_body_from_api_request(request) -> str:
    try:
        body = request.params["Body"]
    except KeyError:
        body = {}
        for param in request.params:
            if param != "Apikey":
                body[param] = request.params[param]
        body = json.dumps(body)
    return body


def get_settings(request):
    settings = {}
    for key, value in request.registry.settings.items():
        if isinstance(value, str):
            settings[key] = value

    return settings
