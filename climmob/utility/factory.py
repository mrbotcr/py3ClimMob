# Add all parameters from matchdict to the request as attributes
def factory(request):
    for key, value in request.matchdict.items():
        setattr(request, key, value)
    return None
