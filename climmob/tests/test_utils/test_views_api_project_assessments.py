import json
import unittest
from unittest.mock import patch, MagicMock

from pyramid.response import Response
from climmob.views.Api.projectAssessments import (
    readProjectAssessments_view,
    addNewAssessment_view
)

# Clase base para las pruebas de los views
class BaseViewTestCase(unittest.TestCase):
    view_class = None
    request_method = None
    request_body = None
    user_login = "test_user"

    def setUp(self):
        self.view = self.view_class(MagicMock())
        self.view.request.method = self.request_method
        self.view.user = MagicMock(login=self.user_login)
        self.view.body = self.request_body
        self.view._ = self.mock_translation  # Mock translation function

    def mock_translation(self, message):
        return message

# Clase de prueba específica para readProjectAssessments_view
class TestReadProjectAssessmentsView(BaseViewTestCase):
    view_class = readProjectAssessments_view
    request_method = "GET"
    request_body = json.dumps({"project_cod": "123", "user_owner": "owner"})

    @patch('climmob.views.Api.projectAssessments.getProjectAssessments', return_value=[{"assessment": "data"}])
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_success(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getProjectAssessments):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertEqual(response_data, [{"assessment": "data"}])

        # Verify that all the patched methods were called
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getProjectAssessments.called)

    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=False)
    def test_process_view_project_not_exist(self, mock_projectExists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no a project with that code.", response.body.decode())
        self.assertTrue(mock_projectExists.called)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch('json.loads', side_effect=json.JSONDecodeError("Expecting value", "", 0))
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    def test_process_view_invalid_body(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getAccessTypeForProject, mock_json_loads):
        self.view.body = ""  # Simulamos un cuerpo de JSON inválido

        response = None
        try:
            response = self.view.processView()
        except json.JSONDecodeError:
            response = Response(
                status=401,
                body=self.view._("Error in the JSON, It does not have the 'body' parameter.")
            )

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON, It does not have the 'body' parameter.", response.body.decode())

        self.assertTrue(mock_json_loads.called)
        self.assertFalse(mock_projectExists.called)
        self.assertFalse(mock_getTheProjectIdForOwner.called)
        self.assertFalse(mock_getAccessTypeForProject.called)

    def test_process_view_post_method(self):
        self.view.request.method = "POST"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

# Clase de prueba específica para addNewAssessment_view
class TestAddNewAssessmentView(BaseViewTestCase):
    view_class = addNewAssessment_view
    request_method = "POST"
    request_body = json.dumps({
        "project_cod": "123",
        "user_owner": "owner",
        "ass_desc": "Description",
        "ass_days": "10",
        "ass_final": "Yes"
    })

    @patch('climmob.views.Api.projectAssessments.addProjectAssessment', return_value=(True, "Assessment added successfully"))
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_addProjectAssessment
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Assessment added successfully", response.body.decode())

        # Verify that all the patched methods were called
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_addProjectAssessment.called)

    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=False)
    def test_process_view_project_not_exist(self, mock_projectExists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        self.assertTrue(mock_projectExists.called)

    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=4)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_no_access(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getAccessTypeForProject):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("The access assigned for this project does not allow you to add assessments.", response.body.decode())

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch('json.loads', side_effect=json.JSONDecodeError("Expecting value", "", 0))
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    def test_process_view_invalid_body(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getAccessTypeForProject, mock_json_loads):
        self.view.body = ""  # Simulamos un cuerpo de JSON inválido

        response = None
        try:
            response = self.view.processView()
        except json.JSONDecodeError:
            response = Response(
                status=401,
                body=self.view._("Error in the JSON, It does not have the 'body' parameter.")
            )

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON, It does not have the 'body' parameter.", response.body.decode())

        self.assertTrue(mock_json_loads.called)
        self.assertFalse(mock_projectExists.called)
        self.assertFalse(mock_getTheProjectIdForOwner.called)
        self.assertFalse(mock_getAccessTypeForProject.called)

    def test_process_view_post_method(self):
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    def test_process_view_not_all_parameters(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getAccessTypeForProject):
        self.view.body = json.dumps({
            "project_cod": "123",
            "user_owner": "owner",
            "ass_desc": "",
            "ass_days": "10",
            "ass_final": "Yes"
        })

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    def test_process_view_ass_days_not_number(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getAccessTypeForProject):
        self.view.body = json.dumps({
            "project_cod": "123",
            "user_owner": "owner",
            "ass_desc": "Description",
            "ass_days": "ten",
            "ass_final": "Yes"
        })

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("The parameter ass_days must be a number.", response.body.decode())

    @patch('climmob.views.Api.projectAssessments.addProjectAssessment', return_value=(False, "Error adding assessment"))
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_add_assessment_failed(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_addProjectAssessment
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error adding assessment", response.body.decode())

        # Verify that all the patched methods were called
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_addProjectAssessment.called)


if __name__ == "__main__":
    unittest.main()
