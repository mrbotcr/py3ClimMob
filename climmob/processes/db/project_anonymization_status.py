import datetime

from climmob.models.climmobv4 import ProjectAnonymizationStatus

__all__ = [
    "get_project_anonymization_status",
    "set_project_anonymization_status",
]

from climmob.models.repository import sql_execute, sql_fetch_one


def get_project_anonymization_status(project_id, request) -> int | None:
    query = request.dbsession.query(
        ProjectAnonymizationStatus.anonymization_status_id
    ).filter(ProjectAnonymizationStatus.project_id == project_id)

    res = query.first()
    if res is None:
        return None
    return res.anonymization_status_id


def set_project_anonymization_status(project_id, anonymization_status_id, request):
    sql = f"""
        SELECT * FROM project_anonymization_status
        WHERE project_id = "{project_id}"
    """

    result = sql_fetch_one(sql)

    if result is None:
        sql = f"""
            INSERT INTO project_anonymization_status VALUES
            ({anonymization_status_id},
            "{project_id}",
            "{request.user_in_session}",
            "{datetime.datetime.now()}");

        """
    else:
        sql = f"""
            UPDATE project_anonymization_status
            SET
            anonymization_status_id = {anonymization_status_id},
            last_updated_by = "{request.user_in_session}",
            last_updated_at = "{datetime.datetime.now()}"
            WHERE project_id = "{project_id}";
        """

    sql_execute(sql)
