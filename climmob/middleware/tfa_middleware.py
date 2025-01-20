from climmob.views.basic_views import LoginView
from pyramid.httpexceptions import HTTPFound
import json
import logging

log = logging.getLogger(__name__)


def two_factor_middleware(handler, registry):
    def tween(request):
        if not hasattr(request, "translate"):
            request.translate = lambda text: text

        log.debug(f"Request path: {request.path}")

        excluded_paths = [
            "/login",
            "/setup2fa",
            "/register",
            "/recover",
        ]

        if request.path in excluded_paths:
            log.debug("Path is excluded from middleware checks.")
            return handler(request)

        if not request.authenticated_userid:
            log.debug("No authenticated user. Passing request.")
            return handler(request)

        authenticated_user = request.authenticated_userid
        try:
            authenticated_user = json.loads(authenticated_user.replace("'", '"'))
        except json.JSONDecodeError as e:
            log.error(f"JSON decode error for authenticated_userid: {e}")
            return handler(request)

        login = authenticated_user.get("login")
        if not login:
            log.warning(
                "Authenticated user does not have a login key. Passing request."
            )
            return handler(request)

        log.debug(f"Authenticated user: {login}")

        login_view = LoginView(request)
        two_fa_method = login_view.get_two_fa_method(login)

        log.debug(f"2FA method for user {login}: {two_fa_method}")

        tfa = request.registry.settings.get("twofactorauth.active", "false")

        if not two_fa_method and tfa == "true":
            if request.path != "/setup2fa":
                log.info(f"Redirecting user {login} to /setup2fa.")
                return HTTPFound(location=request.route_url("setup2fa"))
        else:
            log.info(f"User {login} already has 2FA configured ({two_fa_method}).")

        return handler(request)

    return tween
