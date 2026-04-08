import datetime

from climmob.models.climmobv4 import ProjectAnonymizationStatus
from climmob.processes.db.anonymized import get_anonymization_percentage
from climmob.utility import AnonymizationStatus


def get_project_anonymization_status(project_id, request) -> int:
    query = request.dbsession.query(
        ProjectAnonymizationStatus.anonymization_status_id
    ).filter(ProjectAnonymizationStatus.project_id == project_id)

    res = query.first()
    if res is None:
        perc = get_anonymization_percentage(project_id, request)
        if perc == 100.0:
            anon_status = AnonymizationStatus.COMPLETED
        else:
            anon_status = AnonymizationStatus.NOT_STARTED
        set_project_anonymization_status(project_id, anon_status.value, request)
        print(
            f"Anonymization status for project_id {project_id} not found. Setting to {anon_status.name}."
        )
        return anon_status.value
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
        query.update({"anonymization_status_id": anonymization_status_id})
