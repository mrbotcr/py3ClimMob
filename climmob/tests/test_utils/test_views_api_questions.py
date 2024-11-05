import json
import unittest
from unittest.mock import patch, MagicMock, ANY
from climmob.tests.test_utils.common import BaseViewTestCase
from climmob.views.Api.questions import (
    CreateQuestionView,
    ReadQuestionsView,
    UpdateQuestionView,
    DeleteQuestionViewApi,
    ReadQuestionValuesView,
    AddQuestionValueViewApi,
    UpdateQuestionValueView,
    DeleteQuestionValueViewApi,
    UpdateQuestionCharacteristicsView,
    UpdateQuestionPerformanceView,
    MultiLanguageQuestionView,
    ReadMultiLanguagesFromQuestionView,
)


class TestCreateQuestionView(BaseViewTestCase):
    view_class = CreateQuestionView
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.valid_data = {
            "question_code": "Q001",
            "question_name": "Sample Question",
            "question_desc": "This is a sample question",
            "question_dtype": "1",
            "qstgroups_id": "1",
            "question_requiredvalue": "1",
            "question_lang": "en",
        }
        self.view.body = json.dumps(self.valid_data)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_missing_obligatory_keys(self):
        invalid_data = self.valid_data.copy()
        del invalid_data["question_name"]
        self.view.body = json.dumps(invalid_data)

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "It is not complying with the obligatory keys.", response.body.decode()
        )

    def test_process_view_unpermitted_keys(self):
        invalid_data = self.valid_data.copy()
        invalid_data["unpermitted_key"] = "value"
        self.view.body = json.dumps(invalid_data)

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the parameters that you want to add.", response.body.decode()
        )

    def test_process_view_empty_parameters(self):
        invalid_data = self.valid_data.copy()
        invalid_data["question_name"] = ""
        self.view.body = json.dumps(invalid_data)

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch("climmob.views.Api.questions.languageExistInI18nUser", return_value=False)
    def test_process_view_language_not_in_user_languages(
        self, mock_language_exist_in_i18n_user
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The language does not belong to your list of languages to be used.",
            response.body.decode(),
        )

        mock_language_exist_in_i18n_user.assert_called_once_with(
            "en", "test_user", self.view.request
        )

    def test_process_view_invalid_zero_or_two_parameters(self):
        invalid_data = self.valid_data.copy()
        invalid_data["question_alwaysinreg"] = "3"
        self.view.body = json.dumps(invalid_data)

        with patch(
            "climmob.views.Api.questions.languageExistInI18nUser",
            return_value=True,
        ) as mock_language_exist_in_i18n_user:
            response = self.view.processView()

            self.assertEqual(response.status_code, 401)
            self.assertIn(
                "The possible values in the parameters: 'question_alwaysinreg','question_alwaysinasse','question_requiredvalue', 'question_quantitative' is 1 or 0.",
                response.body.decode(),
            )

            mock_language_exist_in_i18n_user.assert_called_once_with(
                "en", "test_user", self.view.request
            )

    def test_process_view_invalid_question_dtype(self):
        invalid_data = self.valid_data.copy()
        invalid_data["question_dtype"] = "99"
        self.view.body = json.dumps(invalid_data)

        with patch(
            "climmob.views.Api.questions.languageExistInI18nUser",
            return_value=True,
        ) as mock_language_exist_in_i18n_user:
            response = self.view.processView()

            self.assertEqual(response.status_code, 401)
            self.assertIn("Check the ID of the question type.", response.body.decode())

            mock_language_exist_in_i18n_user.assert_called_once_with(
                "en", "test_user", self.view.request
            )

    @patch("climmob.views.Api.questions.questionExists", return_value=True)
    @patch("climmob.views.Api.questions.languageExistInI18nUser", return_value=True)
    def test_process_view_question_already_exists(
        self, mock_language_exist_in_i18n_user, mock_question_exists
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is another question with the same code.", response.body.decode()
        )

        mock_language_exist_in_i18n_user.assert_called_once_with(
            "en", "test_user", self.view.request
        )
        mock_question_exists.assert_called_once_with(
            "test_user", "Q001", self.view.request
        )

    @patch("climmob.views.Api.questions.categoryExistsById", return_value=None)
    @patch("climmob.views.Api.questions.questionExists", return_value=False)
    @patch("climmob.views.Api.questions.languageExistInI18nUser", return_value=True)
    def test_process_view_category_does_not_exist(
        self,
        mock_language_exist_in_i18n_user,
        mock_question_exists,
        mock_category_exists_by_id,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no category with this identifier.", response.body.decode()
        )

        mock_language_exist_in_i18n_user.assert_called_once_with(
            "en", "test_user", self.view.request
        )
        mock_question_exists.assert_called_once_with(
            "test_user", "Q001", self.view.request
        )
        mock_category_exists_by_id.assert_called_once_with(
            "test_user", "1", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.addQuestion",
        return_value=(False, "Error adding question"),
    )
    @patch(
        "climmob.views.Api.questions.categoryExistsById",
        return_value={"user_name": "test_user"},
    )
    @patch("climmob.views.Api.questions.questionExists", return_value=False)
    @patch("climmob.views.Api.questions.languageExistInI18nUser", return_value=True)
    def test_process_view_add_question_failure(
        self,
        mock_language_exist_in_i18n_user,
        mock_question_exists,
        mock_category_exists_by_id,
        mock_add_question,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error adding question", response.body.decode())

        mock_language_exist_in_i18n_user.assert_called_once_with(
            "en", "test_user", self.view.request
        )
        mock_question_exists.assert_called_once_with(
            "test_user", "Q001", self.view.request
        )
        mock_category_exists_by_id.assert_called_once_with(
            "test_user", "1", self.view.request
        )
        mock_add_question.assert_called_once_with(ANY, self.view.request)

    @patch(
        "climmob.views.Api.questions.addQuestion",
        return_value=(True, "Q001"),
    )
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value={"question_data": "data"},
    )
    @patch(
        "climmob.views.Api.questions.categoryExistsById",
        return_value={"user_name": "test_user"},
    )
    @patch("climmob.views.Api.questions.questionExists", return_value=False)
    @patch("climmob.views.Api.questions.languageExistInI18nUser", return_value=True)
    def test_process_view_success(
        self,
        mock_language_exist_in_i18n_user,
        mock_question_exists,
        mock_category_exists_by_id,
        mock_get_question_data,
        mock_add_question,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.body.decode()), {"question_data": "data"})

        mock_language_exist_in_i18n_user.assert_called_once_with(
            "en", "test_user", self.view.request
        )
        mock_question_exists.assert_called_once_with(
            "test_user", "Q001", self.view.request
        )
        mock_category_exists_by_id.assert_called_once_with(
            "test_user", "1", self.view.request
        )
        mock_add_question.assert_called_once_with(ANY, self.view.request)
        mock_get_question_data.assert_called_once_with(
            "test_user", "Q001", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.addQuestion",
        return_value=(True, "Q001"),
    )
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value={"question_data": "data"},
    )
    @patch(
        "climmob.views.Api.questions.categoryExistsById",
        return_value={"user_name": "test_user"},
    )
    @patch("climmob.views.Api.questions.questionExists", return_value=False)
    @patch("climmob.views.Api.questions.languageExistInI18nUser", return_value=True)
    def test_process_view_success_with_dtype_5(
        self,
        mock_language_exist_in_i18n_user,
        mock_question_exists,
        mock_category_exists_by_id,
        mock_get_question_data,
        mock_add_question,
    ):
        self.valid_data["question_dtype"] = "5"
        self.view.body = json.dumps(self.valid_data)

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.body.decode()), {"question_data": "data"})

        mock_language_exist_in_i18n_user.assert_called_once_with(
            "en", "test_user", self.view.request
        )
        mock_question_exists.assert_called_once_with(
            "test_user", "Q001", self.view.request
        )
        mock_category_exists_by_id.assert_called_once_with(
            "test_user", "1", self.view.request
        )
        mock_add_question.assert_called_once_with(ANY, self.view.request)
        mock_get_question_data.assert_called_once_with(
            "test_user", "Q001", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.addQuestion",
        return_value=(True, "Q001"),
    )
    @patch(
        "climmob.views.Api.questions.categoryExistsById",
        return_value={"user_name": "test_user"},
    )
    @patch("climmob.views.Api.questions.questionExists", return_value=False)
    @patch("climmob.views.Api.questions.languageExistInI18nUser", return_value=True)
    def test_process_view_success_with_dtype_9(
        self,
        mock_language_exist_in_i18n_user,
        mock_question_exists,
        mock_category_exists_by_id,
        mock_add_question,
    ):
        self.valid_data["question_dtype"] = "9"
        self.view.body = json.dumps(self.valid_data)

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The question was successfully added. Configure the ranking of options now.",
            response.body.decode(),
        )

        mock_language_exist_in_i18n_user.assert_called_once_with(
            "en", "test_user", self.view.request
        )
        mock_question_exists.assert_called_once_with(
            "test_user", "Q001", self.view.request
        )
        mock_category_exists_by_id.assert_called_once_with(
            "test_user", "1", self.view.request
        )
        mock_add_question.assert_called_once_with(ANY, self.view.request)

    @patch(
        "climmob.views.Api.questions.addQuestion",
        return_value=(True, "Q001"),
    )
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value={"question_data": "data"},
    )
    @patch(
        "climmob.views.Api.questions.categoryExistsById",
        return_value={"user_name": "test_user"},
    )
    @patch("climmob.views.Api.questions.questionExists", return_value=False)
    @patch("climmob.views.Api.questions.languageExistInI18nUser", return_value=True)
    def test_process_view_success_with_dtype_10(
        self,
        mock_language_exist_in_i18n_user,
        mock_question_exists,
        mock_category_exists_by_id,
        mock_get_question_data,
        mock_add_question,
    ):
        self.valid_data["question_dtype"] = "10"
        self.view.body = json.dumps(self.valid_data)

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.body.decode()), {"question_data": "data"})

        mock_language_exist_in_i18n_user.assert_called_once_with(
            "en", "test_user", self.view.request
        )
        mock_question_exists.assert_called_once_with(
            "test_user", "Q001", self.view.request
        )
        mock_category_exists_by_id.assert_called_once_with(
            "test_user", "1", self.view.request
        )
        mock_add_question.assert_called_once_with(ANY, self.view.request)
        mock_get_question_data.assert_called_once_with(
            "test_user", "Q001", self.view.request
        )


