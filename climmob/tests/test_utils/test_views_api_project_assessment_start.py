import json
import os
from uuid import UUID
import shutil
import unittest
from unittest.mock import patch, MagicMock

from pyramid.httpexceptions import HTTPForbidden, HTTPNotFound
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
    request_body = '{"project_cod": "123", "user_owner": "OWNER", "ass_cod": "ASS123"}'

    def setUp(self):
        super().setUp()
        self.request.params = {"Apikey": "fake-api-key"}
        patchers_funcs = [
            patch("climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner"),
            patch("climmob.views.Api.projectAssessmentStart.getAccessTypeForProject"),
            patch("climmob.views.Api.projectAssessmentStart.getProjectProgress"),
            patch("climmob.views.Api.projectAssessmentStart.projectAsessmentStatus"),
            patch("climmob.views.Api.projectAssessmentStart.checkAssessments"),
            patch(
                "climmob.views.Api.projectAssessmentStart.getTheGroupOfThePackageCodeAssessment"
            ),
            patch("climmob.views.Api.projectAssessmentStart.getProjectData"),
            patch("climmob.views.Api.projectAssessmentStart.generateAssessmentFiles"),
            patch(
                "climmob.views.Api.projectAssessmentStart.setAssessmentIndividualStatus"
            ),
            patch("climmob.views.Api.projectAssessmentStart.getPackages"),
            patch("climmob.views.Api.projectAssessmentStart.getDataFormPreview"),
            patch("climmob.views.Api.projectAssessmentStart.create_document_form"),
            patch("climmob.views.Api.projectAssessmentStart.update_project_status"),
            patch("climmob.views.classes.getUserByApiKey"),
            patch("climmob.views.classes.update_last_login"),
        ]
        self.mock_get_project = patchers_funcs[0].start()
        self.mock_get_access = patchers_funcs[1].start()
        self.mock_get_progress = patchers_funcs[2].start()
        self.mock_assess_status = patchers_funcs[3].start()
        self.mock_check_asses = patchers_funcs[4].start()
        self.mock_group_pack = patchers_funcs[5].start()
        self.mock_project_data = patchers_funcs[6].start()
        self.mock_gen_asses_files = patchers_funcs[7].start()
        self.mock_asses_status = patchers_funcs[8].start()
        self.mock_get_packages = patchers_funcs[9].start()
        self.mock_get_data_prev = patchers_funcs[10].start()
        self.mock_create_document = patchers_funcs[11].start()
        self.mock_update_project = patchers_funcs[12].start()
        self.mock_apiKey = patchers_funcs[13].start()
        self.mock_update_login = patchers_funcs[14].start()

        for patcher in patchers_funcs:
            self.addCleanup(patcher.stop)

        self.mock_get_project.return_value = 999
        self.mock_get_access.return_value = 1
        self.mock_get_progress.return_value = (
            {"regsubmissions": 2, "assessment": True},
            True,
        )
        self.mock_assess_status.return_value = True
        self.mock_check_asses.return_value = (True, {})
        self.mock_group_pack.return_value = {"data": "data"}
        self.mock_project_data.return_value = {
            "project_label_a": 1,
            "project_label_b": 2,
            "project_label_c": 3,
            "languages": [
                {"lang_code": "es"},
                {"lang_code": "en"},
            ],
        }
        self.mock_gen_asses_files.return_value = [
            {"code": "data", "result": True, "error": "error"},
        ]
        self.mock_get_packages.return_value = (2, 3)
        self.mock_get_data_prev.return_value = (2, 3)
        self.mock_update_project.return_value = (True, "")
        self.mock_apiKey.return_value = MagicMock(login="test_user")

    def test_project_exists_validator_fails(self):
        with patch.object(
            self.view,
            "_validate",
            side_effect=HTTPNotFound("There is no a project with that code."),
        ):
            response = self.view()
            self.assertEqual(response.status_code, 404)
            self.assertIn("There is no a project with that code", str(response.body))

    def test_project_open_validator_fails(self):
        with patch.object(
            self.view,
            "_validate",
            side_effect=HTTPForbidden(
                "This project has been closed and is now in read-only mode. Modifications are no longer permitted to ensure the integrity of the final data."
            ),
        ):
            response = self.view()
            self.assertEqual(response.status_code, 403)
            self.assertIn("closed", str(response.body))

    def test_missing_required_field_returns_bad_request(self):
        bad_body = '{"user_owner": "owner", "ass_cod": "ASS123"}'
        original_body = self.view.body
        self.view.body = bad_body
        response = self.view()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            "b'The following fields are required: project_cod, user_owner, ass_cod'",
            str(response.body),
        )
        self.view.body = original_body

    def test_only_post_method_allowed(self):
        original_method = self.request.method
        self.request.method = "GET"
        response = self.view()
        self.assertEqual(response.status_code, 405)
        self.assertEqual("b'Method GET Not Allowed'", str(response.body))
        self.request.method = original_method

    def test_access_type_4(self):
        self.mock_get_access.return_value = 4
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            "b'The access assigned for this project does not allow you to do this action.'",
            str(response.body),
        )
        self.mock_get_access.return_value = 1

    def test_already_started(self):
        self.mock_get_progress.return_value = (
            {"regsubmissions": 1, "assessment": True},
            True,
        )
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            "b'You cannot add data collection moments. You already started data collection.'",
            str(response.body),
        )
        self.mock_get_progress.return_value = (
            {"regsubmissions": 2, "assessment": True},
            True,
        )

    def test_collection_already_create(self):
        self.mock_assess_status.return_value = False
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual("b'Data collection has already started.'", str(response.body))
        self.mock_assess_status.return_value = True

    def test_must_create_ass(self):
        self.mock_get_progress.return_value = (
            {"regsubmissions": 2, "assessment": False},
            True,
        )
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            "b'You must have created the assessment forms.'", str(response.body)
        )
        self.mock_get_progress.return_value = (
            {"regsubmissions": 2, "assessment": True},
            True,
        )

    def test_check_asses(self):
        self.mock_check_asses.return_value = (False, "ERROR")
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(b'{"errors": "ERROR"}', response.body)
        self.mock_check_asses.return_value = (True, {})

    def test_problem_with_the_structure(self):
        self.mock_gen_asses_files.return_value = [
            {"code": "data", "result": False, "error": "error"},
        ]
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            b"There has been a problem in the creation of the basic structure of the project, this may be due to something wrong with the form. Contact the ClimMob team with the next message to get the solution to the problem: error",
            response.body,
        )
        self.mock_gen_asses_files.return_value = [
            {"code": "data", "result": True, "error": "error"},
        ]

    def test_success_if_languages(self):
        response = self.view.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"Data collection started.", response.body)

    def test_success_if_not_languages(self):
        self.mock_project_data.return_value = {
            "project_label_a": 1,
            "project_label_b": 2,
            "project_label_c": 3,
            "languages": [],
        }
        response = self.view.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"Data collection started.", response.body)


