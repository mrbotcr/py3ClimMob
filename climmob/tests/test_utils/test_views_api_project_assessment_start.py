import json
import unittest
from unittest.mock import patch, MagicMock
from pyramid.response import Response
from climmob.views.Api.projectAssessmentStart import (
    createProjectAssessment_view,
    cancelAssessmentApi_view,
    closeAssessmentApi_view,
    readAssessmentStructure_view
)
from climmob.tests.test_utils.common import BaseViewTestCase

class TestCreateProjectAssessmentView(BaseViewTestCase):
    view_class = createProjectAssessment_view
    request_method = "POST"
    request_body = json.dumps({
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "ass123"
    })

    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not project with that code.", response.body.decode())
        mock_project_exists.assert_called_with('test_user', 'owner', '123', self.view.request)

    @patch('climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessmentStart.getAccessTypeForProject', return_value=4)
    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=True)
    def test_process_view_no_access(self, mock_project_exists, mock_get_project_id, mock_get_access_type):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("The access assigned for this project does not allow you to do this action.", response.body.decode())
        mock_project_exists.assert_called_with('test_user', 'owner', '123', self.view.request)
        mock_get_project_id.assert_called_with('test_user', 1, self.view.request)
        mock_get_access_type.assert_called_with('owner', '123', self.view.request)

    @patch('climmob.views.Api.projectAssessmentStart.getProjectProgress', return_value=({"regsubmissions": 1, "assessment": False}, False))
    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessmentStart.getAccessTypeForProject', return_value=1)
    def test_process_view_invalid_progress(self, mock_get_access_type, mock_get_project_id, mock_project_exists, mock_get_project_progress):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("You cannot add data collection moments. You alreaday started data collection.", response.body.decode())
        mock_project_exists.assert_called_with('test_user', 'owner', '123', self.view.request)
        mock_get_project_id.assert_called_with('owner', '123', self.view.request)
        mock_get_access_type.assert_called_with('test_user', 1, self.view.request)
        mock_get_project_progress.assert_called_with('owner', '123', 1, self.view.request)

    @patch('climmob.views.Api.projectAssessmentStart.projectAsessmentStatus', return_value=False)
    @patch('climmob.views.Api.projectAssessmentStart.getProjectProgress', return_value=({"regsubmissions": 2, "assessment": True}, True))
    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessmentStart.getAccessTypeForProject', return_value=1)
    def test_process_view_assessment_already_started(self, mock_get_access_type, mock_get_project_id, mock_project_exists, mock_get_project_progress, mock_project_assessment_status):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Data collection has already started.", response.body.decode())
        mock_project_exists.assert_called_with('test_user', 'owner', '123', self.view.request)
        mock_get_project_id.assert_called_with('owner', '123', self.view.request)
        mock_get_access_type.assert_called_with('test_user', 1, self.view.request)
        mock_get_project_progress.assert_called_with('owner', '123', 1, self.view.request)
        mock_project_assessment_status.assert_called_with(1, 'ass123', self.view.request)

    @patch('climmob.views.Api.projectAssessmentStart.checkAssessments', return_value=(False, ["error1", "error2"]))
    @patch('climmob.views.Api.projectAssessmentStart.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessmentStart.getProjectProgress', return_value=({"regsubmissions": 2, "assessment": True}, True))
    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessmentStart.getAccessTypeForProject', return_value=1)
    def test_process_view_check_assessments_failed(self, mock_get_access_type, mock_get_project_id, mock_project_exists, mock_get_project_progress, mock_project_assessment_status, mock_check_assessments):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("errors", response.body.decode())
        mock_project_exists.assert_called_with('test_user', 'owner', '123', self.view.request)
        mock_get_project_id.assert_called_with('owner', '123', self.view.request)
        mock_get_access_type.assert_called_with('test_user', 1, self.view.request)
        mock_get_project_progress.assert_called_with('owner', '123', 1, self.view.request)
        mock_project_assessment_status.assert_called_with(1, 'ass123', self.view.request)
        mock_check_assessments.assert_called_with(1, 'ass123', self.view.request)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch('json.loads', side_effect=json.JSONDecodeError("Expecting value", "", 0))
    def test_process_view_invalid_body(self, mock_json_loads):
        self.view.body = ""

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

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=True)
    def test_process_view_missing_parameters(self, mock_project_exists):
        self.view.body = json.dumps({
            "project_cod": "123",
            "user_owner": "",
            "ass_cod": "ass123"
        })

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())
        mock_project_exists.assert_not_called()

