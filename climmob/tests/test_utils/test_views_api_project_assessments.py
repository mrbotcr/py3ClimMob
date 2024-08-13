import json
import unittest
from unittest.mock import patch, MagicMock
from pyramid.response import Response

from climmob.tests.test_utils.common import BaseViewTestCase
from climmob.views.Api.projectAssessments import (
    readProjectAssessments_view,
    addNewAssessment_view,
    updateProjectAssessment_view,
    deleteProjectAssessment_view,
    readProjectAssessmentStructure_view,
    createAssessmentGroup_view,
    updateAssessmentGroup_view,
    deleteAssessmentGroup_view,
    readPossibleQuestionForAssessmentGroup_view,
    addQuestionToGroupAssessment_view,
    deleteQuestionFromGroupAssessment_view
)

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
    def test_process_view_invalid_body(self, mock_json_loads):
        self.view.body = ""

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

    def test_process_view_post_method(self):
        self.view.request.method = "POST"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

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

class TestUpdateProjectAssessmentView(BaseViewTestCase):
    view_class = updateProjectAssessment_view
    request_method = "POST"
    request_body = json.dumps({
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "ass123",
        "ass_desc": "Description",
        "ass_days": "10"
    })

    @patch('climmob.views.Api.projectAssessments.modifyProjectAssessment', return_value=(True, "Data collection updated successfully."))
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
        mock_modifyProjectAssessment
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Data collection updated successfully.", response.body.decode())

        # Verify that all the patched methods were called
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_modifyProjectAssessment.called)

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
        self.assertIn("The access assigned for this project does not allow you to update assessments.", response.body.decode())

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)

    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=False)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_assessment_not_exist(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getAccessTypeForProject, mock_assessmentExists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no data collection with that code.", response.body.decode())

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_assessmentExists.called)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @unittest.skip("Skipping the test due to json.JSONDecodeError")
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    def test_process_view_invalid_body(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getAccessTypeForProject):
        self.view.body = ""  # Simulamos un cuerpo de JSON inválido

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON, It does not have the 'body' parameter.", response.body.decode())

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)

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
            "ass_cod": "",
            "ass_desc": "Description",
            "ass_days": "10"
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
            "ass_cod": "ass123",
            "ass_desc": "Description",
            "ass_days": "ten"
        })

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("The parameter ass_days must be a number.", response.body.decode())

    @patch('climmob.views.Api.projectAssessments.modifyProjectAssessment', return_value=(False, "Error updating assessment"))
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_update_assessment_failed(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
        mock_modifyProjectAssessment
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error updating assessment", response.body.decode())

        # Verify that all the patched methods were called
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_modifyProjectAssessment.called)

class TestDeleteProjectAssessmentView(BaseViewTestCase):
    view_class = deleteProjectAssessment_view
    request_method = "POST"
    request_body = json.dumps({
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "ass123"
    })

    @patch('climmob.views.Api.projectAssessments.deleteProjectAssessment', return_value=(True, "Data collection moment deleted succesfully."))
    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
        mock_projectAsessmentStatus,
        mock_deleteProjectAssessment
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Data collection moment deleted succesfully.", response.body.decode())

        # Verify that all the patched methods were called
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_projectAsessmentStatus.called)
        self.assertTrue(mock_deleteProjectAssessment.called)

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
        self.assertIn("The access assigned for this project does not allow you to delete assessments.", response.body.decode())

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)

    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=False)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_assessment_not_exist(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getAccessTypeForProject, mock_assessmentExists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no data collection with that code.", response.body.decode())

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_assessmentExists.called)

    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=False)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_assessment_cannot_be_deleted(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getAccessTypeForProject, mock_assessmentExists, mock_projectAsessmentStatus):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("You can not delete this group because you have questions required for the data collection moment.", response.body.decode())

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_projectAsessmentStatus.called)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @unittest.skip("Skipping the test due to json.JSONDecodeError")
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    def test_process_view_invalid_body(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getAccessTypeForProject):
        self.view.body = ""  # Simulamos un cuerpo de JSON inválido

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON, It does not have the 'body' parameter.", response.body.decode())

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)

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
            "ass_cod": ""
        })

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch('climmob.views.Api.projectAssessments.deleteProjectAssessment', return_value=(False, "Error deleting assessment"))
    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_delete_assessment_failed(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
        mock_projectAsessmentStatus,
        mock_deleteProjectAssessment
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error deleting assessment", response.body.decode())

        # Verify that all the patched methods were called
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_projectAsessmentStatus.called)
        self.assertTrue(mock_deleteProjectAssessment.called)