class TestCancelAssessmentApiView(ViewBaseTest):
    view_class = CancelAssessmentApiView
    request_method = "POST"
    request_body = '{"project_cod": "123", "user_owner": "OWNER", "ass_cod": "ASS123"}'

    def setUp(self):
        super().setUp()
        self.request.params = {"Apikey": "fake-api-key"}
        patchers_funcs = [
            patch("climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner"),
            patch("climmob.views.Api.projectAssessmentStart.getAccessTypeForProject"),
            patch("climmob.views.Api.projectAssessmentStart.isAssessmentOpen"),
            patch(
                "climmob.views.Api.projectAssessmentStart.setAssessmentIndividualStatus"
            ),
            patch("climmob.views.classes.getUserByApiKey"),
            patch("climmob.views.classes.update_last_login"),
            patch(
                "climmob.views.Api.projectAssessmentStart.clean_assessments_error_logs"
            ),
            patch(
                "climmob.views.Api.projectAssessmentStart.delete_anonymized_values_by_form_id"
            ),
        ]
        self.mock_get_project = patchers_funcs[0].start()
        self.mock_get_access = patchers_funcs[1].start()
        self.mock_assess_status = patchers_funcs[2].start()
        self.mock_ind_status = patchers_funcs[3].start()
        self.mock_apiKey = patchers_funcs[4].start()
        self.mock_update_login = patchers_funcs[5].start()
        self.mock_clean_assessments_error_logs = patchers_funcs[6].start()
        self.mock_delete_anonymized_values_by_form_id = patchers_funcs[7].start()

        for patcher in patchers_funcs:
            self.addCleanup(patcher.stop)

        self.mock_get_project.return_value = 999
        self.mock_get_access.return_value = 1
        self.mock_assess_status.return_value = True
        self.mock_ind_status.return_value = True
        self.mock_apiKey.return_value = MagicMock(login="test_user")

    def test_project_exists_validator_fails(self):
        with patch.object(
            self.view,
            "_validate",
            side_effect=HTTPNotFound("There is no a project with that code."),
        ):
            response = self.view()
            self.assertEqual(response.status_code, 404)
            self.assertIn("There is no a project with that code", str(response.body))

    def test_project_open_validator_fails(self):
        with patch.object(
            self.view,
            "_validate",
            side_effect=HTTPForbidden(
                "This project has been closed and is now in read-only mode. Modifications are no longer permitted to ensure the integrity of the final data."
            ),
        ):
            response = self.view()
            self.assertEqual(response.status_code, 403)
            self.assertIn("closed", str(response.body))

    def test_missing_required_field_returns_bad_request(self):
        bad_body = '{"user_owner": "owner", "ass_cod": "ASS123"}'
        original_body = self.view.body
        self.view.body = bad_body
        response = self.view()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            "b'The following fields are required: project_cod, user_owner, ass_cod'",
            str(response.body),
        )
        self.view.body = original_body

    def test_only_post_method_allowed(self):
        original_method = self.request.method
        self.request.method = "GET"
        response = self.view()
        self.assertEqual(response.status_code, 405)
        self.assertEqual("b'Method GET Not Allowed'", str(response.body))
        self.request.method = original_method

    def test_access_type_4(self):
        self.mock_get_access.return_value = 4
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            "b'The access assigned for this project does not allow you to cancel the assessment.'",
            str(response.body),
        )
        self.mock_get_access.return_value = 1

    def test_ass_has_not_started(self):
        self.mock_assess_status.return_value = False
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            "b'Data collection has not started. You cannot cancel it.'",
            str(response.body),
        )
        self.mock_assess_status.return_value = False

    def test_success(self):
        response = self.view.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual("b'Cancel data collection'", str(response.body))
        self.mock_clean_assessments_error_logs.assert_called_once_with(
            self.request, self.mock_get_project.return_value, "ASS123"
        )
        schema = "OWNER" + "_" + "123"
        self.mock_delete_anonymized_values_by_form_id.assert_called_once_with(
            schema, "ASS123"
        )


