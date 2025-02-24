from climmob.models import (
    ProjectUnitOfAnalysis,
    I18nProjectUnitOfAnalysis,
    LocationUnitOfAnalysis,
    mapFromSchema,
)
from sqlalchemy import func, and_

__all__ = [
    "get_all_unit_of_analysis_by_location",
    "get_unit_of_analysis_by_id",
    "get_unit_of_analysis_by_unit_of_analysis_id_details",
]


def get_all_unit_of_analysis_by_location(request, location_id):

    sub_query = request.dbsession.query(LocationUnitOfAnalysis.puoa_id).filter(
        LocationUnitOfAnalysis.plocation_id == location_id
    )

    result = mapFromSchema(
        request.dbsession.query(
            ProjectUnitOfAnalysis,
            func.coalesce(
                I18nProjectUnitOfAnalysis.puoa_name, ProjectUnitOfAnalysis.puoa_name
            ).label("puoa_name"),
        )
        .join(
            I18nProjectUnitOfAnalysis,
            and_(
                ProjectUnitOfAnalysis.puoa_id == I18nProjectUnitOfAnalysis.puoa_id,
                I18nProjectUnitOfAnalysis.lang_code == request.locale_name,
            ),
            isouter=True,
        )
        .filter(ProjectUnitOfAnalysis.puoa_id.in_(sub_query))
        .order_by(
            func.coalesce(
                I18nProjectUnitOfAnalysis.puoa_name, ProjectUnitOfAnalysis.puoa_name
            )
        )
        .all()
    )

    return result


def get_unit_of_analysis_by_id(request, unit_of_analysis_id):

    res = mapFromSchema(
        request.dbsession.query(ProjectUnitOfAnalysis)
        .filter(ProjectUnitOfAnalysis.puoa_id == unit_of_analysis_id)
        .first()
    )

    return res


def get_unit_of_analysis_by_unit_of_analysis_id_details(request, unit_of_analysis_id):

    result = mapFromSchema(
        request.dbsession.query(
            ProjectUnitOfAnalysis,
            func.coalesce(
                I18nProjectUnitOfAnalysis.puoa_name, ProjectUnitOfAnalysis.puoa_name
            ).label("puoa_name"),
        )
        .join(
            I18nProjectUnitOfAnalysis,
            and_(
                ProjectUnitOfAnalysis.puoa_id == I18nProjectUnitOfAnalysis.puoa_id,
                I18nProjectUnitOfAnalysis.lang_code == request.locale_name,
            ),
            isouter=True,
        )
        .filter(ProjectUnitOfAnalysis.puoa_id == unit_of_analysis_id)
        .order_by(
            func.coalesce(
                I18nProjectUnitOfAnalysis.puoa_name, ProjectUnitOfAnalysis.puoa_name
            )
        )
        .first()
    )

    return result