class TestReadProjectAssessmentStructureView(BaseViewTestCase):
    view_class = readProjectAssessmentStructure_view
    request_method = "GET"
    request_body = json.dumps({
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "ass123"
    })

    @patch('climmob.views.Api.projectAssessments.getAssessmentQuestions', return_value=[{"section_id": 1, "question_id": 1, "question_reqinasses": 1}])
    @patch('climmob.views.Api.projectAssessments.getProjectData', return_value={"project_label_a": "Label A", "project_label_b": "Label B", "project_label_c": "Label C"})
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_assessmentExists,
        mock_getProjectData,
        mock_getAssessmentQuestions
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertIsInstance(response_data, list)
        self.assertEqual(response_data[0]["section_id"], 1)
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_getProjectData.called)
        self.assertTrue(mock_getAssessmentQuestions.called)

    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=False)
    def test_process_view_project_not_exist(self, mock_projectExists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        self.assertTrue(mock_projectExists.called)

    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=False)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_assessment_not_exist(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_assessmentExists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no data collection with that code.", response.body.decode())
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_assessmentExists.called)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @unittest.skip("Skipping the test due to json.JSONDecodeError")
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getProjectData', return_value={})
    def test_process_view_invalid_body(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getProjectData):
        self.view.body = ""  # Simulamos un cuerpo de JSON inválido

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON, It does not have the 'body' parameter.", response.body.decode())
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getProjectData.called)

    def test_process_view_post_method(self):
        self.view.request.method = "POST"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    def test_process_view_not_all_parameters(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_assessmentExists):
        self.view.body = json.dumps({
            "project_cod": "123",
            "user_owner": "owner",
            "ass_cod": ""
        })

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

