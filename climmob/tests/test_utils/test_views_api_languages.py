import json
import unittest
from unittest.mock import patch, MagicMock

from climmob.views.Api.languages import (
    readListOfLanguages_view,
    addLanguageForUse_view,
    deleteLanguage_view,
    readListOfUnusedLanguages_view,
    readAllGeneralPhrases_view,
    changeGeneralPhrases_view,
)


class TestReadListOfLanguagesView(unittest.TestCase):
    def setUp(self):
        self.view = readListOfLanguages_view(MagicMock())
        self.view.request.method = "GET"
        self.view.user = MagicMock(login="test_user")

    def mock_translation(self, message):
        return message

    @patch(
        "climmob.views.Api.languages.getListOfLanguagesByUser",
        return_value=[{"lang_code": "en", "lang_name": "English"}],
    )
    def test_process_view_success(self, mock_getListOfLanguagesByUser):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertEqual(response_data, [{"lang_code": "en", "lang_name": "English"}])

    def test_process_view_post_method(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.method = "POST"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())


class TestAddLanguageForUseView(unittest.TestCase):
    def setUp(self):
        self.view = addLanguageForUse_view(MagicMock())
        self.view.request.method = "POST"
        self.view.request.body = json.dumps({"lang_code": "es"})
        self.view.user = MagicMock(login="test_user")
        self.view.body = self.view.request.body  # Ensure self.body is set

    def mock_translation(self, message):
        return message

    @patch("climmob.views.Api.languages.languageExistInI18nUser", return_value=False)
    @patch("climmob.views.Api.languages.languageExistInI18n", return_value=True)
    @patch("climmob.views.Api.languages.addI18nUser", return_value=(True, None))
    def test_process_view_success(
        self, mock_addI18nUser, mock_languageExistInI18n, mock_languageExistInI18nUser
    ):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Language added successfully.", response.body.decode())

    @patch("climmob.views.Api.languages.languageExistInI18nUser", return_value=True)
    def test_process_view_language_already_added(self, mock_languageExistInI18nUser):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("This language has already been added.", response.body.decode())

    @patch("climmob.views.Api.languages.languageExistInI18nUser", return_value=False)
    @patch("climmob.views.Api.languages.languageExistInI18n", return_value=False)
    def test_process_view_language_not_exist(
        self, mock_languageExistInI18n, mock_languageExistInI18nUser
    ):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The language does not exist in the list of languages available for use in ClimMob.",
            response.body.decode(),
        )

    @patch("climmob.views.Api.languages.languageExistInI18nUser", return_value=False)
    @patch("climmob.views.Api.languages.languageExistInI18n", return_value=True)
    @patch(
        "climmob.views.Api.languages.addI18nUser",
        return_value=(False, "Error adding language"),
    )
    def test_process_view_add_language_failed(
        self, mock_addI18nUser, mock_languageExistInI18n, mock_languageExistInI18nUser
    ):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("The language could not be added.", response.body.decode())

    def test_process_view_invalid_json(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.body = '{"wrong_key": "value"}'
        self.view.body = self.view.request.body  # Ensure self.body is set

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "It is not complying with the obligatory keys.", response.body.decode()
        )

    def test_process_view_missing_data(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.body = '{"lang_code": ""}'
        self.view.body = self.view.request.body  # Ensure self.body is set

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    def test_process_view_invalid_keys(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.body = '{"invalid_key": "value"}'
        self.view.body = self.view.request.body  # Ensure self.body is set

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "It is not complying with the obligatory keys.", response.body.decode()
        )

    def test_process_view_post_method(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())


class TestDeleteLanguageView(unittest.TestCase):
    def setUp(self):
        self.view = deleteLanguage_view(MagicMock())
        self.view.request.method = "POST"
        self.view.request.body = json.dumps({"lang_code": "es"})
        self.view.user = MagicMock(login="test_user")
        self.view.body = self.view.request.body  # Ensure self.body is set

    def mock_translation(self, message):
        return message

    @patch("climmob.views.Api.languages.languageExistInI18nUser", return_value=True)
    @patch("climmob.views.Api.languages.deleteI18nUser", return_value=(True, None))
    def test_process_view_success(
        self, mock_deleteI18nUser, mock_languageExistInI18nUser
    ):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Language successfully deleted.", response.body.decode())

    @patch("climmob.views.Api.languages.languageExistInI18nUser", return_value=False)
    def test_process_view_language_not_included(self, mock_languageExistInI18nUser):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The language could not be removed because it is not included in their languages of use.",
            response.body.decode(),
        )

    @patch("climmob.views.Api.languages.languageExistInI18nUser", return_value=True)
    @patch(
        "climmob.views.Api.languages.deleteI18nUser",
        return_value=(False, "Error deleting language"),
    )
    def test_process_view_delete_language_failed(
        self, mock_deleteI18nUser, mock_languageExistInI18nUser
    ):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("The language could not be removed.", response.body.decode())

    def test_process_view_invalid_json(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.body = '{"wrong_key": "value"}'
        self.view.body = self.view.request.body  # Ensure self.body is set

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "It is not complying with the obligatory keys.", response.body.decode()
        )

    def test_process_view_missing_data(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.body = '{"lang_code": ""}'
        self.view.body = self.view.request.body  # Ensure self.body is set

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    def test_process_view_invalid_keys(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.body = '{"invalid_key": "value"}'
        self.view.body = self.view.request.body  # Ensure self.body is set

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "It is not complying with the obligatory keys.", response.body.decode()
        )

    def test_process_view_post_method(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())


class TestReadListOfUnusedLanguagesView(unittest.TestCase):
    def setUp(self):
        self.view = readListOfUnusedLanguages_view(MagicMock())
        self.view.request.method = "GET"
        self.view.user = MagicMock(login="test_user")

    def mock_translation(self, message):
        return message

    @patch(
        "climmob.views.Api.languages.getListOfUnusedLanguagesByUser",
        return_value=["en", "fr", "de"],
    )
    def test_process_view_success(self, mock_getListOfUnusedLanguagesByUser):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertEqual(response_data, ["en", "fr", "de"])

    def test_process_view_post_method(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.method = "POST"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())


class TestReadAllGeneralPhrasesView(unittest.TestCase):
    def setUp(self):
        self.view = readAllGeneralPhrases_view(MagicMock())
        self.view.request.method = "GET"
        self.view.user = MagicMock(login="test_user")
        self.view.body = json.dumps({"lang_code": "en"})

    def mock_translation(self, message):
        return message

    @patch(
        "climmob.views.Api.languages.getAllTranslationsOfPhrasesByLanguage",
        return_value=[{"phrase": "hello", "translation": "hola"}],
    )
    @patch("climmob.views.Api.languages.languageExistInI18nUser", return_value=True)
    def test_process_view_success(
        self, mock_languageExistInI18nUser, mock_getAllTranslationsOfPhrasesByLanguage
    ):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertEqual(response_data[0]["phrase"], "hello")
        self.assertEqual(response_data[0]["translation"], "hola")

    @patch("climmob.views.Api.languages.languageExistInI18nUser", return_value=False)
    def test_process_view_language_not_in_list(self, mock_languageExistInI18nUser):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The language does not belong to your list of languages to be used.",
            response.body.decode(),
        )

    def test_process_view_invalid_json(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON", response.body.decode())

    def test_process_view_invalid_body(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = None

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )

    def test_process_view_missing_data(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = json.dumps({"lang_code": ""})

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    def test_process_view_post_method(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.method = "POST"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())


class TestChangeGeneralPhrasesView(unittest.TestCase):
    def setUp(self):
        self.view = changeGeneralPhrases_view(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view.body = json.dumps(
            {"lang_code": "en", "phrase_id": 1, "phrase_desc": "Hello"}
        )

    def mock_translation(self, message):
        return message

    @patch("climmob.views.Api.languages.savePhraseTranslation", return_value=(True, ""))
    @patch("climmob.views.Api.languages.generalPhraseExistsWithID", return_value=True)
    @patch("climmob.views.Api.languages.languageExistInI18nUser", return_value=True)
    def test_process_view_success(
        self,
        mock_languageExistInI18nUser,
        mock_generalPhraseExistsWithID,
        mock_savePhraseTranslation,
    ):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Phrase successfully saved.", response.body.decode())

    @patch("climmob.views.Api.languages.languageExistInI18nUser", return_value=False)
    def test_process_view_language_not_in_list(self, mock_languageExistInI18nUser):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The language could not be used because it is not included in their languages of use.",
            response.body.decode(),
        )

    @patch("climmob.views.Api.languages.generalPhraseExistsWithID", return_value=False)
    @patch("climmob.views.Api.languages.languageExistInI18nUser", return_value=True)
    def test_process_view_phrase_not_exist(
        self, mock_languageExistInI18nUser, mock_generalPhraseExistsWithID
    ):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no phrase with this ID.", response.body.decode())

    @patch("climmob.views.Api.languages.languageExistInI18nUser", return_value=True)
    @patch("climmob.views.Api.languages.generalPhraseExistsWithID", return_value=True)
    @patch(
        "climmob.views.Api.languages.savePhraseTranslation",
        return_value=(False, "Error when modifying the phrase."),
    )
    def test_process_view_save_phrase_failed(
        self,
        mock_languageExistInI18nUser,
        mock_generalPhraseExistsWithID,
        mock_savePhraseTranslation,
    ):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error when modifying the phrase.", response.body.decode())

    def test_process_view_invalid_json(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "It is not complying with the obligatory keys.", response.body.decode()
        )

    def test_process_view_missing_data(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = json.dumps(
            {"lang_code": "en", "phrase_id": "", "phrase_desc": "Hello"}
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    def test_process_view_post_method(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())


if __name__ == "__main__":
    unittest.main()
