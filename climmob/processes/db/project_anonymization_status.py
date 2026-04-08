import datetime

from climmob.models.climmobv4 import ProjectAnonymizationStatus
from climmob.utility import AnonymizationStatus


def get_project_anonymization_status(project_id, request):
    query = request.dbsession.query(
        ProjectAnonymizationStatus.anonymization_status_id
    ).filter(ProjectAnonymizationStatus.project_id == project_id)

    res = query.first()
    if res is None:
        # TODO: Check percentage of anonymized data and set status accordingly
        #  if 100% set to COMPLETED,
        #  else set to NOT_STARTED
        anonymization_status_id = AnonymizationStatus.NOT_STARTED.value
        set_project_anonymization_status(project_id, anonymization_status_id, request)
        print(
            f"Anonymization status for project_id {project_id} not found. Setting to NOT_STARTED."
        )
        return anonymization_status_id
    print(f"Status: {res.anonymization_status_id}")
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
