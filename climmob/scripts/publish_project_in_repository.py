import argparse
import os
import sys

from pyramid.paster import get_appsettings

from climmob.models.repository import create_request
from climmob.services import PublicationService


def main(raw_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("ini_path", help="Path to ini file")
    parser.add_argument("project_id", help="Project id")
    parser.add_argument("destination", help="repository name")
    args = parser.parse_args(raw_args)

    if not os.path.exists(os.path.abspath(args.ini_path)):
        print("Ini file does not exists")
        sys.exit(1)

    settings = get_appsettings(args.ini_path, "climmob")

    with create_request(settings, "en", "bioversity") as request:
        publication_service: PublicationService = request.find_service(
            name="publication"
        )
        publication_service._request_repository(args.project_id, args.destination)
        publication_service._approve_repository(args.project_id, args.destination)
        success, msg = publication_service._publish_repository(
            args.project_id, args.destination
        )
        print(f"success: {success}\nmsg:{msg}")