class TestCloseAssessmentApiView(ViewBaseTest):
    view_class = CloseAssessmentApiView
    request_method = "POST"
    request_body = '{"project_cod": "123", "user_owner": "OWNER", "ass_cod": "ASS123"}'

    def setUp(self):
        super().setUp()
        self.request.params = {"Apikey": "fake-api-key"}
        patchers_funcs = [
            patch("climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner"),
            patch("climmob.views.Api.projectAssessmentStart.getAccessTypeForProject"),
            patch("climmob.views.Api.projectAssessmentStart.assessmentExists"),
            patch("climmob.views.Api.projectAssessmentStart.projectAsessmentStatus"),
            patch(
                "climmob.views.Api.projectAssessmentStart.setAssessmentIndividualStatus"
            ),
            patch("climmob.views.classes.getUserByApiKey"),
            patch("climmob.views.classes.update_last_login"),
        ]
        self.mock_get_project = patchers_funcs[0].start()
        self.mock_get_access = patchers_funcs[1].start()
        self.mock_assess_exists = patchers_funcs[2].start()
        self.mock_assess_status = patchers_funcs[3].start()
        self.mock_individual_status = patchers_funcs[4].start()
        self.mock_apiKey = patchers_funcs[5].start()
        self.mock_update_login = patchers_funcs[6].start()

        for patcher in patchers_funcs:
            self.addCleanup(patcher.stop)

        self.mock_get_project.return_value = 999
        self.mock_get_access.return_value = 1
        self.mock_assess_exists.return_value = True
        self.mock_assess_status.return_value = False
        self.mock_individual_status.return_value = Response(
            status=200,
            body="Data registered.",
        )
        self.mock_apiKey.return_value = MagicMock(login="test_user")

    def test_project_exists_validator_fails(self):
        with patch.object(
            self.view,
            "_validate",
            side_effect=HTTPNotFound("There is no a project with that code."),
        ):
            response = self.view()
            self.assertEqual(response.status_code, 404)
            self.assertIn("There is no a project with that code", str(response.body))

    def test_project_open_validator_fails(self):
        with patch.object(
            self.view,
            "_validate",
            side_effect=HTTPForbidden(
                "This project has been closed and is now in read-only mode. Modifications are no longer permitted to ensure the integrity of the final data."
            ),
        ):
            response = self.view()
            self.assertEqual(response.status_code, 403)
            self.assertIn("closed", str(response.body))

    def test_missing_required_field_returns_bad_request(self):
        bad_body = '{"user_owner": "owner", "ass_cod": "ASS123"}'
        original_body = self.view.body
        self.view.body = bad_body
        response = self.view()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            "b'The following fields are required: project_cod, user_owner, ass_cod'",
            str(response.body),
        )
        self.view.body = original_body

    def test_only_post_method_allowed(self):
        original_method = self.request.method
        self.request.method = "GET"
        response = self.view()
        self.assertEqual(response.status_code, 405)
        self.assertEqual("b'Method GET Not Allowed'", str(response.body))
        self.request.method = original_method

    def test_access_type_4(self):
        self.mock_get_access.return_value = 4
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            "b'The access assigned for this project does not allow you to cancel the assessment.'",
            str(response.body),
        )
        self.mock_get_access.return_value = 1

    def test_no_data_collection_with_that_code(self):
        self.mock_assess_exists.return_value = False
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            "b'There is no data collection with that code.'", str(response.body)
        )
        self.mock_assess_exists.return_value = True

    def test_ass_has_not_started(self):
        self.mock_assess_status.return_value = True
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            "b'Data collection has not started. You cannot cancel it.'",
            str(response.body),
        )
        self.mock_assess_status.return_value = False

    def test_success(self):
        response = self.view.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual("b'Data collection closed.'", str(response.body))


