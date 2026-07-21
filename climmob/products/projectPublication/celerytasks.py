import climmob.plugins as p
from climmob.config.celery_app import celeryApp
from climmob.models.repository import create_request
from climmob.plugins.utilities import climmobCeleryTask
from climmob.processes import (
    save_project_publication_status,
    get_project_by_id,
    get_project_publication_license_id,
)
from climmob.services.notification_service import NotificationService
from climmob.utility import (
    PublicationStatus,
    PublicationLicenseLabel,
    PublicationLicense,
)


@celeryApp.task(base=climmobCeleryTask)
def publish_project_task(
    settings,
    locale,
    user_in_session,
    cropname,
    project_id,
    destinations,
    file_path,
    notify_success=False,
):
    with create_request(settings, locale, user_in_session) as request:
        p.load_all(settings)
        results = {True: [], False: []}
        for plugin in p.PluginImplementations(p.IPublisher):
            destination_name = plugin.get_destination_name()
            if destination_name in destinations:
                print(f"Publishing to {destination_name}")
                success, msg = plugin.publish(
                    settings, request, file_path, project_id, cropname
                )
                results[success].append(destination_name)
                status = (
                    PublicationStatus.PUBLISHED if success else PublicationStatus.FAILED
                )
                success, msg = save_project_publication_status(
                    project_id, status.value, user_in_session, destination_name
                )
                if success:
                    print(f"SUCCESS: Published to {plugin.get_destination_name()}")
                else:
                    print(
                        f"FAILURE: Failed to publish to {plugin.get_destination_name()}"
                    )
        print(f"Success: {results[True]}")
        print(f"Failure: {results[False]}")
        notification_service: NotificationService = request.find_service("notification")
        if notify_success:
            project_license_id = get_project_publication_license_id(project_id, request)
            license_name = PublicationLicenseLabel[
                PublicationLicense(project_license_id).name
            ].value
            notification_service.notify_publication_success(
                {
                    "project": get_project_by_id(project_id, request),
                    "repositories": destinations,
                    "license": license_name,
                    "_": request.translate,  # TODO: check translation effectiveness
                }
            )
        if results[False]:
            notification_service.notify_publication_failure({})

    return ""
