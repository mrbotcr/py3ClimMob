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
)
from climmob.products.projectPublication.project_publication import publish_project
from climmob.services.notification_service import NotificationService
from climmob.services.service import Service
from climmob.utility import (
    PublicationStatus,
    is_status_approvable,
    is_status_requestable,
    is_status_publishable,
    is_status_rejectable,
)

log = logging.getLogger("climmob")


class PublicationService(Service):
    def __init__(self, request):
        super().__init__(request)
        self.notification_service: NotificationService = self.request.find_service(
            name="notification"
        )

    def request_project_publication(self, project_id, license, destinations):
        project_license_id = get_project_publication_license_id(
            project_id, self.request
        )
        if not project_license_id:
            if not license:
                return False, self._(
                    "Please select a license before requesting publication."
                )
            save_project_publication_license(project_id, license, self.request)

        status = get_project_publication_status_by_destination_name(
            self.request, project_id, "climmob"
        )
        if not status:
            success, msg = self._request_repository(project_id, "climmob")
            if success:
                success, msg = self._approve_repository(project_id, "climmob")
            if success:
                success, msg = self._publish_repository(project_id, "climmob")
            if not success:
                self.notification_service.notify_publication_failure()

        global_status = get_global_project_publication_status_id(
            self.request, project_id
        )

        if (
            global_status in [PublicationStatus.NOT_REQUESTED, PublicationStatus.REQUESTED]
        ):
            for destination in destinations:
                self._request_repository(project_id, destination)
        elif global_status in [
            PublicationStatus.APPROVED,
            PublicationStatus.PUBLISHED,
            PublicationStatus.FAILED,
            PublicationStatus.PARTIAL,
        ]:
            for destination in destinations:
                self._request_repository(project_id, destination)
                self._approve_repository(project_id, destination)
                self._publish_repository(project_id, destination)
        elif global_status == PublicationStatus.REJECTED:
            for destination in destinations:
                self._reject_repository(project_id, destination)

        self.notification_service.notify_publication_request()

        return True, ""

    def _request_repository(self, project_id, destination):
        status = get_project_publication_status_by_destination_name(
            self.request, project_id, destination
        )
        if not status or is_status_requestable(status["publication_status_id"]):
            success, msg = save_project_publication_status(
                self.request,
                project_id,
                PublicationStatus.REQUESTED.value,
                self.request.user_in_session,
                destination,
            )
            return success, msg
        return (
            False,
            f"Cannot request publication for destination {destination} with status {status['publication_status_id']}",
        )

    def approve_project_publication(self, project_id):
        statuses = get_all_project_publication_statuses(self.request, project_id)
        active_destinations = [
            plugin.get_destination_name()
            for plugin in p.PluginImplementations(p.IPublisher)
        ]
        errors = []
        global_success = True
        for status in statuses:
            if (
                status["destination"] != "climmob"
                and status["destination"] in active_destinations
            ):
                success, msg = self._approve_repository(
                    project_id, status["destination"]
                )
                if not success:
                    global_success = False
                    errors.append((status["destination"], msg))
        return global_success, errors

    def _approve_repository(self, project_id, destination):
        status = get_project_publication_status_by_destination_name(
            self.request, project_id, destination
        )
        if status and is_status_approvable(status["publication_status_id"]):
            success, msg = save_project_publication_status(
                self.request,
                project_id,
                PublicationStatus.APPROVED.value,
                self.request.user_in_session,
                status["destination"],
            )
            return success, msg
        return (
            False,
            f"Cannot approve publication for destination {destination} with status {status['publication_status_id']}",
        )

    def reject_project_publication(self, project_id):
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
            self.notification_service.notify_publication_rejection()
        return global_success, errors

    def _reject_repository(self, project_id, destination):
        status = get_project_publication_status_by_destination_name(
            self.request, project_id, destination
        )
        if status and is_status_rejectable(status["publication_status_id"]):
            success, msg = save_project_publication_status(
                self.request,
                project_id,
                PublicationStatus.REJECTED.value,
                self.request.user_in_session,
                destination,
            )
            return success, msg
        return (
            False,
            f"Cannot reject publication for destination {destination} with status {status['publication_status_id']}",
        )

    def handle_publication_approval(
        self, project_id, project_publication_approval: int
    ):
        # TODO: check against previous status
        if project_publication_approval == PublicationStatus.APPROVED:
            success, errors = self.approve_project_publication(project_id)
            if not success:
                log.error(errors)
            else:
                self.publish_project(project_id)
        elif project_publication_approval == PublicationStatus.REJECTED:
            success, errors = self.reject_project_publication(project_id)
            if not success:
                log.error(errors)
        else:
            log.error(
                f"Invalid project publication approval status: {project_publication_approval}"
            )

    def publish_project(self, project_id):
        # TODO: take the username from the request
        project = get_project_by_id(project_id, self.request)
        statuses = get_all_project_publication_statuses(self.request, project_id)
        destinations = [
            destination["destination"]
            for destination in statuses
            if is_status_publishable(destination["publication_status_id"])
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
        status = get_project_publication_status_by_destination_name(
            self.request, project_id, destination
        )
        if status and is_status_publishable(status["publication_status_id"]):
            project = get_project_by_id(project_id, self.request)
            publish_project(
                project_id,
                project["project_cod"],
                project["owner"]["user_name"],
                project["project_curated_cropname"],
                [destination],
                self.request,
                notify=False,
            )
            return True, ""
        return (
            False,
            f"Cannot publish to repository {destination} with status {status['publication_status_id']}",
        )
