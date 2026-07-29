import logging

import climmob.plugins as p
from climmob.processes import (
    get_all_project_publication_statuses,
    save_project_publication_status,
    save_project_publication_license,
    get_project_publication_status_by_destination_name,
    get_project_by_id,
    get_project_publication_license_id,
    get_global_project_publication_status_id,
    save_project_publication_approved,
    get_project_publication_approved,
)
from climmob.products.projectPublication.project_publication import publish_project
from climmob.services.notification_service import NotificationService
from climmob.services.service import Service
from climmob.utility import (
    PublicationStatus,
    PublicationLicenseLabel,
    PublicationLicense,
    PublicationApproved,
)

log = logging.getLogger("climmob")


class PublicationService(Service):
    def __init__(self, request):
        super().__init__(request)
        self.notification_service: NotificationService = self.request.find_service(
            name="notification"
        )

    def request_project_publication(self, project_id, license, destinations):
        current_project_license_id = get_project_publication_license_id(
            project_id, self.request
        )
        if not current_project_license_id:
            if not license:
                return False, "no_license"
            save_project_publication_license(project_id, license, self.request)

        climmob_status = get_project_publication_status_by_destination_name(
            self.request, project_id, "climmob"
        )
        if climmob_status:
            if (
                climmob_status["publication_status_id"]
                != PublicationStatus.PUBLISHED.value
            ):
                for destination in destinations:
                    success, msg = save_project_publication_status(
                        project_id,
                        PublicationStatus.FAILED.value,
                        self.request.user_in_session,
                        destination,
                    )
                    if not success:
                        return False, "db_error"
                self.notification_service.notify_publication_failure(
                    {
                        "repositories": [
                            {
                                "destination": destination,
                                "msg": "ClimMob repository is in FAILED status, therefore the publication file might not exist",
                            }
                            for destination in destinations
                        ],
                        "project": get_project_by_id(project_id, self.request),
                    }
                )
                return True, ""
        else:
            self._request_repository(project_id, "climmob")
            self._publish_repository(project_id, "climmob")

        statuses = get_all_project_publication_statuses(self.request, project_id)

        approved = get_project_publication_approved(self.request, project_id)

        if approved == PublicationApproved.DEFAULT.value:
            for destination in destinations:
                self._request_repository(project_id, destination)
        elif approved == PublicationApproved.REJECTED.value:
            for destination in destinations:
                self._reject_repository(project_id, destination)
        elif approved == PublicationApproved.APPROVED.value:
            for destination in destinations:
                self._request_repository(project_id, destination)
                self._publish_repository(project_id, destination)

        project = get_project_by_id(project_id, self.request)
        license_name = PublicationLicenseLabel[
            PublicationLicense(current_project_license_id or int(license)).name
        ].value
        repositories = ", ".join([status["destination_label"] for status in statuses])
        # TODO: notify only if there are changes? just once?
        # TODO: include repositories and license in the email?
        self.notification_service.notify_publication_request(
            {
                "project": project,
                "repositories": repositories,
                "license": license_name,
                "_": self._,
            }
        )

        return True, ""

    def _request_repository(self, project_id, destination):
        active_destinations = [
            plugin.get_destination_name()
            for plugin in p.PluginImplementations(p.IPublisher)
        ]
        if destination in active_destinations:
            success, msg = save_project_publication_status(
                project_id,
                PublicationStatus.REQUESTED.value,
                self.request.user_in_session,
                destination,
            )
            return success, msg
        else:
            return False, f"Repository {destination} is not active"

    def approve_project_publication(self, project_id):
        # TODO: verify climmob success
        success, msg = save_project_publication_approved(
            self.request, project_id, PublicationApproved.APPROVED.value
        )
        if not success:
            return False, [msg]

        statuses = get_all_project_publication_statuses(self.request, project_id)
        errors = []
        global_success = True
        for status in statuses:
            if status["destination"] != "climmob":
                success, msg = self._approve_repository(
                    project_id, status["destination"]
                )
                if not success:
                    global_success = False
                    errors.append((status["destination"], msg))
        return global_success, errors

    def _approve_repository(self, project_id, destination):
        active_destinations = [
            plugin.get_destination_name()
            for plugin in p.PluginImplementations(p.IPublisher)
        ]
        if destination in active_destinations:
            success, msg = save_project_publication_status(
                project_id,
                PublicationStatus.APPROVED.value,
                self.request.user_in_session,
                destination,
            )
            return success, msg
        else:
            return False, f"Repository {destination} is not active"

    def reject_project_publication(self, project_id, admin_message):
        success, msg = save_project_publication_approved(
            self.request, project_id, PublicationApproved.REJECTED.value
        )
        if not success:
            return False, [msg]

        statuses = get_all_project_publication_statuses(self.request, project_id)
        errors = []
        global_success = True
        for status in statuses:
            if status["destination"] != "climmob":
                success, msg = self._reject_repository(
                    project_id, status["destination"]
                )
                if not success:
                    global_success = False
                    errors.append((status["destination"], msg))
        if global_success:
            project = get_project_by_id(project_id, self.request)
            project_license_id = get_project_publication_license_id(
                project_id, self.request
            )
            license_name = PublicationLicenseLabel[
                PublicationLicense(project_license_id).name
            ].value
            repositories = ", ".join(
                [status["destination_label"] for status in statuses]
            )
            self.notification_service.notify_publication_rejection(
                {
                    "project": project,
                    "repositories": repositories,
                    "license": license_name,
                    "admin_message": admin_message,
                    "_": self._,
                }
            )
        return global_success, errors

    def _reject_repository(self, project_id, destination):
        active_destinations = [
            plugin.get_destination_name()
            for plugin in p.PluginImplementations(p.IPublisher)
        ]
        if destination in active_destinations:
            success, msg = save_project_publication_status(
                project_id,
                PublicationStatus.REJECTED.value,
                self.request.user_in_session,
                destination,
            )
            return success, msg
        else:
            return False, f"Repository {destination} is not active"

    def handle_publication_approval(
        self, project_id, project_publication_approval: int, admin_message
    ):
        # TODO: verify climmob success
        approved = get_project_publication_approved(self.request, project_id)
        if approved == project_publication_approval:
            return
        if project_publication_approval == PublicationApproved.APPROVED:
            success, errors = self.approve_project_publication(project_id)
            if not success:
                log.error(errors)
            else:
                self.publish_project(project_id)
        elif project_publication_approval == PublicationApproved.REJECTED:
            success, errors = self.reject_project_publication(project_id, admin_message)
            if not success:
                log.error(errors)
        else:
            log.error(
                f"Invalid project publication approval status: {project_publication_approval}"
            )

    def publish_project(self, project_id):
        project = get_project_by_id(project_id, self.request)
        statuses = get_all_project_publication_statuses(self.request, project_id)
        destinations = [
            destination["destination"]
            for destination in statuses
            if destination["destination"] != "climmob"
        ]
        publish_project(
            project_id,
            project["project_cod"],
            project["owner"]["user_name"],
            project["project_curated_cropname"],
            destinations,
            self.request,
        )

    def _publish_repository(self, project_id, destination):
        print(f"Publishing project {project_id} to destination {destination}")
        active_destinations = [
            plugin.get_destination_name()
            for plugin in p.PluginImplementations(p.IPublisher)
        ]
        if destination in active_destinations:
            project = get_project_by_id(project_id, self.request)
            publish_project(
                project_id,
                project["project_cod"],
                project["owner"]["user_name"],
                project["project_curated_cropname"],
                [destination],
                self.request,
                notify_success=False,
            )
            return True, ""
        else:
            return False, f"Repository {destination} is not active"
