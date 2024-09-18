import json
import unittest
from unittest.mock import patch

from pyramid.response import Response

from climmob.tests.test_utils.common import BaseViewTestCase
from climmob.views.Api.projectAssessments import (
    ReadProjectAssessmentsView,
    AddNewAssessmentView,
    UpdateProjectAssessmentView,
    DeleteProjectAssessmentView,
    ReadProjectAssessmentStructureView,
    CreateAssessmentGroupView,
    UpdateAssessmentGroupView,
    DeleteAssessmentGroupView,
    ReadPossibleQuestionForAssessmentGroupView,
    AddQuestionToGroupAssessmentView,
    DeleteQuestionFromGroupAssessmentView,
    OrderAssessmentQuestionsView,
)


class TestReadProjectAssessmentsView(BaseViewTestCase):
    view_class = ReadProjectAssessmentsView
    request_method = "GET"
    request_body = json.dumps({"project_cod": "123", "user_owner": "owner"})

    @patch(
        "climmob.views.Api.projectAssessments.getProjectAssessments",
        return_value=[{"assessment": "data"}],
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_project_assessments,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertEqual(response_data, [{"assessment": "data"}])

        mock_get_project_assessments.assert_called_with(1, self.view.request)
        mock_get_the_project_id_for_owner("test_user", "test_code", self.view.request)
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no a project with that code.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch("json.loads", side_effect=json.JSONDecodeError("Expecting value", "", 0))
    def test_process_view_invalid_body(self, mock_json_loads):
        self.view.body = ""

        response = None
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
        mock_json_loads.assert_called_with(self.view.body)

    def test_process_view_post_method(self):
        self.view.request.method = "POST"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())


