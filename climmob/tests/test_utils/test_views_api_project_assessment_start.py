import json
import os
from uuid import UUID
import shutil
import unittest
from unittest.mock import patch, MagicMock
from pyramid.response import Response
from climmob.views.Api.projectAssessmentStart import (
    CreateProjectAssessmentView,
    CancelAssessmentApiView,
    CloseAssessmentApiView,
    ReadAssessmentStructureView,
    PushJsonToAssessmentView,
    ApiAssessmentPushProcess,
    ReadAssessmentDataView,
    AssessmentDataCleaningView,
)
from climmob.tests.test_utils.common import ViewBaseTest


class MockResponse:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self.body = body


class FakeSelf:
    def __init__(self):
        self.apiKey = "TESTKEY"
        self.user = MagicMock()
        self.user.login = "test_user"
        self.request = MagicMock()
        self._ = lambda x: x


class TestCreateProjectAssessmentView(ViewBaseTest):
    view_class = CreateProjectAssessmentView
    request_method = "POST"
    request_body = json.dumps(
        {"project_cod": "123", "user_owner": "owner", "ass_cod": "ass123"}
    )

    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not project with that code.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=4,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_no_access(
        self, mock_project_exists, mock_get_project_id, mock_get_access_type
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to do this action.",
            response.body.decode(),
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("test_user", 1, self.view.request)
        mock_get_access_type.assert_called_with("owner", "123", self.view.request)

    @patch(
        "climmob.views.Api.projectAssessmentStart.getProjectProgress",
        return_value=({"regsubmissions": 1, "assessment": False}, False),
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    def test_process_view_invalid_progress(
        self,
        mock_get_access_type,
        mock_get_project_id,
        mock_project_exists,
        mock_get_project_progress,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot add data collection moments. You alreaday started data collection.",
            response.body.decode(),
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_get_access_type.assert_called_with("test_user", 1, self.view.request)
        mock_get_project_progress.assert_called_with(
            "owner", "123", 1, self.view.request
        )

    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getProjectProgress",
        return_value=({"regsubmissions": 2, "assessment": True}, True),
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    def test_process_view_assessment_already_started(
        self,
        mock_get_access_type,
        mock_get_project_id,
        mock_project_exists,
        mock_get_project_progress,
        mock_project_assessment_status,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Data collection has already started.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_get_access_type.assert_called_with("test_user", 1, self.view.request)
        mock_get_project_progress.assert_called_with(
            "owner", "123", 1, self.view.request
        )
        mock_project_assessment_status.assert_called_with(
            1, "ass123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectAssessmentStart.checkAssessments",
        return_value=(False, ["error1", "error2"]),
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getProjectProgress",
        return_value=({"regsubmissions": 2, "assessment": True}, True),
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    def test_process_view_check_assessments_failed(
        self,
        mock_get_access_type,
        mock_get_project_id,
        mock_project_exists,
        mock_get_project_progress,
        mock_project_assessment_status,
        mock_check_assessments,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("errors", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_get_access_type.assert_called_with("test_user", 1, self.view.request)
        mock_get_project_progress.assert_called_with(
            "owner", "123", 1, self.view.request
        )
        mock_project_assessment_status.assert_called_with(
            1, "ass123", self.view.request
        )
        mock_check_assessments.assert_called_with(1, "ass123", self.view.request)

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

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_missing_parameters(self, mock_project_exists):
        self.view.body = json.dumps(
            {"project_cod": "123", "user_owner": "", "ass_cod": "ass123"}
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())
        mock_project_exists.assert_not_called()

    @patch(
        "climmob.views.Api.projectAssessmentStart.generateAssessmentFiles",
        return_value=[
            {"code": "data", "result": False, "error": "error"},
            {"code": "data", "result": False, "error": b"error"},
        ],
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getProjectData",
        return_value=(
            {"project_label_a": 1, "project_label_b": 2, "project_label_c": 3}
        ),
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheGroupOfThePackageCodeAssessment",
        return_value=({"data": "data"}),
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.checkAssessments",
        return_value=(True, {}),
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getProjectProgress",
        return_value=({"regsubmissions": 2, "assessment": True}, True),
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    def test_process_view_check_generate_assessment_error(
        self,
        mock_get_access_type,
        mock_get_project_id,
        mock_project_exists,
        mock_get_project_progress,
        mock_project_assessment_status,
        mock_check_assessments,
        mock_getTheGroupOfThePackageCodeAssessment,
        mock_getProjectData,
        mock_generateAssessmentFiles,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There has been a problem in the creation of the basic structure of the project, this may be due to something wrong with the form. Contact the ClimMob team with the next message to get the solution to the problem: error",
            response.body.decode(),
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_get_access_type.assert_called_with("test_user", 1, self.view.request)
        mock_get_project_progress.assert_called_with(
            "owner", "123", 1, self.view.request
        )
        mock_project_assessment_status.assert_called_with(
            1, "ass123", self.view.request
        )
        mock_check_assessments.assert_called_with(1, "ass123", self.view.request)

    @patch("climmob.views.Api.projectAssessmentStart.create_document_form")
    @patch(
        "climmob.views.Api.projectAssessmentStart.getDataFormPreview",
        return_value=(2, 3),
    )
    @patch("climmob.views.Api.projectAssessmentStart.getPackages", return_value=(2, 3))
    @patch("climmob.views.Api.projectAssessmentStart.setAssessmentIndividualStatus")
    @patch(
        "climmob.views.Api.projectAssessmentStart.generateAssessmentFiles",
        return_value=[
            {"code": "data", "result": True, "error": "error"},
            {"code": "data", "result": True, "error": b"error"},
        ],
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getProjectData",
        return_value=(
            {
                "project_label_a": 1,
                "project_label_b": 2,
                "project_label_c": 3,
                "languages": [
                    {"lang_code": "es"},
                    {"lang_code": "en"},
                ],
            }
        ),
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheGroupOfThePackageCodeAssessment",
        return_value=({"data": "data"}),
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.checkAssessments",
        return_value=(True, {}),
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getProjectProgress",
        return_value=({"regsubmissions": 2, "assessment": True}, True),
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    def test_process_view_check_generate_success(
        self,
        mock_get_access_type,
        mock_get_project_id,
        mock_project_exists,
        mock_get_project_progress,
        mock_project_assessment_status,
        mock_check_assessments,
        mock_getTheGroupOfThePackageCodeAssessment,
        mock_getProjectData,
        mock_generateAssessmentFiles,
        mock_setAssessmentIndividualStatus,
        mock_getPackages,
        mock_getDataFormPreview,
        mock_create_document_form,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Data collection started", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_get_access_type.assert_called_with("test_user", 1, self.view.request)
        mock_get_project_progress.assert_called_with(
            "owner", "123", 1, self.view.request
        )
        mock_project_assessment_status.assert_called_with(
            1, "ass123", self.view.request
        )
        mock_check_assessments.assert_called_with(1, "ass123", self.view.request)

    @patch("climmob.views.Api.projectAssessmentStart.create_document_form")
    @patch(
        "climmob.views.Api.projectAssessmentStart.getDataFormPreview",
        return_value=(2, 3),
    )
    @patch("climmob.views.Api.projectAssessmentStart.getPackages", return_value=(2, 3))
    @patch("climmob.views.Api.projectAssessmentStart.setAssessmentIndividualStatus")
    @patch(
        "climmob.views.Api.projectAssessmentStart.generateAssessmentFiles",
        return_value=[
            {"code": "data", "result": True, "error": "error"},
            {"code": "data", "result": True, "error": b"error"},
        ],
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getProjectData",
        return_value=(
            {
                "project_label_a": 1,
                "project_label_b": 2,
                "project_label_c": 3,
                "languages": None,
            }
        ),
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheGroupOfThePackageCodeAssessment",
        return_value=({"data": "data"}),
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.checkAssessments",
        return_value=(True, {}),
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getProjectProgress",
        return_value=({"regsubmissions": 2, "assessment": True}, True),
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    def test_process_view_check_generate_success_2(
        self,
        mock_get_access_type,
        mock_get_project_id,
        mock_project_exists,
        mock_get_project_progress,
        mock_project_assessment_status,
        mock_check_assessments,
        mock_getTheGroupOfThePackageCodeAssessment,
        mock_getProjectData,
        mock_generateAssessmentFiles,
        mock_setAssessmentIndividualStatus,
        mock_getPackages,
        mock_getDataFormPreview,
        mock_create_document_form,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Data collection started", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_get_access_type.assert_called_with("test_user", 1, self.view.request)
        mock_get_project_progress.assert_called_with(
            "owner", "123", 1, self.view.request
        )
        mock_project_assessment_status.assert_called_with(
            1, "ass123", self.view.request
        )
        mock_check_assessments.assert_called_with(1, "ass123", self.view.request)

    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getProjectProgress",
        return_value=({"regsubmissions": 2, "assessment": False}, False),
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    def test_process_view_invalid_progress_must_create_assessment_form(
        self,
        mock_get_access_type,
        mock_get_project_id,
        mock_project_exists,
        mock_get_project_progress,
        mock_projectAsessmentStatus,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You must have created the assessment forms.",
            response.body.decode(),
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_get_access_type.assert_called_with("test_user", 1, self.view.request)
        mock_get_project_progress.assert_called_with(
            "owner", "123", 1, self.view.request
        )


class TestCancelAssessmentApiView(ViewBaseTest):
    view_class = CancelAssessmentApiView
    request_method = "POST"
    request_body = json.dumps(
        {"project_cod": "123", "user_owner": "owner", "ass_cod": "ass123"}
    )

    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.setAssessmentIndividualStatus",
        return_value=True,
    )
    def test_process_view_success(
        self,
        mock_set_assessment_status,
        mock_project_assessment_status,
        mock_get_access_type,
        mock_get_project_id,
        mock_project_exists,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Cancel data collection", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_get_access_type.assert_called_with("test_user", 1, self.view.request)
        mock_project_assessment_status.assert_called_with(
            1, "ass123", self.view.request
        )
        self.assertTrue(mock_set_assessment_status.called)

    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=4,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_no_access(
        self, mock_project_exists, mock_get_project_id, mock_get_access_type
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to cancel the assessment.",
            response.body.decode(),
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("test_user", 1, self.view.request)
        mock_get_access_type.assert_called_with("owner", "123", self.view.request)

    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=True,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    def test_process_view_assessment_already_started(
        self,
        mock_get_access_type,
        mock_get_project_id,
        mock_project_exists,
        mock_project_assessment_status,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Data collection has not started. You cannot cancel it.",
            response.body.decode(),
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_get_access_type.assert_called_with("test_user", 1, self.view.request)
        mock_project_assessment_status.assert_called_with(
            1, "ass123", self.view.request
        )

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

    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_missing_parameters(self, mock_project_exists):
        self.view.body = json.dumps(
            {"project_cod": "123", "user_owner": "", "ass_cod": "ass123"}
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())
        mock_project_exists.assert_not_called()


class TestCloseAssessmentApiView(ViewBaseTest):
    view_class = CloseAssessmentApiView
    request_method = "POST"
    request_body = json.dumps(
        {"project_cod": "123", "user_owner": "owner", "ass_cod": "ass123"}
    )

    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.assessmentExists", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.setAssessmentIndividualStatus",
        return_value=True,
    )
    def test_process_view_success(
        self,
        mock_set_assessment_status,
        mock_assessment_exists,
        mock_project_assessment_status,
        mock_get_access_type,
        mock_get_project_id,
        mock_project_exists,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Data collection closed.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_get_access_type.assert_called_with("test_user", 1, self.view.request)
        mock_project_assessment_status.assert_called_with(
            1, "ass123", self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        self.assertTrue(mock_set_assessment_status.called)

    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=4,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_no_access(
        self, mock_project_exists, mock_get_project_id, mock_get_access_type
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to cancel the assessment.",
            response.body.decode(),
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("test_user", 1, self.view.request)
        mock_get_access_type.assert_called_with("owner", "123", self.view.request)

    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=True,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    def test_process_view_assessment_already_started(
        self,
        mock_get_access_type,
        mock_get_project_id,
        mock_project_exists,
        mock_project_assessment_status,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Data collection has not started. You cannot cancel it.",
            response.body.decode(),
        )
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_get_access_type.assert_called_with("test_user", 1, self.view.request)
        mock_project_assessment_status.assert_called_with(
            1, "ass123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectAssessmentStart.assessmentExists", return_value=False
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=False,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    def test_process_view_assessment_not_exist(
        self,
        mock_get_access_type,
        mock_get_project_id,
        mock_project_exists,
        mock_project_assessment_status,
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
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_get_access_type.assert_called_with("test_user", 1, self.view.request)
        mock_project_assessment_status.assert_called_with(
            1, "ass123", self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)

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

    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_missing_parameters(self, mock_project_exists):
        self.view.body = json.dumps(
            {"project_cod": "123", "user_owner": "", "ass_cod": "ass123"}
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())
        mock_project_exists.assert_not_called()


class TestReadAssessmentStructureView(ViewBaseTest):
    view_class = ReadAssessmentStructureView
    request_method = "GET"
    request_body = json.dumps(
        {"project_cod": "123", "user_owner": "owner", "ass_cod": "ass123"}
    )

    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.assessmentExists", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.generateStructureForInterfaceForms",
        return_value={"structure": "data"},
    )
    def test_process_view_success(
        self,
        mock_generate_structure,
        mock_assessment_exists,
        mock_project_assessment_status,
        mock_get_project_id,
        mock_project_exists,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("structure", json.loads(response.body))
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_project_assessment_status.assert_called_with(
            1, "ass123", self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)
        self.assertTrue(mock_generate_structure.called)

    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=False)
    def test_process_view_project_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=True,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_assessment_not_started(
        self, mock_project_exists, mock_get_project_id, mock_project_assessment_status
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Data collection has not started.", response.body.decode())
        mock_project_exists.assert_called_with(
            "test_user", "owner", "123", self.view.request
        )
        mock_get_project_id.assert_called_with(1, "ass123", self.view.request)
        mock_project_assessment_status.assert_called_with(
            "owner", "123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectAssessmentStart.assessmentExists", return_value=False
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=False,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    def test_process_view_assessment_not_exist(
        self,
        mock_get_project_id,
        mock_project_exists,
        mock_project_assessment_status,
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
        mock_get_project_id.assert_called_with("owner", "123", self.view.request)
        mock_project_assessment_status.assert_called_with(
            1, "ass123", self.view.request
        )
        mock_assessment_exists.assert_called_with(1, "ass123", self.view.request)

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON", response.body.decode())

    def test_process_view_invalid_json_wrong(self):
        del self.view.body
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter",
            response.body.decode(),
        )

    def test_process_view_invalid_method(self):
        self.view.request.method = "POST"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_missing_parameters(self, mock_project_exists):
        self.view.body = json.dumps(
            {"project_cod": "123", "user_owner": "", "ass_cod": "ass123"}
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())
        mock_project_exists.assert_not_called()


class TestPushJsonToAssessmentView(ViewBaseTest):
    view_class = PushJsonToAssessmentView
    request_method = "POST"
    request_body = json.dumps(
        {
            "project_cod": "123",
            "user_owner": "owner",
            "ass_cod": "ass123",
            "json": "json",
        }
    )

    def test_process_view_test_push_invalid_method(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_test_push_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_test_push_no_data_json(self):
        self.view.body = '{"project_cod": "", "user_owner": "owner", "ass_cod": "ass123", "json": "json"}'
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=False)
    def test_process_view_test_push_no_project_exist(self, mock_projectExists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())

    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=4,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_test_push_access_no_allow_push(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to push information.",
            response.body.decode(),
        )

    @patch(
        "climmob.views.Api.projectAssessmentStart.assessmentExists", return_value=False
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_test_push_no_collection_code(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )

    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.assessmentExists", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_test_push_collection_no_started(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
        mock_projectAsessmentStatus,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Data collection has not started.", response.body.decode())

    @patch(
        "climmob.views.Api.projectAssessmentStart.isAssessmentOpen", return_value=False
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.assessmentExists", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_test_push_collection_no_more_data(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
        mock_projectAsessmentStatus,
        mock_isAssessmentOpen,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Data collection is closed. After you close data collection, no more data can be entered.",
            response.body.decode(),
        )

    @patch(
        "climmob.views.Api.projectAssessmentStart.ApiAssessmentPushProcess",
        return_value={"data": "data"},
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.generateStructureForInterfaceForms",
        return_value={"data": "data"},
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.isAssessmentOpen", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.assessmentExists", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_test_push_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
        mock_projectAsessmentStatus,
        mock_isAssessmentOpen,
        mock_generateStructureForInterfaceForms,
        mock_ApiAssessmentPushProcess,
    ):
        mock_ApiAssessmentPushProcess.return_value = MockResponse(
            status_code=200, body=b"Data registered."
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Data registered.", response.body.decode())


class TestApiAssessmentPushProcess(unittest.TestCase):
    def setUp(self):
        self.fake_self = FakeSelf()
        if not os.path.exists("./temp_test_repo"):
            os.makedirs("./temp_test_repo")

    def tearDown(self):
        if os.path.exists("./temp_test_repo"):
            shutil.rmtree("./temp_test_repo")

    def test_api_registration_no_structure(self):
        structure = {}
        dataworking = {}
        response = ApiAssessmentPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertEqual(response.body, b"The data do not have structure.")

    def test_api_registration_json_raises_exception(self):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST162",
                        "question_datafield": "package_id",
                        "question_requiredvalue": 1,
                        "question_dtype2": 1,
                        "question_dtype": "qst",
                    },
                    {
                        "question_code": "QST163",
                        "question_datafield": "farmer_code",
                        "question_requiredvalue": 1,
                        "question_dtype2": 1,
                        "question_dtype": "qst",
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "some_data",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                        "question_dtype": "qst",
                    },
                ]
            }
        ]

        dataworking = {
            "json": '{"package_id": "123", "bad_json":}',
            "user_owner": "Owner_user",
            "project_cod": "PRJ001",
            "ass_cod": "ASS001",
        }
        response = ApiAssessmentPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertIn(b"Error in the JSON sent by parameter.", response.body)

    def test_api_registration_error_json(self):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST162",
                        "question_datafield": "package_id",
                        "question_requiredvalue": 1,
                        "question_dtype2": 1,
                        "question_dtype": "qst",
                    },
                    {
                        "question_code": "QST163",
                        "question_datafield": "farmer_code",
                        "question_requiredvalue": 1,
                        "question_dtype2": 1,
                        "question_dtype": "qst",
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "some_data",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                        "question_dtype": "qst",
                    },
                ]
            }
        ]

        dataworking = {
            "json": json.dumps(
                {
                    "package_id": "5",
                    "farmer_code": "123",
                    "some_data": "A",
                    "clm_start": "2024-01-01 12:00:00",
                    "clm_end": "2024-01-01 12:05:00",
                    "bad_key": "Key",
                }
            ),
            "user_owner": "Owner_user",
            "project_cod": "PRJ001",
            "ass_cod": "ASS001",
        }
        response = ApiAssessmentPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertEqual(
            response.body,
            b"Error in the JSON sent by parameter. Check the permitted Keys.",
        )

    def test_api_registration_error_json_obligatory_keys(self):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST162",
                        "question_datafield": "package_id",
                        "question_requiredvalue": 1,
                        "question_dtype2": 1,
                        "question_dtype": "qst",
                    },
                    {
                        "question_code": "QST163",
                        "question_datafield": "farmer_code",
                        "question_requiredvalue": 1,
                        "question_dtype2": 1,
                        "question_dtype": "qst",
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "some_data",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                        "question_dtype": "qst",
                    },
                ]
            }
        ]

        dataworking = {
            "json": json.dumps(
                {
                    "farmer_code": "123",
                    "some_data": "A",
                    "clm_start": "2024-01-01 12:00:00",
                    "clm_end": "2024-01-01 12:05:00",
                }
            ),
            "user_owner": "Owner_user",
            "project_cod": "PRJ001",
            "ass_cod": "ASS001",
        }
        response = ApiAssessmentPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertIn(
            response.body,
            b"Error in the JSON sent by parameter. Check the obligatory Keys: package_id, farmer_code, some_data..",
        )

    def test_api_registration_error_json_obligatory_not_empty(self):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST162",
                        "question_datafield": "package_id",
                        "question_requiredvalue": 1,
                        "question_dtype2": 1,
                        "question_dtype": "qst",
                    },
                    {
                        "question_code": "QST163",
                        "question_datafield": "farmer_code",
                        "question_requiredvalue": 1,
                        "question_dtype2": 1,
                        "question_dtype": "qst",
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "some_data",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                        "question_dtype": "qst",
                    },
                ]
            }
        ]

        dataworking = {
            "json": json.dumps(
                {
                    "package_id": "",
                    "farmer_code": "123",
                    "some_data": "A",
                    "clm_start": "2024-01-01 12:00:00",
                    "clm_end": "2024-01-01 12:05:00",
                }
            ),
            "user_owner": "Owner_user",
            "project_cod": "PRJ001",
            "ass_cod": "ASS001",
        }
        response = ApiAssessmentPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertIn(
            response.body,
            b"Error in the JSON. Not all parameters have data. Check the columns: package_id.",
        )

    def test_api_registration_error_farmer_code_int(self):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST162",
                        "question_datafield": "package_id",
                        "question_requiredvalue": 1,
                        "question_dtype2": 1,
                        "question_dtype": "qst",
                    },
                    {
                        "question_code": "QST163",
                        "question_datafield": "farmer_code",
                        "question_requiredvalue": 1,
                        "question_dtype2": 1,
                        "question_dtype": "qst",
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "some_data",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                        "question_dtype": "qst",
                    },
                ]
            }
        ]

        dataworking = {
            "json": json.dumps(
                {
                    "package_id": "5",
                    "farmer_code": "one-two-three",
                    "some_data": "A",
                    "clm_start": "2024-01-01 12:00:00",
                    "clm_end": "2024-01-01 12:05:00",
                }
            ),
            "user_owner": "Owner_user",
            "project_cod": "PRJ001",
            "ass_cod": "ASS001",
        }
        response = ApiAssessmentPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertIn(
            response.body,
            b"ERROR: The farmer code must be a number.",
        )

    def test_api_registration_error_repeated_column(self):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST162",
                        "question_datafield": "package_id",
                        "question_requiredvalue": 1,
                        "question_dtype2": 1,
                        "question_dtype": "qst",
                    },
                    {
                        "question_code": "QST163",
                        "question_datafield": "farmer_code",
                        "question_requiredvalue": 1,
                        "question_dtype2": 1,
                        "question_dtype": "qst",
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "option_1",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                        "question_dtype": "qst",
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "option_2",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                        "question_dtype": "qst",
                    },
                ]
            }
        ]

        dataworking = {
            "json": json.dumps(
                {
                    "package_id": "5",
                    "farmer_code": "123",
                    "option_1": "A",
                    "option_2": "A",
                }
            ),
            "user_owner": "Owner_user",
            "project_cod": "PRJ001",
            "ass_cod": "ASS001",
        }
        response = ApiAssessmentPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertIn(
            response.body,
            b"You have repeated data in the next column: option_2. Remember that the options can not be repeated.",
        )

    @patch("climmob.views.Api.projectAssessmentStart.open")
    @patch("climmob.views.Api.projectAssessmentStart.uuid.uuid1")
    @patch("climmob.views.Api.projectAssessmentStart.os.path.join")
    @patch("climmob.views.Api.projectAssessmentStart.storeJSONInMySQL")
    @patch(
        "climmob.views.Api.projectAssessmentStart.os.path.exists", return_value=False
    )
    def test_api_registration_success(
        self,
        mock_storeJSONInMySQL,
        mock_os_path_join,
        mock_uuid1,
        mock_os_path_exist,
        mock_open,
    ):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST162",
                        "question_datafield": "package_id",
                        "question_requiredvalue": 1,
                        "question_dtype2": 1,
                        "question_dtype": "qst",
                    },
                    {
                        "question_code": "QST163",
                        "question_datafield": "farmer_code",
                        "question_requiredvalue": 1,
                        "question_dtype2": 1,
                        "question_dtype": "qst",
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "option_1",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                        "question_dtype": "qst",
                    },
                ]
            }
        ]

        dataworking = {
            "json": json.dumps(
                {
                    "package_id": "5",
                    "farmer_code": "123",
                    "option_1": "A",
                    "clm_start": "2024-01-01 12:00:00",
                    "clm_end": "2024-01-01 12:05:00",
                }
            ),
            "user_owner": "Owner_user",
            "project_cod": "PRJ001",
            "ass_cod": "ASS001",
        }
        response = ApiAssessmentPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )
        self.assertEqual(response.status, "200 OK")
        self.assertIn(response.body, b"Data registered.")

    @patch("climmob.views.Api.projectAssessmentStart.open")
    @patch("uuid.uuid1", return_value=UUID("12345678-1234-5678-1234-567812345678"))
    @patch(
        "climmob.views.Api.projectAssessmentStart.os.path.join",
        side_effect=os.path.join,
    )
    @patch("climmob.views.Api.projectAssessmentStart.storeJSONInMySQL")
    def test_api_registration_data_could_not_be_saved(
        self, mock_storeJSONInMySQL, mock_os_path_join, mock_uuid1, mock_open
    ):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST162",
                        "question_datafield": "package_id",
                        "question_requiredvalue": 1,
                        "question_dtype2": 1,
                        "question_dtype": "qst",
                    },
                    {
                        "question_code": "QST163",
                        "question_datafield": "farmer_code",
                        "question_requiredvalue": 1,
                        "question_dtype2": 1,
                        "question_dtype": "qst",
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "option_1",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                        "question_dtype": "qst",
                    },
                ]
            }
        ]
        unique_id = "12345678-1234-5678-1234-567812345678"
        dataworking = {
            "json": json.dumps(
                {
                    "package_id": "5",
                    "farmer_code": "123",
                    "option_1": "A",
                    "clm_start": "2024-01-01 12:00:00",
                    "clm_end": "2024-01-01 12:05:00",
                }
            ),
            "user_owner": "Owner_user",
            "project_cod": "PRJ001",
            "ass_cod": "ASS001",
        }

        json_dir = os.path.join(
            self.fake_self.request.registry.settings["user.repository"],
            "Owner_user",
            "PRJ001",
            "data",
            "ass",
            "ASS001",
            "json",
            unique_id,
        )

        os.makedirs(json_dir, exist_ok=True)

        log_path = os.path.join(json_dir, f"{unique_id}.log")
        with open(log_path, "w") as f:
            f.write(
                """<?xml version="1.0"?>
                <log>
                    <error Error="Simulated system failure"/>
                </log>"""
            )

        response = ApiAssessmentPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )

        self.assertEqual(response.status, "401 Unauthorized")
        self.assertIn(
            b"The data could not be saved. ERROR: Simulated system failure",
            response.body,
        )


