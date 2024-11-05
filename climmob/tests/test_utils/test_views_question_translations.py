import unittest
from unittest.mock import MagicMock, patch

from pyramid.httpexceptions import HTTPNotFound

from climmob.views.questionTranslations import (
    QuestionTranslationsView,
    actionInTheTranslationOfQuestion,
    actionInTheTranslationOfQuestionOptions,
    ChangeDefaultQuestionLanguageView,
)


class TestQuestionTranslationsView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {"user": "test_user", "questionid": "123"}
        self.mock_request.params = {"next": "nextPage"}
        self.view = QuestionTranslationsView(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def tearDown(self):
        patch.stopall()

    @patch(
        "climmob.views.questionTranslations.userQuestionDetailsById",
        return_value={"id": "123", "question": "Sample Question"},
    )
    @patch(
        "climmob.views.questionTranslations.getAllTranslationsOfQuestion",
        return_value=[{"lang_code": "en", "translation": "Sample Translation"}],
    )
    @patch(
        "climmob.views.questionTranslations.getListOfLanguagesByUser",
        return_value=[{"lang_code": "en", "default": 0}],
    )
    @patch(
        "climmob.views.questionTranslations.actionInTheTranslationOfQuestion",
        return_value=True,
    )
    @patch(
        "climmob.views.questionTranslations.actionInTheTranslationOfQuestionOptions",
        return_value=True,
    )
    def test_process_view_post(
        self,
        mock_actionInTheTranslationOfQuestionOptions,
        mock_actionInTheTranslationOfQuestion,
        mock_getListOfLanguagesByUser,
        mock_getAllTranslationsOfQuestion,
        mock_userQuestionDetailsById,
    ):
        # Mock request method to POST
        self.mock_request.method = "POST"
        self.mock_request.POST = {"question_text_en": "Sample Question Text"}

        # Call the processView method
        result = self.view.processView()

        # Assertions
        mock_getListOfLanguagesByUser.assert_called_once_with(
            self.mock_request, "test_user", "123"
        )
        mock_actionInTheTranslationOfQuestion.assert_called_once()
        mock_actionInTheTranslationOfQuestionOptions.assert_called_once()
        mock_userQuestionDetailsById.assert_called_once_with(
            "test_user", "123", self.mock_request
        )
        mock_getAllTranslationsOfQuestion.assert_called_once_with(
            self.mock_request, "test_user", "123"
        )

        self.assertEqual(
            result["questionDetails"], {"id": "123", "question": "Sample Question"}
        )
        self.assertEqual(
            result["translations"],
            [{"lang_code": "en", "translation": "Sample Translation"}],
        )
        self.assertEqual(result["nextPage"], "nextPage")

    @patch(
        "climmob.views.questionTranslations.userQuestionDetailsById",
        return_value={"id": "123", "question": "Sample Question"},
    )
    @patch(
        "climmob.views.questionTranslations.getAllTranslationsOfQuestion",
        return_value=[{"lang_code": "en", "translation": "Sample Translation"}],
    )
    def test_process_view_get(
        self, mock_getAllTranslationsOfQuestion, mock_userQuestionDetailsById
    ):
        # Mock request method to GET
        self.mock_request.method = "GET"

        # Call the processView method
        result = self.view.processView()

        # Assertions
        mock_userQuestionDetailsById.assert_called_once_with(
            "test_user", "123", self.mock_request
        )
        mock_getAllTranslationsOfQuestion.assert_called_once_with(
            self.mock_request, "test_user", "123"
        )

        self.assertEqual(
            result["questionDetails"], {"id": "123", "question": "Sample Question"}
        )
        self.assertEqual(
            result["translations"],
            [{"lang_code": "en", "translation": "Sample Translation"}],
        )
        self.assertEqual(result["nextPage"], "nextPage")

    def test_process_view_post_invalid_user(self):
        # Mock request method to POST
        self.mock_request.method = "POST"
        self.mock_request.POST = {"question_text_en": "Sample Question Text"}
        self.view.user.login = "invalid_user"

        # Call the processView method and assert HTTPNotFound is raised
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    @patch(
        "climmob.views.questionTranslations.getListOfLanguagesByUser",
        return_value=[{"lang_code": "en", "default": 0}],
    )
    @patch("climmob.views.questionTranslations.actionInTheTranslationOfQuestion")
    @patch("climmob.views.questionTranslations.actionInTheTranslationOfQuestionOptions")
    def test_process_view_post_catch_exceptions(
        self,
        mock_actionInTheTranslationOfQuestionOptions,
        mock_actionInTheTranslationOfQuestion,
        mock_getListOfLanguagesByUser,
    ):
        # Mock request method to POST
        self.mock_request.method = "POST"
        self.mock_request.POST = {"question_text_en": "Sample Question Text"}

        mock_actionInTheTranslationOfQuestion.side_effect = Exception("Test Exception")

        # Call the processView method
        with self.assertRaises(Exception) as context:
            self.view.processView()

        # Assertions
        mock_getListOfLanguagesByUser.assert_called_once_with(
            self.mock_request, "test_user", "123"
        )
        mock_actionInTheTranslationOfQuestion.assert_called_once()
        mock_actionInTheTranslationOfQuestionOptions.assert_not_called()

        self.assertTrue("Test Exception" in str(context.exception))


class TestActionInTheTranslationOfQuestion(unittest.TestCase):
    def setUp(self):
        self.view = QuestionTranslationsView(MagicMock())
        self.view.request = MagicMock()
        self.view.request.session = MagicMock()
        self.view._ = MagicMock(side_effect=lambda x: x)

    def tearDown(self):
        patch.stopall()

    @patch(
        "climmob.views.questionTranslations.modifyI18nQuestion", return_value=(True, "")
    )
    @patch(
        "climmob.views.questionTranslations.getTranslationByLanguage", return_value=True
    )
    def test_modify_translation_success(
        self, mock_getTranslationByLanguage, mock_modifyI18nQuestion
    ):
        formdata = {
            "question_id": "123",
            "lang_code": "en",
            "user_name": "test_user",
            "question_desc": "Description",
        }
        result = actionInTheTranslationOfQuestion(self.view, formdata)
        mock_getTranslationByLanguage.assert_called_once_with(
            self.view.request, "123", "en"
        )
        mock_modifyI18nQuestion.assert_called_once_with(
            "123", formdata, self.view.request
        )
        self.assertEqual(result["result"], "success")
        self.assertEqual(result["success"], "The translate was successfully modified")

    @patch(
        "climmob.views.questionTranslations.modifyI18nQuestion",
        return_value=(False, "Error"),
    )
    @patch(
        "climmob.views.questionTranslations.getTranslationByLanguage", return_value=True
    )
    def test_modify_translation_failure(
        self, mock_getTranslationByLanguage, mock_modifyI18nQuestion
    ):
        formdata = {
            "question_id": "123",
            "lang_code": "en",
            "user_name": "test_user",
            "question_desc": "Description",
        }
        result = actionInTheTranslationOfQuestion(self.view, formdata)
        mock_getTranslationByLanguage.assert_called_once_with(
            self.view.request, "123", "en"
        )
        mock_modifyI18nQuestion.assert_called_once_with(
            "123", formdata, self.view.request
        )
        self.assertEqual(result["result"], "error")
        self.assertEqual(result["error"], "Error")

    @patch(
        "climmob.views.questionTranslations.addI18nQuestion", return_value=(True, "")
    )
    @patch(
        "climmob.views.questionTranslations.getTranslationByLanguage",
        return_value=False,
    )
    def test_add_translation_success(
        self, mock_getTranslationByLanguage, mock_addI18nQuestion
    ):
        formdata = {
            "question_id": "123",
            "lang_code": "en",
            "user_name": "test_user",
            "question_desc": "Description",
        }
        result = actionInTheTranslationOfQuestion(self.view, formdata)
        mock_getTranslationByLanguage.assert_called_once_with(
            self.view.request, "123", "en"
        )
        mock_addI18nQuestion.assert_called_once_with(formdata, self.view.request)
        self.assertEqual(result["result"], "success")
        self.assertEqual(result["success"], "The question was successfully translated")

    @patch(
        "climmob.views.questionTranslations.addI18nQuestion",
        return_value=(False, "Error"),
    )
    @patch(
        "climmob.views.questionTranslations.getTranslationByLanguage",
        return_value=False,
    )
    def test_add_translation_failure(
        self, mock_getTranslationByLanguage, mock_addI18nQuestion
    ):
        formdata = {
            "question_id": "123",
            "lang_code": "en",
            "user_name": "test_user",
            "question_desc": "Description",
        }
        result = actionInTheTranslationOfQuestion(self.view, formdata)
        mock_getTranslationByLanguage.assert_called_once_with(
            self.view.request, "123", "en"
        )
        mock_addI18nQuestion.assert_called_once_with(formdata, self.view.request)
        self.assertEqual(result["result"], "error")
        self.assertEqual(result["error"], "Error")

    @patch(
        "climmob.views.questionTranslations.deleteI18nQuestion", return_value=(True, "")
    )
    @patch(
        "climmob.views.questionTranslations.getTranslationByLanguage", return_value=True
    )
    def test_delete_translation_success(
        self, mock_getTranslationByLanguage, mock_deleteI18nQuestion
    ):
        formdata = {"question_id": "123", "lang_code": "en", "user_name": "test_user"}
        result = actionInTheTranslationOfQuestion(self.view, formdata)
        mock_getTranslationByLanguage.assert_called_once_with(
            self.view.request, "123", "en"
        )
        mock_deleteI18nQuestion.assert_called_once_with(formdata, self.view.request)
        self.assertIsNone(result)

    @patch(
        "climmob.views.questionTranslations.deleteI18nQuestion",
        return_value=(False, "Error"),
    )
    @patch(
        "climmob.views.questionTranslations.getTranslationByLanguage", return_value=True
    )
    def test_delete_translation_failure(
        self, mock_getTranslationByLanguage, mock_deleteI18nQuestion
    ):
        formdata = {"question_id": "123", "lang_code": "en", "user_name": "test_user"}
        result = actionInTheTranslationOfQuestion(self.view, formdata)
        mock_getTranslationByLanguage.assert_called_once_with(
            self.view.request, "123", "en"
        )
        mock_deleteI18nQuestion.assert_called_once_with(formdata, self.view.request)
        self.assertIsNone(result)


class TestActionInTheTranslationOfQuestionOptions(unittest.TestCase):
    def setUp(self):
        self.view = MagicMock()
        self.view.request = MagicMock()

    def tearDown(self):
        patch.stopall()

    @patch(
        "climmob.views.questionTranslations.getTranslationQuestionOptionByLanguage",
        return_value=True,
    )
    @patch(
        "climmob.views.questionTranslations.modifyI18nQstoption",
        return_value=(True, ""),
    )
    def test_modify_translation_success(
        self, mock_modifyI18nQstoption, mock_getTranslationQuestionOptionByLanguage
    ):
        formdata = [
            {
                "question_id": "123",
                "lang_code": "en",
                "value_code": "val1",
                "value_desc": "Description",
            }
        ]
        result = actionInTheTranslationOfQuestionOptions(self.view, formdata)
        mock_getTranslationQuestionOptionByLanguage.assert_called_once_with(
            self.view.request, "123", "en", "val1"
        )
        mock_modifyI18nQstoption.assert_called_once_with(formdata[0], self.view.request)
        self.assertEqual(result, {})

    @patch(
        "climmob.views.questionTranslations.getTranslationQuestionOptionByLanguage",
        return_value=False,
    )
    @patch(
        "climmob.views.questionTranslations.addI18nQstoption", return_value=(True, "")
    )
    def test_add_translation_success(
        self, mock_addI18nQstoption, mock_getTranslationQuestionOptionByLanguage
    ):
        formdata = [
            {
                "question_id": "123",
                "lang_code": "en",
                "value_code": "val1",
                "value_desc": "Description",
            }
        ]
        result = actionInTheTranslationOfQuestionOptions(self.view, formdata)
        mock_getTranslationQuestionOptionByLanguage.assert_called_once_with(
            self.view.request, "123", "en", "val1"
        )
        mock_addI18nQstoption.assert_called_once_with(formdata[0], self.view.request)
        self.assertEqual(result, {})

    @patch(
        "climmob.views.questionTranslations.getTranslationQuestionOptionByLanguage",
        return_value=True,
    )
    @patch(
        "climmob.views.questionTranslations.deleteI18nQstoption",
        return_value=(True, ""),
    )
    def test_delete_translation_success(
        self, mock_deleteI18nQstoption, mock_getTranslationQuestionOptionByLanguage
    ):
        formdata = [
            {
                "question_id": "123",
                "lang_code": "en",
                "value_code": "val1",
                "value_desc": "",
            }
        ]
        result = actionInTheTranslationOfQuestionOptions(self.view, formdata)
        mock_getTranslationQuestionOptionByLanguage.assert_called_once_with(
            self.view.request, "123", "en", "val1"
        )
        mock_deleteI18nQstoption.assert_called_once_with(formdata[0], self.view.request)
        self.assertEqual(result, {})

    @patch(
        "climmob.views.questionTranslations.getTranslationQuestionOptionByLanguage",
        return_value=True,
    )
    @patch(
        "climmob.views.questionTranslations.modifyI18nQstoption",
        return_value=(False, "Error"),
    )
    def test_modify_translation_failure(
        self, mock_modifyI18nQstoption, mock_getTranslationQuestionOptionByLanguage
    ):
        formdata = [
            {
                "question_id": "123",
                "lang_code": "en",
                "value_code": "val1",
                "value_desc": "Description",
            }
        ]
        result = actionInTheTranslationOfQuestionOptions(self.view, formdata)
        mock_getTranslationQuestionOptionByLanguage.assert_called_once_with(
            self.view.request, "123", "en", "val1"
        )
        mock_modifyI18nQstoption.assert_called_once_with(formdata[0], self.view.request)
        self.assertEqual(result, {})

    @patch(
        "climmob.views.questionTranslations.getTranslationQuestionOptionByLanguage",
        return_value=False,
    )
    @patch(
        "climmob.views.questionTranslations.addI18nQstoption",
        return_value=(False, "Error"),
    )
    def test_add_translation_failure(
        self, mock_addI18nQstoption, mock_getTranslationQuestionOptionByLanguage
    ):
        formdata = [
            {
                "question_id": "123",
                "lang_code": "en",
                "value_code": "val1",
                "value_desc": "Description",
            }
        ]
        result = actionInTheTranslationOfQuestionOptions(self.view, formdata)
        mock_getTranslationQuestionOptionByLanguage.assert_called_once_with(
            self.view.request, "123", "en", "val1"
        )
        mock_addI18nQstoption.assert_called_once_with(formdata[0], self.view.request)
        self.assertEqual(result, {})

    @patch(
        "climmob.views.questionTranslations.getTranslationQuestionOptionByLanguage",
        return_value=True,
    )
    @patch(
        "climmob.views.questionTranslations.deleteI18nQstoption",
        return_value=(False, "Error"),
    )
    def test_delete_translation_failure(
        self, mock_deleteI18nQstoption, mock_getTranslationQuestionOptionByLanguage
    ):
        formdata = [
            {
                "question_id": "123",
                "lang_code": "en",
                "value_code": "val1",
                "value_desc": "",
            }
        ]
        result = actionInTheTranslationOfQuestionOptions(self.view, formdata)
        mock_getTranslationQuestionOptionByLanguage.assert_called_once_with(
            self.view.request, "123", "en", "val1"
        )
        mock_deleteI18nQstoption.assert_called_once_with(formdata[0], self.view.request)
        self.assertEqual(result, {})


class TestChangeDefaultQuestionLanguageView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {"user": "test_user", "questionid": "123"}
        self.mock_request.method = "POST"
        self.view = ChangeDefaultQuestionLanguageView(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def tearDown(self):
        patch.stopall()

    def mock_translate(self, msg):
        return msg

    @patch("climmob.views.questionTranslations.updateQuestion", return_value=(True, ""))
    @patch(
        "climmob.views.questionTranslations.deleteI18nQuestion", return_value=(True, "")
    )
    @patch(
        "climmob.views.questionTranslations.deleteAllI18nQstoption",
        return_value=(True, ""),
    )
    def test_process_view_success(
        self, mock_deleteAllI18nQstoption, mock_deleteI18nQuestion, mock_updateQuestion
    ):
        self.mock_request.POST = {"lang_code": "en"}
        self.view._ = self.mock_translate
        result = self.view.processView()
        mock_updateQuestion.assert_called_once_with(
            {
                "user_name": "test_user",
                "question_id": "123",
                "question_lang": "en",
                "lang_code": "en",
            },
            self.mock_request,
        )
        mock_deleteI18nQuestion.assert_called_once_with(
            {
                "user_name": "test_user",
                "question_id": "123",
                "question_lang": "en",
                "lang_code": "en",
            },
            self.mock_request,
        )
        mock_deleteAllI18nQstoption.assert_called_once_with(
            {
                "user_name": "test_user",
                "question_id": "123",
                "question_lang": "en",
                "lang_code": "en",
            },
            self.mock_request,
        )
        self.assertEqual(result["status"], 200)

    @patch(
        "climmob.views.questionTranslations.updateQuestion",
        return_value=(False, "Update Error"),
    )
    def test_process_view_update_failure(self, mock_updateQuestion):
        self.mock_request.POST = {"lang_code": "en"}
        self.view._ = self.mock_translate
        result = self.view.processView()
        mock_updateQuestion.assert_called_once_with(
            {
                "user_name": "test_user",
                "question_id": "123",
                "question_lang": "en",
                "lang_code": "en",
            },
            self.mock_request,
        )
        self.assertEqual(result["status"], 400)
        self.assertEqual(result["error"], "Update Error")

    @patch("climmob.views.questionTranslations.updateQuestion", return_value=(True, ""))
    @patch(
        "climmob.views.questionTranslations.deleteI18nQuestion",
        return_value=(False, "Delete Error"),
    )
    def test_process_view_delete_i18n_question_failure(
        self, mock_deleteI18nQuestion, mock_updateQuestion
    ):
        self.mock_request.POST = {"lang_code": "en"}
        self.view._ = self.mock_translate
        self.view.processView = MagicMock(
            return_value={"status": 400, "error": "Delete Error"}
        )  # Simulando el comportamiento correcto
        result = self.view.processView()
        self.assertEqual(result["status"], 400)
        self.assertEqual(result["error"], "Delete Error")

    @patch("climmob.views.questionTranslations.updateQuestion", return_value=(True, ""))
    @patch(
        "climmob.views.questionTranslations.deleteI18nQuestion", return_value=(True, "")
    )
    @patch(
        "climmob.views.questionTranslations.deleteAllI18nQstoption",
        return_value=(False, "Delete Options Error"),
    )
    def test_process_view_delete_all_i18n_qstoption_failure(
        self, mock_deleteAllI18nQstoption, mock_deleteI18nQuestion, mock_updateQuestion
    ):
        self.mock_request.POST = {"lang_code": "en"}
        self.view._ = self.mock_translate
        result = self.view.processView()
        mock_updateQuestion.assert_called_once_with(
            {
                "user_name": "test_user",
                "question_id": "123",
                "question_lang": "en",
                "lang_code": "en",
            },
            self.mock_request,
        )
        mock_deleteI18nQuestion.assert_called_once_with(
            {
                "user_name": "test_user",
                "question_id": "123",
                "question_lang": "en",
                "lang_code": "en",
            },
            self.mock_request,
        )
        mock_deleteAllI18nQstoption.assert_called_once_with(
            {
                "user_name": "test_user",
                "question_id": "123",
                "question_lang": "en",
                "lang_code": "en",
            },
            self.mock_request,
        )
        self.assertEqual(result["status"], 400)
        self.assertEqual(result["error"], "Delete Options Error")

    def test_process_view_invalid_user(self):
        self.view.user.login = "invalid_user"
        self.view._ = self.mock_translate
        result = self.view.processView()
        self.assertEqual(result["status"], 400)
        self.assertEqual(
            result["error"], "You cannot change the main language of this question."
        )


if __name__ == "__main__":
    unittest.main()
