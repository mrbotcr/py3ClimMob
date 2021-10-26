from ...models import RegistryJsonLog, AssessmentJsonLog
import datetime
from sqlalchemy.exc import IntegrityError

__all__ = ["addJsonLog"]


def addJsonLog(
    request,
    type,
    user_name,
    user_enum,
    assessment_id,
    log_id,
    json_file,
    log_file,
    projectId,
):

    if type == "REG":
        new_log = RegistryJsonLog(
            project_id=projectId,
            enum_user=user_name,
            enum_id=user_enum,
            log_id=log_id,
            log_dtime=datetime.datetime.now(),
            json_file=json_file,
            log_file=log_file,
            status=1,
        )
    else:
        new_log = AssessmentJsonLog(
            project_id=projectId,
            enum_user=user_name,
            enum_id=user_enum,
            ass_cod=assessment_id,
            log_id=log_id,
            log_dtime=datetime.datetime.now(),
            json_file=json_file,
            log_file=log_file,
            status=1,
        )

    try:
        request.dbsession.add(new_log)

        return True, ""
    except IntegrityError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)