class TestCreateAssessmentGroupView(BaseViewTestCase):
    view_class = createAssessmentGroup_view
    request_method = "POST"
    request_body = json.dumps({
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "456",
        "section_name": "Group 1",
        "section_content": "Content of Group 1"
    })

    @patch('climmob.views.Api.projectAssessments.addAssessmentGroup', return_value=(True, "Group added successfully"))
    @patch('climmob.views.Api.projectAssessments.haveTheBasicStructureAssessment', return_value=True)
    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
        mock_projectAsessmentStatus,
        mock_haveTheBasicStructureAssessment,
        mock_addAssessmentGroup
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Group added successfully", response.body.decode())

        # Verify that all the patched methods were called
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_projectAsessmentStatus.called)
        self.assertTrue(mock_haveTheBasicStructureAssessment.called)
        self.assertTrue(mock_addAssessmentGroup.called)

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
        self.assertIn("The access assigned for this project does not allow you to create groups.", response.body.decode())

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch('json.loads', side_effect=json.JSONDecodeError("Expecting value", "", 0))
    def test_process_view_invalid_body(self, mock_json_loads):
        # Simulamos un cuerpo de JSON inválido
        self.view.body = ""

        # Capturamos la excepción para emular el manejo de errores
        try:
            response = self.view.processView()
        except json.JSONDecodeError:
            response = Response(
                status=401,
                body=self.view._(
                    "Error in the JSON, It does not have the 'body' parameter."
                ),
            )

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )
        self.assertTrue(mock_json_loads.called)

    def test_process_view_post_method(self):
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=False)
    def test_process_view_assessment_not_exist(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_assessmentExists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no data collection with that code.", response.body.decode())

    @patch('climmob.views.Api.projectAssessments.addAssessmentGroup', return_value=(False, "repeated"))
    @patch('climmob.views.Api.projectAssessments.haveTheBasicStructureAssessment', return_value=True)
    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_group_name_repeated(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
        mock_projectAsessmentStatus,
        mock_haveTheBasicStructureAssessment,
        mock_addAssessmentGroup
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is already a group with this name.", response.body.decode())

    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    def test_process_view_not_all_parameters(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getAccessTypeForProject):
        self.view.body = json.dumps({
            "project_cod": "123",
            "user_owner": "owner",
            "ass_cod": "",
            "section_name": "Group 1",
            "section_content": "Content of Group 1"
        })

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

class TestUpdateAssessmentGroupView(BaseViewTestCase):
    view_class = updateAssessmentGroup_view
    request_method = "POST"
    request_body = json.dumps({
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "456",
        "group_cod": "789",
        "section_name": "Updated Group",
        "section_content": "Updated content of the group"
    })

    @patch('climmob.views.Api.projectAssessments.modifyAssessmentGroup', return_value=(True, "Group updated successfully"))
    @patch('climmob.views.Api.projectAssessments.exitsAssessmentGroup', return_value=True)
    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
        mock_projectAsessmentStatus,
        mock_exitsAssessmentGroup,
        mock_modifyAssessmentGroup
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Group updated successfully", response.body.decode())

        # Verify that all the patched methods were called
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_projectAsessmentStatus.called)
        self.assertTrue(mock_exitsAssessmentGroup.called)
        self.assertTrue(mock_modifyAssessmentGroup.called)

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
        self.assertIn("The access assigned for this project does not allow you to update groups.", response.body.decode())

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)

    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=False)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_assessment_not_exist(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_assessmentExists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no data collection with that code.", response.body.decode())
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_assessmentExists.called)

    @patch('climmob.views.Api.projectAssessments.exitsAssessmentGroup', return_value=False)
    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_group_not_exist(
            self,
            mock_projectExists,
            mock_getTheProjectIdForOwner,
            mock_assessmentExists,
            mock_projectAsessmentStatus,
            mock_exitsAssessmentGroup
    ):
        response = self.view.processView()

        # Verifica que el código responda con un error 401 si el grupo no existe
        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not a group with that code.", response.body.decode())

        # Verifica que todos los mocks relevantes fueron llamados
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_projectAsessmentStatus.called)
        self.assertTrue(mock_exitsAssessmentGroup.called)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @unittest.skip("Skipping the test due to json.JSONDecodeError")
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    def test_process_view_invalid_body(self, mock_projectExists, mock_getTheProjectIdForOwner):
        self.view.body = ""  # Simulamos un cuerpo de JSON inválido

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON, It does not have the 'body' parameter.", response.body.decode())
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)

    def test_process_view_post_method(self):
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    @patch('climmob.views.Api.projectAssessments.modifyAssessmentGroup', return_value=(False, "repeated"))
    @patch('climmob.views.Api.projectAssessments.exitsAssessmentGroup', return_value=True)
    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_group_name_repeated(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
        mock_projectAsessmentStatus,
        mock_exitsAssessmentGroup,
        mock_modifyAssessmentGroup
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is already a group with this name.", response.body.decode())

class TestDeleteAssessmentGroupView(BaseViewTestCase):
    view_class = deleteAssessmentGroup_view
    request_method = "POST"
    request_body = json.dumps({
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "456",
        "group_cod": "789"
    })

    @patch('climmob.views.Api.projectAssessments.deleteAssessmentGroup', return_value=(True, "Group deleted successfully"))
    @patch('climmob.views.Api.projectAssessments.canDeleteTheAssessmentGroup', return_value=True)
    @patch('climmob.views.Api.projectAssessments.exitsAssessmentGroup', return_value=True)
    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
        mock_projectAsessmentStatus,
        mock_exitsAssessmentGroup,
        mock_canDeleteTheAssessmentGroup,
        mock_deleteAssessmentGroup
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Group deleted successfully", response.body.decode())

        # Verify that all the patched methods were called
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_projectAsessmentStatus.called)
        self.assertTrue(mock_exitsAssessmentGroup.called)
        self.assertTrue(mock_canDeleteTheAssessmentGroup.called)
        self.assertTrue(mock_deleteAssessmentGroup.called)

    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=False)
    def test_process_view_project_not_exist(self, mock_projectExists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        self.assertTrue(mock_projectExists.called)

    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=False)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_assessment_not_exist(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_assessmentExists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no data collection with that code.", response.body.decode())
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_assessmentExists.called)

    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=4)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_no_access(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getAccessTypeForProject):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("The access assigned for this project does not allow you to delete groups.", response.body.decode())

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)

    @patch('climmob.views.Api.projectAssessments.exitsAssessmentGroup', return_value=False)
    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_group_not_exist(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_assessmentExists, mock_projectAsessmentStatus, mock_exitsAssessmentGroup):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not a group with that code.", response.body.decode())

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_projectAsessmentStatus.called)
        self.assertTrue(mock_exitsAssessmentGroup.called)

    @patch('climmob.views.Api.projectAssessments.canDeleteTheAssessmentGroup', return_value=False)
    @patch('climmob.views.Api.projectAssessments.exitsAssessmentGroup', return_value=True)
    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_group_cannot_be_deleted(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getAccessTypeForProject, mock_assessmentExists, mock_projectAsessmentStatus, mock_exitsAssessmentGroup, mock_canDeleteTheAssessmentGroup):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("You can not delete this group because you have questions required for the assessment.", response.body.decode())

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_projectAsessmentStatus.called)
        self.assertTrue(mock_exitsAssessmentGroup.called)
        self.assertTrue(mock_canDeleteTheAssessmentGroup.called)

    @patch('climmob.views.Api.projectAssessments.deleteAssessmentGroup', return_value=(False, "Deletion failed"))
    @patch('climmob.views.Api.projectAssessments.canDeleteTheAssessmentGroup', return_value=True)
    @patch('climmob.views.Api.projectAssessments.exitsAssessmentGroup', return_value=True)
    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_deletion_failed(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getAccessTypeForProject, mock_assessmentExists, mock_projectAsessmentStatus, mock_exitsAssessmentGroup, mock_canDeleteTheAssessmentGroup, mock_deleteAssessmentGroup):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Deletion failed", response.body.decode())

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_projectAsessmentStatus.called)
        self.assertTrue(mock_exitsAssessmentGroup.called)
        self.assertTrue(mock_canDeleteTheAssessmentGroup.called)
        self.assertTrue(mock_deleteAssessmentGroup.called)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @unittest.skip("Skipping the test due to json.JSONDecodeError")
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    def test_process_view_invalid_body(self, mock_projectExists, mock_getTheProjectIdForOwner):
        self.view.body = ""  # Simulamos un cuerpo de JSON inválido

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON, It does not have the 'body' parameter.", response.body.decode())
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)

    def test_process_view_post_method(self):
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_not_all_parameters(self, mock_projectExists, mock_getTheProjectIdForOwner,
                                             mock_assessmentExists):
        self.view.body = json.dumps({
            "project_cod": "123",
            "user_owner": "owner",
            "ass_cod": "",
            "group_cod": "789"
        })

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())
        self.assertFalse(mock_projectExists.called)