class TestReadQuestionsView(BaseViewTestCase):
    view_class = ReadQuestionsView
    request_method = "GET"

    def setUp(self):
        super().setUp()
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def test_process_view_invalid_method(self):
        self.view.request.method = "POST"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    @patch("climmob.views.Api.questions.UserQuestion")
    def test_process_view_success(self, mock_user_question):
        mock_user_question.side_effect = [
            [{"id": 1, "question": "Question 1"}],
            [{"id": 2, "question": "Question 2"}],
        ]
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body.decode())
        expected_data = [
            {"id": 1, "question": "Question 1"},
            {"id": 2, "question": "Question 2"},
        ]
        self.assertEqual(response_data, expected_data)
        mock_user_question.assert_any_call("test_user", self.view.request)
        mock_user_question.assert_any_call("bioversity", self.view.request)
        self.assertEqual(mock_user_question.call_count, 2)

    @patch("climmob.views.Api.questions.UserQuestion")
    def test_process_view_no_questions(self, mock_user_question):
        mock_user_question.side_effect = [
            [],
            [],
        ]
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body.decode())
        expected_data = []
        self.assertEqual(response_data, expected_data)
        mock_user_question.assert_any_call("test_user", self.view.request)
        mock_user_question.assert_any_call("bioversity", self.view.request)
        self.assertEqual(mock_user_question.call_count, 2)


