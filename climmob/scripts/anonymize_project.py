import sys

from pyramid.paster import get_appsettings, setup_logging
from climmob.models import (
    get_engine,
    Base,
    get_tm_session,
    get_session_factory,
    initialize_schema,
)
import transaction
import requests
import argparse
import pyramid
import os

from climmob.processes import anonymize_project


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

        request = requests.Session()
        request.dbsession = dbsession
        request.registry = pyramid.registry.Registry
        request.registry.settings = settings
        request.locale_name = "en"

        initialize_schema()

        success, msg = anonymize_project(args.project_id, request)

        if success:
            print(f"Successfully anonymized project {args.project_id}")
        else:
            print(f"Failed to anonymized project {args.project_id}")

    engine.dispose()
