from climmob.processes import (
    get_all_project_publication_statuses,
    save_project_publication_status,
    save_project_publication_license,
    get_project_publication_status_by_destination_name,
    get_project_by_id,
    get_project_publication_status_by_status_id,
)
from climmob.products.projectPublication.project_publication import publish_project
from climmob.services.notification_service import NotificationService
from climmob.services.service import Service
from climmob.utility import PublicationStatus


class PublicationService(Service):
    def __init__(self, request):
        super().__init__(request)
        self.notification_service: NotificationService = self.request.find_service(
            name="notification"
        )

    def request_project_publication(self, project_id, license, destinations):
        save_project_publication_license(project_id, license, self.request)

        # TODO: publish climmob, if it is not already published
        climmob_status = get_project_publication_status_by_destination_name(
            self.request, project_id, "climmob"
        )
        if (
            climmob_status
            and climmob_status["publication_status_id"] != PublicationStatus.PUBLISHED
        ):
            self._publish_repository(project_id, "climmob")
            # TODO: what happens if climmob publish fails

        # TODO: Check if the project is already requested for publication
        #  if it is, match the status accordingly
        #  if it is not, request each destination

        for destination in destinations:
            # TODO: Check if the status is not requested
            self._request_repository(project_id, destination)

        self.notification_service.notify_publication_request()

    def _request_repository(self, project_id, destination):
        save_project_publication_status(
            self.request,
            project_id,
            PublicationStatus.REQUESTED,
            self.request.user_in_session,
            destination,
        )

    def approve_project_publication(self, project_id):
        statuses = get_all_project_publication_statuses(self.request, project_id)
        for status in statuses:
            if status["destination"] != "climmob":
                self._approve_repository(project_id, status["destination"])

    def _approve_repository(self, project_id, destination):
        # TODO?: Check if the status is requested or rejected before saving
        save_project_publication_status(
            self.request,
            project_id,
            PublicationStatus.APPROVED,
            self.request.user_in_session,
            destination,
        )

    def reject_project_publication(self, project_id):
        statuses = get_all_project_publication_statuses(self.request, project_id)
        for status in statuses:
            if status["destination"] != "climmob":
                self._reject_repository(project_id, status["destination"])

        self.notification_service.notify_publication_rejection()

    def _reject_repository(self, project_id, destination):
        # TODO?: Check if the status is requested or approved before saving
        save_project_publication_status(
            self.request,
            project_id,
            PublicationStatus.REJECTED,
            self.request.user_in_session,
            destination,
        )

    def publish_project(self, project_id):
        project = get_project_by_id(project_id, self.request, extra=True)
        destinations = [
            destination["destination"]
            for destination in get_project_publication_status_by_status_id(
                self.request, project_id, PublicationStatus.APPROVED.value
            )
        ]
        publish_project(
            project_id,
            project["owner"]["user_name"],
            project["project_curated_cropname"],
            destinations,
            self.request,
        )
        # @celeryApp.task(base=climmobCeleryTask)
        # def task(settings):
        #     statuses = get_all_project_publication_statuses(self.request, project_id)
        #
        #     for status in statuses:
        #         # if status["destination"] != "climmob":
        #             success = self._publish_repository(project_id, status["destination"])
        #             # TODO: update individual repo status
        #
        #     # TODO: Only if all are successfully published, notify success
        #     self.notification_service.notify_publication_success()
        #
        #     # TODO: If any of the destinations fail to publish, notify failure
        #     self.notification_service.notify_publication_failure()
        #
        # task.apply_async(args=(
        #     get_settings(self.request),
        # ),
        # queue="ClimMob",)

    def _publish_repository(self, project_id, destination):
        # TODO?: Check if the status is approved before saving
        print(f"Publishing project {project_id} to destination {destination}")
        # publisher = get_publisher_by_destination_name(destination)
        # success = publisher.publish()
        #
        # save_project_publication_status(
        #     self.request,
        #     project_id,
        #     PublicationStatus.PUBLISHED,
        #     self.request.user_in_session,
        #     destination,
        # )

        # return success
