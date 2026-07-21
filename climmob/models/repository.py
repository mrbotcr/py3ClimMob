from contextlib import contextmanager

import pyramid
import requests
import transaction
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from climmob.config.celery_app import get_ini_value
from climmob.config.jinja_extensions import initialize
from climmob.models import (
    add_modules_to_schema,
)
from climmob.models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    initialize_schema,
)
from climmob.products.climmob_products import register_products


def sql_fetch_one(sql):
    engine = create_engine(get_ini_value("sqlalchemy.url"), poolclass=NullPool)
    connection = engine.connect()
    res = connection.execute(sql).fetchone()
    connection.invalidate()
    engine.dispose()
    return res


def sql_fetch_all(sql):
    engine = create_engine(get_ini_value("sqlalchemy.url"), poolclass=NullPool)
    connection = engine.connect()
    res = connection.execute(sql).fetchall()
    connection.invalidate()
    engine.dispose()
    return res


def sql_execute(sql):
    engine = create_engine(get_ini_value("sqlalchemy.url"), poolclass=NullPool)
    connection = engine.connect()
    res = connection.execute(sql)
    connection.invalidate()
    engine.dispose()
    return res


def execute_two_sqls(sql1, sql2):
    engine = create_engine(get_ini_value("sqlalchemy.url"), poolclass=NullPool)
    connection = engine.connect()
    res1 = connection.execute(sql1)
    res2 = connection.execute(sql2)
    connection.invalidate()
    engine.dispose()
    return res2


import climmob.products as prd


@contextmanager
def create_request(settings: dict, locale_name: str, user_in_session: str):
    def find_service(request_, name):
        if name == "publication":
            from climmob.services.publication_service import PublicationService

            return PublicationService(request_)
        if name == "notification":
            from climmob.services.notification_service import NotificationService

            return NotificationService(request_)
        return None

    engine = get_engine(settings)

    session_factory = get_session_factory(engine)
    with transaction.manager:
        initialize("climmob/templates")
        dbsession = get_tm_session(session_factory, transaction.manager)
        modules_allowed = ["climmob.models.climmobv4"]
        add_modules_to_schema(modules_allowed)

        try:
            for product in register_products(None):
                prd.addProduct(product)
        except Exception as e:
            print(e)

        request = requests.Session()
        request.dbsession = dbsession
        request.registry = pyramid.registry.Registry
        request.registry.settings = settings
        request.locale_name = locale_name
        request.user_in_session = user_in_session
        request.translate = lambda x: x
        request.find_service = lambda name: find_service(request, name)

        initialize_schema()

        yield request

    engine.dispose()
