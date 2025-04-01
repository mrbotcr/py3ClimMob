from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.exc import NoResultFound

from climmob.models import (
    ProjectObjectives,
    I18nProjectObjectives,
    LocationUnitOfAnalysis,
    LocationUnitOfAnalysisObjectives,
    mapFromSchema,
)
from sqlalchemy import func, and_

__all__ = [
    "get_all_objectives_by_location_and_unit_of_analysis",
    "add_objective",
    "get_objective_by_id",
    "update_objective",
    "delete_objective_by_id",
]

from climmob.processes import getAllLocationUnitOfAnalysis

def get_objective_by_name(request, name):
    try:
        return (
            request.dbsession.query(ProjectObjectives)
            .filter(ProjectObjectives.pobjective_name == name)
            .one()
        )
    except NoResultFound:
        raise HTTPNotFound

def get_objective_by_id(request, obj_id):
    try:
        res = (
            request.dbsession.query(ProjectObjectives)
            .filter(ProjectObjectives.pobjective_id == obj_id)
            .one()
        )
        return mapFromSchema(res)
    except NoResultFound:
        raise HTTPNotFound

def add_objective(request, name):
    try:
        get_objective_by_name(request, name)
        return False, "Objective already exists"
    except HTTPNotFound:
        pass
    new_objective = ProjectObjectives()
    new_objective.pobjective_name = name
    new_objective.pobjective_lang = "en"
    try:
        request.dbsession.add(new_objective)
        new_objective = get_objective_by_name(request, name)

        uoas = getAllLocationUnitOfAnalysis(request)
        for uoa in uoas:

            new_luoa = LocationUnitOfAnalysisObjectives()
            new_luoa.pobjective_id = new_objective.pobjective_id
            new_luoa.pluoa_id = uoa["pluoa_id"]

            request.dbsession.add(new_luoa)
        return True, ""
    except Exception as e:
        return False, str(e)


def delete_objective_by_id(request, obj_id):
    try:
        (
            request.dbsession.query(ProjectObjectives)
            .filter(ProjectObjectives.pobjective_id == obj_id)
            .delete()
        )
        return True, ""
    except Exception as e:
        return False, e

def update_objective(request, objective: ProjectObjectives):
    try:
        get_objective_by_name(request, objective.pobjective_name)
        return False, "Objective name is already in use."
    except HTTPNotFound:
        pass
    try:
        (
            request.dbsession.query(ProjectObjectives)
            .filter(ProjectObjectives.pobjective_id == objective.pobjective_id)
            .update({"pobjective_name": objective.pobjective_name})
        )
        return True, ""
    except Exception as e:
        return False, e

def get_all_objectives_by_location_and_unit_of_analysis(
    request, location_id, unit_of_analysis_id
):
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

    result = mapFromSchema(
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
