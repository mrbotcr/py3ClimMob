from climmob.models import (
    mapFromSchema,
    LocationUnitOfAnalysis,
    ProjectLocation,
    ProjectUnitOfAnalysis,
    I18nProjectLocation,
    I18nProjectUnitOfAnalysis,
)
from climmob.processes.db.project_location import get_location_by_id_with_details
from climmob.processes.db.project_unit_of_analysis import (
    get_unit_of_analysis_by_unit_of_analysis_id_details,
)

from sqlalchemy import and_, func

__all__ = [
    "getAllLocationUnitOfAnalysis",
    "get_location_unit_of_analysis_by_combination",
    "get_location_unit_of_analysis_by_pluoa_id",
]


def getAllLocationUnitOfAnalysis(request):

    result = mapFromSchema(
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

    result = mapFromSchema(
        request.dbsession.query(LocationUnitOfAnalysis)
        .filter(LocationUnitOfAnalysis.plocation_id == location_id)
        .filter(LocationUnitOfAnalysis.puoa_id == unit_of_analysis_id)
        .first()
    )

    return result


def get_location_unit_of_analysis_by_pluoa_id(request, pluoa_id):

    result = mapFromSchema(
        request.dbsession.query(LocationUnitOfAnalysis)
        .filter(LocationUnitOfAnalysis.pluoa_id == pluoa_id)
        .first()
    )

    if result:
        result["project_location"] = get_location_by_id_with_details(
            request, result["plocation_id"]
        )
        result[
            "unit_of_analysis"
        ] = get_unit_of_analysis_by_unit_of_analysis_id_details(
            request, result["puoa_id"]
        )

    return result
