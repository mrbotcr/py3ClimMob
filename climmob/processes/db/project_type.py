from sqlalchemy import func, and_
from climmob.models import ProjectType, I18nProjectType, mapFromSchema

__all__ = ["getListOfProjectTypes"]


def getListOfProjectTypes(request):

    res = mapFromSchema(
        request.dbsession.query(
            ProjectType,
            func.coalesce(I18nProjectType.prjtype_name, ProjectType.prjtype_name).label(
                "prjtype_name"
            ),
            func.coalesce(
                I18nProjectType.prjtype_description, ProjectType.prjtype_description
            ).label("prjtype_description"),
        )
        .join(
            I18nProjectType,
            and_(
                ProjectType.prjtype_id == I18nProjectType.prjtype_id,
                I18nProjectType.lang_code == request.locale_name,
            ),
            isouter=True,
        )
        .all()
    )

    return res
