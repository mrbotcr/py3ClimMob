import sys

if os.environ.get("CLIMMOB_PYTEST_RUNNING", "false") == "false" and os.environ.get("CLIMMOB_RUN_FROM_CELERY", "false") == "false":
    if sys.version_info[0] == 3 and sys.version_info[1] >= 6:
        import gevent.monkey

        gevent.monkey.patch_all()

from climmob.config.environment import load_environment
from pyramid.config import Configurator
import os
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_authstack import AuthenticationStackPolicy


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    auth_policy = AuthenticationStackPolicy()
    policy_array = []

    main_policy = AuthTktAuthenticationPolicy(
        settings["auth.secret"],
        timeout=settings.get("auth.secret.cookie.timeout", 7200),
        cookie_name=settings["auth.secret.cookie"],
    )
    auth_policy.add_policy("main", main_policy)
    policy_array.append({"name": "main", "policy": main_policy})

    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(
        settings=settings,
        authentication_policy=auth_policy,
        authorization_policy=authz_policy,
    )

    apppath = os.path.dirname(os.path.abspath(__file__))

    config.include(".models")
    # Load and configure the host application
    load_environment(settings, config, apppath, policy_array)

    return config.make_wsgi_app()