class TestCancelAssessmentApiView(BaseViewTestCase):
    view_class = cancelAssessmentApi_view
    request_method = "POST"
    request_body = json.dumps({
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "ass123"
    })

    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessmentStart.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessmentStart.projectAsessmentStatus', return_value=False)
    @patch('climmob.views.Api.projectAssessmentStart.setAssessmentIndividualStatus', return_value=True)
    def test_process_view_success(self,
                                  mock_set_assessment_status,
                                  mock_project_assessment_status,
                                  mock_get_access_type,
                                  mock_get_project_id,
                                  mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Cancel data collection", response.body.decode())
        mock_project_exists.assert_called_with('test_user', 'owner', '123', self.view.request)
        mock_get_project_id.assert_called_with('owner', '123', self.view.request)
        mock_get_access_type.assert_called_with('test_user', 1, self.view.request)
        mock_project_assessment_status.assert_called_with(1, 'ass123', self.view.request)
        self.assertTrue(mock_set_assessment_status.called)

    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_with('test_user', 'owner', '123', self.view.request)

    @patch('climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessmentStart.getAccessTypeForProject', return_value=4)
    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=True)
    def test_process_view_no_access(self, mock_project_exists, mock_get_project_id, mock_get_access_type):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("The access assigned for this project does not allow you to cancel the assessment.", response.body.decode())
        mock_project_exists.assert_called_with('test_user', 'owner', '123', self.view.request)
        mock_get_project_id.assert_called_with('test_user', 1, self.view.request)
        mock_get_access_type.assert_called_with('owner', '123', self.view.request)

    @patch('climmob.views.Api.projectAssessmentStart.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessmentStart.getAccessTypeForProject', return_value=1)
    def test_process_view_assessment_already_started(self, mock_get_access_type, mock_get_project_id, mock_project_exists, mock_project_assessment_status):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Data collection has not started. You cannot cancel it.", response.body.decode())
        mock_project_exists.assert_called_with('test_user', 'owner', '123', self.view.request)
        mock_get_project_id.assert_called_with('owner', '123', self.view.request)
        mock_get_access_type.assert_called_with('test_user', 1, self.view.request)
        mock_project_assessment_status.assert_called_with(1, 'ass123', self.view.request)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=True)
    def test_process_view_missing_parameters(self, mock_project_exists):
        self.view.body = json.dumps({
            "project_cod": "123",
            "user_owner": "",
            "ass_cod": "ass123"
        })

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())
        mock_project_exists.assert_not_called()

class TestCloseAssessmentApiView(BaseViewTestCase):
    view_class = closeAssessmentApi_view
    request_method = "POST"
    request_body = json.dumps({
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "ass123"
    })

    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessmentStart.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessmentStart.projectAsessmentStatus', return_value=False)
    @patch('climmob.views.Api.projectAssessmentStart.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessmentStart.setAssessmentIndividualStatus', return_value=True)
    def test_process_view_success(self,
                                  mock_set_assessment_status,
                                  mock_assessment_exists,
                                  mock_project_assessment_status,
                                  mock_get_access_type,
                                  mock_get_project_id,
                                  mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Data collection closed.", response.body.decode())
        mock_project_exists.assert_called_with('test_user', 'owner', '123', self.view.request)
        mock_get_project_id.assert_called_with('owner', '123', self.view.request)
        mock_get_access_type.assert_called_with('test_user', 1, self.view.request)
        mock_project_assessment_status.assert_called_with(1, 'ass123', self.view.request)
        mock_assessment_exists.assert_called_with(1, 'ass123', self.view.request)
        self.assertTrue(mock_set_assessment_status.called)

    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_with('test_user', 'owner', '123', self.view.request)

    @patch('climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessmentStart.getAccessTypeForProject', return_value=4)
    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=True)
    def test_process_view_no_access(self, mock_project_exists, mock_get_project_id, mock_get_access_type):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("The access assigned for this project does not allow you to cancel the assessment.", response.body.decode())
        mock_project_exists.assert_called_with('test_user', 'owner', '123', self.view.request)
        mock_get_project_id.assert_called_with('test_user', 1, self.view.request)
        mock_get_access_type.assert_called_with('owner', '123', self.view.request)

    @patch('climmob.views.Api.projectAssessmentStart.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessmentStart.getAccessTypeForProject', return_value=1)
    def test_process_view_assessment_already_started(self, mock_get_access_type, mock_get_project_id, mock_project_exists, mock_project_assessment_status):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Data collection has not started. You cannot cancel it.", response.body.decode())
        mock_project_exists.assert_called_with('test_user', 'owner', '123', self.view.request)
        mock_get_project_id.assert_called_with('owner', '123', self.view.request)
        mock_get_access_type.assert_called_with('test_user', 1, self.view.request)
        mock_project_assessment_status.assert_called_with(1, 'ass123', self.view.request)

    @patch('climmob.views.Api.projectAssessmentStart.assessmentExists', return_value=False)
    @patch('climmob.views.Api.projectAssessmentStart.projectAsessmentStatus', return_value=False)
    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessmentStart.getAccessTypeForProject', return_value=1)
    def test_process_view_assessment_not_exist(self, mock_get_access_type, mock_get_project_id, mock_project_exists, mock_project_assessment_status, mock_assessment_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no data collection with that code.", response.body.decode())
        mock_project_exists.assert_called_with('test_user', 'owner', '123', self.view.request)
        mock_get_project_id.assert_called_with('owner', '123', self.view.request)
        mock_get_access_type.assert_called_with('test_user', 1, self.view.request)
        mock_project_assessment_status.assert_called_with(1, 'ass123', self.view.request)
        mock_assessment_exists.assert_called_with(1, 'ass123', self.view.request)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=True)
    def test_process_view_missing_parameters(self, mock_project_exists):
        self.view.body = json.dumps({
            "project_cod": "123",
            "user_owner": "",
            "ass_cod": "ass123"
        })

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())
        mock_project_exists.assert_not_called()