class TestReadAssessmentStructureView(ViewBaseTest):
    view_class = ReadAssessmentStructureView
    request_method = "GET"
    request_body = '{"project_cod": "123", "user_owner": "OWNER", "ass_cod": "ASS123"}'

    def setUp(self):
        super().setUp()
        self.request.params = {"Apikey": "fake-api-key"}
        patchers_funcs = [
            patch("climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner"),
            patch("climmob.views.Api.projectAssessmentStart.projectAsessmentStatus"),
            patch("climmob.views.Api.projectAssessmentStart.assessmentExists"),
            patch(
                "climmob.views.Api.projectAssessmentStart.generateStructureForInterfaceForms"
            ),
            patch("climmob.views.classes.getUserByApiKey"),
            patch("climmob.views.classes.update_last_login"),
        ]

        self.mock_get_project = patchers_funcs[0].start()
        self.mock_assess_status = patchers_funcs[1].start()
        self.mock_assess_exists = patchers_funcs[2].start()
        self.mock_structure = patchers_funcs[3].start()
        self.mock_apiKey = patchers_funcs[4].start()
        self.mock_update_login = patchers_funcs[5].start()

        for patcher in patchers_funcs:
            self.addCleanup(patcher.stop)

        self.mock_get_project.return_value = 999
        self.mock_assess_exists.return_value = True
        self.mock_assess_status.return_value = False
        self.mock_structure.return_value = {"structure": "data"}
        self.mock_apiKey.return_value = MagicMock(login="test_user")

    def test_project_exists_validator_fails(self):
        with patch.object(
            self.view,
            "_validate",
            side_effect=HTTPNotFound("There is no a project with that code."),
        ):
            response = self.view()
            self.assertEqual(response.status_code, 404)
            self.assertIn("There is no a project with that code", str(response.body))

    def test_project_open_validator_fails(self):
        with patch.object(
            self.view,
            "_validate",
            side_effect=HTTPForbidden(
                "This project has been closed and is now in read-only mode. Modifications are no longer permitted to ensure the integrity of the final data."
            ),
        ):
            response = self.view()
            self.assertEqual(response.status_code, 403)
            self.assertIn("closed", str(response.body))

    def test_missing_required_field_returns_bad_request(self):
        bad_body = '{"user_owner": "owner", "ass_cod": "ASS123"}'
        original_body = self.view.body
        self.view.body = bad_body
        response = self.view()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            "b'The following fields are required: project_cod, user_owner, ass_cod'",
            str(response.body),
        )
        self.view.body = original_body

    def test_only_GET_method_allowed(self):
        original_method = self.request.method
        self.request.method = "POST"
        response = self.view()
        self.assertEqual(response.status_code, 405)
        self.assertEqual("b'Method POST Not Allowed'", str(response.body))
        self.request.method = original_method

    def test_ass_has_not_started(self):
        self.mock_assess_status.return_value = True
        response = self.view.get()
        self.assertEqual(response.status_code, 401)
        self.assertEqual("b'Data collection has not started.'", str(response.body))
        self.mock_assess_status.return_value = False

    def test_no_data_collection_with_that_code(self):
        self.mock_assess_exists.return_value = False
        response = self.view.get()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            "b'There is no data collection with that code.'", str(response.body)
        )
        self.mock_assess_exists.return_value = True

    def test_success(self):
        response = self.view.get()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'{"structure": "data"}', response.body)


