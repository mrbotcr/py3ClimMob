import json
import unittest
from unittest.mock import patch, MagicMock

from climmob.tests.test_utils.common import ViewBaseTest
from climmob.views.Api.project_analysis import (
    ReadDataOfProjectViewApi,
    ReadVariablesForAnalysisViewApi,
    GenerateAnalysisByApiViewApi,
)
from climmob.views.validators.ProjectExistsValidator import ProjectExistsValidator
from climmob.views.validators.project import HasAccessToProjectValidator


class TestReadDataOfProjectViewAPI(ViewBaseTest):
    view_class = ReadDataOfProjectViewApi
    body = {"project_cod": "123", "user_owner": "owner"}
    request_body = json.dumps(body)

    def test_has_validators(self):
        self.assertEqual(
            self.view.validators, (ProjectExistsValidator, HasAccessToProjectValidator)
        )

    @patch(
        "climmob.views.Api.project_analysis.getJSONResult",
        return_value={"data": "some_data"},
    )
    def test_get_success(self, mock_get_json_result):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.get()

        self.assertEqual(response.status_code, 200)
        self.assertIn("some_data", response.body.decode())

        mock_get_json_result.assert_called_once_with(
            self.body["user_owner"],
            self.view.context.active_project_id,
            self.body["project_cod"],
            self.view.request,
            anonymize=True,
        )


class TestReadVariablesForAnalysisViewAPI(unittest.TestCase):
    def setUp(self):
        self.view = ReadVariablesForAnalysisViewApi(MagicMock())
        self.view.request.method = "GET"
        self.view.user = MagicMock(login="test_user")
        self.view.body = json.dumps({"project_cod": "123", "user_owner": "owner"})

    def mock_translation(self, message):
        return message

    @patch(
        "climmob.views.Api.project_analysis.getQuestionsByType",
        return_value=(["question1", "question2"], ["assessment1"]),
    )
    @patch(
        "climmob.views.Api.project_analysis.getProjectProgress",
        return_value=(
            {"assessments": [{"ass_status": 1, "asstotal": 10}], "regtotal": 6},
            0,
        ),
    )
    @patch(
        "climmob.views.Api.project_analysis.getProjectData",
        return_value={"project_registration_and_analysis": 1},
    )
    @patch("climmob.views.Api.project_analysis.getAccessTypeForProject", return_value=1)
    @patch("climmob.views.Api.project_analysis.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.project_analysis.projectExists", return_value=True)
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
        self.assertEqual(
            response_data,
            {
                "dataForAnalysis": ["question1", "question2"],
                "assessmentsList": ["assessment1"],
            },
        )

        # Verify that all the patched methods were called
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_getProjectData.called)
        self.assertTrue(mock_getProjectProgress.called)
        self.assertTrue(mock_getQuestionsByType.called)

    @patch("climmob.views.Api.project_analysis.projectExists", return_value=False)
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

    @patch("json.loads", side_effect=json.JSONDecodeError("Expecting value", "", 0))
    def test_process_view_invalid_body(self, mock_json_loads):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = ""

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )
        self.assertTrue(mock_json_loads.called)

    def test_process_view_post_method(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.method = "POST"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    @patch("climmob.views.Api.project_analysis.getAccessTypeForProject", return_value=4)
    @patch("climmob.views.Api.project_analysis.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.project_analysis.projectExists", return_value=True)
    def test_process_read_variables_analysis_no_allow_create_analysis(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
    ):
        self.view._ = self.mock_translation
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body.decode(),
            "The access assigned for this project does not allow you to create an analysis.",
        )
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)

    @patch(
        "climmob.views.Api.project_analysis.getProjectProgress",
        return_value=(
            {"assessments": [{"ass_status": 1, "asstotal": 0}], "regtotal": 0},
            0,
        ),
    )
    @patch(
        "climmob.views.Api.project_analysis.getProjectData",
        return_value={"project_registration_and_analysis": 1},
    )
    @patch("climmob.views.Api.project_analysis.getAccessTypeForProject", return_value=1)
    @patch("climmob.views.Api.project_analysis.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.project_analysis.projectExists", return_value=True)
    def test_process_view_read_variables_analysis_no_enough_info(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_getProjectData,
        mock_getProjectProgress,
    ):
        self.view._ = self.mock_translation  # Mock translation function
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"You don't have the amount of information needed to do a ClimMob analysis.",
        )
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_getProjectData.called)
        self.assertTrue(mock_getProjectProgress.called)


