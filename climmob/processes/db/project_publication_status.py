import datetime

__all__ = [
    "save_project_publication_status",
    "get_global_project_publication_status_id",
    "get_global_project_publication_status_name",
    "get_all_project_publication_statuses",
]

from sqlalchemy import and_

from climmob.models import mapFromSchema
from climmob.models.climmobv4 import ProjectPublicationStatus, PublicationStatus
from climmob.utility import (
    PublicationStatus as PublicationStatusEnum,
    PublicationStatusLabel,
)


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
        status.publication_status_id == PublicationStatusEnum.IN_REVIEW
        for status in res
    ):
        return PublicationStatusEnum.IN_REVIEW.value

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
    return mapFromSchema(query.all())
