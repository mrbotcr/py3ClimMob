from climmob.models import (
    LocationUnitOfAnalysisObjectives,
    mapFromSchema,
)

__all__ = [
    "get_location_unit_of_analysis_objectives_by_combination",
    "get_location_unit_of_analysis_objectives_by_proj_objective_id",
    "add_location_unit_of_analysis_objective",
    "delete_location_unit_of_analysis_objective",
]


def get_location_unit_of_analysis_objectives_by_combination(
    request, pluoa_id, pobjective_id
):
    result = mapFromSchema(
        request.dbsession.query(LocationUnitOfAnalysisObjectives)
        .filter(LocationUnitOfAnalysisObjectives.pluoa_id == pluoa_id)
        .filter(LocationUnitOfAnalysisObjectives.pobjective_id == pobjective_id)
        .first()
    )

    return result


def get_location_unit_of_analysis_objectives_by_proj_objective_id(
    request, pobjective_id
):
    result = mapFromSchema(
        request.dbsession.query(LocationUnitOfAnalysisObjectives)
        .filter(LocationUnitOfAnalysisObjectives.pobjective_id == pobjective_id)
        .all()
    )
    return result


def add_location_unit_of_analysis_objective(request, pobjective_id, pluoa_id):
    new_pluoaobj = LocationUnitOfAnalysisObjectives(
        pobjective_id=pobjective_id, pluoa_id=pluoa_id
    )
    try:
        request.dbsession.add(new_pluoaobj)
        return True, None
    except Exception as e:
        return False, "Could not add new objective"


def delete_location_unit_of_analysis_objective(request, pluoaobj_id):
    try:
        (
            request.dbsession.query(LocationUnitOfAnalysisObjectives)
            .filter(LocationUnitOfAnalysisObjectives.pluoaobj_id == pluoaobj_id)
            .delete()
        )
    except Exception as e:
        return False, "Could not delete location_unit_of_analysis_objective"