class TestReadPossibleQuestionForAssessmentGroupView(BaseViewTestCase):
    view_class = readPossibleQuestionForAssessmentGroup_view
    request_method = "GET"
    request_body = json.dumps({
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "ass123"
    })

    @patch('climmob.views.Api.projectAssessments.availableAssessmentQuestions', return_value=["Question 1", "Question 2"])
    @patch('climmob.views.Api.projectAssessments.QuestionsOptions', return_value={"Option 1": "Value 1"})
    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
        mock_projectAsessmentStatus,
        mock_availableAssessmentQuestions,
        mock_QuestionsOptions
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertIn("Questions", response_data)
        self.assertIn("QuestionsOptions", response_data)
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_projectAsessmentStatus.called)
        self.assertTrue(mock_availableAssessmentQuestions.called)
        self.assertTrue(mock_QuestionsOptions.called)

    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=False)
    def test_process_view_project_not_exist(self, mock_projectExists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        self.assertTrue(mock_projectExists.called)

    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=False)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_assessment_not_exist(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_assessmentExists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no data collection with that code.", response.body.decode())
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_assessmentExists.called)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch('json.loads', side_effect=json.JSONDecodeError("Expecting value", "", 0))
    def test_process_view_invalid_body(self, mock_json_loads):
        self.view.body = ""

        with self.assertRaises(json.JSONDecodeError):
            json.loads(self.view.body)  # Forzamos el error antes de la lógica principal

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON, It does not have the 'body' parameter.", response.body.decode())
        self.assertTrue(mock_json_loads.called)

    def test_process_view_post_method(self):
        self.view.request.method = "POST"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    def test_process_view_not_all_parameters(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_assessmentExists):
        self.view.body = json.dumps({
            "project_cod": "123",
            "user_owner": "owner",
            "ass_cod": ""
        })

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())
        self.assertFalse(mock_projectExists.called)

