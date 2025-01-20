import os
import sys
import climmob.plugins as p
from climmob.views.basic_views import LoginView

if (
    os.environ.get("CLIMMOB_PYTEST_RUNNING", "false") == "false"
    and os.environ.get("CLIMMOB_RUN_FROM_CELERY", "false") == "false"
):
    if sys.version_info[0] == 3 and sys.version_info[1] >= 6:
        import gevent.monkey

        gevent.monkey.patch_all()

from climmob.config.environment import load_environment
from pyramid.config import Configurator
import os
from configparser import ConfigParser, NoOptionError
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_authstack import AuthenticationStackPolicy

import sentry_sdk
from sentry_sdk.integrations.pyramid import PyramidIntegration
from climmob.middleware.tfa_middleware import two_factor_middleware
import pyramid.tweens


def main(global_config, **settings):

    apppath = os.path.dirname(os.path.abspath(__file__))

    if global_config is not None:  # pragma: no cover
        config = ConfigParser()
        config.read(global_config["__file__"])
        try:
            threads = config.get("server:main", "threads")
        except NoOptionError:
            threads = "1"
        settings["apppath"] = apppath
        settings["server:threads"] = threads
        settings["global:config:file"] = global_config["__file__"]

    """This function returns a Pyramid WSGI application."""
    auth_policy = AuthenticationStackPolicy()
    policy_array = []
    p.load_all(settings)
    main_policy = AuthTktAuthenticationPolicy(
        settings["auth.secret"],
        timeout=settings.get("auth.secret.cookie.timeout", 7200),
        cookie_name=settings["auth.secret.cookie"],
    )
    auth_policy.add_policy("main", main_policy)
    policy_array.append({"name": "main", "policy": main_policy})

    for plugin in p.PluginImplementations(p.IAuthenticationPolicy):
        new_policies = plugin.get_new_authentication_policy_details(settings)
        for a_policy in new_policies:
            new_policy = AuthTktAuthenticationPolicy(
                a_policy["secret"],
                timeout=a_policy["cookie_timeout"],
                cookie_name=a_policy["cookie_name"],
            )
            auth_policy.add_policy(a_policy["policy_name"], new_policy)
            policy_array.append({"name": a_policy["policy_name"], "policy": new_policy})

    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(
        settings=settings,
        authentication_policy=auth_policy,
        authorization_policy=authz_policy,
    )

    config.include(".models")
    # Load and configure the host application
    load_environment(settings, config, apppath, policy_array)

    sentry = settings.get("sentry_sdk.dsn", "")
    if sentry != "":
        sentry_sdk.init(
            dsn=sentry,
            integrations=[
                PyramidIntegration(),
            ],
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production.
            traces_sample_rate=1.0,
        )

    config.add_tween(
        "climmob.middleware.tfa_middleware.two_factor_middleware",
        under=pyramid.tweens.EXCVIEW,
    )

    return config.make_wsgi_app()