class TestPushJsonToAssessmentView(ViewBaseTest):
    view_class = PushJsonToAssessmentView
    request_method = "POST"
    request_body = '{"project_cod": "123", "user_owner": "OWNER", "ass_cod": "ASS123", "json": "json"}'

    def setUp(self):
        super().setUp()
        self.request.params = {"Apikey": "fake-api-key"}
        patchers_funcs = [
            patch("climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner"),
            patch("climmob.views.Api.projectAssessmentStart.getAccessTypeForProject"),
            patch("climmob.views.Api.projectAssessmentStart.assessmentExists"),
            patch("climmob.views.Api.projectAssessmentStart.projectAsessmentStatus"),
            patch("climmob.views.Api.projectAssessmentStart.isAssessmentOpen"),
            patch(
                "climmob.views.Api.projectAssessmentStart.generateStructureForInterfaceForms"
            ),
            patch("climmob.views.Api.projectAssessmentStart.ApiAssessmentPushProcess"),
            patch("climmob.views.classes.getUserByApiKey"),
            patch("climmob.views.classes.update_last_login"),
        ]
        self.mock_get_project = patchers_funcs[0].start()
        self.mock_get_access = patchers_funcs[1].start()
        self.mock_assess_exists = patchers_funcs[2].start()
        self.mock_assess_status = patchers_funcs[3].start()
        self.mock_is_open = patchers_funcs[4].start()
        self.mock_gen_structure = patchers_funcs[5].start()
        self.mock_push_process = patchers_funcs[6].start()
        self.mock_apiKey = patchers_funcs[7].start()
        self.mock_update_login = patchers_funcs[8].start()

        for patcher in patchers_funcs:
            self.addCleanup(patcher.stop)

        self.mock_get_project.return_value = 999
        self.mock_get_access.return_value = 1
        self.mock_assess_exists.return_value = True
        self.mock_assess_status.return_value = False
        self.mock_is_open.return_value = True
        self.mock_push_process.return_value = Response(
            status=200,
            body="Data registered.",
        )
        self.mock_apiKey.return_value = MagicMock(login="test_user")

    def test_project_exists_validator_fails(self):
        with patch.object(
            self.view,
            "_validate",
            side_effect=HTTPNotFound("There is no a project with that code."),
        ):
            response = self.view()
            self.assertEqual(response.status_code, 404)
            self.assertIn("There is no a project with that code", str(response.body))

    def test_project_open_validator_fails(self):
        with patch.object(
            self.view,
            "_validate",
            side_effect=HTTPForbidden(
                "This project has been closed and is now in read-only mode. Modifications are no longer permitted to ensure the integrity of the final data."
            ),
        ):
            response = self.view()
            self.assertEqual(response.status_code, 403)
            self.assertIn("closed", str(response.body))

    def test_missing_required_field_returns_bad_request(self):
        bad_body = '{"user_owner": "owner", "ass_cod": "ASS123"}'
        original_body = self.view.body
        self.view.body = bad_body
        response = self.view()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            "b'The following fields are required: project_cod, user_owner, ass_cod, json'",
            str(response.body),
        )
        self.view.body = original_body

    def test_only_post_method_allowed(self):
        original_method = self.request.method
        self.request.method = "GET"
        response = self.view()
        self.assertEqual(response.status_code, 405)
        self.assertEqual("b'Method GET Not Allowed'", str(response.body))
        self.request.method = original_method

    def test_access_type_4(self):
        self.mock_get_access.return_value = 4
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            "b'The access assigned for this project does not allow you to push information.'",
            str(response.body),
        )
        self.mock_get_access.return_value = 1

    def test_no_data_collection_with_that_code(self):
        self.mock_assess_exists.return_value = False
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            "b'There is no data collection with that code.'", str(response.body)
        )
        self.mock_assess_exists.return_value = True

    def test_ass_has_not_started(self):
        self.mock_assess_status.return_value = True
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual("b'Data collection has not started.'", str(response.body))
        self.mock_assess_status.return_value = False

    def test_assessment_is_closed(self):
        self.mock_is_open.return_value = False
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            "b'Data collection is closed. After you close data collection, no more data can be entered.'",
            str(response.body),
        )
        self.mock_is_open.return_value = True

    def test_success(self):
        response = self.view.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual("b'Data registered.'", str(response.body))


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
    @patch(
        "climmob.views.Api.projectAssessmentStart.storeJSONInMySQL",
        return_value=(True, ""),
    )
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
    @patch(
        "climmob.views.Api.projectAssessmentStart.storeJSONInMySQL",
        return_value=(True, ""),
    )
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
    request_body = '{"project_cod": "123", "user_owner": "OWNER", "ass_cod": "ASS123"}'

    def setUp(self):
        super().setUp()
        self.request.params = {"Apikey": "fake-api-key"}
        patchers_funcs = [
            patch("climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner"),
            patch("climmob.views.Api.projectAssessmentStart.projectAsessmentStatus"),
            patch("climmob.views.Api.projectAssessmentStart.assessmentExists"),
            patch("climmob.views.Api.projectAssessmentStart.getJSONResult"),
            patch("climmob.views.classes.getUserByApiKey"),
            patch("climmob.views.classes.update_last_login"),
        ]

        self.mock_get_project = patchers_funcs[0].start()
        self.mock_assess_status = patchers_funcs[1].start()
        self.mock_assess_exists = patchers_funcs[2].start()
        self.mock_json_result = patchers_funcs[3].start()
        self.mock_apiKey = patchers_funcs[4].start()
        self.mock_update_login = patchers_funcs[5].start()

        for patcher in patchers_funcs:
            self.addCleanup(patcher.stop)

        self.mock_get_project.return_value = 999
        self.mock_assess_exists.return_value = True
        self.mock_assess_status.return_value = False
        self.mock_json_result.return_value = {
            "data": "data",
            "assessments": "assessments",
        }
        self.mock_apiKey.return_value = MagicMock(login="test_user")

    def test_project_exists_validator_fails(self):
        with patch.object(
            self.view,
            "_validate",
            side_effect=HTTPNotFound("There is no a project with that code."),
        ):
            response = self.view()
            self.assertEqual(response.status_code, 404)
            self.assertIn("There is no a project with that code", str(response.body))

    def test_project_open_validator_fails(self):
        with patch.object(
            self.view,
            "_validate",
            side_effect=HTTPForbidden(
                "This project has been closed and is now in read-only mode. Modifications are no longer permitted to ensure the integrity of the final data."
            ),
        ):
            response = self.view()
            self.assertEqual(response.status_code, 403)
            self.assertIn("closed", str(response.body))

    def test_missing_required_field_returns_bad_request(self):
        bad_body = '{"user_owner": "owner", "ass_cod": "ASS123"}'
        original_body = self.view.body
        self.view.body = bad_body
        response = self.view()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            "b'The following fields are required: project_cod, user_owner, ass_cod'",
            str(response.body),
        )
        self.view.body = original_body

    def test_only_GET_method_allowed(self):
        original_method = self.request.method
        self.request.method = "POST"
        response = self.view()
        self.assertEqual(response.status_code, 405)
        self.assertEqual("b'Method POST Not Allowed'", str(response.body))
        self.request.method = original_method

    def test_ass_has_not_started(self):
        self.mock_assess_status.return_value = True
        response = self.view.get()
        self.assertEqual(response.status_code, 401)
        self.assertEqual("b'Data collection has not started.'", str(response.body))
        self.mock_assess_status.return_value = False

    def test_no_data_collection_with_that_code(self):
        self.mock_assess_exists.return_value = False
        response = self.view.get()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            "b'There is no data collection with that code.'", str(response.body)
        )
        self.mock_assess_exists.return_value = True

    def test_success(self):
        response = self.view.get()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'{"structure": "a", "data": "data"}', response.body)


