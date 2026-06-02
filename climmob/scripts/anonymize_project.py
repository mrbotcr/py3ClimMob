import argparse
import os
import sys

import pyramid
import requests
import transaction
from pyramid.paster import get_appsettings, setup_logging

from climmob.models import (
    get_engine,
    Base,
    get_tm_session,
    get_session_factory,
    initialize_schema,
    add_modules_to_schema,
)
from climmob.products.analysisdata import process_anonymization


def main(raw_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("ini_path", help="Path to ini file")
    parser.add_argument("project_id", help="Project id")
    args = parser.parse_args(raw_args)

    if not os.path.exists(os.path.abspath(args.ini_path)):
        print("Ini file does not exists")
        sys.exit(1)

    settings = get_appsettings(args.ini_path, "climmob")

    engine = get_engine(
        settings,
    )

    Base.metadata.create_all(engine)
    session_factory = get_session_factory(engine)

    with transaction.manager:

        dbsession = get_tm_session(session_factory, transaction.manager)
        setup_logging(args.ini_path)

        modules_allowed = ["climmob.models.climmobv4"]
        add_modules_to_schema(modules_allowed)

        request = requests.Session()
        request.dbsession = dbsession
        request.registry = pyramid.registry.Registry
        request.registry.settings = settings
        request.locale_name = "en"
        request.user_in_session = "bioversity"
        request.translate = lambda x: x

        initialize_schema()

        success = process_anonymization(args.project_id, request)

        if success:
            print(f"Successfully anonymized project {args.project_id}")
        else:
            print(f"Failed to anonymized project {args.project_id}")

    engine.dispose()
