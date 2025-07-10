import sys

from climmob.products.projectsSummary.projectsSummary import create_projects_summary
from pyramid.paster import get_appsettings, setup_logging
import requests
import argparse
import pyramid
import os


def main(raw_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("ini_path", help="Path to ini file")
    args = parser.parse_args(raw_args)

    if not os.path.exists(os.path.abspath(args.ini_path)):
        print("Ini file does not exists")
        sys.exit(1)

    setup_logging(args.ini_path)
    settings = get_appsettings(args.ini_path, "climmob")

    request = requests.Session()
    request.registry = pyramid.registry.Registry
    request.registry.settings = settings

    create_projects_summary(request)
