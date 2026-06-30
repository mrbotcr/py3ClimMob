import datetime

__all__ = [
    "save_project_publication_status",
    "get_global_project_publication_status_id",
    "get_project_publication_status",
]

from sqlalchemy import and_

from climmob.models.climmobv4 import ProjectPublicationStatus
from climmob.utility import PublicationStatus


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


def get_global_project_publication_status_id(request, project_id: str):
    res = (
        request.dbsession.query(ProjectPublicationStatus)
        .filter(ProjectPublicationStatus.project_id == project_id)
        .all()
    )
    if not res:
        return PublicationStatus.INITIAL

    if any(status.publication_status_id == PublicationStatus.FAILED for status in res):
        return PublicationStatus.FAILED

    if any(
        status.publication_status_id == PublicationStatus.PUBLISHED for status in res
    ):
        return PublicationStatus.PUBLISHED

    if any(
        status.publication_status_id == PublicationStatus.APPROVED for status in res
    ):
        return PublicationStatus.APPROVED

    if any(
        status.publication_status_id == PublicationStatus.REJECTED for status in res
    ):
        return PublicationStatus.REJECTED

    if any(
        status.publication_status_id == PublicationStatus.IN_REVIEW for status in res
    ):
        return PublicationStatus.IN_REVIEW

    if any(
        status.publication_status_id == PublicationStatus.REQUESTED for status in res
    ):
        return PublicationStatus.REQUESTED


def get_project_publication_status(request, project_id: str):
    query = (
        request.dbsession.query(ProjectPublicationStatus)
        .filter(ProjectPublicationStatus.project_id == project_id)

    )
    return query.all()
