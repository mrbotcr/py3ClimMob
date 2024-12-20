from climmob.models import (
    ProjectObjectives,
    I18nProjectObjectives,
    LocationUnitOfAnalysis,
    LocationUnitOfAnalysisObjectives,
    mapFromSchema,
    mapFromSchemaWithRelationships,
)
from sqlalchemy import func, and_

__all__ = [
    "get_all_objectives_by_location_and_unit_of_analysis",
]


def get_all_objectives_by_location_and_unit_of_analysis(
    request, location_id, unit_of_analysis_id, method_from_schema=None
):
    if not method_from_schema:
        method_from_schema = mapFromSchemaWithRelationships
    else:
        method_from_schema = mapFromSchema

    sub_query_LocationUnitOfAnalysis = (
        request.dbsession.query(LocationUnitOfAnalysis.pluoa_id)
        .filter(LocationUnitOfAnalysis.plocation_id == location_id)
        .filter(LocationUnitOfAnalysis.puoa_id == unit_of_analysis_id)
    )

    sub_query_LocationUnitOfAnalysisObjectives = request.dbsession.query(
        LocationUnitOfAnalysisObjectives.pobjective_id
    ).filter(
        LocationUnitOfAnalysisObjectives.pluoa_id.in_(sub_query_LocationUnitOfAnalysis)
    )

    result = method_from_schema(
        request.dbsession.query(
            ProjectObjectives,
            func.coalesce(
                I18nProjectObjectives.pobjective_name, ProjectObjectives.pobjective_name
            ).label("pobjective_name"),
        )
        .join(
            I18nProjectObjectives,
            and_(
                ProjectObjectives.pobjective_id == I18nProjectObjectives.pobjective_id,
                I18nProjectObjectives.lang_code == request.locale_name,
            ),
            isouter=True,
        )
        .filter(
            ProjectObjectives.pobjective_id.in_(
                sub_query_LocationUnitOfAnalysisObjectives
            )
        )
        .order_by(
            func.coalesce(
                I18nProjectObjectives.pobjective_name, ProjectObjectives.pobjective_name
            )
        )
        .all()
    )

    return result
