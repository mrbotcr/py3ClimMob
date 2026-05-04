import datetime

from climmob.models.climmobv4 import ProjectAnonymizationStatus

__all__ = [
    "get_project_anonymization_status",
    "set_project_anonymization_status",
]


def get_project_anonymization_status(project_id, request) -> int | None:
    query = request.dbsession.query(
        ProjectAnonymizationStatus.anonymization_status_id
    ).filter(ProjectAnonymizationStatus.project_id == project_id)

    res = query.first()
    if res is None:
        return None
    return res.anonymization_status_id


def set_project_anonymization_status(project_id, anonymization_status_id, request):
    query = request.dbsession.query(ProjectAnonymizationStatus).filter(
        ProjectAnonymizationStatus.project_id == project_id
    )

    if query.first() is None:
        project_anonymization_status = ProjectAnonymizationStatus(
            anonymization_status_id=anonymization_status_id,
            project_id=project_id,
            last_updated_by=request.user_in_session,
            last_updated_at=datetime.datetime.now(),
        )
        request.dbsession.add(project_anonymization_status)
    else:
        query.update(
            {
                "anonymization_status_id": anonymization_status_id,
                "last_updated_by": request.user_in_session,
                "last_updated_at": datetime.datetime.now(),
            }
        )
