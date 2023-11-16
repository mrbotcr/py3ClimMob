from climmob.models import (
    ExtraForm,
    ExtraFormAnswer,
    Products,
    userProject,
    mapFromSchema,
)

__all__ = ["getActiveForm"]


def getActiveForm(request, userName):

    subqueryProject = (
        request.dbsession.query(userProject.project_id)
        .filter(userProject.user_name == userName)
        .filter(userProject.access_type == 1)
    )

    haveReport = mapFromSchema(
        request.dbsession.query(Products)
        .filter(Products.project_id.in_(subqueryProject))
        .all()
    )

    if haveReport:
        result = mapFromSchema(
            request.dbsession.query(ExtraForm)
            .filter(ExtraForm.form_status == 1)
            .first()
        )

        if result:
            answered = mapFromSchema(
                request.dbsession.query(ExtraFormAnswer)
                .filter(ExtraFormAnswer.form_id == result["form_id"])
                .filter(ExtraFormAnswer.user_name == userName)
                .all()
            )
            if answered:

                return False, None

            return True, result

    return False, None
