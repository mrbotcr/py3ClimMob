from climmob.models import (
    mapToSchema,
    mapFromSchemaWithRelationships,
    LocationUnitOfAnalysis,
    ProjectLocation,
    ProjectUnitOfAnalysis,
    I18nProjectLocation,
    I18nProjectUnitOfAnalysis,
)
from sqlalchemy import and_, func

__all__ = [
    "getAllLocationUnitOfAnalysis",
    "get_location_unit_of_analysis_by_combination",
]


def getAllLocationUnitOfAnalysis(request):

    result = mapFromSchemaWithRelationships(
        request.dbsession.query(
            LocationUnitOfAnalysis,
            func.coalesce(
                I18nProjectLocation.plocation_name, ProjectLocation.plocation_name
            ).label("plocation_name"),
            func.coalesce(
                I18nProjectUnitOfAnalysis.puoa_name, ProjectUnitOfAnalysis.puoa_name
            ).label("puoa_name"),
        )
        .join(
            I18nProjectLocation,
            and_(
                LocationUnitOfAnalysis.plocation_id == I18nProjectLocation.plocation_id,
                I18nProjectLocation.lang_code == request.locale_name,
            ),
            isouter=True,
        )
        .join(
            I18nProjectUnitOfAnalysis,
            and_(
                LocationUnitOfAnalysis.puoa_id == I18nProjectUnitOfAnalysis.puoa_id,
                I18nProjectUnitOfAnalysis.lang_code == request.locale_name,
            ),
            isouter=True,
        )
        .filter(LocationUnitOfAnalysis.plocation_id == ProjectLocation.plocation_id)
        .filter(LocationUnitOfAnalysis.puoa_id == ProjectUnitOfAnalysis.puoa_id)
        .order_by(LocationUnitOfAnalysis.plocation_id, LocationUnitOfAnalysis.puoa_id)
        .all()
    )

    return result


def get_location_unit_of_analysis_by_combination(
    request, location_id, unit_of_analysis_id
):

    result = mapFromSchemaWithRelationships(
        request.dbsession.query(LocationUnitOfAnalysis)
        .filter(LocationUnitOfAnalysis.plocation_id == location_id)
        .filter(LocationUnitOfAnalysis.puoa_id == unit_of_analysis_id)
        .first()
    )

    return result