class TestUpdateQuestionView(BaseViewTestCase):
    view_class = UpdateQuestionView
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.view.user = MagicMock()
        self.view.user.login = "test_user"
        self.valid_data = {
            "question_id": "QST123",
            "question_name": "New Question Name",
            "question_dtype": "1",
            "question_lang": "en",
        }
        self.view.body = json.dumps(self.valid_data)

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    @patch("climmob.views.Api.questions.updateQuestion", return_value=(True, "Success"))
    @patch(
        "climmob.views.Api.questions.categoryExistsById",
        return_value={"user_name": "test_user"},
    )
    @patch("climmob.views.Api.questions.getQuestionData")
    @patch("climmob.views.Api.questions.languageExistInI18nUser", return_value=True)
    def test_process_view_success(
        self,
        mock_language_exist,
        mock_get_question_data,
        mock_category_exists,
        mock_update_question,
    ):
        mock_get_question_data.return_value = (
            {
                "question_alwaysinreg": "1",
                "question_alwaysinasse": "0",
                "question_requiredvalue": "1",
                "question_tied": "0",
                "question_notobserved": "0",
                "question_quantitative": "1",
                "question_unit": "kg",
                "question_dtype": "1",
            },
            True,
        )

        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn("The question was successfully modified.", response.body.decode())
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        if "qstgroups_id" in self.valid_data:
            mock_category_exists.assert_called_once_with(
                "test_user", self.valid_data["qstgroups_id"], self.view.request
            )
        mock_update_question.assert_called_once_with(ANY, self.view.request)

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"user_name": "test_user"}, False),
    )
    def test_process_view_question_not_editable(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "This question has already been assigned to a form. You cannot edit it.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch("climmob.views.Api.questions.getQuestionData", return_value=(None, False))
    def test_process_view_question_not_found(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID.", response.body.decode()
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch("climmob.views.Api.questions.getQuestionData")
    @patch("climmob.views.Api.questions.languageExistInI18nUser", return_value=False)
    def test_process_view_invalid_language(
        self, mock_language_exists, mock_get_question_data
    ):

        mock_get_question_data.return_value = (
            {
                "question_alwaysinreg": "1",
                "question_alwaysinasse": "0",
                "question_requiredvalue": "1",
                "question_tied": "0",
                "question_notobserved": "0",
                "question_quantitative": "1",
                "question_unit": "kg",
                "question_dtype": "1",
            },
            True,
        )

        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The language does not belong to your list of languages to be used..",
            response.body.decode(),
        )
        mock_language_exists.assert_called_once_with(
            "en", "test_user", self.view.request
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    def test_process_view_missing_question_id(self):
        self.view.body = json.dumps({"question_name": "New Name"})
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "It is not complying with the obligatory keys.", response.body.decode()
        )


class TestDeleteQuestionViewApi(BaseViewTestCase):
    view_class = DeleteQuestionViewApi
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.view.user = MagicMock()
        self.view.user.login = "test_user"
        self.valid_data = {"question_id": "QST123"}
        self.view.body = json.dumps(self.valid_data)

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_missing_obligatory_keys(self):
        self.view.body = json.dumps({})
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch("climmob.views.Api.questions.getQuestionData")
    def test_process_view_question_not_found(self, mock_get_question_data):
        mock_get_question_data.return_value = (None, False)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID.", response.body.decode()
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch("climmob.views.Api.questions.getQuestionData")
    def test_process_view_question_not_editable(self, mock_get_question_data):
        mock_get_question_data.return_value = ({"user_name": "test_user"}, False)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "This question has already been assigned to a form. You cannot delete it.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch("climmob.views.Api.questions.getQuestionData")
    def test_process_view_question_not_editable_library(self, mock_get_question_data):
        mock_get_question_data.return_value = ({"user_name": "bioversity"}, False)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The question is from the ClimMob library. You cannot delete it.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch("climmob.views.Api.questions.deleteQuestion")
    @patch("climmob.views.Api.questions.getQuestionData")
    def test_process_view_delete_failed(
        self, mock_get_question_data, mock_delete_question
    ):
        mock_get_question_data.return_value = ({"user_name": "test_user"}, True)
        mock_delete_question.return_value = (False, "Delete failed")
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Delete failed", response.body.decode())
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        mock_delete_question.assert_called_once_with(
            {"question_id": "QST123", "user_name": "test_user"}, self.view.request
        )

    @patch("climmob.views.Api.questions.deleteQuestion")
    @patch("climmob.views.Api.questions.getQuestionData")
    def test_process_view_success(self, mock_get_question_data, mock_delete_question):
        mock_get_question_data.return_value = ({"user_name": "test_user"}, True)
        mock_delete_question.return_value = (True, "Deleted")
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn("The question was deleted successfully.", response.body.decode())
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        mock_delete_question.assert_called_once_with(
            {"question_id": "QST123", "user_name": "test_user"}, self.view.request
        )


class TestReadQuestionValuesView(BaseViewTestCase):
    view_class = ReadQuestionValuesView
    request_method = "GET"

    def setUp(self):
        super().setUp()
        self.view.user = MagicMock()
        self.view.user.login = "test_user"
        self.valid_data = {"question_id": "QST123", "user_name": "test_user"}
        self.view.body = json.dumps(self.valid_data)

    def test_process_view_invalid_method(self):
        self.view.request.method = "POST"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    def test_process_view_invalid_json(self):
        self.view.body = "Invalid JSON"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )

    def test_process_view_missing_obligatory_keys(self):

        self.view.body = json.dumps({"user_name": "test_user"})
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch("climmob.views.Api.questions.getQuestionData", return_value=(None, False))
    def test_process_view_question_not_found(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID.", response.body.decode()
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 1}, True),
    )
    def test_process_view_invalid_question_type(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "This is not a question of type Select one or Multiple selection.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionOptions",
        return_value=[
            {"option_id": 1, "option_text": "Option 1"},
            {"option_id": 2, "option_text": "Option 2"},
        ],
    )
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 5, "question_id": "QST123"}, True),
    )
    def test_process_view_success(
        self, mock_get_question_data, mock_get_question_options
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        expected_response = [
            {"option_id": 1, "option_text": "Option 1"},
            {"option_id": 2, "option_text": "Option 2"},
        ]
        self.assertEqual(json.loads(response.body.decode()), expected_response)
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        mock_get_question_options.assert_called_once_with("QST123", self.view.request)

    @patch(
        "climmob.views.Api.questions.getQuestionOptions",
        return_value=[
            {"option_id": 1, "option_text": "Option A"},
            {"option_id": 2, "option_text": "Option B"},
        ],
    )
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 6, "question_id": "QST123"}, True),
    )
    def test_process_view_success_multiple_selection(
        self, mock_get_question_data, mock_get_question_options
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        expected_response = [
            {"option_id": 1, "option_text": "Option A"},
            {"option_id": 2, "option_text": "Option B"},
        ]
        self.assertEqual(json.loads(response.body.decode()), expected_response)
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        mock_get_question_options.assert_called_once_with("QST123", self.view.request)


class TestAddQuestionValueViewApi(BaseViewTestCase):
    view_class = AddQuestionValueViewApi
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.view.user = MagicMock()
        self.view.user.login = "test_user"
        self.valid_data = {
            "question_id": "QST123",
            "value_code": "OPT1",
            "value_desc": "Option 1",
            "user_name": "test_user",
        }
        self.view.body = json.dumps(self.valid_data)

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_missing_obligatory_keys(self):
        self.view.body = json.dumps({"question_id": "QST123", "value_code": "OPT1"})
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "It is not complying with the obligatory keys.", response.body.decode()
        )

    def test_process_view_unpermitted_keys(self):
        invalid_data = self.valid_data.copy()
        invalid_data["invalid_key"] = "invalid_value"
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the parameters that you want to add.", response.body.decode()
        )

    def test_process_view_empty_parameters(self):
        invalid_data = self.valid_data.copy()
        invalid_data["value_desc"] = ""
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch("climmob.views.Api.questions.getQuestionData", return_value=(None, False))
    def test_process_view_question_not_found(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID.", response.body.decode()
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 1, "user_name": "test_user"}, True),
    )
    def test_process_view_invalid_question_type(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "This is not a question of type Select one or Multiple selection.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 5, "user_name": "test_user"}, False),
    )
    def test_process_view_question_not_editable(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "This question has already been assigned to a form. You cannot add it.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch("climmob.views.Api.questions.optionExists", return_value=True)
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 5, "user_name": "test_user"}, True),
    )
    def test_process_view_option_code_exists(
        self, mock_get_question_data, mock_option_exists
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is already an option with that code.", response.body.decode()
        )
        mock_option_exists.assert_called_once_with("QST123", "OPT1", self.view.request)

    @patch("climmob.views.Api.questions.optionExists", return_value=False)
    @patch("climmob.views.Api.questions.optionExistsWithName", return_value=True)
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 5, "user_name": "test_user"}, True),
    )
    def test_process_view_option_desc_exists(
        self, mock_get_question_data, mock_option_exists_with_name, mock_option_exists
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is already an option with that description.", response.body.decode()
        )
        mock_option_exists.assert_called_once_with("QST123", "OPT1", self.view.request)
        mock_option_exists_with_name.assert_called_once_with(
            "QST123", "Option 1", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.addOptionToQuestion",
        return_value=(False, "Failed to add option"),
    )
    @patch("climmob.views.Api.questions.optionExists", return_value=False)
    @patch("climmob.views.Api.questions.optionExistsWithName", return_value=False)
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 5, "user_name": "test_user"}, True),
    )
    def test_process_view_add_option_failure(
        self,
        mock_get_question_data,
        mock_option_exists_with_name,
        mock_option_exists,
        mock_add_option,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Failed to add option", response.body.decode())
        mock_add_option.assert_called_once_with(
            {
                "question_id": "QST123",
                "value_code": "OPT1",
                "value_desc": "Option 1",
                "user_name": "test_user",
                "value_isother": 0,
                "value_isna": 0,
            },
            self.view.request,
        )

    @patch(
        "climmob.views.Api.questions.addOptionToQuestion",
        return_value=(True, "Option added"),
    )
    @patch("climmob.views.Api.questions.opcionNAinQuestion", return_value=False)
    @patch("climmob.views.Api.questions.opcionOtherInQuestion", return_value=False)
    @patch("climmob.views.Api.questions.optionExists", return_value=False)
    @patch("climmob.views.Api.questions.optionExistsWithName", return_value=False)
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 5, "user_name": "test_user"}, True),
    )
    def test_process_view_success(
        self,
        mock_get_question_data,
        mock_option_exists_with_name,
        mock_option_exists,
        mock_opcion_other,
        mock_opcion_na,
        mock_add_option,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn("The option was successfully added.", response.body.decode())
        mock_add_option.assert_called_once_with(
            {
                "question_id": "QST123",
                "value_code": "OPT1",
                "value_desc": "Option 1",
                "user_name": "test_user",
                "value_isother": 0,
                "value_isna": 0,
            },
            self.view.request,
        )

    @patch("climmob.views.Api.questions.opcionOtherInQuestion", return_value=True)
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 5, "user_name": "test_user"}, True),
    )
    def test_process_view_other_option_exists(
        self, mock_get_question_data, mock_opcion_other
    ):
        data_with_other = self.valid_data.copy()
        data_with_other["value_isother"] = "1"
        self.view.body = json.dumps(data_with_other)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("There is already an 'Other' option.", response.body.decode())

    @patch("climmob.views.Api.questions.opcionNAinQuestion", return_value=True)
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 5, "user_name": "test_user"}, True),
    )
    def test_process_view_na_option_exists(
        self, mock_get_question_data, mock_opcion_na
    ):
        data_with_na = self.valid_data.copy()
        data_with_na["value_isna"] = "1"
        self.view.body = json.dumps(data_with_na)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is already an 'Not applicable' option.", response.body.decode()
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 5, "user_name": "test_user"}, True),
    )
    def test_process_view_option_both_other_and_na(self, mock_get_question_data):
        data_with_both = self.valid_data.copy()
        data_with_both["value_isother"] = "1"
        data_with_both["value_isna"] = "1"
        self.view.body = json.dumps(data_with_both)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "An option cannot be 'Other' and 'Not applicable'.", response.body.decode()
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 5, "user_name": "bioversity"}, False),
    )
    def test_process_view_question_from_library(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The question is from the ClimMob library. You cannot add it.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )


