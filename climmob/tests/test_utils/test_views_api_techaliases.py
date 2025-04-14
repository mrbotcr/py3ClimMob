import json
import unittest
from unittest.mock import patch, MagicMock
from climmob.views.Api.techaliases import (
    CreateAliasView,
    ReadAliasView

)

class TestCreateAliasView(unittest.TestCase):
    def setUp(self):
        self.view = CreateAliasView(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)

    def mock_translation(self, message):
        return message

    def test_process_view_no_create_no_post(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_no_create_json_error_other_param(self):
        self.view.body = json.dumps(
            {
                "Other": "fake_name",
                "tech_id": "123",
                "alias_name": "Fake Alias",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_no_create_json_error_less_param(self):
        self.view.body = json.dumps(
            {
                "alias_name": "Fake Alias",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_no_create_no_param(self):
        self.view.body = json.dumps(
            {
                "tech_id": "",
                "alias_name": "Fake Alias",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    def test_process_view_no_create_no_param_2(self):
        self.view.body = json.dumps(
            {
                "tech_id": "123",
                "alias_name": "",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch('climmob.views.Api.techaliases.getTechnologyByUser', return_value=False)
    def test_process_view_no_create_no_user_technology(self, mock_getTechnologyByUser):
        self.view.body = json.dumps(
            {
                "tech_id": "123",
                "alias_name": "Fake Alias",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"You do not have a technology with this ID.")

    @patch('climmob.views.Api.techaliases.findTechalias', return_value=True)
    @patch('climmob.views.Api.techaliases.getTechnologyByUser', return_value=True)
    def test_process_view_no_create_technology_already_exist(self, mock_getTechnologyByUser, mock_findTechalias):
        self.view.body = json.dumps(
            {
                "tech_id": "123",
                "alias_name": "Fake Alias",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"This technology option already exists in the technology.")

    @patch('climmob.views.Api.techaliases.addTechAlias', return_value=(False,"Error at Add"))
    @patch('climmob.views.Api.techaliases.findTechalias', return_value=False)
    @patch('climmob.views.Api.techaliases.getTechnologyByUser', return_value=True)
    def test_process_view_no_create_add_false(self, mock_getTechnologyByUser, mock_findTechalias, addTechAlias):
        self.view.body = json.dumps(
            {
                "tech_id": "123",
                "alias_name": "test_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error at Add")

    @patch('climmob.views.Api.techaliases.addTechAlias', return_value=(True, ''))
    @patch('climmob.views.Api.techaliases.findTechalias', return_value=False)
    @patch('climmob.views.Api.techaliases.getTechnologyByUser', return_value=True)
    def test_process_view_no_create_add_false(self, mock_getTechnologyByUser, mock_findTechalias, mock_addTechAlias):
        self.view.body = json.dumps(
            {
                "tech_id": "123",
                "alias_name": "test_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b'""')
        expected_body = json.loads(self.view.body)
        expected_body.update({
            "user_name": "test_user",
            "alias_id": None
        })
        mock_addTechAlias.assert_called_once_with(expected_body, self.view.request, "API")


class TestReadAliasView(unittest.TestCase):
    def setup(self):
        self.view = ReadAliasView(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)

    def mock_translation(self, message):
        return message





if __name__ == "__main__":
    unittest.main()