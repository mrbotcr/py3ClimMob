from climmob.models import mapFromSchema, I18nGeneralPhrases, mapToSchema
from climmob.processes.db.i18n_user import getListOfLanguagesByUser
from climmob.processes.db.general_phrases import (
    getListOfGeneralPhrases,
    generalPhraseByID,
)

__all__ = [
    "getAllTranslationsOfPhrases",
    "getPhraseTranslationInLanguage",
    "getAllTranslationsOfPhrasesByLanguage",
    "savePhraseTranslation",
    "addI18nGeneralPhrases",
    "modifyI18nGeneralPhrases",
]


def getAllTranslationsOfPhrases(request, userName):

    languages = getListOfLanguagesByUser(request, userName)

    for lang in languages:
        phrases = getListOfGeneralPhrases(request)
        lang["translations"] = []
        for phrase in phrases:
            dictPhrase = {}
            dictPhrase["id"] = phrase["phrase_id"]
            dictPhrase["desc"] = phrase["phrase_desc"]

            dictPhrase["translations"] = {}

            dictPhrase["translations"]["climmob"] = getPhraseTranslationInLanguage(
                request, phrase["phrase_id"], "bioversity", lang["lang_code"]
            )

            if lang["lang_code"] == "en" and not dictPhrase["translations"]["climmob"]:

                dictPhrase["translations"]["climmob"] = {
                    "phrase_desc": phrase["phrase_desc"]
                }

            dictPhrase["translations"]["user"] = getPhraseTranslationInLanguage(
                request, phrase["phrase_id"], userName, lang["lang_code"]
            )
            lang["translations"].append(dictPhrase)

    return languages


def getAllTranslationsOfPhrasesByLanguage(request, userName, language):

    phrases = getListOfGeneralPhrases(request)

    for phrase in phrases:

        phrase["language"] = language

        phrase["translations"] = {}

        phrase["translations"]["climmob"] = getPhraseTranslationInLanguage(
            request, phrase["phrase_id"], "bioversity", language
        )

        if language == "en" and not phrase["translations"]["climmob"]:

            phrase["translations"]["climmob"] = {"phrase_desc": phrase["phrase_desc"]}

        phrase["translations"]["user"] = getPhraseTranslationInLanguage(
            request, phrase["phrase_id"], userName, language
        )

    return phrases


def getPhraseTranslationInLanguage(
    request,
    textId,
    userName,
    language,
    returnSuggestion=None,
    returnOriginal=None,
    dbsession=None,
):
    _DBsession_ = None

    if request and not dbsession:
        _DBsession_ = request.dbsession
    if dbsession and not request:
        _DBsession_ = dbsession

    translation = mapFromSchema(
        _DBsession_.query(
            I18nGeneralPhrases,
        )
        .filter(I18nGeneralPhrases.phrase_id == textId)
        .filter(I18nGeneralPhrases.user_name == userName)
        .filter(I18nGeneralPhrases.lang_code == language)
        .first()
    )

    if not translation and returnSuggestion:
        return getPhraseTranslationInLanguage(
            request,
            textId,
            "bioversity",
            language,
            returnOriginal=True,
            dbsession=dbsession,
        )

    if not translation and returnOriginal:
        return generalPhraseByID(request, textId, dbsession=dbsession)

    return translation


def savePhraseTranslation(request, textId, textValue, userName, language):

    phrase = getPhraseTranslationInLanguage(request, textId, userName, language)

    if phrase:
        if textValue != "":
            return modifyI18nGeneralPhrases(
                request, textId, textValue, userName, language
            )
        else:
            return deleteI18nGeneralPhrases(request, textId, userName, language)
    else:
        phrase = getPhraseTranslationInLanguage(request, textId, "bioversity", language)

        if not phrase or phrase["phrase_desc"] != textValue:
            info = {
                "phrase_id": textId,
                "user_name": userName,
                "lang_code": language,
                "phrase_desc": textValue,
            }

            return addI18nGeneralPhrases(info, request)
        else:

            return True, ""


def addI18nGeneralPhrases(data, request):
    mappedData = mapToSchema(I18nGeneralPhrases, data)
    newI18nGeneralPhrases = I18nGeneralPhrases(**mappedData)
    try:
        request.dbsession.add(newI18nGeneralPhrases)
        return True, ""
    except Exception as e:
        return False, str(e)


def modifyI18nGeneralPhrases(request, textId, textValue, userName, language):
    try:

        request.dbsession.query(I18nGeneralPhrases).filter(
            I18nGeneralPhrases.phrase_id == textId
        ).filter(I18nGeneralPhrases.user_name == userName).filter(
            I18nGeneralPhrases.lang_code == language
        ).update(
            {"phrase_desc": textValue}
        )
        return True, ""
    except Exception as e:
        return False, e


def deleteI18nGeneralPhrases(request, textId, userName, language):
    try:
        request.dbsession.query(I18nGeneralPhrases).filter(
            I18nGeneralPhrases.phrase_id == textId
        ).filter(I18nGeneralPhrases.user_name == userName).filter(
            I18nGeneralPhrases.lang_code == language
        ).delete()
        return True, ""
    except Exception as e:
        # print(str(e))
        return False, str(e)