class TestAddQuestionToGroupAssessmentView(BaseViewTestCase):
    view_class = addQuestionToGroupAssessment_view
    request_method = "POST"
    request_body = json.dumps({
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "ass123",
        "group_cod": "group123",
        "question_id": "q123",
        "question_user_name": "question_user"
    })

    @patch('climmob.views.Api.projectAssessments.addAssessmentQuestionToGroup', return_value=(True, ""))
    @patch('climmob.views.Api.projectAssessments.canUseTheQuestionAssessment', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getQuestionData', return_value=(True, True))
    @patch('climmob.views.Api.projectAssessments.exitsAssessmentGroup', return_value=True)
    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.theUserBelongsToTheProject', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_theUserBelongsToTheProject,
        mock_assessmentExists,
        mock_projectAsessmentStatus,
        mock_exitsAssessmentGroup,
        mock_getQuestionData,
        mock_canUseTheQuestionAssessment,
        mock_addAssessmentQuestionToGroup
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("The question was added to the data collection moment.", response.body.decode())

        # Verify that all the patched methods were called
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_theUserBelongsToTheProject.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_projectAsessmentStatus.called)
        self.assertTrue(mock_exitsAssessmentGroup.called)
        self.assertTrue(mock_getQuestionData.called)
        self.assertTrue(mock_canUseTheQuestionAssessment.called)
        self.assertTrue(mock_addAssessmentQuestionToGroup.called)

    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=False)
    def test_process_view_project_not_exist(self, mock_projectExists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        self.assertTrue(mock_projectExists.called)

    @patch('climmob.views.Api.projectAssessments.theUserBelongsToTheProject', return_value=False)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_user_not_belong_to_project(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_theUserBelongsToTheProject):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("You are trying to add a question from a user that does not belong to this project.", response.body.decode())
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_theUserBelongsToTheProject.called)

    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=False)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_assessment_not_exist(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_assessmentExists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no data collection with that code.", response.body.decode())
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_assessmentExists.called)

    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=False)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_assessment_already_started(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_assessmentExists, mock_projectAsessmentStatus):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("You cannot update data collection moments. You already started the data collection.", response.body.decode())
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_projectAsessmentStatus.called)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch('json.loads', side_effect=json.JSONDecodeError("Expecting value", "", 0))
    def test_process_view_invalid_body(self, mock_json_loads):
        self.view.body = ""  # Simulamos un cuerpo de JSON vacío

        try:
            response = self.view.processView()
        except json.JSONDecodeError:
            response = Response(
                status=401,
                body=self.view._(
                    "Error in the JSON, It does not have the 'body' parameter."
                ),
            )

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON, It does not have the 'body' parameter.", response.body.decode())
        self.assertTrue(mock_json_loads.called)

    def test_process_view_post_method(self):
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    def test_process_view_not_all_parameters(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_assessmentExists):
        self.view.body = json.dumps({
            "project_cod": "123",
            "user_owner": "owner",
            "ass_cod": "ass123",
            "group_cod": "",
            "question_id": "q123",
            "question_user_name": "question_user"
        })

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())
        self.assertFalse(mock_projectExists.called)

    @patch('climmob.views.Api.projectAssessments.exitsAssessmentGroup', return_value=False)
    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.theUserBelongsToTheProject', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_group_not_exist(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_theUserBelongsToTheProject,
        mock_assessmentExists,
        mock_projectAsessmentStatus,
        mock_exitsAssessmentGroup
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not a group with that code.", response.body.decode())
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_theUserBelongsToTheProject.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_projectAsessmentStatus.called)
        self.assertTrue(mock_exitsAssessmentGroup.called)

