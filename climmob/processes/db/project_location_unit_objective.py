from climmob.models import (
    ProjectLocaUnitObjective,
    LocationUnitOfAnalysisObjectives,
    ProjectObjectives,
    I18nProjectObjectives,
    mapToSchema,
    mapFromSchema,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_

__all__ = [
    "add_project_location_unit_objective",
    "delete_all_project_location_unit_objective",
    "get_project_objectives_by_project_id",
]


def add_project_location_unit_objective(data, request):
    mappedData = mapToSchema(ProjectLocaUnitObjective, data)
    newPrjLang = ProjectLocaUnitObjective(**mappedData)
    try:
        request.dbsession.add(newPrjLang)
        return True, ""
    except Exception as e:
        return False, str(e)


def delete_all_project_location_unit_objective(projectId, request):
    try:
        request.dbsession.query(ProjectLocaUnitObjective).filter(
            ProjectLocaUnitObjective.project_id == projectId
        ).delete()
        request.dbsession.flush()
        return True, ""
    except IntegrityError as e:
        return False, e
    except Exception as e:
        # print(str(e))
        return False, e


def get_project_objectives_by_project_id(request, project_id):

    result = mapFromSchema(
        request.dbsession.query(
            ProjectLocaUnitObjective,
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
        .filter(ProjectLocaUnitObjective.project_id == project_id)
        .filter(
            ProjectLocaUnitObjective.pluoaobj_id
            == LocationUnitOfAnalysisObjectives.pluoaobj_id
        )
        .filter(
            LocationUnitOfAnalysisObjectives.pobjective_id
            == ProjectObjectives.pobjective_id
        )
        .all()
    )

    return result