class TestUpdateQuestionValueView(BaseViewTestCase):
    view_class = UpdateQuestionValueView
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.view.user = MagicMock()
        self.view.user.login = "test_user"
        self.valid_data = {
            "question_id": "QST123",
            "value_code": "OPT1",
            "value_desc": "Updated Option Description",
            "user_name": "test_user",
        }
        self.view.body = json.dumps(self.valid_data)

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_missing_obligatory_keys(self):
        self.view.body = json.dumps({"question_id": "QST123", "value_code": "OPT1"})
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "It is not complying with the obligatory keys.", response.body.decode()
        )

    def test_process_view_unpermitted_keys(self):
        invalid_data = self.valid_data.copy()
        invalid_data["invalid_key"] = "invalid_value"
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the parameters that you want to add.", response.body.decode()
        )

    def test_process_view_empty_parameters(self):
        invalid_data = self.valid_data.copy()
        invalid_data["value_desc"] = ""
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch("climmob.views.Api.questions.getQuestionData", return_value=(None, False))
    def test_process_view_question_not_found(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID.", response.body.decode()
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"user_name": "test_user", "question_dtype": 5}, False),
    )
    def test_process_view_question_not_editable(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "This question has already been assigned to a form. You cannot edit it.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"user_name": "test_user", "question_dtype": 1}, True),
    )
    def test_process_view_invalid_question_type(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "This is not a question of type Select one or Multiple selection.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch("climmob.views.Api.questions.optionExists", return_value=False)
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"user_name": "test_user", "question_dtype": 5}, True),
    )
    def test_process_view_option_not_exists(
        self, mock_get_question_data, mock_option_exists
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Does not have an option with this value_code", response.body.decode()
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        mock_option_exists.assert_called_once_with("QST123", "OPT1", self.view.request)

    @patch(
        "climmob.views.Api.questions.updateOption",
        return_value=(False, "Update failed"),
    )
    @patch(
        "climmob.views.Api.questions.getOptionData",
        return_value={"value_isother": 0, "value_isna": 0},
    )
    @patch("climmob.views.Api.questions.optionExists", return_value=True)
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"user_name": "test_user", "question_dtype": 5}, True),
    )
    def test_process_view_update_option_failure(
        self,
        mock_get_question_data,
        mock_option_exists,
        mock_get_option_data,
        mock_update_option,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Update failed", response.body.decode())
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        mock_option_exists.assert_called_once_with("QST123", "OPT1", self.view.request)
        mock_get_option_data.assert_called_once_with(
            "QST123", "OPT1", self.view.request
        )
        expected_dataworking = self.valid_data.copy()
        expected_dataworking["value_isother"] = 0
        expected_dataworking["value_isna"] = 0
        mock_update_option.assert_called_once_with(
            expected_dataworking, self.view.request
        )

    @patch(
        "climmob.views.Api.questions.updateOption",
        return_value=(True, "Option updated"),
    )
    @patch(
        "climmob.views.Api.questions.getOptionData",
        return_value={"value_isother": 0, "value_isna": 0},
    )
    @patch("climmob.views.Api.questions.optionExists", return_value=True)
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"user_name": "test_user", "question_dtype": 5}, True),
    )
    def test_process_view_success(
        self,
        mock_get_question_data,
        mock_option_exists,
        mock_get_option_data,
        mock_update_option,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn("The option was successfully update.", response.body.decode())
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        mock_option_exists.assert_called_once_with("QST123", "OPT1", self.view.request)
        mock_get_option_data.assert_called_once_with(
            "QST123", "OPT1", self.view.request
        )
        expected_dataworking = self.valid_data.copy()
        expected_dataworking["value_isother"] = 0
        expected_dataworking["value_isna"] = 0
        mock_update_option.assert_called_once_with(
            expected_dataworking, self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"user_name": "bioversity", "question_dtype": 5}, False),
    )
    def test_process_view_question_from_library(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The question is from the ClimMob library. You cannot edit it.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    def test_process_view_not_all_parameters_have_data(self):
        invalid_data = self.valid_data.copy()
        invalid_data["value_desc"] = ""
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())