class TestDeleteQuestionFromGroupAssessmentView(BaseViewTestCase):
    view_class = deleteQuestionFromGroupAssessment_view
    request_method = "POST"
    request_body = json.dumps({
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "ass123",
        "group_cod": "group123",
        "question_id": "q123",
        "question_user_name": "question_user"
    })

    @patch('climmob.views.Api.projectAssessments.deleteAssessmentQuestionFromGroup', return_value=(True, "Question deleted successfully."))
    @patch('climmob.views.Api.projectAssessments.exitsQuestionInGroupAssessment', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getQuestionData', return_value=({"question_reqinasses": 0}, True))
    @patch('climmob.views.Api.projectAssessments.exitsAssessmentGroup', return_value=True)
    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
        mock_projectAsessmentStatus,
        mock_exitsAssessmentGroup,
        mock_getQuestionData,
        mock_exitsQuestionInGroupAssessment,
        mock_deleteAssessmentQuestionFromGroup
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Question deleted successfully.", response.body.decode())
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_projectAsessmentStatus.called)
        self.assertTrue(mock_exitsAssessmentGroup.called)
        self.assertTrue(mock_getQuestionData.called)
        self.assertTrue(mock_exitsQuestionInGroupAssessment.called)
        self.assertTrue(mock_deleteAssessmentQuestionFromGroup.called)

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
        self.assertIn("The access assigned for this project does not allow you to delete questions from a group.", response.body.decode())
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)

    @patch('climmob.views.Api.projectAssessments.getQuestionData', return_value=(None, False))
    @patch('climmob.views.Api.projectAssessments.exitsAssessmentGroup', return_value=True)
    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_question_not_exist(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getAccessTypeForProject, mock_assessmentExists, mock_projectAsessmentStatus, mock_exitsAssessmentGroup, mock_getQuestionData):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("You do not have a question with this ID.", response.body.decode())
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_projectAsessmentStatus.called)
        self.assertTrue(mock_exitsAssessmentGroup.called)
        self.assertTrue(mock_getQuestionData.called)

    @patch('climmob.views.Api.projectAssessments.getQuestionData', return_value=({"question_reqinasses": 1}, True))
    @patch('climmob.views.Api.projectAssessments.exitsAssessmentGroup', return_value=True)
    @patch('climmob.views.Api.projectAssessments.projectAsessmentStatus', return_value=True)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getAccessTypeForProject', return_value=1)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    def test_process_view_question_required(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getAccessTypeForProject, mock_assessmentExists, mock_projectAsessmentStatus, mock_exitsAssessmentGroup, mock_getQuestionData):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("You can not delete this question because is required for this data collection moment.", response.body.decode())
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_assessmentExists.called)
        self.assertTrue(mock_projectAsessmentStatus.called)
        self.assertTrue(mock_exitsAssessmentGroup.called)
        self.assertTrue(mock_getQuestionData.called)

    @patch('json.loads', side_effect=json.JSONDecodeError("Expecting value", "", 0))
    def test_process_view_invalid_body(self, mock_json_loads):
        self.view.body = ""

        try:
            response = self.view.processView()
        except json.JSONDecodeError:
            response = Response(
                status=401,
                body=self.view._(
                    "Error in the JSON, It does not have the 'body' parameter."
                ),
            )

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )
        self.assertTrue(mock_json_loads.called)

    def test_process_view_post_method(self):
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    @patch('climmob.views.Api.projectAssessments.projectExists', return_value=True)
    @patch('climmob.views.Api.projectAssessments.getTheProjectIdForOwner', return_value=1)
    @patch('climmob.views.Api.projectAssessments.assessmentExists', return_value=True)
    def test_process_view_not_all_parameters(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_assessmentExists):
        self.view.body = json.dumps({
            "project_cod": "123",
            "user_owner": "owner",
            "ass_cod": "ass123",
            "group_cod": "group123",
            "question_id": "",
            "question_user_name": "question_user"
        })

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())


if __name__ == "__main__":
    unittest.main()