class TestReadAssessmentDataView(ViewBaseTest):
    view_class = ReadAssessmentDataView
    request_method = "GET"
    request_body = json.dumps(
        {"project_cod": "123", "user_owner": "owner", "ass_cod": "ass123"}
    )

    def test_process_view_read_assessment_req_method(self):
        self.view.request.method = "POST"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    def test_process_view_read_assessment_json_wrong(self):
        del self.view.body
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter",
            response.body.decode(),
        )

    def test_process_view_read_assessment_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON", response.body.decode())

    def test_process_view_read_assessment_missing_parameters(
        self,
    ):
        self.view.body = json.dumps(
            {"project_cod": "123", "user_owner": "", "ass_cod": "ass123"}
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=False)
    def test_process_view_read_assessment_no_project_code(self, mock_projectExists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())

    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_read_assessment_data_collect_no_started(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_projectAsessmentStatus,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Data collection has not started.", response.body.decode())

    @patch(
        "climmob.views.Api.projectAssessmentStart.assessmentExists", return_value=False
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_read_assessment_no_data_collect_with_id(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_projectAsessmentStatus,
        mock_assessmentExists,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )

    @patch(
        "climmob.views.Api.projectAssessmentStart.getJSONResult",
        return_value={"data": "data", "assessments": "assessments"},
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.assessmentExists", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_read_assessment_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_projectAsessmentStatus,
        mock_assessmentExists,
        mock_getJSONResult,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn('{"structure": "a", "data": "data"}', response.body.decode())


class TestAssessmentDataCleaningView(ViewBaseTest):
    view_class = AssessmentDataCleaningView
    request_method = "POST"
    request_body = '{"project_cod": "123", "user_owner": "owner", "ass_cod": "ass123", "json": "json"}'

    def test_process_view_assessment_data_req_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_assessment_data_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON", response.body.decode())

    def test_process_view_assessment_data_missing_parameters(
        self,
    ):
        self.view.body = '{"project_cod": "", "user_owner": "owner", "ass_cod": "ass123", "json": "json"}'
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=False)
    def test_process_view_assessment_data_no_project_code(self, mock_projectExists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())

    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=4,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_assessment_data_access_not_allow_to_push(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to push information.",
            response.body.decode(),
        )

    @patch(
        "climmob.views.Api.projectAssessmentStart.assessmentExists", return_value=False
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_assessment_data_no_data_collect_id(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )

    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.assessmentExists", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_assessment_data_data_collect_no_started(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
        mock_projectAsessmentStatus,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Data collection has not started.", response.body.decode())

    @patch(
        "climmob.views.Api.projectAssessmentStart.isAssessmentOpen", return_value=False
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.assessmentExists", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_assessment_data_data_collect_closed(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
        mock_projectAsessmentStatus,
        mock_isAssessmentOpen,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Data collection is closed. After you close data collection, no more data can be entered.",
            response.body.decode(),
        )

    @patch(
        "climmob.views.Api.projectAssessmentStart.functionForProcessAndValidateUpdate"
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.generateStructureForInterfaceForms",
        return_value={"data": "data"},
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.isAssessmentOpen", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.projectAsessmentStatus",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.assessmentExists", return_value=True
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getAccessTypeForProject",
        return_value=1,
    )
    @patch(
        "climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch("climmob.views.Api.projectAssessmentStart.projectExists", return_value=True)
    def test_process_view_assessment_data_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_assessmentExists,
        mock_projectAsessmentStatus,
        mock_isAssessmentOpen,
        mock_generateStructureForInterfaceForms,
        mock_functionForProcessAndValidateUpdate,
    ):
        mock_functionForProcessAndValidateUpdate.return_value = MockResponse(
            status_code=200, body=b"Data registered."
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Data registered.", response.body.decode())


if __name__ == "__main__":
    unittest.main()