class TestDeleteQuestionValueViewApi(BaseViewTestCase):
    view_class = DeleteQuestionValueViewApi
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.view.user = MagicMock()
        self.view.user.login = "test_user"
        self.valid_data = {
            "question_id": "QST123",
            "value_code": "OPT1",
            "user_name": "test_user",
        }
        self.view.body = json.dumps(self.valid_data)

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    def test_process_view_missing_obligatory_keys(self):
        invalid_data = self.valid_data.copy()
        del invalid_data["question_id"]
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch("climmob.views.Api.questions.getQuestionData", return_value=(None, False))
    def test_process_view_question_not_found(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID.", response.body.decode()
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"user_name": "test_user", "question_dtype": 5}, False),
    )
    def test_process_view_question_not_editable(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "This question has already been assigned to a form. You cannot delete it.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"user_name": "bioversity", "question_dtype": 5}, False),
    )
    def test_process_view_question_from_library(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The question is from the ClimMob library. You cannot delete it.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 1}, True),
    )
    def test_process_view_invalid_question_type(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "This is not a question of type Select one or Multiple selection.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch("climmob.views.Api.questions.optionExists", return_value=False)
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 5}, True),
    )
    def test_process_view_option_not_exists(
        self, mock_get_question_data, mock_option_exists
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Does not have an option with this value_code", response.body.decode()
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        mock_option_exists.assert_called_once_with("QST123", "OPT1", self.view.request)

    @patch(
        "climmob.views.Api.questions.deleteOption",
        return_value=(False, "Error message"),
    )
    @patch("climmob.views.Api.questions.optionExists", return_value=True)
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 5}, True),
    )
    def test_process_view_delete_option_failure(
        self, mock_get_question_data, mock_option_exists, mock_delete_option
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error message", response.body.decode())
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        mock_option_exists.assert_called_once_with("QST123", "OPT1", self.view.request)
        mock_delete_option.assert_called_once_with("QST123", "OPT1", self.view.request)

    @patch("climmob.views.Api.questions.deleteOption", return_value=(True, "Success"))
    @patch("climmob.views.Api.questions.optionExists", return_value=True)
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 5}, True),
    )
    def test_process_view_success(
        self, mock_get_question_data, mock_option_exists, mock_delete_option
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn("The option was successfully deleted.", response.body.decode())
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        mock_option_exists.assert_called_once_with("QST123", "OPT1", self.view.request)
        mock_delete_option.assert_called_once_with("QST123", "OPT1", self.view.request)


class TestUpdateQuestionCharacteristicsView(BaseViewTestCase):
    view_class = UpdateQuestionCharacteristicsView
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.view.user = MagicMock()
        self.view.user.login = "test_user"
        self.valid_data = {
            "question_id": "QST123",
            "question_posstm": "Positive statement",
            "question_negstm": "Negative statement",
            "user_name": "test_user",
        }
        self.view.body = json.dumps(self.valid_data)

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_missing_obligatory_keys(self):
        invalid_data = self.valid_data.copy()
        del invalid_data["question_negstm"]
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "It is not complying with the obligatory keys.", response.body.decode()
        )

    def test_process_view_unpermitted_keys(self):
        invalid_data = self.valid_data.copy()
        invalid_data["invalid_key"] = "invalid_value"
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the parameters that you want to add.", response.body.decode()
        )

    def test_process_view_empty_parameters(self):
        invalid_data = self.valid_data.copy()
        invalid_data["question_posstm"] = ""
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch("climmob.views.Api.questions.getQuestionData", return_value=(None, False))
    def test_process_view_question_not_found(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID.", response.body.decode()
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"user_name": "test_user", "question_dtype": 9}, False),
    )
    def test_process_view_question_not_editable(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "This question has already been assigned to a form. You cannot edit it.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"user_name": "bioversity", "question_dtype": 9}, False),
    )
    def test_process_view_question_from_library(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The question is from the ClimMob library. You cannot edit it.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.updateQuestion",
        return_value=(False, "Update failed"),
    )
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 9}, True),
    )
    def test_process_view_update_failed(
        self, mock_get_question_data, mock_update_question
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Update failed", response.body.decode())
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        expected_dataworking = self.valid_data.copy()
        mock_update_question.assert_called_once_with(
            expected_dataworking, self.view.request
        )

    @patch("climmob.views.Api.questions.updateQuestion", return_value=(True, "Success"))
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 9}, True),
    )
    def test_process_view_success(self, mock_get_question_data, mock_update_question):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "You successfully updated the ranking of options.", response.body.decode()
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        expected_dataworking = self.valid_data.copy()
        mock_update_question.assert_called_once_with(
            expected_dataworking, self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 1}, True),
    )
    def test_process_view_invalid_question_type(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "This is not a question of type ranking of options.", response.body.decode()
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    def test_process_view_not_all_parameters_have_data(self):
        invalid_data = self.valid_data.copy()
        invalid_data["question_negstm"] = ""
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())


