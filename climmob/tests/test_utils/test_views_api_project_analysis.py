import unittest
from unittest.mock import patch, MagicMock
import json
from pyramid.response import Response

from climmob.views.Api.project_analysis import (
    readDataOfProjectView_api,
    readVariablesForAnalysisView_api,
    generateAnalysisByApiView_api
)

class TestReadDataOfProjectViewAPI(unittest.TestCase):
    def setUp(self):
        self.view = readDataOfProjectView_api(MagicMock())
        self.view.request.method = "GET"
        self.view.user = MagicMock(login="test_user")
        self.view.body = json.dumps({"project_cod": "123", "user_owner": "owner"})

    def mock_translation(self, message):
        return message

    @patch('climmob.views.Api.project_analysis.getJSONResult', return_value={"data": "some_data"})
    @patch('climmob.views.Api.project_analysis.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.project_analysis.projectExists', return_value=True)
    def test_process_view_success(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getJSONResult):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("some_data", response.body.decode())

    @patch('climmob.views.Api.project_analysis.projectExists', return_value=False)
    def test_process_view_project_not_exist(self, mock_projectExists):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("This project does not exist.", response.body.decode())

    def test_process_view_invalid_json(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch('json.loads', side_effect=json.JSONDecodeError("Expecting value", "", 0))
    def test_process_view_invalid_body(self, mock_json_loads):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = ""

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON, It does not have the 'body' parameter.", response.body.decode())

    def test_process_view_post_method(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.method = "POST"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

class TestReadVariablesForAnalysisViewAPI(unittest.TestCase):
    def setUp(self):
        self.view = readVariablesForAnalysisView_api(MagicMock())
        self.view.request.method = "GET"
        self.view.user = MagicMock(login="test_user")
        self.view.body = json.dumps({"project_cod": "123", "user_owner": "owner"})

    def mock_translation(self, message):
        return message

    @patch('climmob.views.Api.project_analysis.getQuestionsByType', return_value=(["question1", "question2"], ["assessment1"]))
    @patch('climmob.views.Api.project_analysis.getProjectProgress', return_value=({"assessments": [{"ass_status": 1, "asstotal": 10}], "regtotal": 6}, 0))
    @patch('climmob.views.Api.project_analysis.getProjectData', return_value={"project_registration_and_analysis": 1})
    @patch('climmob.views.Api.project_analysis.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.project_analysis.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.project_analysis.projectExists', return_value=True)
    def test_process_view_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_getProjectData,
        mock_getProjectProgress,
        mock_getQuestionsByType,
    ):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertEqual(response_data, {
            "dataForAnalysis": ["question1", "question2"],
            "assessmentsList": ["assessment1"]
        })

        # Verify that all the patched methods were called
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_getProjectData.called)
        self.assertTrue(mock_getProjectProgress.called)
        self.assertTrue(mock_getQuestionsByType.called)

    @patch('climmob.views.Api.project_analysis.projectExists', return_value=False)
    def test_process_view_project_not_exist(self, mock_projectExists):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("This project does not exist.", response.body.decode())
        self.assertTrue(mock_projectExists.called)

    def test_process_view_invalid_json(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch('json.loads', side_effect=json.JSONDecodeError("Expecting value", "", 0))
    def test_process_view_invalid_body(self, mock_json_loads):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = ""

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON, It does not have the 'body' parameter.", response.body.decode())
        self.assertTrue(mock_json_loads.called)

    def test_process_view_post_method(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.method = "POST"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

class TestGenerateAnalysisByApiViewAPI(unittest.TestCase):
    def setUp(self):
        self.view = generateAnalysisByApiView_api(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view.body = json.dumps({
            "project_cod": "123",
            "user_owner": "owner",
            "variables_to_analyze": ["var1", "var2"],
            "infosheets": "1"
        })

    def mock_translation(self, message):
        return message

    @patch('climmob.views.Api.project_analysis.processToGenerateTheReport', return_value=True)
    @patch('climmob.views.Api.project_analysis.getQuestionsByType', return_value=({"key1": [{"codeForAnalysis": "var1"}, {"codeForAnalysis": "var2"}]}, ["assessment1"]))
    @patch('climmob.views.Api.project_analysis.getProjectProgress', return_value=({"assessments": [{"ass_status": 1, "asstotal": 10}], "regtotal": 6}, 0))
    @patch('climmob.views.Api.project_analysis.getProjectData', return_value={"project_registration_and_analysis": 1})
    @patch('climmob.views.Api.project_analysis.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.project_analysis.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.project_analysis.projectExists', return_value=True)
    def test_process_view_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_getProjectData,
        mock_getProjectProgress,
        mock_getQuestionsByType,
        mock_processToGenerateTheReport,
    ):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("The analysis is being generated", response.body.decode())

        # Verify that all the patched methods were called
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_getProjectData.called)
        self.assertTrue(mock_getProjectProgress.called)
        self.assertTrue(mock_getQuestionsByType.called)
        self.assertTrue(mock_processToGenerateTheReport.called)

    @patch('climmob.views.Api.project_analysis.projectExists', return_value=False)
    def test_process_view_project_not_exist(self, mock_projectExists):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("This project does not exist.", response.body.decode())
        self.assertTrue(mock_projectExists.called)

    @patch('climmob.views.Api.project_analysis.getAccessTypeForProject', return_value=4)
    @patch('climmob.views.Api.project_analysis.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.project_analysis.projectExists', return_value=True)
    def test_process_view_no_access(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getAccessTypeForProject):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("The access assigned for this project does not allow you to create an analysis.", response.body.decode())

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)

    @patch('climmob.views.Api.project_analysis.getProjectProgress', return_value=({"assessments": [{"ass_status": 0, "asstotal": 0}], "regtotal": 4}, 0))
    @patch('climmob.views.Api.project_analysis.getProjectData', return_value={"project_registration_and_analysis": 0})
    @patch('climmob.views.Api.project_analysis.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.project_analysis.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.project_analysis.projectExists', return_value=True)
    def test_process_view_not_enough_data(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getAccessTypeForProject, mock_getProjectData, mock_getProjectProgress):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("You don't have the amount of information needed to do a ClimMob analysis.", response.body.decode())

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_getProjectData.called)
        self.assertTrue(mock_getProjectProgress.called)

    def test_process_view_invalid_json(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch('json.loads', side_effect=json.JSONDecodeError("Expecting value", "", 0))
    def test_process_view_invalid_body(self, mock_json_loads):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = ""

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON, It does not have the 'body' parameter.", response.body.decode())
        self.assertTrue(mock_json_loads.called)

    def test_process_view_get_method(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())


if __name__ == "__main__":
    unittest.main()
