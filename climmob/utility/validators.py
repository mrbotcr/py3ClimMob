from ..processes import userExists, emailExists

# Form validation

__all__ = ["valideRegisterForm"]


def valideRegisterForm(data, request, _):
    error_summary = {}
    errors = False

    if data["user_password"] != data["user_password2"]:
        error_summary["InvalidPassword"] = _("Invalid password")
        errors = True
    if userExists(data["user_name"], request):
        error_summary["UserExists"] = _("User name already exits")
        errors = True
    if emailExists(data["user_email"], request):
        error_summary["EmailExists"] = _(
            "There is already an account using to this email"
        )
        errors = True
    if data["user_policy"] == "False":
        error_summary["CheckPolicy"] = _(
            "You need to accept the terms of service"
        )
        errors = True
    if data["user_name"] == "":
        error_summary["EmptyUser"] = _("User cannot be emtpy")
        errors = True
    if data["user_password"] == "":
        error_summary["EmptyPass"] = _("Password cannot be emtpy")
        errors = True
    if data["user_fullname"] == "":
        error_summary["EmptyName"] = _("Full name cannot be emtpy")
        errors = True
    if data["user_email"] == "":
        error_summary["EmptyEmail"] = _("Email cannot be emtpy")
        errors = True

    return errors, error_summary
