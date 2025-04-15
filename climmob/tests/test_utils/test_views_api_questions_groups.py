import json
import unittest
import uuid
from unittest.mock import patch, MagicMock
from climmob.views.Api.questionsGroups import (
    CreateGroupOfQuestionView,
    UpdateGroupOfQuestionView,
    DeleteGroupOfQuestionView,
    ReadGroupsOfQuestionsView
)

class TestCreateGroupOfQuestionView(unittest.TestCase):
    def setUp(self):
        self.view = CreateGroupOfQuestionView(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)

    def mock_translation(self, message):
        return message

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
        self.assertEqual(response.body, b"It is not complying with the obligatory keys.")

    def test_process_view_no_create_no_params(self):
        self.view.body = json.dumps(
            {
                "qstgroups_name": "",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch('climmob.views.Api.questionsGroups.categoryExists', return_value=True)
    def test_process_view_no_create_category_exist(self, mock_categoryExists):
        self.view.body = json.dumps(
            {
                "qstgroups_name": "Categorized Example",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is already a category with this name.")

    @patch('climmob.views.Api.questionsGroups.addCategory', return_value=(False,"Error at add."))
    @patch('climmob.views.Api.questionsGroups.categoryExists', return_value=False)
    def test_process_view_no_create_error_add(self, mock_categoryExists, mock_addCategory):
        self.view.body = json.dumps(
            {
                "qstgroups_name": "Categorized Example",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There was a problem with the creation of the category.")

    @patch('climmob.views.Api.questionsGroups.getCategoryById')
    @patch('climmob.views.Api.questionsGroups.addCategory', return_value=(True, ""))
    @patch('climmob.views.Api.questionsGroups.categoryExists', return_value=False)
    def test_process_view_no_create_error_add(self, mock_categoryExists, mock_addCategory, mock_getCategoryById):
        fake_id = str(uuid.uuid4())[-12:]
        expected_response = {
            "user_name": "test_user",
            "qstgroups_id": fake_id,
            "qstgroups_name": "Categorized Example"
        }
        mock_getCategoryById.return_value = expected_response
        request_payload = {
            "qstgroups_name": "Categorized Example",
            "user_name": ""
        }
        self.view.body = json.dumps(request_payload)
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.body.decode()), expected_response)