class TestUpdateQuestionPerformanceView(BaseViewTestCase):
    view_class = UpdateQuestionPerformanceView
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.view.user = MagicMock()
        self.view.user.login = "test_user"
        self.valid_data = {
            "question_id": "QST123",
            "question_perfstmt": "Compare with {{option}}",
            "user_name": "test_user",
        }
        self.view.body = json.dumps(self.valid_data)

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_missing_obligatory_keys(self):
        invalid_data = self.valid_data.copy()
        del invalid_data["question_perfstmt"]
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "It is not complying with the obligatory keys.", response.body.decode()
        )

    def test_process_view_unpermitted_keys(self):
        invalid_data = self.valid_data.copy()
        invalid_data["invalid_key"] = "invalid_value"
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the parameters that you want to add.", response.body.decode()
        )

    def test_process_view_empty_parameters(self):
        invalid_data = self.valid_data.copy()
        invalid_data["question_perfstmt"] = ""
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch("climmob.views.Api.questions.getQuestionData", return_value=(None, False))
    def test_process_view_question_not_found(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID.", response.body.decode()
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"user_name": "test_user", "question_dtype": 10}, False),
    )
    def test_process_view_question_not_editable(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "This question has already been assigned to a form. You cannot edit it.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"user_name": "bioversity", "question_dtype": 10}, False),
    )
    def test_process_view_question_from_library(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The question is from the ClimMob library. You cannot edit it.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 1}, True),
    )
    def test_process_view_invalid_question_type(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "This is not a question of type comparison with check.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 10}, True),
    )
    def test_process_view_missing_wildcard(self, mock_get_question_data):
        invalid_data = self.valid_data.copy()
        invalid_data["question_perfstmt"] = "Compare with option"
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The comparison with check must have the wildcard {{option}}",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.updateQuestion",
        return_value=(False, "Update failed"),
    )
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 10}, True),
    )
    def test_process_view_update_failed(
        self, mock_get_question_data, mock_update_question
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Update failed", response.body.decode())
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        expected_dataworking = self.valid_data.copy()
        mock_update_question.assert_called_once_with(
            expected_dataworking, self.view.request
        )

    @patch("climmob.views.Api.questions.updateQuestion", return_value=(True, "Success"))
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_dtype": 10}, True),
    )
    def test_process_view_success(self, mock_get_question_data, mock_update_question):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "You successfully updated the comparison with check.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        expected_dataworking = self.valid_data.copy()
        mock_update_question.assert_called_once_with(
            expected_dataworking, self.view.request
        )

    def test_process_view_not_all_parameters_have_data(self):
        invalid_data = self.valid_data.copy()
        invalid_data["question_perfstmt"] = ""
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())