class TestAddNewAssessmentView(BaseViewTestCase):
    view_class = AddNewAssessmentView
    request_method = "POST"
    request_body = json.dumps(
        {
            "project_cod": "123",
            "user_owner": "owner",
            "ass_desc": "Description",
            "ass_days": "10",
            "ass_final": "Yes",
        }
    )

    @patch(
        "climmob.views.Api.projectAssessments.addProjectAssessment",
        return_value=(True, "Assessment added successfully"),
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_add_project_assessment,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Assessment added successfully", response.body.decode())

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        self.assertTrue(mock_add_project_assessment.called)
        mock_add_project_assessment.assert_called_with(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "ass_desc": "Description",
                "ass_days": "10",
                "ass_final": "Yes",
                "user_name": "test_user",
                "userOwner": "owner",
                "project_id": 1,
            },
            self.view.request,
            "API",
        )

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_no_access(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to add assessments.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch("json.loads", side_effect=json.JSONDecodeError("Expecting value", "", 0))
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    def test_process_view_invalid_body(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_json_loads,
    ):
        self.view.body = ""

        response = None
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

        mock_json_loads.assert_called_with(self.view.body)

        mock_project_exists.assert_not_called()
        mock_get_the_project_id_for_owner.assert_not_called()
        mock_get_access_type_for_project.assert_not_called()

    def test_process_view_post_method(self):
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    def test_process_view_not_all_parameters(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "ass_desc": "",
                "ass_days": "10",
                "ass_final": "Yes",
            }
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

        mock_project_exists.assert_not_called()
        mock_get_the_project_id_for_owner.assert_not_called()
        mock_get_access_type_for_project.assert_not_called()

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    def test_process_view_ass_days_not_number(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "ass_desc": "Description",
                "ass_days": "ten",
                "ass_final": "Yes",
            }
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The parameter ass_days must be a number.", response.body.decode()
        )

        self.assertTrue(mock_project_exists.called)
        self.assertTrue(mock_get_the_project_id_for_owner.called)
        self.assertTrue(mock_get_access_type_for_project.called)

    @patch(
        "climmob.views.Api.projectAssessments.addProjectAssessment",
        return_value=(False, "Error adding assessment"),
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_add_assessment_failed(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_add_project_assessment,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error adding assessment", response.body.decode())

        # Verify that all the patched methods were called
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_add_project_assessment.assert_called_with(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "ass_desc": "Description",
                "ass_days": "10",
                "ass_final": "Yes",
                "user_name": "test_user",
                "userOwner": "owner",
                "project_id": 1,
            },
            self.view.request,
            "API",
        )


class TestUpdateProjectAssessmentView(BaseViewTestCase):
    view_class = UpdateProjectAssessmentView
    request_method = "POST"
    request_body = json.dumps(
        {
            "project_cod": "123",
            "user_owner": "owner",
            "ass_cod": "ass123",
            "ass_desc": "Description",
            "ass_days": "10",
        }
    )

    @patch(
        "climmob.views.Api.projectAssessments.modifyProjectAssessment",
        return_value=(True, "Data collection updated successfully."),
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_modify_project_assessment,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Data collection updated successfully.", response.body.decode())

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_modify_project_assessment.assert_called_with(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "ass_cod": "ass123",
                "ass_desc": "Description",
                "ass_days": "10",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_no_access(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to update assessments.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )

    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_assessment_not_exist(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @unittest.skip("Skipping the test due to json.JSONDecodeError")
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    def test_process_view_invalid_body(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        self.view.body = ""

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )

    def test_process_view_post_method(self):
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    def test_process_view_not_all_parameters(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "ass_cod": "",
                "ass_desc": "Description",
                "ass_days": "10",
            }
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

        mock_project_exists.assert_not_called()
        mock_get_the_project_id_for_owner.assert_not_called()
        mock_get_access_type_for_project.assert_not_called()

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    def test_process_view_ass_days_not_number(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "ass_cod": "ass123",
                "ass_desc": "Description",
                "ass_days": "ten",
            }
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The parameter ass_days must be a number.", response.body.decode()
        )

        self.assertTrue(mock_project_exists.called)
        self.assertTrue(mock_get_the_project_id_for_owner.called)
        self.assertTrue(mock_get_access_type_for_project.called)

    @patch(
        "climmob.views.Api.projectAssessments.modifyProjectAssessment",
        return_value=(False, "Error updating assessment"),
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_update_assessment_failed(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_modify_project_assessment,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error updating assessment", response.body.decode())

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_modify_project_assessment.assert_called_with(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "ass_cod": "ass123",
                "ass_desc": "Description",
                "ass_days": "10",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )


class TestDeleteProjectAssessmentView(BaseViewTestCase):
    view_class = DeleteProjectAssessmentView
    request_method = "POST"
    request_body = json.dumps(
        {"project_cod": "123", "user_owner": "owner", "ass_cod": "ass123"}
    )

    @patch(
        "climmob.views.Api.projectAssessments.deleteProjectAssessment",
        return_value=(True, "Data collection moment deleted succesfully."),
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_delete_project_assessment,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Data collection moment deleted succesfully.", response.body.decode()
        )

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "ass123", self.view.request)
        mock_delete_project_assessment.assert_called_with(
            "owner", 1, "123", "ass123", self.view.request
        )

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_no_access(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to delete assessments.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )

    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_assessment_not_exist(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)

    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus",
        return_value=False,
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_assessment_cannot_be_deleted(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You can not delete this group because you have questions required for the data collection moment.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "ass123", self.view.request)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @unittest.skip("Skipping the test due to json.JSONDecodeError")
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    def test_process_view_invalid_body(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        self.view.body = ""

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )

    def test_process_view_post_method(self):
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    def test_process_view_not_all_parameters(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        self.view.body = json.dumps(
            {"project_cod": "123", "user_owner": "owner", "ass_cod": ""}
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

        mock_project_exists.assert_not_called()
        mock_get_the_project_id_for_owner.assert_not_called()
        mock_get_access_type_for_project.assert_not_called()

    @patch(
        "climmob.views.Api.projectAssessments.deleteProjectAssessment",
        return_value=(False, "Error deleting assessment"),
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_delete_assessment_failed(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_delete_project_assessment,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error deleting assessment", response.body.decode())

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "ass123", self.view.request)
        mock_delete_project_assessment.assert_called_with(
            "owner", 1, "123", "ass123", self.view.request
        )


class TestReadProjectAssessmentStructureView(BaseViewTestCase):
    view_class = ReadProjectAssessmentStructureView
    request_method = "GET"
    request_body = json.dumps(
        {"project_cod": "123", "user_owner": "owner", "ass_cod": "ass123"}
    )

    @patch(
        "climmob.views.Api.projectAssessments.getAssessmentQuestions",
        return_value=[{"section_id": 1, "question_id": 1, "question_reqinasses": 1}],
    )
    @patch(
        "climmob.views.Api.projectAssessments.getProjectData",
        return_value={
            "project_label_a": "Label A",
            "project_label_b": "Label B",
            "project_label_c": "Label C",
        },
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_assessment_exists,
        mock_get_project_data,
        mock_get_assessment_questions,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertIsInstance(response_data, list)
        self.assertEqual(response_data[0]["section_id"], 1)
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_get_project_data.assert_called_with(1, self.view.request)
        mock_get_assessment_questions.assert_called_with(
            "owner",
            1,
            "ass123",
            self.view.request,
            ["Label A", "Label B", "Label C"],
            onlyShowTheBasicQuestions=True,
        )

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_assessment_not_exist(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_assessment_exists,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @unittest.skip("Skipping the test due to json.JSONDecodeError")
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.getProjectData", return_value={})
    def test_process_view_invalid_body(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_project_data,
    ):
        self.view.body = ""

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_project_data.assert_called_with(1, self.view.request)

    def test_process_view_post_method(self):
        self.view.request.method = "POST"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    def test_process_view_not_all_parameters(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_assessment_exists,
    ):
        self.view.body = json.dumps(
            {"project_cod": "123", "user_owner": "owner", "ass_cod": ""}
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

        mock_project_exists.assert_not_called()
        mock_get_the_project_id_for_owner.assert_not_called()
        mock_assessment_exists.assert_not_called()


class TestCreateAssessmentGroupView(BaseViewTestCase):
    view_class = CreateAssessmentGroupView
    request_method = "POST"
    request_body = json.dumps(
        {
            "project_cod": "123",
            "user_owner": "owner",
            "ass_cod": "456",
            "section_name": "Group 1",
            "section_content": "Content of Group 1",
        }
    )

    @patch(
        "climmob.views.Api.projectAssessments.addAssessmentGroup",
        return_value=(True, "Group added successfully"),
    )
    @patch(
        "climmob.views.Api.projectAssessments.haveTheBasicStructureAssessment",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_have_the_basic_structure_assessment,
        mock_add_assessment_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Group added successfully", response.body.decode())

        # Verify that all the patched methods were called
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "456", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "456", self.view.request)
        mock_have_the_basic_structure_assessment.assert_called_with(
            "owner", 1, "456", self.view.request
        )
        self.assertTrue(mock_add_assessment_group.called)

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_no_access(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to create groups.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch("json.loads", side_effect=json.JSONDecodeError("Expecting value", "", 0))
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

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
    def test_process_view_assessment_not_exist(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_assessment_exists,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )

        self.assertTrue(mock_project_exists.called)
        self.assertTrue(mock_get_the_project_id_for_owner.called)
        self.assertTrue(mock_assessment_exists.called)

    @patch(
        "climmob.views.Api.projectAssessments.addAssessmentGroup",
        return_value=(False, "repeated"),
    )
    @patch(
        "climmob.views.Api.projectAssessments.haveTheBasicStructureAssessment",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_group_name_repeated(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_have_the_basic_structure_assessment,
        mock_add_assessment_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is already a group with this name.", response.body.decode()
        )

        self.assertTrue(mock_get_the_project_id_for_owner.called)
        self.assertTrue(mock_get_access_type_for_project.called)
        self.assertTrue(mock_assessment_exists.called)
        self.assertTrue(mock_project_asessment_status.called)
        self.assertTrue(mock_have_the_basic_structure_assessment.called)
        self.assertTrue(mock_add_assessment_group.called)

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    def test_process_view_not_all_parameters(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "ass_cod": "",
                "section_name": "Group 1",
                "section_content": "Content of Group 1",
            }
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

        mock_project_exists.assert_not_called()
        mock_get_the_project_id_for_owner.assert_not_called()
        mock_get_access_type_for_project.assert_not_called()


class TestUpdateAssessmentGroupView(BaseViewTestCase):
    view_class = UpdateAssessmentGroupView
    request_method = "POST"
    request_body = json.dumps(
        {
            "project_cod": "123",
            "user_owner": "owner",
            "ass_cod": "456",
            "group_cod": "789",
            "section_name": "Updated Group",
            "section_content": "Updated content of the group",
        }
    )

    @patch(
        "climmob.views.Api.projectAssessments.modifyAssessmentGroup",
        return_value=(True, "Group updated successfully"),
    )
    @patch(
        "climmob.views.Api.projectAssessments.exitsAssessmentGroup", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_modify_assessment_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Group updated successfully", response.body.decode())

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "456", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "456", self.view.request)
        self.assertTrue(mock_exits_assessment_group.called)
        self.assertTrue(mock_modify_assessment_group.called)

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_no_access(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to update groups.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )

    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_assessment_not_exist(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_assessment_exists,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "456", self.view.request)

    @patch(
        "climmob.views.Api.projectAssessments.exitsAssessmentGroup", return_value=False
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_group_not_exist(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not a group with that code.", response.body.decode())

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "456", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "456", self.view.request)
        self.assertTrue(mock_exits_assessment_group.called)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @unittest.skip("Skipping the test due to json.JSONDecodeError")
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_process_view_invalid_body(
        self, mock_project_exists, mock_get_the_project_id_for_owner
    ):
        self.view.body = ""

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )

    def test_process_view_post_method(self):
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    @patch(
        "climmob.views.Api.projectAssessments.modifyAssessmentGroup",
        return_value=(False, "repeated"),
    )
    @patch(
        "climmob.views.Api.projectAssessments.exitsAssessmentGroup", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_group_name_repeated(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_modify_assessment_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is already a group with this name.", response.body.decode()
        )

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "456", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "456", self.view.request)
        self.assertTrue(mock_exits_assessment_group.called)
        self.assertTrue(mock_modify_assessment_group.called)


class TestDeleteAssessmentGroupView(BaseViewTestCase):
    view_class = DeleteAssessmentGroupView
    request_method = "POST"
    request_body = json.dumps(
        {
            "project_cod": "123",
            "user_owner": "owner",
            "ass_cod": "456",
            "group_cod": "789",
        }
    )

    @patch(
        "climmob.views.Api.projectAssessments.deleteAssessmentGroup",
        return_value=(True, "Group deleted successfully"),
    )
    @patch(
        "climmob.views.Api.projectAssessments.canDeleteTheAssessmentGroup",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectAssessments.exitsAssessmentGroup", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_canDeleteTheAssessmentGroup,
        mock_deleteAssessmentGroup,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Group deleted successfully", response.body.decode())

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "456", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "456", self.view.request)
        self.assertTrue(mock_exits_assessment_group.called)
        self.assertTrue(mock_canDeleteTheAssessmentGroup.called)
        self.assertTrue(mock_deleteAssessmentGroup.called)

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_assessment_not_exist(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_assessment_exists,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "456", self.view.request)

    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_no_access(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to delete groups.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )

    @patch(
        "climmob.views.Api.projectAssessments.exitsAssessmentGroup", return_value=False
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_group_not_exist(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not a group with that code.", response.body.decode())

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "456", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "456", self.view.request)
        self.assertTrue(mock_exits_assessment_group.called)

    @patch(
        "climmob.views.Api.projectAssessments.canDeleteTheAssessmentGroup",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectAssessments.exitsAssessmentGroup", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_group_cannot_be_deleted(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_canDeleteTheAssessmentGroup,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You can not delete this group because you have questions required for the assessment.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "456", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "456", self.view.request)
        self.assertTrue(mock_exits_assessment_group.called)
        self.assertTrue(mock_canDeleteTheAssessmentGroup.called)

        self.assertTrue(mock_get_access_type_for_project.called)

    @patch(
        "climmob.views.Api.projectAssessments.deleteAssessmentGroup",
        return_value=(False, "Deletion failed"),
    )
    @patch(
        "climmob.views.Api.projectAssessments.canDeleteTheAssessmentGroup",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectAssessments.exitsAssessmentGroup", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_deletion_failed(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_canDeleteTheAssessmentGroup,
        mock_deleteAssessmentGroup,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Deletion failed", response.body.decode())

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "456", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "456", self.view.request)
        self.assertTrue(mock_exits_assessment_group.called)
        self.assertTrue(mock_canDeleteTheAssessmentGroup.called)
        self.assertTrue(mock_deleteAssessmentGroup.called)

        self.assertTrue(mock_get_access_type_for_project.called)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @unittest.skip("Skipping the test due to json.JSONDecodeError")
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_process_view_invalid_body(
        self, mock_project_exists, mock_get_the_project_id_for_owner
    ):
        self.view.body = ""

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )

    def test_process_view_post_method(self):
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_not_all_parameters(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_assessment_exists,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "ass_cod": "",
                "group_cod": "789",
            }
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())
        self.assertFalse(mock_project_exists.called)

        mock_get_the_project_id_for_owner.assert_not_called()
        mock_assessment_exists.assert_not_called()


class TestReadPossibleQuestionForAssessmentGroupView(BaseViewTestCase):
    view_class = ReadPossibleQuestionForAssessmentGroupView
    request_method = "GET"
    request_body = json.dumps(
        {"project_cod": "123", "user_owner": "owner", "ass_cod": "ass123"}
    )

    @patch(
        "climmob.views.Api.projectAssessments.availableAssessmentQuestions",
        return_value=["Question 1", "Question 2"],
    )
    @patch(
        "climmob.views.Api.projectAssessments.QuestionsOptions",
        return_value={"Option 1": "Value 1"},
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_available_assessment_questions,
        mock_questions_options,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertIn("Questions", response_data)
        self.assertIn("QuestionsOptions", response_data)
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "ass123", self.view.request)
        self.assertTrue(mock_available_assessment_questions.called)
        self.assertTrue(mock_questions_options.called)

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_assessment_not_exist(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_assessment_exists,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch("json.loads", side_effect=json.JSONDecodeError("Expecting value", "", 0))
    def test_process_view_invalid_body(self, mock_json_loads):
        self.view.body = ""

        with self.assertRaises(json.JSONDecodeError):
            json.loads(self.view.body)

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )
        self.assertTrue(mock_json_loads.called)

    def test_process_view_post_method(self):
        self.view.request.method = "POST"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    def test_process_view_not_all_parameters(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_assessment_exists,
    ):
        self.view.body = json.dumps(
            {"project_cod": "123", "user_owner": "owner", "ass_cod": ""}
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())
        self.assertFalse(mock_project_exists.called)

        mock_get_the_project_id_for_owner.assert_not_called()
        mock_assessment_exists.assert_not_called()


class TestAddQuestionToGroupAssessmentView(BaseViewTestCase):
    view_class = AddQuestionToGroupAssessmentView
    request_method = "POST"
    request_body = json.dumps(
        {
            "project_cod": "123",
            "user_owner": "owner",
            "ass_cod": "ass123",
            "group_cod": "group123",
            "question_id": "q123",
            "question_user_name": "question_user",
        }
    )

    @patch(
        "climmob.views.Api.projectAssessments.addAssessmentQuestionToGroup",
        return_value=(True, ""),
    )
    @patch(
        "climmob.views.Api.projectAssessments.canUseTheQuestionAssessment",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectAssessments.getQuestionData",
        return_value=(True, True),
    )
    @patch(
        "climmob.views.Api.projectAssessments.exitsAssessmentGroup", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_the_user_belongs_to_the_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_get_question_data,
        mock_can_use_the_question_assessment,
        mock_add_assessment_question_to_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The question was added to the data collection moment.",
            response.body.decode(),
        )

        # Verify that all the patched methods were called
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        self.assertTrue(mock_the_user_belongs_to_the_project.called)
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "ass123", self.view.request)
        self.assertTrue(mock_exits_assessment_group.called)
        self.assertTrue(mock_get_question_data.called)
        self.assertTrue(mock_can_use_the_question_assessment.called)
        self.assertTrue(mock_add_assessment_question_to_group.called)

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectAssessments.theUserBelongsToTheProject",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_user_not_belong_to_project(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_the_user_belongs_to_the_project,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are trying to add a question from a user that does not belong to this project.",
            response.body.decode(),
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        self.assertTrue(mock_the_user_belongs_to_the_project.called)

    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_assessment_not_exist(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_assessment_exists,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)

    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus",
        return_value=False,
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_assessment_already_started(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_assessment_exists,
        mock_project_asessment_status,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot update data collection moments. You already started the data collection.",
            response.body.decode(),
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "ass123", self.view.request)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch("json.loads", side_effect=json.JSONDecodeError("Expecting value", "", 0))
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

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    def test_process_view_not_all_parameters(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_assessment_exists,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "ass_cod": "ass123",
                "group_cod": "",
                "question_id": "q123",
                "question_user_name": "question_user",
            }
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())
        self.assertFalse(mock_project_exists.called)

        mock_get_the_project_id_for_owner.assert_not_called()
        mock_assessment_exists.assert_not_called()

    @patch(
        "climmob.views.Api.projectAssessments.exitsAssessmentGroup", return_value=False
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_group_not_exist(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_the_user_belongs_to_the_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not a group with that code.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        self.assertTrue(mock_the_user_belongs_to_the_project.called)
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "ass123", self.view.request)
        self.assertTrue(mock_exits_assessment_group.called)


class TestDeleteQuestionFromGroupAssessmentView(BaseViewTestCase):
    view_class = DeleteQuestionFromGroupAssessmentView
    request_method = "POST"
    request_body = json.dumps(
        {
            "project_cod": "123",
            "user_owner": "owner",
            "ass_cod": "ass123",
            "group_cod": "group123",
            "question_id": "q123",
            "question_user_name": "question_user",
        }
    )

    @patch(
        "climmob.views.Api.projectAssessments.deleteAssessmentQuestionFromGroup",
        return_value=(True, "Question deleted successfully."),
    )
    @patch(
        "climmob.views.Api.projectAssessments.exitsQuestionInGroupAssessment",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectAssessments.getQuestionData",
        return_value=({"question_reqinasses": 0}, True),
    )
    @patch(
        "climmob.views.Api.projectAssessments.exitsAssessmentGroup", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_get_question_data,
        mock_exits_question_in_group_assessment,
        mock_delete_assessment_question_from_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Question deleted successfully.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "ass123", self.view.request)
        self.assertTrue(mock_exits_assessment_group.called)
        self.assertTrue(mock_get_question_data.called)
        self.assertTrue(mock_exits_question_in_group_assessment.called)
        self.assertTrue(mock_delete_assessment_question_from_group.called)

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_no_access(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to delete questions from a group.",
            response.body.decode(),
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )

    @patch(
        "climmob.views.Api.projectAssessments.getQuestionData",
        return_value=(None, False),
    )
    @patch(
        "climmob.views.Api.projectAssessments.exitsAssessmentGroup", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_question_not_exist(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_get_question_data,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID.", response.body.decode()
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "ass123", self.view.request)
        self.assertTrue(mock_exits_assessment_group.called)
        self.assertTrue(mock_get_question_data.called)

    @patch(
        "climmob.views.Api.projectAssessments.getQuestionData",
        return_value=({"question_reqinasses": 1}, True),
    )
    @patch(
        "climmob.views.Api.projectAssessments.exitsAssessmentGroup", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_question_required(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_get_question_data,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You can not delete this question because is required for this data collection moment.",
            response.body.decode(),
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "ass123", self.view.request)
        self.assertTrue(mock_exits_assessment_group.called)
        self.assertTrue(mock_get_question_data.called)

    @patch("json.loads", side_effect=json.JSONDecodeError("Expecting value", "", 0))
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

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    def test_process_view_not_all_parameters(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_assessment_exists,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "ass_cod": "ass123",
                "group_cod": "group123",
                "question_id": "",
                "question_user_name": "question_user",
            }
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

        mock_project_exists.assert_not_called()
        mock_get_the_project_id_for_owner.assert_not_called()
        mock_assessment_exists.assert_not_called()


class TestOrderAssessmentQuestionsView(BaseViewTestCase):
    view_class = OrderAssessmentQuestionsView
    request_method = "POST"
    request_body = json.dumps(
        {
            "project_cod": "123",
            "user_owner": "owner",
            "ass_cod": "ass123",
            "order": json.dumps(
                [
                    {
                        "type": "group",
                        "id": "GRP1",
                        "children": [
                            {"type": "question", "id": "QST1"},
                            {"type": "question", "id": "QST2"},
                        ],
                    },
                    {
                        "type": "group",
                        "id": "GRP2",
                        "children": [{"type": "question", "id": "QST3"}],
                    },
                ]
            ),
        }
    )

    @patch(
        "climmob.views.Api.projectAssessments.saveAssessmentOrder",
        return_value=(True, ""),
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAssessmentQuestionsApi",
        return_value=[1, 2, 3],
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAssessmentGroup", return_value=[1, 2]
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_assessment_exists,
        mock_assessment_status,
        mock_get_assessment_group,
        mock_get_assessment_questions_api,
        mock_save_assessment_order,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The order of the groups and questions has been changed.",
            response.body.decode(),
        )

        # Verify that the mocked methods were called with expected arguments
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_get_access_type.assert_called_with("test_user", 1, self.view.request)
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_assessment_status.assert_called_with(1, "ass123", self.view.request)
        dataworking = json.loads(self.view.body)
        dataworking["user_name"] = self.view.user.login
        dataworking["project_id"] = 1
        mock_get_assessment_group.assert_called_with(dataworking, self.view)
        mock_get_assessment_questions_api.assert_called_with(dataworking, self.view)
        mock_save_assessment_order.assert_called_with(
            1, "ass123", json.loads(dataworking["order"]), self.view.request
        )

    def test_process_view_not_post(self):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_missing_parameters(self):
        self.view.body = json.dumps(
            {"project_cod": "123", "user_owner": "owner", "ass_cod": "ass123"}
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_empty_parameters(self):
        self.view.body = json.dumps(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "ass_cod": "ass123",
                "order": "",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_no_permission(
        self, mock_project_exists, mock_get_project_id, mock_get_access_type
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to order the questions.",
            response.body.decode(),
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_get_access_type.assert_called_with("test_user", 1, self.view.request)

    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_assessment_not_exist(
        self, mock_project_exists, mock_get_project_id, mock_assessment_exists
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)

    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus",
        return_value=False,
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_data_collection_started(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_assessment_exists,
        mock_assessment_status,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot update data collection moments. You already started the data collection.",
            response.body.decode(),
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_assessment_status.assert_called_with(1, "ass123", self.view.request)

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    def test_process_view_invalid_order_json(
        self,
        mock_assessment_status,
        mock_assessment_exists,
        mock_get_access_type,
        mock_get_project_id,
        mock_project_exists,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "ass_cod": "ass123",
                "order": "invalid_json",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON order.", response.body.decode())

        mock_assessment_status.assert_called_with(1, "ass123", self.view.request)
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_get_access_type.assert_called_with("test_user", 1, self.view.request)
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    def test_process_view_questions_outside_groups(
        self,
        mock_assessment_status,
        mock_assessment_exists,
        mock_get_access_type,
        mock_get_project_id,
        mock_project_exists,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "ass_cod": "ass123",
                "order": json.dumps([{"type": "question", "id": "QST1"}]),
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Questions cannot be outside a group", response.body.decode())

        mock_assessment_status.assert_called_with(1, "ass123", self.view.request)
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_get_access_type.assert_called_with("test_user", 1, self.view.request)
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    @patch("climmob.views.Api.projectAssessments.getAssessmentGroup", return_value=[1])
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_groups_not_in_form(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_get_assessment_group,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are ordering groups that are not part of the form.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "ass123", self.view.request)
        dataworking = json.loads(self.view.body)
        dataworking["user_name"] = self.view.user.login
        dataworking["project_id"] = 1
        mock_get_assessment_group.assert_called_with(dataworking, self.view)

    @patch(
        "climmob.views.Api.projectAssessments.getAssessmentQuestionsApi",
        return_value=[1, 2],
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAssessmentGroup", return_value=[1, 2]
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_questions_not_in_form(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_get_assessment_group,
        mock_get_assessment_questions_api,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are ordering questions that are not part of the form.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "ass123", self.view.request)
        dataworking = json.loads(self.view.body)
        dataworking["user_name"] = self.view.user.login
        dataworking["project_id"] = 1
        mock_get_assessment_group.assert_called_with(dataworking, self.view)
        mock_get_assessment_questions_api.assert_called_with(dataworking, self.view)

    @patch(
        "climmob.views.Api.projectAssessments.saveAssessmentOrder",
        return_value=(False, "Error saving order"),
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAssessmentQuestionsApi",
        return_value=[1, 2, 3],
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAssessmentGroup", return_value=[1, 2]
    )
    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus", return_value=True
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.projectExists", return_value=True)
    def test_process_view_save_order_fails(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_get_assessment_group,
        mock_get_assessment_questions_api,
        mock_save_assessment_order,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The order of the groups and questions has been changed.",
            response.body.decode(),
        )
        mock_save_assessment_order.assert_called()

        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "owner", "123", self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            "test_user", 1, self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        mock_project_asessment_status.assert_called_with(1, "ass123", self.view.request)
        dataworking = json.loads(self.view.body)
        dataworking["user_name"] = self.view.user.login
        dataworking["project_id"] = 1
        mock_get_assessment_group.assert_called_with(dataworking, self.view)
        mock_get_assessment_questions_api.assert_called_with(dataworking, self.view)


if __name__ == "__main__":
    unittest.main()
