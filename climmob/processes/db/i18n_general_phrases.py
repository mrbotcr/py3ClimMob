from climmob.models import mapFromSchema, I18nGeneralPhrases
from climmob.processes.db.i18n_user import getListOfLanguagesByUser
from climmob.processes.db.general_phrases import getListOfGeneralPhrases

__all__ = ["getAllTranslationsOfPhrases", "getPhraseTranslationInLanguage"]


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


def getPhraseTranslationInLanguage(request, textId, userName, language):

    translation = mapFromSchema(
        request.dbsession.query(
            I18nGeneralPhrases,
        )
        .filter(I18nGeneralPhrases.phrase_id == textId)
        .filter(I18nGeneralPhrases.user_name == userName)
        .filter(I18nGeneralPhrases.lang_code == language)
        .first()
    )

    return translation