class TestAssessmentDataCleaningView(ViewBaseTest):
    view_class = AssessmentDataCleaningView
    request_method = "POST"
    request_body = '{"project_cod": "123", "user_owner": "OWNER", "ass_cod": "ASS123", "json": "JSON"}'

    def setUp(self):
        super().setUp()
        self.request.params = {"Apikey": "fake-api-key"}
        patchers_funcs = [
            patch("climmob.views.Api.projectAssessmentStart.getTheProjectIdForOwner"),
            patch("climmob.views.Api.projectAssessmentStart.getAccessTypeForProject"),
            patch("climmob.views.Api.projectAssessmentStart.assessmentExists"),
            patch("climmob.views.Api.projectAssessmentStart.projectAsessmentStatus"),
            patch("climmob.views.Api.projectAssessmentStart.isAssessmentOpen"),
            patch(
                "climmob.views.Api.projectAssessmentStart.generateStructureForInterfaceForms"
            ),
            patch(
                "climmob.views.Api.projectAssessmentStart.functionForProcessAndValidateUpdate"
            ),
            patch("climmob.views.classes.getUserByApiKey"),
            patch("climmob.views.classes.update_last_login"),
        ]
        self.mock_get_project = patchers_funcs[0].start()
        self.mock_get_access = patchers_funcs[1].start()
        self.mock_assess_exists = patchers_funcs[2].start()
        self.mock_assess_status = patchers_funcs[3].start()
        self.mock_is_open = patchers_funcs[4].start()
        self.mock_gen_structure = patchers_funcs[5].start()
        self.mock_process = patchers_funcs[6].start()
        self.mock_apiKey = patchers_funcs[7].start()
        self.mock_update_login = patchers_funcs[8].start()

        for patcher in patchers_funcs:
            self.addCleanup(patcher.stop)

        self.mock_get_project.return_value = 999
        self.mock_get_access.return_value = 1
        self.mock_assess_exists.return_value = True
        self.mock_assess_status.return_value = False
        self.mock_is_open.return_value = True
        self.mock_process.return_value = Response(
            status=200,
            body="Data registered.",
        )
        self.mock_apiKey.return_value = MagicMock(login="test_user")

    def test_project_exists_validator_fails(self):
        with patch.object(
            self.view,
            "_validate",
            side_effect=HTTPNotFound("There is no a project with that code."),
        ):
            response = self.view()
            self.assertEqual(response.status_code, 404)
            self.assertIn("There is no a project with that code", str(response.body))

    def test_project_open_validator_fails(self):
        with patch.object(
            self.view,
            "_validate",
            side_effect=HTTPForbidden(
                "This project has been closed and is now in read-only mode. Modifications are no longer permitted to ensure the integrity of the final data."
            ),
        ):
            response = self.view()
            self.assertEqual(response.status_code, 403)
            self.assertIn("closed", str(response.body))

    def test_missing_required_field_returns_bad_request(self):
        bad_body = '{"user_owner": "owner", "ass_cod": "ASS123", "json": "{}"}'
        original_body = self.view.body
        self.view.body = bad_body
        response = self.view()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            "b'The following fields are required: project_cod, user_owner, ass_cod, json'",
            str(response.body),
        )
        self.view.body = original_body

    def test_only_post_method_allowed(self):
        original_method = self.request.method
        self.request.method = "GET"
        response = self.view()
        self.assertEqual(response.status_code, 405)
        self.assertEqual("b'Method GET Not Allowed'", str(response.body))
        self.request.method = original_method

    def test_access_type_4(self):
        self.mock_get_access.return_value = 4
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            "b'The access assigned for this project does not allow you to push information.'",
            str(response.body),
        )
        self.mock_get_access.return_value = 1

    def test_no_data_collection_with_that_code(self):
        self.mock_assess_exists.return_value = False
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            "b'There is no data collection with that code.'", str(response.body)
        )
        self.mock_assess_exists.return_value = True

    def test_ass_has_not_started(self):
        self.mock_assess_status.return_value = True
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual("b'Data collection has not started.'", str(response.body))
        self.mock_assess_status.return_value = False

    def test_assessment_is_closed(self):
        self.mock_is_open.return_value = False
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            "b'Data collection is closed. After you close data collection, no more data can be entered.'",
            str(response.body),
        )
        self.mock_is_open.return_value = True

    def test_success(self):
        response = self.view.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual("b'Data registered.'", str(response.body))


if __name__ == "__main__":
    unittest.main()