class TestMultiLanguageQuestionView(BaseViewTestCase):
    view_class = MultiLanguageQuestionView
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.view.user = MagicMock()
        self.view.user.login = "test_user"
        self.valid_data = {
            "question_id": "QST123",
            "question_name": "Translated Question Name",
            "lang_code": "es",
            "user_name": "test_user",
        }
        self.view.body = json.dumps(self.valid_data)

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_missing_question_id(self):
        invalid_data = self.valid_data.copy()
        del invalid_data["question_id"]
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("The question_id parameter is required.", response.body.decode())

    @patch("climmob.views.Api.questions.getQuestionData", return_value=(None, False))
    def test_process_view_question_not_found(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID.", response.body.decode()
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_lang": None}, True),
    )
    def test_process_view_question_language_not_set(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "It is not possible to translate a question without first assigning a language to it.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_lang": "en", "user_name": "bioversity"}, True),
    )
    def test_process_view_question_from_library(self, mock_get_question_data):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The question is from the ClimMob library. You cannot edit it.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=({"question_lang": "es", "user_name": "test_user"}, True),
    )
    def test_process_view_same_language_translation(self, mock_get_question_data):
        self.valid_data["lang_code"] = "es"
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The question cannot be translated into the same language that has been defined as the main language.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=(
            {"question_lang": "en", "user_name": "test_user", "question_dtype": 10},
            True,
        ),
    )
    def test_process_view_missing_option_wildcard(self, mock_get_question_data):
        self.valid_data["question_perfstmt"] = "Compare with option"
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The parameter question_perfstmt must contain the value: {{option}} in the text.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    def test_process_view_unpermitted_keys(self):
        invalid_data = self.valid_data.copy()
        invalid_data["invalid_key"] = "invalid_value"
        invalid_data["question_desc"] = "Some description"
        self.view.body = json.dumps(invalid_data)
        with patch(
            "climmob.views.Api.questions.getQuestionData",
            return_value=(
                {"question_lang": "en", "user_name": "test_user", "question_dtype": 1},
                True,
            ),
        ):
            response = self.view.processView()
            self.assertEqual(response.status_code, 401)
            self.assertIn(
                "Error in the parameters that you want to add.", response.body.decode()
            )

    def test_process_view_missing_obligatory_keys(self):
        invalid_data = self.valid_data.copy()
        invalid_data["question_desc"] = "Some description"
        del invalid_data["question_name"]
        self.view.body = json.dumps(invalid_data)
        with patch(
            "climmob.views.Api.questions.getQuestionData",
            return_value=(
                {"question_lang": "en", "user_name": "test_user", "question_dtype": 1},
                True,
            ),
        ):
            response = self.view.processView()
            self.assertEqual(response.status_code, 401)
            self.assertIn(
                "It is not complying with the obligatory keys", response.body.decode()
            )

    def test_process_view_empty_parameters(self):
        invalid_data = self.valid_data.copy()
        invalid_data["question_name"] = ""
        invalid_data["question_desc"] = "Some description"
        self.view.body = json.dumps(invalid_data)
        with patch(
            "climmob.views.Api.questions.getQuestionData",
            return_value=(
                {"question_lang": "en", "user_name": "test_user", "question_dtype": 1},
                True,
            ),
        ):
            response = self.view.processView()
            self.assertEqual(response.status_code, 401)
            self.assertIn("Not all parameters have data.", response.body.decode())

    @patch("climmob.views.Api.questions.languageExistInI18nUser", return_value=False)
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=(
            {"question_lang": "en", "user_name": "test_user", "question_dtype": 1},
            True,
        ),
    )
    def test_process_view_language_not_in_user_list(
        self, mock_get_question_data, mock_language_exist
    ):
        self.valid_data["question_desc"] = "Some description"
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The language does not belong to your list of languages to be used.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        mock_language_exist.assert_called_once_with(
            "es", "test_user", self.view.request
        )

    @patch(
        "climmob.views.Api.questions.actionInTheTranslationOfQuestion",
        return_value={"result": "error", "error": "Translation failed"},
    )
    @patch("climmob.views.Api.questions.languageExistInI18nUser", return_value=True)
    @patch(
        "climmob.views.Api.questions.getQuestionData",
        return_value=(
            {"question_lang": "en", "user_name": "test_user", "question_dtype": 1},
            True,
        ),
    )
    def test_process_view_translation_failure(
        self, mock_get_question_data, mock_language_exist, mock_action_translation
    ):
        self.valid_data["question_desc"] = "Some description"
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Translation failed", response.body.decode())
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        mock_language_exist.assert_called_once_with(
            "es", "test_user", self.view.request
        )
        expected_dataworking = self.valid_data.copy()
        mock_action_translation.assert_called_once_with(self.view, expected_dataworking)

    @patch(
        "climmob.views.Api.questions.actionInTheTranslationOfQuestion",
        return_value={"result": "success", "success": "Translation added"},
    )
    @patch("climmob.views.Api.questions.languageExistInI18nUser", return_value=True)
    @patch("climmob.views.Api.questions.getQuestionData")
    @patch("climmob.views.Api.questions.actionInTheTranslationOfQuestionOptions")
    def test_process_view_success(
        self,
        mock_action_translation_options,
        mock_get_question_data,
        mock_language_exist,
        mock_action_translation,
    ):

        mock_get_question_data.return_value = (
            {"question_lang": "en", "user_name": "test_user", "question_dtype": 1},
            True,
        )

        self.valid_data["question_desc"] = "Some description"
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Translation added", response.body.decode())

        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        mock_language_exist.assert_called_once_with(
            "es", "test_user", self.view.request
        )
        expected_dataworking = self.valid_data.copy()
        mock_action_translation.assert_called_once_with(self.view, expected_dataworking)
        mock_action_translation_options.assert_not_called()

    @patch("climmob.views.Api.questions.getQuestionOptions")
    @patch(
        "climmob.views.Api.questions.actionInTheTranslationOfQuestion",
        return_value={"result": "success", "success": "Translation added"},
    )
    @patch("climmob.views.Api.questions.languageExistInI18nUser", return_value=True)
    @patch("climmob.views.Api.questions.getQuestionData")
    @patch("climmob.views.Api.questions.actionInTheTranslationOfQuestionOptions")
    def test_process_view_success_with_options(
        self,
        mock_action_translation_options,
        mock_get_question_data,
        mock_language_exist,
        mock_action_translation,
        mock_get_question_options,
    ):

        mock_get_question_data.return_value = (
            {"question_lang": "en", "user_name": "test_user", "question_dtype": 5},
            True,
        )

        mock_get_question_options.return_value = [
            {"value_code": "OPT1"},
            {"value_code": "OPT2"},
        ]

        self.valid_data["option_OPT1"] = "Opción 1"
        self.valid_data["option_OPT2"] = "Opción 2"
        self.valid_data["question_desc"] = "Some description"
        self.view.body = json.dumps(self.valid_data)

        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Translation added", response.body.decode())

        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        mock_language_exist.assert_called_once_with(
            "es", "test_user", self.view.request
        )
        expected_dataworking = self.valid_data.copy()
        mock_action_translation.assert_called_once_with(self.view, expected_dataworking)

        expected_options = [
            {
                "question_id": "QST123",
                "lang_code": "es",
                "value_code": "OPT1",
                "value_desc": "Opción 1",
            },
            {
                "question_id": "QST123",
                "lang_code": "es",
                "value_code": "OPT2",
                "value_desc": "Opción 2",
            },
        ]
        mock_action_translation_options.assert_called_once_with(
            self.view, expected_options
        )

    @patch("climmob.views.Api.questions.getQuestionOptions")
    @patch("climmob.views.Api.questions.languageExistInI18nUser", return_value=True)
    @patch("climmob.views.Api.questions.getQuestionData")
    def test_process_view_missing_option_translation(
        self, mock_get_question_data, mock_language_exist, mock_get_question_options
    ):

        mock_get_question_data.return_value = (
            {"question_lang": "en", "user_name": "test_user", "question_dtype": 5},
            True,
        )

        mock_get_question_options.return_value = [
            {"value_code": "OPT1"},
            {"value_code": "OPT2"},
        ]

        self.valid_data["option_OPT1"] = "Opción 1"
        self.valid_data["question_desc"] = "Some description"
        self.view.body = json.dumps(self.valid_data)

        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "It is not complying with the obligatory keys", response.body.decode()
        )

        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch("climmob.views.Api.questions.getQuestionOptions")
    @patch("climmob.views.Api.questions.languageExistInI18nUser", return_value=True)
    @patch("climmob.views.Api.questions.getQuestionData")
    def test_process_view_unpermitted_option_keys(
        self, mock_get_question_data, mock_language_exist, mock_get_question_options
    ):

        mock_get_question_data.return_value = (
            {"question_lang": "en", "user_name": "test_user", "question_dtype": 5},
            True,
        )

        mock_get_question_options.return_value = [
            {"value_code": "OPT1"},
            {"value_code": "OPT2"},
        ]

        self.valid_data["option_OPT1"] = "Opción 1"
        self.valid_data["option_OPT2"] = "Opción 2"
        self.valid_data["question_desc"] = "Some description"

        self.valid_data["option_OPT3"] = "Opción 3"

        self.view.body = json.dumps(self.valid_data)

        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the parameters that you want to add.", response.body.decode()
        )

        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

        mock_get_question_options.assert_called_once_with("QST123", self.view.request)

    @patch("climmob.views.Api.questions.getQuestionOptions")
    @patch(
        "climmob.views.Api.questions.actionInTheTranslationOfQuestion",
        return_value={"result": "success", "success": "Translation added"},
    )
    @patch("climmob.views.Api.questions.languageExistInI18nUser", return_value=True)
    @patch("climmob.views.Api.questions.getQuestionData")
    @patch("climmob.views.Api.questions.actionInTheTranslationOfQuestionOptions")
    def test_process_view_empty_option_translation(
        self,
        mock_action_translation_options,
        mock_get_question_data,
        mock_language_exist,
        mock_action_translation,
        mock_get_question_options,
    ):

        mock_get_question_data.return_value = (
            {"question_lang": "en", "user_name": "test_user", "question_dtype": 5},
            True,
        )

        mock_get_question_options.return_value = [
            {"value_code": "OPT1"},
            {"value_code": "OPT2"},
        ]

        self.valid_data["option_OPT1"] = "Opción 1"
        self.valid_data["option_OPT2"] = ""
        self.valid_data["question_desc"] = "Some description"
        self.view.body = json.dumps(self.valid_data)

        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )


