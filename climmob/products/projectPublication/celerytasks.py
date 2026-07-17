import os

import climmob.plugins as p
from climmob.config.celery_app import celeryApp
from climmob.models.repository import create_request
from climmob.plugins.utilities import climmobCeleryTask
from climmob.services.notification_service import NotificationService


@celeryApp.task(base=climmobCeleryTask)
def publish_project_task(
    settings,
    locale,
    user_in_session,
    cropname,
    project_id,
    owner_username,
    destinations,
    file_path,
    notify=False,
):
    with create_request(settings, locale, user_in_session) as request:
        p.load_all(settings)
        results = {True: [], False: []}
        for plugin in p.PluginImplementations(p.IPublisher):
            if plugin.get_destination_name() in destinations:
                print(f"Publishing to {plugin.get_destination_name()}")
                # success = plugin.publish(
                #     settings, request, file_path, project_id, cropname
                # )
                # results[success].append(plugin.get_destination_name())
                # if success:
                #     print(f"Published to {plugin.get_destination_name()}")
                # else:
                #     print(f"Failed to publish to {plugin.get_destination_name()}")

        if notify:
            notification_service: NotificationService = request.find_service(
                "notification"
            )
            notification_service.notify_publication_failure()

    return ""
