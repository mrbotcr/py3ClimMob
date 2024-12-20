from climmob.models import (
    ProjectLocation,
    I18nProjectLocation,
    mapToSchema,
    mapFromSchemaWithRelationships,
    mapFromSchema,
)
from sqlalchemy import func, and_

__all__ = ["get_all_project_location", "get_location_by_id"]


def get_all_project_location(request, method_from_schema=None):
    if not method_from_schema:
        method_from_schema = mapFromSchemaWithRelationships
    else:
        method_from_schema = mapFromSchema

    result = method_from_schema(
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

    res = mapFromSchemaWithRelationships(
        request.dbsession.query(ProjectLocation)
        .filter(ProjectLocation.plocation_id == location_id)
        .first()
    )

    return res
