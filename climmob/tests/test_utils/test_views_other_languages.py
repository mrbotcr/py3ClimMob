import unittest
from unittest.mock import MagicMock, patch

from jinja2 import Environment

from climmob.views.otherLanguages import (
    OtherLanguagesView,
    SaveOtherLanguagesView,
    GetOtherLanguagesView,
)


class TestOtherLanguagesView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.params = {}
        self.mock_user = MagicMock()
        self.mock_user.login = "test_user"

        self.view = OtherLanguagesView(self.mock_request)
        self.view.user = self.mock_user

    @patch(
        "climmob.views.otherLanguages.getListOfLanguagesInClimMob",
        return_value=["en", "es", "fr"],
    )
    @patch(
        "climmob.views.otherLanguages.getListOfLanguagesByUser",
        return_value=["en", "es"],
    )
    def test_process_view(
        self, mock_getListOfLanguagesByUser, mock_getListOfLanguagesInClimMob
    ):
        result = self.view.processView()

        mock_getListOfLanguagesByUser.assert_called_once_with(
            self.mock_request, "test_user"
        )
        mock_getListOfLanguagesInClimMob.assert_called_once_with(self.mock_request)
        self.assertEqual(
            result,
            {
                "listOflanguages": ["en", "es"],
                "listOfLanguagesInClimMob": ["en", "es", "fr"],
                "sectionActive": "otherLanguages",
                "help": None,
            },
        )


class TestSaveOtherLanguagesView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_user = MagicMock()
        self.mock_user.login = "test_user"

        self.view = SaveOtherLanguagesView(self.mock_request)
        self.view.user = self.mock_user

    @patch(
        "climmob.views.otherLanguages.savePhraseTranslation",
        return_value=(True, "Success"),
    )
    def test_process_view_post(self, mock_savePhraseTranslation):
        self.mock_request.method = "POST"
        self.view.getPostDict = MagicMock(
            return_value={
                "phrase_en_1": "Hello",
                "phrase_es_1": "Hola",
                "other_key": "OtherValue",
            }
        )

        result = self.view.processView()

        self.assertTrue(self.view.returnRawViewResult)
        mock_savePhraseTranslation.assert_any_call(
            self.mock_request, "1", "Hello", "test_user", "en"
        )
        mock_savePhraseTranslation.assert_any_call(
            self.mock_request, "1", "Hola", "test_user", "es"
        )
        self.assertEqual(result, {"status": 200})

    def test_process_view_not_post(self):
        self.mock_request.method = "GET"
        self.view.returnRawViewResult = True

        result = self.view.processView()

        self.assertTrue(self.view.returnRawViewResult)
        self.assertEqual(
            result, {"status": 400, "error": "Only POST methods are accepted"}
        )


class TestGetOtherLanguagesView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.method = "GET"
        self.mock_request.matchdict = {"language": "en"}
        self.mock_user = MagicMock()
        self.mock_user.login = "test_user"

        self.view = GetOtherLanguagesView(self.mock_request)
        self.view.user = self.mock_user

    @patch(
        "climmob.views.otherLanguages.getAllTranslationsOfPhrasesByLanguage",
        return_value=[{"phrase": "Hello", "translation": "Hola"}],
    )
    @patch.object(Environment, "get_template")
    def test_process_view_get(self, mock_get_template, mock_getAllTranslations):
        mock_template = MagicMock()
        mock_template.render.return_value = "Rendered Template"
        mock_get_template.return_value = mock_template

        result = self.view.processView()

        self.assertTrue(self.view.returnRawViewResult)
        mock_getAllTranslations.assert_called_once_with(
            self.mock_request, "test_user", "en"
        )
        mock_get_template.assert_called_once_with("tableOfPhrases.jinja2")
        mock_template.render.assert_called_once_with(
            {
                "translations": [{"phrase": "Hello", "translation": "Hola"}],
                "_": self.view._,
            }
        )
        self.assertEqual(result, "Rendered Template")

    def test_process_view_not_get(self):
        self.mock_request.method = "POST"

        result = self.view.processView()

        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
