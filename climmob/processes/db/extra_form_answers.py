from climmob.models import (
    ExtraFormAnswer,
    mapToSchema,
)

__all__ = ["addExtraFormAnswers"]


def addExtraFormAnswers(data, request):
    mappedData = mapToSchema(ExtraFormAnswer, data)
    newExtraFormAnswer = ExtraFormAnswer(**mappedData)
    try:
        request.dbsession.add(newExtraFormAnswer)
        return True, ""
    except Exception as e:
        return False, str(e)
