import datetime

__all__ = ["save_project_publish_status"]

from sqlalchemy import and_

from climmob.models.climmobv4 import ProjectPublishStatus


def save_project_publish_status(
    request, project_id: str, status: int, user_name: str, destination: str
):
    res = request.dbsession.query(ProjectPublishStatus).filter(
        and_(
            ProjectPublishStatus.project_id == project_id,
            ProjectPublishStatus.destination == destination,
        )
    )

    if res.first() is None:
        project_publish_status = ProjectPublishStatus(
            publish_status_id=status,
            project_id=project_id,
            last_updated_by=user_name,
            last_updated_at=datetime.datetime.now(),
            destination=destination,
        )
        request.dbsession.add(project_publish_status)
    else:
        res.update({"publish_status_id": status})