class TestReadMultiLanguagesFromQuestionView(BaseViewTestCase):
    view_class = ReadMultiLanguagesFromQuestionView
    request_method = "GET"

    def setUp(self):
        super().setUp()
        self.view.user = MagicMock()
        self.view.user.login = "test_user"
        self.valid_data = {"question_id": "QST123", "user_name": "test_user"}
        self.view.body = json.dumps(self.valid_data)

    def test_process_view_invalid_method(self):

        self.view.request.method = "POST"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    def test_process_view_invalid_json(self):

        self.view.body = "invalid json"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )

    def test_process_view_empty_body(self):

        self.view.body = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )

    def test_process_view_none_body(self):

        self.view.body = None
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )

    def test_process_view_missing_obligatory_keys(self):

        invalid_data = self.valid_data.copy()
        del invalid_data["question_id"]
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch("climmob.views.Api.questions.getQuestionData", return_value=(None, False))
    def test_process_view_question_not_found(self, mock_get_question_data):

        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID.", response.body.decode()
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch("climmob.views.Api.questions.getQuestionData")
    def test_process_view_question_language_not_set(self, mock_get_question_data):

        mock_get_question_data.return_value = (
            {"question_id": "QST123", "question_lang": None, "user_name": "test_user"},
            True,
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "This question does not have a main language configured, so it does not have translations.",
            response.body.decode(),
        )
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )

    @patch("climmob.views.Api.questions.getAllTranslationsOfQuestion")
    @patch("climmob.views.Api.questions.getQuestionData")
    def test_process_view_success(
        self, mock_get_question_data, mock_get_all_translations
    ):

        mock_get_question_data.return_value = (
            {"question_id": "QST123", "question_lang": "en", "user_name": "test_user"},
            True,
        )
        mock_get_all_translations.return_value = [
            {"lang_code": "es", "question_name": "Nombre en español"},
            {"lang_code": "fr", "question_name": "Nom en français"},
        ]
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body.decode())
        self.assertIn("translations", response_data)
        self.assertEqual(len(response_data["translations"]), 2)
        mock_get_question_data.assert_called_once_with(
            "test_user", "QST123", self.view.request
        )
        mock_get_all_translations.assert_called_once_with(
            self.view.request, "test_user", "QST123"
        )


if __name__ == "__main__":
    unittest.main()
