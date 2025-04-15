import json
import unittest
import uuid
from unittest.mock import patch, MagicMock
from climmob.views.Api.questionsGroups import (
    CreateGroupOfQuestionView,
    UpdateGroupOfQuestionView,
    DeleteGroupOfQuestionView,
    ReadGroupsOfQuestionsView,
)


class TestCreateGroupOfQuestionView(unittest.TestCase):
    def setUp(self):
        self.view = CreateGroupOfQuestionView(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)

    def test_process_view_no_create_no_post(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts POST method.")

    def test_process_view_no_create_json_error(self):
        self.view.body = json.dumps(
            {
                "other_cathegory": "Uncategorized",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"It is not complying with the obligatory keys."
        )

    def test_process_view_no_create_no_params(self):
        self.view.body = json.dumps(
            {
                "qstgroups_name": "",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch("climmob.views.Api.questionsGroups.categoryExists", return_value=True)
    def test_process_view_no_create_category_exist(self, mock_categoryExists):
        self.view.body = json.dumps(
            {
                "qstgroups_name": "Categorized Example",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is already a category with this name.")

    @patch(
        "climmob.views.Api.questionsGroups.addCategory",
        return_value=(False, "Error at add."),
    )
    @patch("climmob.views.Api.questionsGroups.categoryExists", return_value=False)
    def test_process_view_no_create_error_add(
        self, mock_categoryExists, mock_addCategory
    ):
        self.view.body = json.dumps(
            {
                "qstgroups_name": "Categorized Example",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"There was a problem with the creation of the category."
        )

    @patch("climmob.views.Api.questionsGroups.getCategoryById")
    @patch("climmob.views.Api.questionsGroups.addCategory", return_value=(True, ""))
    @patch("climmob.views.Api.questionsGroups.categoryExists", return_value=False)
    def test_process_view_create_add_true(
        self, mock_categoryExists, mock_addCategory, mock_getCategoryById
    ):
        fake_id = str(uuid.uuid4())[-12:]
        expected_response = {
            "user_name": "test_user",
            "qstgroups_id": fake_id,
            "qstgroups_name": "Categorized Example",
        }
        mock_getCategoryById.return_value = expected_response
        request_payload = {"qstgroups_name": "Categorized Example", "user_name": ""}
        self.view.body = json.dumps(request_payload)
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.body.decode()), expected_response)
        mock_addCategory.assert_called_once()


class TestUpdateGroupOfQuestionView(unittest.TestCase):
    def setUp(self):
        self.view = UpdateGroupOfQuestionView(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)

    def test_process_view_no_update_no_post(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts POST method.")

    def test_process_view_no_update_json_error(self):
        fake_id = str(uuid.uuid4())[-12:]
        self.view.body = json.dumps(
            {
                "qstgroups_id": fake_id,
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"It is not complying with the obligatory keys."
        )

    def test_process_view_no_update_no_params(self):
        fake_id = str(uuid.uuid4())[-12:]
        self.view.body = json.dumps(
            {
                "qstgroups_name": "",
                "qstgroups_id": fake_id,
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    def test_process_view_no_update_no_params_2(self):
        self.view.body = json.dumps(
            {
                "qstgroups_name": "Categorized Example",
                "qstgroups_id": "",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch(
        "climmob.views.Api.questionsGroups.categoryExistsByUserAndId",
        return_value=False,
    )
    def test_process_view_no_update_category_no_belong(
        self, mock_categoryExistsByUserAndId
    ):
        fake_id = str(uuid.uuid4())[-12:]
        self.view.body = json.dumps(
            {
                "qstgroups_name": "Categorized Example",
                "qstgroups_id": fake_id,
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"You cannot edit this category because it does not belong to your personal library.",
        )

    @patch(
        "climmob.views.Api.questionsGroups.categoryExistsWithDifferentId",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.questionsGroups.categoryExistsByUserAndId", return_value=True
    )
    def test_process_view_no_update_category_already_exist(
        self, mock_categoryExistsByUserAndId, mock_categoryExistsWithDifferentId
    ):
        fake_id = str(uuid.uuid4())[-12:]
        self.view.body = json.dumps(
            {
                "qstgroups_name": "Categorized Example",
                "qstgroups_id": fake_id,
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is already a category with this name.")

    @patch(
        "climmob.views.Api.questionsGroups.updateCategory",
        return_value=(False, "Error at editing category."),
    )
    @patch(
        "climmob.views.Api.questionsGroups.categoryExistsWithDifferentId",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.questionsGroups.categoryExistsByUserAndId", return_value=True
    )
    def test_process_view_no_update_edit_error(
        self,
        mock_categoryExistsByUserAndId,
        mock_categoryExistsWithDifferentId,
        mock_updateCategory,
    ):
        fake_id = str(uuid.uuid4())[-12:]
        self.view.body = json.dumps(
            {
                "qstgroups_name": "Categorized Example",
                "qstgroups_id": fake_id,
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There was a problem updating the category.")

    @patch("climmob.views.Api.questionsGroups.getCategoryById")
    @patch("climmob.views.Api.questionsGroups.updateCategory", return_value=(True, ""))
    @patch(
        "climmob.views.Api.questionsGroups.categoryExistsWithDifferentId",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.questionsGroups.categoryExistsByUserAndId", return_value=True
    )
    def test_process_view_update_true(
        self,
        mock_categoryExistsByUserAndId,
        mock_categoryExistsWithDifferentId,
        mock_updateCategory,
        mock_getCategoryById,
    ):

        fake_id = str(uuid.uuid4())[-12:]
        expected_response = {
            "user_name": "test_user",
            "qstgroups_id": fake_id,
            "qstgroups_name": "Categorized Example",
        }
        mock_getCategoryById.return_value = expected_response
        self.view.body = json.dumps(
            {
                "qstgroups_name": "Categorized Example",
                "qstgroups_id": fake_id,
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.body.decode()), expected_response)


class TestDeleteGroupOfQuestionView(unittest.TestCase):
    def setUp(self):
        self.view = DeleteGroupOfQuestionView(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)

    def test_process_view_no_delete_no_post(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts POST method.")

    def test_process_view_no_delete_json_error(self):
        self.view.body = json.dumps({})
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"It is not complying with the obligatory keys."
        )

    def test_process_view_no_delete_no_params(self):
        self.view.body = json.dumps(
            {
                "qstgroups_id": "",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch(
        "climmob.views.Api.questionsGroups.categoryExistsByUserAndId",
        return_value=False,
    )
    def test_process_view_no_delete_no_belong(self, mock_categoryExistsByUserAndId):
        fake_id = str(uuid.uuid4())[-12:]
        self.view.body = json.dumps(
            {
                "qstgroups_id": fake_id,
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"You cannot delete this category because it does not belong to your personal library.",
        )

    @patch(
        "climmob.views.Api.questionsGroups.theCategoryHaveQuestions", return_value=True
    )
    @patch(
        "climmob.views.Api.questionsGroups.categoryExistsByUserAndId", return_value=True
    )
    def test_process_view_no_delete_have_questions(
        self, mock_categoryExistsByUserAndId, mock_theCategoryHaveQuestions
    ):
        fake_id = str(uuid.uuid4())[-12:]
        self.view.body = json.dumps(
            {
                "qstgroups_id": fake_id,
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"This category cannot be removed because it has questions."
        )

    @patch(
        "climmob.views.Api.questionsGroups.deleteCategory",
        return_value=(False, "Error to delete"),
    )
    @patch(
        "climmob.views.Api.questionsGroups.theCategoryHaveQuestions", return_value=False
    )
    @patch(
        "climmob.views.Api.questionsGroups.categoryExistsByUserAndId", return_value=True
    )
    def test_process_view_no_delete_delete_error(
        self,
        mock_categoryExistsByUserAndId,
        mock_theCategoryHaveQuestions,
        mock_deleteCategory,
    ):
        fake_id = str(uuid.uuid4())[-12:]
        self.view.body = json.dumps(
            {
                "qstgroups_id": fake_id,
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There was a problem removing the category.")

    @patch("climmob.views.Api.questionsGroups.deleteCategory", return_value=(True, ""))
    @patch(
        "climmob.views.Api.questionsGroups.theCategoryHaveQuestions", return_value=False
    )
    @patch(
        "climmob.views.Api.questionsGroups.categoryExistsByUserAndId", return_value=True
    )
    def test_process_view_delete_true(
        self,
        mock_categoryExistsByUserAndId,
        mock_theCategoryHaveQuestions,
        mock_deleteCategory,
    ):
        fake_id = str(uuid.uuid4())[-12:]
        self.view.body = json.dumps(
            {
                "qstgroups_id": fake_id,
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"The category was removed.")
        mock_deleteCategory.assert_called_once()


class TestReadGroupsOfQuestionsView(unittest.TestCase):
    def setUp(self):
        self.view = ReadGroupsOfQuestionsView(MagicMock())
        self.view.request.method = "GET"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)

    def test_process_view_no_read_no_get(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts GET method.")

    @patch("climmob.views.Api.questionsGroups.getCategoriesParents")
    def test_process_view_no_read_no_params(self, mock_getCategoriesParents):
        self.view.request.method = "GET"
        expected_db_response = [
            ("test_user", "4581ab3c093d", "Grupo de preguntas", 12),
            ("bioversity", "9a7e1c0d8e42", "Grupo en español", 5),
        ]
        mock_getCategoriesParents.return_value = expected_db_response
        expected_response = [
            {
                "user_name": "test_user",
                "qstgroups_id": "4581ab3c093d",
                "qstgroups_name": "Grupo de preguntas",
                "numberOfQuestions": 12,
            },
            {
                "user_name": "bioversity",
                "qstgroups_id": "9a7e1c0d8e42",
                "qstgroups_name": "Grupo en español",
                "numberOfQuestions": 5,
            },
        ]

        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.body.decode()), expected_response)
        mock_getCategoriesParents.assert_called_once()