class TestReadAssessmentStructureView(BaseViewTestCase):
    view_class = readAssessmentStructure_view
    request_method = "GET"
    request_body = json.dumps({
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "ass123"
    })

    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessmentStart.projectAsessmentStatus', return_value=False)
    @patch('climmob.views.Api.projectAssessmentStart.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessmentStart.generateStructureForInterfaceForms', return_value={"structure": "data"})
    def test_process_view_success(self,
                                  mock_generate_structure,
                                  mock_assessment_exists,
                                  mock_project_assessment_status,
                                  mock_get_project_id,
                                  mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("structure", json.loads(response.body))
        mock_project_exists.assert_called_with('test_user', 'owner', '123', self.view.request)
        mock_get_project_id.assert_called_with('owner', '123', self.view.request)
        mock_project_assessment_status.assert_called_with(1, 'ass123', self.view.request)
        mock_assessment_exists.assert_called_with(1, 'ass123', self.view.request)
        self.assertTrue(mock_generate_structure.called)

    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_with('test_user', 'owner', '123', self.view.request)

    @patch('climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessmentStart.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=True)
    def test_process_view_assessment_not_started(self, mock_project_exists, mock_get_project_id, mock_project_assessment_status):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Data collection has not started.", response.body.decode())
        mock_project_exists.assert_called_with('test_user', 'owner', '123', self.view.request)
        mock_get_project_id.assert_called_with(1, 'ass123', self.view.request)
        mock_project_assessment_status.assert_called_with('owner', '123', self.view.request)

    @patch('climmob.views.Api.projectAssessmentStart.assessmentExists', return_value=False)
    @patch('climmob.views.Api.projectAssessmentStart.projectAsessmentStatus', return_value=False)
    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner', return_value=1)
    def test_process_view_assessment_not_exist(self, mock_get_project_id, mock_project_exists, mock_project_assessment_status, mock_assessment_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no data collection with that code.", response.body.decode())
        mock_project_exists.assert_called_with('test_user', 'owner', '123', self.view.request)
        mock_get_project_id.assert_called_with('owner', '123', self.view.request)
        mock_project_assessment_status.assert_called_with(1, 'ass123', self.view.request)
        mock_assessment_exists.assert_called_with(1, 'ass123', self.view.request)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON", response.body.decode())

    def test_process_view_invalid_method(self):
        self.view.request.method = "POST"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    @patch('climmob.views.Api.projectAssessmentStart.projectExists', return_value=True)
    def test_process_view_missing_parameters(self, mock_project_exists):
        self.view.body = json.dumps({
            "project_cod": "123",
            "user_owner": "",
            "ass_cod": "ass123"
        })

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())
        mock_project_exists.assert_not_called()


if __name__ == "__main__":
    unittest.main()
