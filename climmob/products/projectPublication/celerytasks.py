import os

import climmob.plugins as p
from climmob.config.celery_app import celeryApp
from climmob.models.repository import create_request
from climmob.plugins.utilities import climmobCeleryTask


@celeryApp.task(base=climmobCeleryTask)
def publish_project_task(
    settings,
    locale,
    user_in_session,
    cropname,
    project_id,
    owner_username,
    destinations,
    product_directory,
):

    with create_request(settings, locale, user_in_session) as request:
        print(
            f"publish_project_task: {project_id}, {owner_username}, {cropname}, {destinations}"
        )
        print(f"path_out: {product_directory}")
        formatted = "{}-{}.json".format(cropname, project_id)
        print(formatted)
        file_path = os.path.join(product_directory, formatted)
        print(file_path)

        p.load_all(settings)
        for plugin in p.PluginImplementations(p.IPublisher):
            if plugin.get_destination_name() in destinations:
                print(f"Publishing to {plugin.get_destination_name()}")
                # plugin.publish(settings, request, file_path, project_id, cropname)

    return ""
