from sqlalchemy.exc import IntegrityError

from climmob.models import (
    ProjectLocation,
    I18nProjectLocation,
    mapFromSchema, mapToSchema,
)
from sqlalchemy import func, and_

__all__ = [
    "get_all_project_location",
    "get_location_by_id",
    "get_location_by_id_with_details",
    "getAllLocation"
]


def getAllLocation(request):
    result = (
        mapFromSchema(request.dbsession.query(ProjectLocation).orderBy(ProjectLocation.plocation_id)
    ))
    return result



def get_all_project_location(request):

    result = mapFromSchema(
        request.dbsession.query(
            ProjectLocation,
            func.coalesce(
                I18nProjectLocation.plocation_name, ProjectLocation.plocation_name
            ).label("plocation_name"),
        )
        .join(
            I18nProjectLocation,
            and_(
                ProjectLocation.plocation_id == I18nProjectLocation.plocation_id,
                I18nProjectLocation.lang_code == request.locale_name,
            ),
            isouter=True,
        )
        .order_by(
            func.coalesce(
                I18nProjectLocation.plocation_name, ProjectLocation.plocation_name
            )
        )
        .all()
    )

    return result


def get_location_by_id(request, location_id):

    res = mapFromSchema(
        request.dbsession.query(ProjectLocation)
        .filter(ProjectLocation.plocation_id == location_id)
        .first()
    )

    return res


def get_location_by_id_with_details(request, location_id):

    result = mapFromSchema(
        request.dbsession.query(
            ProjectLocation,
            func.coalesce(
                I18nProjectLocation.plocation_name, ProjectLocation.plocation_name
            ).label("plocation_name"),
        )
        .join(
            I18nProjectLocation,
            and_(
                ProjectLocation.plocation_id == I18nProjectLocation.plocation_id,
                I18nProjectLocation.lang_code == request.locale_name,
            ),
            isouter=True,
        )
        .filter(ProjectLocation.plocation_id == location_id)
        .first()
    )
    return result

def add_Location_DB(data, request):
    mappedData = mapToSchema(
        ProjectLocation, data)
    print("Mapped Data:", mappedData)
    newProjectLocation = ProjectLocation(**mappedData)
    try:
        request.dbsession.add(newProjectLocation)
        request.dbsession.commit()
        return True, ""
    except Exception as e:
        return False, str(e)

def editLocation(data, locationid, error_summary, request ):
    data["plocation_id"] = locationid
    data["plocation_name"] = data["edit_plocation_name"]
    data["plocation_lang"] = data["plocation_lang"]
    mappedData = mapToSchema(ProjectLocation, data)
    print("Mapped Data:", mappedData)
    try:
        request.dbsession.query(ProjectLocation).filter(ProjectLocation.plocation_id ==
                                                        locationid).update(mappedData)
        return True, ""
    except Exception as e:
        return False, e


def deleteLocationdb(location,request):
    try:
        request.dbsession.query(ProjectLocation).filter(
            ProjectLocation.plocation_id == location
        ).delete()
        return True, ""
    except IntegrityError as e:
        print("capturado")
        return False, e
    except Exception as e:
        # print(str(e))
        return False, e