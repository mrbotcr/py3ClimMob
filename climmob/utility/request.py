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
