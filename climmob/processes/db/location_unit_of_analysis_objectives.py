from climmob.models import (
    LocationUnitOfAnalysisObjectives,
    mapFromSchemaWithRelationships,
)

__all__ = ["get_location_unit_of_analysis_objectives_by_combination"]


def get_location_unit_of_analysis_objectives_by_combination(
    request, pluoa_id, pobjective_id
):

    result = mapFromSchemaWithRelationships(
        request.dbsession.query(LocationUnitOfAnalysisObjectives)
        .filter(LocationUnitOfAnalysisObjectives.pluoa_id == pluoa_id)
        .filter(LocationUnitOfAnalysisObjectives.pobjective_id == pobjective_id)
        .first()
    )

    return result
