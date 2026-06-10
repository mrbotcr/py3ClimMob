import datetime

__all__ = ["save_project_publication_status"]

from sqlalchemy import and_

from climmob.models.climmobv4 import ProjectPublicationStatus


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
