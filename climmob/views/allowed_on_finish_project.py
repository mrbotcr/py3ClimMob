def is_allowed_exception(request):
    path = request.path.lower()

    # allowed exeptions when the useer marks the project as complete
    if path.endswith("/project/new"):
        return True
    if path.endswith("/editprofile"):
        return True

    return False