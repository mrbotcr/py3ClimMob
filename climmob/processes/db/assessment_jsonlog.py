from climmob.models import AssessmentJsonLog, Enumerator
from ...models.schema import mapToSchema, mapFromSchema
from .registry_jsonlog import get_error_from_log
import os
from xml.dom import minidom

all = [
    "get_assessment_logs","get_assessment_log_by_log","update_assessment_status_log"
]

def get_assessment_logs(request, user_name, project_cod, ass_cod):

    result = mapFromSchema(
        request.dbsession.query(AssessmentJsonLog,Enumerator)
        .filter(AssessmentJsonLog.user_name == user_name)
        .filter(AssessmentJsonLog.project_cod == project_cod)
        .filter(AssessmentJsonLog.status == 1)
        .filter(Enumerator.user_name == user_name)
        .filter(AssessmentJsonLog.enum_id == Enumerator.enum_id)
        .filter(AssessmentJsonLog.enum_user == user_name)
        .filter(AssessmentJsonLog.ass_cod == ass_cod)
        .order_by(AssessmentJsonLog.log_dtime)
        .all()
    )

    for registry in result:

        registry["detail"] = get_error_from_log(registry["log_file"])
        registry["lod_dtime"] = registry["log_dtime"].strftime("%m/%d/%Y, %H:%M:%S")

    return result

def get_assessment_log_by_log(request, user_name, project_cod,ass_cod,log_id):

    result = (
        request.dbsession.query(AssessmentJsonLog.json_file)
            .filter(AssessmentJsonLog.user_name == user_name)
            .filter(AssessmentJsonLog.project_cod == project_cod)
            .filter(AssessmentJsonLog.status == 1)
            .filter(Enumerator.user_name == user_name)
            .filter(AssessmentJsonLog.enum_id == Enumerator.enum_id)
            .filter(AssessmentJsonLog.enum_user == user_name)
            .filter(AssessmentJsonLog.log_id == log_id)
            .filter(AssessmentJsonLog.ass_cod == ass_cod)
            .first()
    )

    if result:
        return True, result[0]

def update_assessment_status_log(request, user, project, codeid,logid,status):
    data = {"status": status}
    mappedData = mapToSchema(AssessmentJsonLog, data)
    try:
        request.dbsession.query(AssessmentJsonLog).filter(AssessmentJsonLog.user_name == user).filter(AssessmentJsonLog.project_cod == project).filter(AssessmentJsonLog.log_id == logid).filter(AssessmentJsonLog.ass_cod == codeid).update(mappedData)
        return True, ""
    except Exception as e:
        return False, e