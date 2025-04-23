# Add all parameters from matchdict to the request as attributes
def factory(request):
    for key, value in request.matchdict.items():
        attribute = getattr(request, key, None)
        if attribute is not None:
            raise AttributeError(f"request already has attribute '{key}'")
        setattr(request, key, value)
