import datetime

__all__ = [
    "save_project_publication_status",
    "get_global_project_publication_status_id",
    "get_global_project_publication_status_name",
    "get_all_project_publication_statuses",
    "get_project_publication_approval_status_id",
    "get_project_publication_status_by_destination_name",
    "get_project_publication_status_by_status_id",
]

from sqlalchemy import and_

from climmob.models import mapFromSchema
from climmob.models.climmobv4 import ProjectPublicationStatus, PublicationStatus
from climmob.utility import (
    PublicationStatus as PublicationStatusEnum,
    PublicationStatusLabel,
)

import climmob.plugins as p


def save_project_publication_status(
    request, project_id: str, status: int, user_name: str, destination: str
):
    res = request.dbsession.query(ProjectPublicationStatus).filter(
        and_(
            ProjectPublicationStatus.project_id == project_id,
            ProjectPublicationStatus.destination == destination,
        )
    )

    if res.first() is None:
        project_publication_status = ProjectPublicationStatus(
            publication_status_id=status,
            project_id=project_id,
            last_updated_by=user_name,
            last_updated_at=datetime.datetime.now(),
            destination=destination,
        )
        request.dbsession.add(project_publication_status)
    else:
        res.update({"publication_status_id": status})


def get_global_project_publication_status_name(request, project_id: str) -> str:
    status_id = get_global_project_publication_status_id(request, project_id)
    return PublicationStatusLabel[PublicationStatusEnum(status_id).name].value


def get_project_publication_approval_status_id(request, project_id: str) -> int:
    status_id = get_global_project_publication_status_id(request, project_id)
    status_map = {
        PublicationStatusEnum.INITIAL: -1,
        PublicationStatusEnum.REQUESTED: 0,
        PublicationStatusEnum.APPROVED: PublicationStatusEnum.APPROVED.value,
        PublicationStatusEnum.REJECTED: PublicationStatusEnum.REJECTED.value,
        PublicationStatusEnum.PUBLISHED: PublicationStatusEnum.APPROVED.value,
        PublicationStatusEnum.FAILED: PublicationStatusEnum.APPROVED.value,
    }
    return status_map[PublicationStatusEnum(status_id)]


def get_global_project_publication_status_id(request, project_id: str) -> int:
    res = (
        request.dbsession.query(ProjectPublicationStatus)
        .filter(ProjectPublicationStatus.project_id == project_id)
        .all()
    )
    if not res:
        return PublicationStatusEnum.INITIAL.value

    if any(
        status.publication_status_id == PublicationStatusEnum.FAILED for status in res
    ):
        return PublicationStatusEnum.FAILED.value

    if any(
        status.publication_status_id == PublicationStatusEnum.PUBLISHED
        for status in res
    ):
        return PublicationStatusEnum.PUBLISHED.value

    if any(
        status.publication_status_id == PublicationStatusEnum.APPROVED for status in res
    ):
        return PublicationStatusEnum.APPROVED.value

    if any(
        status.publication_status_id == PublicationStatusEnum.REJECTED for status in res
    ):
        return PublicationStatusEnum.REJECTED.value

    if any(
        status.publication_status_id == PublicationStatusEnum.REQUESTED
        for status in res
    ):
        return PublicationStatusEnum.REQUESTED.value


def get_all_project_publication_statuses(
    request, project_id: str
) -> list[ProjectPublicationStatus]:
    query = (
        request.dbsession.query(
            ProjectPublicationStatus, PublicationStatus.publication_status_name
        )
        .join(
            PublicationStatus,
            PublicationStatus.publication_status_id
            == ProjectPublicationStatus.publication_status_id,
        )
        .filter(ProjectPublicationStatus.project_id == project_id)
    )
    result = mapFromSchema(query.all())
    publishers = p.PluginImplementations(p.IPublisher)
    for repo in result:
        for plugin in publishers:
            if repo["destination"] == plugin.get_destination_name():
                repo["destination_label"] = plugin.get_label()

    return result


def get_project_publication_status_by_destination_name(
    request, project_id: str, destination_name: str
) -> ProjectPublicationStatus:
    query = (
        request.dbsession.query(ProjectPublicationStatus)
        .filter(ProjectPublicationStatus.project_id == project_id)
        .filter(ProjectPublicationStatus.destination == destination_name)
    )
    result = mapFromSchema(query.one())
    return result


def get_project_publication_status_by_status_id(
    request, project_id: str, status_id: int
) -> list[ProjectPublicationStatus]:
    query = (
        request.dbsession.query(ProjectPublicationStatus)
        .filter(ProjectPublicationStatus.project_id == project_id)
        .filter(ProjectPublicationStatus.publication_status_id == status_id)
    )
    result = mapFromSchema(query.all())
    return result
