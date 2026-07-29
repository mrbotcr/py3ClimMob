import datetime

__all__ = [
    "save_project_publication_status",
    "get_global_project_publication_status_id",
    "get_global_project_publication_status_name",
    "get_all_project_publication_statuses",
    "get_project_publication_approval_status_id",
    "get_project_publication_status_by_destination_name",
    "get_project_publication_status_by_status_id",
    "get_project_publication_approved",
    "save_project_publication_approved",
]

import logging

from sqlalchemy.exc import NoResultFound

from climmob.models import mapFromSchema
from climmob.models.climmobv4 import (
    ProjectPublicationStatus,
    PublicationStatus,
    Project,
)
from climmob.models.repository import sql_fetch_one, sql_execute
from climmob.utility import (
    PublicationStatus as PublicationStatusEnum,
    PublicationStatusLabel,
    PublicationApproved,
)

import climmob.plugins as p

log = logging.getLogger("climmob")


def save_project_publication_status(
    project_id: str, status: int, user_name: str, destination: str
):
    try:
        sql = f"""
            SELECT * FROM project_publication_status
            WHERE project_id = "{project_id}" AND destination = "{destination}"
        """

        result = sql_fetch_one(sql)

        if result is None:
            sql = f"""
                    INSERT INTO project_publication_status VALUES
                    ({status},
                    "{project_id}",
                    "{destination}",
                    "{user_name}",
                    "{datetime.datetime.now()}");
    
                """
        else:
            sql = f"""
                    UPDATE project_publication_status
                    SET
                        publication_status_id = {status}
                    WHERE project_id = "{project_id}" AND destination = "{destination}";
                """

        sql_execute(sql)

        return True, ""
    except Exception as e:
        log.error(f"Error in save_project_publication_status: {e}")
        return False, str(e)


def get_global_project_publication_status_name(request, project_id: str) -> str:
    status_id = get_global_project_publication_status_id(request, project_id)
    return PublicationStatusLabel[PublicationStatusEnum(status_id).name].value


def get_project_publication_approval_status_id(request, project_id: str) -> int:
    status_id = get_global_project_publication_status_id(request, project_id)
    status_map = {
        PublicationStatusEnum.NOT_REQUESTED: -1,
        PublicationStatusEnum.REQUESTED: 0,
        PublicationStatusEnum.APPROVED: PublicationStatusEnum.APPROVED.value,
        PublicationStatusEnum.REJECTED: PublicationStatusEnum.REJECTED.value,
        PublicationStatusEnum.PUBLISHED: PublicationStatusEnum.APPROVED.value,
        PublicationStatusEnum.FAILED: PublicationStatusEnum.APPROVED.value,
    }
    return status_map[PublicationStatusEnum(status_id)]


def get_project_publication_approved(request, project_id: str) -> int | None:
    try:
        res = (
            request.dbsession.query(Project.project_publication_approved)
            .filter(Project.project_id == project_id)
            .one()
        )
        return res[0]
    except NoResultFound:
        return None


def save_project_publication_approved(request, project_id: str, status: int):
    try:
        request.dbsession.query(Project).filter(
            Project.project_id == project_id
        ).update({"project_publication_approved": status})
        return True, ""
    except Exception as e:
        log.error(e)
        return False, ""


# TODO: how to detect approval if only climmob is selected?
#  should we make it obligatory to select more repos?
#  use Project.project_publication_approved
def get_global_project_publication_status_id(request, project_id: str) -> int:
    res = (
        request.dbsession.query(ProjectPublicationStatus)
        .filter(ProjectPublicationStatus.project_id == project_id)
        .all()
    )
    publication_approved = get_project_publication_approved(request, project_id)

    if not res:
        global_status = PublicationStatusEnum.NOT_REQUESTED

    elif publication_approved == PublicationApproved.REJECTED.value:
        global_status = PublicationStatusEnum.REJECTED

    elif publication_approved == PublicationApproved.APPROVED.value:
        global_status = PublicationStatusEnum.APPROVED
        for status in res:
            if status.publication_status_id == PublicationStatusEnum.FAILED:
                if any(
                    s.publication_status_id == PublicationStatusEnum.PUBLISHED
                    and s.destination != "climmob"
                    for s in res
                ):
                    global_status = PublicationStatusEnum.PARTIAL
                else:
                    global_status = PublicationStatusEnum.FAILED
                break
            if status.publication_status_id == PublicationStatusEnum.PUBLISHED:
                if status.destination != "climmob":
                    global_status = PublicationStatusEnum.PUBLISHED
    else:
        global_status = PublicationStatusEnum.REQUESTED

    return global_status.value


def get_all_project_publication_statuses(
    request, project_id: str
) -> list[ProjectPublicationStatus]:
    query = (
        request.dbsession.query(
            ProjectPublicationStatus, PublicationStatus.publication_status_name
        )
        .join(
            PublicationStatus,
            PublicationStatus.publication_status_id
            == ProjectPublicationStatus.publication_status_id,
        )
        .filter(ProjectPublicationStatus.project_id == project_id)
    )
    result = mapFromSchema(query.all())
    publishers = p.PluginImplementations(p.IPublisher)
    for repo in result:
        for plugin in publishers:
            if repo["destination"] == plugin.get_destination_name():
                repo["destination_label"] = plugin.get_label()

    return result


def get_project_publication_status_by_destination_name(
    request, project_id: str, destination_name: str
) -> ProjectPublicationStatus | None:
    try:
        query = (
            request.dbsession.query(ProjectPublicationStatus)
            .filter(ProjectPublicationStatus.project_id == project_id)
            .filter(ProjectPublicationStatus.destination == destination_name)
        )
        result = mapFromSchema(query.one())
        return result
    except NoResultFound:
        return None


def get_project_publication_status_by_status_id(
    request, project_id: str, status_id: int
) -> list[ProjectPublicationStatus]:
    query = (
        request.dbsession.query(ProjectPublicationStatus)
        .filter(ProjectPublicationStatus.project_id == project_id)
        .filter(ProjectPublicationStatus.publication_status_id == status_id)
    )
    result = mapFromSchema(query.all())
    return result
