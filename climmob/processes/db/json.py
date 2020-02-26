
from ...models import RegistryJsonLog, AssessmentJsonLog
import datetime
from sqlalchemy.exc import IntegrityError

__all__ = [
    "addJsonLog"
]

def addJsonLog(
    request,
    type,
    user_name,
    user_enum,
    project_cod,
    assessment_id,
    log_id,
    json_file,
    log_file,
):

    if type == "REG":
        new_log = RegistryJsonLog(
            user_name=user_name,
            project_cod=project_cod,
            enum_user= user_name,
            enum_id= user_enum,
            log_id=log_id,
            log_dtime= datetime.datetime.now(),
            json_file=json_file,
            log_file=log_file,
            status=1
        )
    else:
        new_log = AssessmentJsonLog(
            user_name=user_name,
            project_cod=project_cod,
            enum_user=user_name,
            enum_id=user_enum,
            ass_cod= assessment_id,
            log_id=log_id,
            log_dtime=datetime.datetime.now(),
            json_file=json_file,
            log_file=log_file,
            status=1
        )

    try:
        request.dbsession.add(new_log)

        return True, ""
    except IntegrityError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

#SELECT user_name, project_cod,fileuid as log_id,Now() as log_dtime,concat("/home/bmadriz/temp/climmob/",user_name,"/",project_cod,"/data/reg/json/",fileuid,"/",fileuid,".json") as json_file, concat("/home/bmadriz/temp/climmob/",user_name,"/",project_cod,"/data/reg/json/",fileuid,"/",fileuid,".json") as log_file, 1 as status, user_name as enum_user,(select enum_id from climmob2020.enumerator where user_name = S.user_name limit 1) as enum_id FROM climmob2020.storageerrors S where submission_type = 'REG';
#SELECT user_name, project_cod, assessment_id as ass_cod,fileuid as log_id,Now() as log_dtime,concat("/home/bmadriz/temp/climmob/",user_name,"/",project_cod,"/data/ass/",assessment_id,"/json/",fileuid,"/",fileuid,".json") as json_file, concat("/home/bmadriz/temp/climmob/",user_name,"/",project_cod,"/data/ass/",assessment_id,"/json/",fileuid,"/",fileuid,".json") as log_file, 1 as status, user_name as enum_user,(select enum_id from climmob2020.enumerator where user_name = S.user_name limit 1) as enum_id FROM climmob2020.storageerrors S where submission_type = 'ASS';

#SELECT concat("INSERT INTO registry_jsonlog VALUES ('",user_name,"','", project_cod,"','",fileuid,"','",Now(),"','",concat("/home/bmadriz/temp/climmob/",user_name,"/",project_cod,"/data/reg/json/",fileuid,"/",fileuid,".json") ,"','",concat("/home/bmadriz/temp/climmob/",user_name,"/",project_cod,"/data/reg/json/",fileuid,"/",fileuid,".log"),"','", 1,"','",(select enum_id from climmob2020.enumerator where user_name = S.user_name limit 1),"','", user_name,"');") FROM climmob2020.storageerrors S where submission_type = 'REG';
#SELECT concat("INSERT INTO assesment_jsonlog VALUES ('",user_name,"','", project_cod,"','",assessment_id,"','",fileuid,"','",Now(),"','",concat("/home/bmadriz/temp/climmob/",user_name,"/",project_cod,"/data/ass/",assessment_id,"/json/",fileuid,"/",fileuid,".json"),"','",concat("/home/bmadriz/temp/climmob/",user_name,"/",project_cod,"/data/ass/",assessment_id,"/json/",fileuid,"/",fileuid,".log"),"','", 1,"','",(select enum_id from climmob2020.enumerator where user_name = S.user_name limit 1) ,"','", user_name,"');") FROM climmob2020.storageerrors S where submission_type = 'ASS';