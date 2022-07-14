from climmob.models import AssessmentJsonLog, Enumerator
from climmob.models.schema import mapToSchema, mapFromSchema
from climmob.processes.db.registry_jsonlog import get_error_from_log

all = [
    "get_assessment_logs",
    "get_assessment_log_by_log",
    "update_assessment_status_log",
    "clean_assessments_error_logs",
]


def get_assessment_logs(request, projectId, ass_cod):

    result = mapFromSchema(
        request.dbsession.query(AssessmentJsonLog, Enumerator)
        .filter(AssessmentJsonLog.project_id == projectId)
        .filter(AssessmentJsonLog.status == 1)
        .filter(AssessmentJsonLog.enum_id == Enumerator.enum_id)
        .filter(AssessmentJsonLog.enum_user == Enumerator.user_name)
        .filter(AssessmentJsonLog.ass_cod == ass_cod)
        .order_by(AssessmentJsonLog.log_dtime)
        .all()
    )

    for registry in result:

        registry["detail"] = get_error_from_log(registry["log_file"])
        registry["lod_dtime"] = registry["log_dtime"].strftime("%m/%d/%Y, %H:%M:%S")

    return result


def get_assessment_log_by_log(request, projectId, ass_cod, log_id):

    result = (
        request.dbsession.query(AssessmentJsonLog.json_file)
        .filter(AssessmentJsonLog.project_id == projectId)
        .filter(AssessmentJsonLog.status == 1)
        .filter(AssessmentJsonLog.enum_user == Enumerator.user_name)
        .filter(AssessmentJsonLog.enum_id == Enumerator.enum_id)
        .filter(AssessmentJsonLog.log_id == log_id)
        .filter(AssessmentJsonLog.ass_cod == ass_cod)
        .first()
    )

    if result:
        return True, result[0]


def update_assessment_status_log(request, projectId, codeid, logid, status):
    data = {"status": status}
    mappedData = mapToSchema(AssessmentJsonLog, data)
    try:
        request.dbsession.query(AssessmentJsonLog).filter(
            AssessmentJsonLog.project_id == projectId
        ).filter(AssessmentJsonLog.log_id == logid).filter(
            AssessmentJsonLog.ass_cod == codeid
        ).update(
            mappedData
        )
        return True, ""
    except Exception as e:
        return False, e


def clean_assessments_error_logs(request, projectId, ass_cod):
    try:
        request.dbsession.query(AssessmentJsonLog).filter(
            AssessmentJsonLog.project_id == projectId
        ).filter(AssessmentJsonLog.ass_cod == ass_cod).delete()
        return True, ""
    except Exception as e:
        return False, str(e)