class TestGenerateAnalysisByApiViewAPI(unittest.TestCase):
    def setUp(self):
        self.view = GenerateAnalysisByApiViewApi(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view.body = json.dumps(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "variables_to_analyze": ["var1", "var2"],
                "infosheets": "1",
            }
        )

    def mock_translation(self, message):
        return message

    @patch(
        "climmob.views.Api.project_analysis.processToGenerateTheReport",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.project_analysis.getQuestionsByType",
        return_value=(
            {"key1": [{"codeForAnalysis": "var1"}, {"codeForAnalysis": "var2"}]},
            ["assessment1"],
        ),
    )
    @patch(
        "climmob.views.Api.project_analysis.getProjectProgress",
        return_value=(
            {"assessments": [{"ass_status": 1, "asstotal": 10}], "regtotal": 6},
            0,
        ),
    )
    @patch(
        "climmob.views.Api.project_analysis.getProjectData",
        return_value={"project_registration_and_analysis": 1},
    )
    @patch("climmob.views.Api.project_analysis.getAccessTypeForProject", return_value=1)
    @patch("climmob.views.Api.project_analysis.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.project_analysis.projectExists", return_value=True)
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

    @patch(
        "climmob.views.Api.project_analysis.processToGenerateTheReport",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.project_analysis.getQuestionsByType",
        return_value=(
            {"key1": [{"codeForAnalysis": "var1"}, {"codeForAnalysis": "var2"}]},
            ["assessment1"],
        ),
    )
    @patch(
        "climmob.views.Api.project_analysis.getProjectProgress",
        return_value=(
            {"assessments": [{"ass_status": 1, "asstotal": 10}], "regtotal": 6},
            0,
        ),
    )
    @patch(
        "climmob.views.Api.project_analysis.getProjectData",
        return_value={"project_registration_and_analysis": 1},
    )
    @patch("climmob.views.Api.project_analysis.getAccessTypeForProject", return_value=1)
    @patch("climmob.views.Api.project_analysis.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.project_analysis.projectExists", return_value=True)
    def test_process_view_success_2(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_getProjectData,
        mock_getProjectProgress,
        mock_getQuestionsByType,
        mock_processToGenerateTheReport,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "variables_to_analyze": ["var1", "var2"],
                "infosheets": "0",
            }
        )
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            b"The analysis is being generated, it is a process that requires time to be processed, as soon as it is ready you will be able to see it in the download list.",
            response.body,
        )

        # Verify that all the patched methods were called
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_getProjectData.called)
        self.assertTrue(mock_getProjectProgress.called)
        self.assertTrue(mock_getQuestionsByType.called)
        self.assertTrue(mock_processToGenerateTheReport.called)

    @patch("climmob.views.Api.project_analysis.projectExists", return_value=False)
    def test_process_view_project_not_exist(self, mock_projectExists):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("This project does not exist.", response.body.decode())
        self.assertTrue(mock_projectExists.called)

    @patch("climmob.views.Api.project_analysis.getAccessTypeForProject", return_value=4)
    @patch("climmob.views.Api.project_analysis.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.project_analysis.projectExists", return_value=True)
    def test_process_view_no_access(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
    ):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to create an analysis.",
            response.body.decode(),
        )

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)

    @patch(
        "climmob.views.Api.project_analysis.getProjectProgress",
        return_value=(
            {"assessments": [{"ass_status": 0, "asstotal": 0}], "regtotal": 4},
            0,
        ),
    )
    @patch(
        "climmob.views.Api.project_analysis.getProjectData",
        return_value={"project_registration_and_analysis": 0},
    )
    @patch("climmob.views.Api.project_analysis.getAccessTypeForProject", return_value=1)
    @patch("climmob.views.Api.project_analysis.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.project_analysis.projectExists", return_value=True)
    def test_process_view_not_enough_data(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_getProjectData,
        mock_getProjectProgress,
    ):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You don't have the amount of information needed to do a ClimMob analysis.",
            response.body.decode(),
        )

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_getProjectData.called)
        self.assertTrue(mock_getProjectProgress.called)

    ###

    @patch(
        "climmob.views.Api.project_analysis.getQuestionsByType",
        side_effect=Exception("boom"),
    )
    @patch(
        "climmob.views.Api.project_analysis.getProjectProgress",
        return_value=(
            {"assessments": [{"ass_status": 1, "asstotal": 10}], "regtotal": 6},
            0,
        ),
    )
    @patch(
        "climmob.views.Api.project_analysis.getProjectData",
        return_value={"project_registration_and_analysis": 1},
    )
    @patch("climmob.views.Api.project_analysis.getAccessTypeForProject", return_value=1)
    @patch("climmob.views.Api.project_analysis.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.project_analysis.projectExists", return_value=True)
    def test_process_view_exception_trow(
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

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            b"Problem with the data sent in the parameter: variables_to_analyze",
            response.body,
        )

        # Verify that all the patched methods were called
        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_getProjectData.called)
        self.assertTrue(mock_getProjectProgress.called)
        self.assertTrue(mock_getQuestionsByType.called)

    ###

    def test_process_view_invalid_json(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch("json.loads", side_effect=json.JSONDecodeError("Expecting value", "", 0))
    def test_process_view_invalid_body(self, mock_json_loads):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = ""

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )
        self.assertTrue(mock_json_loads.called)

    def test_process_view_post_method(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    @patch(
        "climmob.views.Api.project_analysis.getQuestionsByType",
        return_value=({"key1": [{"codeForAnalysis": "var1"}]}, ["assessment1"]),
    )
    @patch(
        "climmob.views.Api.project_analysis.getProjectProgress",
        return_value=(
            {"assessments": [{"ass_status": 1, "asstotal": 10}], "regtotal": 6},
            0,
        ),
    )
    @patch(
        "climmob.views.Api.project_analysis.getProjectData",
        return_value={"project_registration_and_analysis": 1},
    )
    @patch("climmob.views.Api.project_analysis.getAccessTypeForProject", return_value=1)
    @patch("climmob.views.Api.project_analysis.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.project_analysis.projectExists", return_value=True)
    def test_process_view_no_variables(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_getProjectData,
        mock_getProjectProgress,
        mock_getQuestionsByType,
    ):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = json.dumps(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "variables_to_analyze": [],
                "infosheets": "1",
            }
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The variable_to_analyze parameter must contain data.",
            response.body.decode(),
        )

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_getProjectData.called)
        self.assertTrue(mock_getProjectProgress.called)
        self.assertTrue(mock_getQuestionsByType.called)

    @patch(
        "climmob.views.Api.project_analysis.getQuestionsByType",
        return_value=({"key1": [{"codeForAnalysis": "var1"}]}, ["assessment1"]),
    )
    @patch(
        "climmob.views.Api.project_analysis.getProjectProgress",
        return_value=(
            {"assessments": [{"ass_status": 1, "asstotal": 10}], "regtotal": 6},
            0,
        ),
    )
    @patch(
        "climmob.views.Api.project_analysis.getProjectData",
        return_value={"project_registration_and_analysis": 1},
    )
    @patch("climmob.views.Api.project_analysis.getAccessTypeForProject", return_value=1)
    @patch("climmob.views.Api.project_analysis.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.project_analysis.projectExists", return_value=True)
    def test_process_view_invalid_variables(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_getProjectData,
        mock_getProjectProgress,
        mock_getQuestionsByType,
    ):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = json.dumps(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "variables_to_analyze": ["invalid_var"],
                "infosheets": "1",
            }
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "One of the variables you sent for analysis does not exist.",
            response.body.decode(),
        )

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_getProjectData.called)
        self.assertTrue(mock_getProjectProgress.called)
        self.assertTrue(mock_getQuestionsByType.called)

    @patch(
        "climmob.views.Api.project_analysis.getQuestionsByType",
        return_value=({"key1": [{"codeForAnalysis": "var1"}]}, ["assessment1"]),
    )
    @patch(
        "climmob.views.Api.project_analysis.getProjectProgress",
        return_value=(
            {"assessments": [{"ass_status": 1, "asstotal": 10}], "regtotal": 6},
            0,
        ),
    )
    @patch(
        "climmob.views.Api.project_analysis.getProjectData",
        return_value={"project_registration_and_analysis": 1},
    )
    @patch("climmob.views.Api.project_analysis.getAccessTypeForProject", return_value=1)
    @patch("climmob.views.Api.project_analysis.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.project_analysis.projectExists", return_value=True)
    def test_process_view_variables_not_list(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_getProjectData,
        mock_getProjectProgress,
        mock_getQuestionsByType,
    ):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = json.dumps(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "variables_to_analyze": "invalid_type",
                "infosheets": "1",
            }
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The variable_to_analyze parameter must be a list.", response.body.decode()
        )

        self.assertTrue(mock_projectExists.called)
        self.assertTrue(mock_getTheProjectIdForOwner.called)
        self.assertTrue(mock_getAccessTypeForProject.called)
        self.assertTrue(mock_getProjectData.called)
        self.assertTrue(mock_getProjectProgress.called)
        self.assertFalse(mock_getQuestionsByType.called)


if __name__ == "__main__":
    unittest.main()
