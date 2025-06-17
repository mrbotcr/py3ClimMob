import json
import unittest
from unittest.mock import patch, MagicMock

from climmob.tests.test_utils.common import ViewBaseTest
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
from climmob.views.validators import TextField, IntegerField, BinaryField
from climmob.views.validators.ProjectExistsValidator import ProjectExistsValidator


class ProjectAssessmentBaseTest(ViewBaseTest):
    body = {}
    patchers = {}
    mocks = {}

    def setUp(self):
        super().setUp()

        for key in self.mocks:
            self.mocks[key].reset_mock()
            self.mocks[key].return_value = self.patchers[key]["return_value"]

    @classmethod
    def setUpClass(cls):
        cls.patchers["getTheProjectIdForOwner"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.getTheProjectIdForOwner"
            ),
            "return_value": 1,
        }
        cls.patchers["getAccessTypeForProject"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.getAccessTypeForProject"
            ),
            "return_value": 1,
        }
        for key in cls.patchers:
            cls.mocks[key] = cls.patchers[key]["patch"].start()

    def tearDown(self):
        if self.get_mock("getTheProjectIdForOwner").called:
            self.get_mock("getTheProjectIdForOwner").assert_called_with(
                self.body["user_owner"], self.body["project_cod"], self.view.request
            )
        if self.get_mock("getAccessTypeForProject").called:
            self.get_mock("getAccessTypeForProject").assert_called_with(
                self.view.user.login,
                self.get_mock("getTheProjectIdForOwner").return_value,
                self.view.request,
            )

    @classmethod
    def tearDownClass(cls):
        for key in cls.patchers:
            cls.patchers[key]["patch"].stop()

    def get_mock(self, name):
        return self.mocks[name]


class TestReadProjectAssessmentsView(ProjectAssessmentBaseTest):
    view_class = ReadProjectAssessmentsView
    body = {"project_cod": "123", "user_owner": "owner"}
    request_body = json.dumps(body)

    @classmethod
    def setUpClass(cls):
        cls.patchers["getProjectAssessments"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.getProjectAssessments",
            ),
            "return_value": [{}],
        }
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.get_mock("getProjectAssessments").called:
            self.get_mock("getProjectAssessments").assert_called_with(
                self.get_mock("getTheProjectIdForOwner").return_value, self.view.request
            )

    def test_has_validators(self):
        self.assertEqual(self.view.validators, (ProjectExistsValidator,))

    def test_has_valid_fields(self):
        self.assertEqual(
            self.view.valid_fields,
            (
                TextField("project_cod"),
                TextField("user_owner"),
            ),
        )

    def test_get_success(self):
        response = self.view.get()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertEqual(
            response_data, self.get_mock("getProjectAssessments").return_value
        )

        self.get_mock("getTheProjectIdForOwner").assert_called()
        self.get_mock("getProjectAssessments").assert_called()

class TestAddNewAssessmentView(ViewBaseTest):
    view_class = AddNewAssessmentView
    body = {
        "project_cod": "123",
        "user_owner": "owner",
        "ass_desc": "Description",
        "ass_days": "10",
        "ass_final": "Yes",
    }
    request_body = json.dumps(body)

    def test_has_validators(self):
        self.assertEqual(self.view.validators, (ProjectExistsValidator,))

    def test_has_valid_fields(self):
        self.assertEqual(
            self.view.valid_fields,
            (
                TextField("project_cod"),
                TextField("user_owner"),
                TextField("ass_desc"),
                IntegerField("ass_days"),
                BinaryField("ass_final"),
            ),
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
    def test_post_success(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_add_project_assessment,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            mock_add_project_assessment.return_value[1], response.body.decode()
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_add_project_assessment.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "userOwner": self.body["user_owner"],
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view.request,
            "API",
        )

    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_post_no_access(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to add assessments.",
            response.body.decode(),
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )

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
    def test_post_add_assessment_failed(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_add_project_assessment,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            mock_add_project_assessment.return_value[1], response.body.decode()
        )

        # Verify that all the patched methods were called
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_add_project_assessment.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "userOwner": self.body["user_owner"],
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view.request,
            "API",
        )


class TestUpdateProjectAssessmentView(ViewBaseTest):
    view_class = UpdateProjectAssessmentView
    body = {
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "ass123",
        "ass_desc": "Description",
        "ass_days": "10",
    }
    request_body = json.dumps(body)

    def test_has_validators(self):
        self.assertEqual(self.view.validators, (ProjectExistsValidator,))

    def test_has_valid_fields(self):
        self.assertEqual(
            self.view.valid_fields,
            (
                TextField("project_cod"),
                TextField("user_owner"),
                TextField("ass_cod"),
                TextField("ass_desc"),
                IntegerField("ass_days"),
            ),
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
    def test_post_success(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_modify_project_assessment,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            mock_modify_project_assessment.return_value[1], response.body.decode()
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_modify_project_assessment.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_post_no_access(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to update assessments.",
            response.body.decode(),
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )

    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_post_assessment_not_exist(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )

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
    def test_post_update_assessment_failed(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_modify_project_assessment,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            mock_modify_project_assessment.return_value[1], response.body.decode()
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_modify_project_assessment.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view.request,
        )


class TestDeleteProjectAssessmentView(ViewBaseTest):
    view_class = DeleteProjectAssessmentView
    body = {"project_cod": "123", "user_owner": "owner", "ass_cod": "ass123"}
    request_body = json.dumps(body)

    def test_has_validators(self):
        self.assertEqual(self.view.validators, (ProjectExistsValidator,))

    def test_has_valid_fields(self):
        self.assertEqual(
            self.view.valid_fields,
            (TextField("project_cod"), TextField("user_owner"), TextField("ass_cod")),
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
    def test_post_success(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_delete_project_assessment,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            mock_delete_project_assessment.return_value[1], response.body.decode()
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_delete_project_assessment.assert_called_with(
            self.body["user_owner"],
            mock_get_the_project_id_for_owner.return_value,
            self.body["project_cod"],
            self.body["ass_cod"],
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_post_no_access(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to delete assessments.",
            response.body.decode(),
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )

    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_post_assessment_not_exist(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )

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
    def test_post_assessment_cannot_be_deleted(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You can not delete this group because you have questions required for the data collection moment.",
            response.body.decode(),
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )

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
    def test_post_delete_assessment_failed(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_delete_project_assessment,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            mock_delete_project_assessment.return_value[1], response.body.decode()
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_delete_project_assessment.assert_called_with(
            self.body["user_owner"],
            mock_get_the_project_id_for_owner.return_value,
            self.body["project_cod"],
            self.body["ass_cod"],
            self.view.request,
        )


class TestReadProjectAssessmentStructureView(ViewBaseTest):
    view_class = ReadProjectAssessmentStructureView
    body = {"project_cod": "123", "user_owner": "owner", "ass_cod": "ass123"}
    request_body = json.dumps(body)

    def test_has_validators(self):
        self.assertEqual(self.view.validators, (ProjectExistsValidator,))

    def test_has_valid_fields(self):
        self.assertEqual(
            self.view.valid_fields,
            (TextField("project_cod"), TextField("user_owner"), TextField("ass_cod")),
        )

    @patch(
        "climmob.views.Api.projectAssessments.getAssessmentQuestions",
        return_value=[{}],
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
    def test_get_success(
        self,
        mock_get_the_project_id_for_owner,
        mock_assessment_exists,
        mock_get_project_data,
        mock_get_assessment_questions,
    ):
        with patch.object(self.view, "set_group_flags") as mock_set_group_flags:
            response = self.view.get()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertEqual(response_data, mock_get_assessment_questions.return_value)

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_get_project_data.assert_called_with(
            mock_get_the_project_id_for_owner.return_value, self.view.request
        )
        mock_get_assessment_questions.assert_called_with(
            self.body["user_owner"],
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
            [
                mock_get_project_data.return_value["project_label_a"],
                mock_get_project_data.return_value["project_label_b"],
                mock_get_project_data.return_value["project_label_c"],
            ],
            onlyShowTheBasicQuestions=True,
        )
        mock_set_group_flags.assert_called_with(
            mock_get_assessment_questions.return_value
        )

    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_get_assessment_not_exist(
        self,
        mock_get_the_project_id_for_owner,
        mock_assessment_exists,
    ):
        response = self.view.get()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )


class TestSetGroupFlags(unittest.TestCase):
    def setUp(self):
        self.view = ReadProjectAssessmentStructureView(MagicMock())
        self.questions = [
            {"section_id": 1, "question_id": 1, "question_reqinasses": 1},  # 0
            {"section_id": 1, "question_id": 2, "question_reqinasses": 0},  # 1
            {"section_id": 1, "question_id": None, "question_reqinasses": 0},  # 2
            {"section_id": 2, "question_id": 3, "question_reqinasses": 0},  # 3
            {"section_id": 2, "question_id": None, "question_reqinasses": 0},  # 4
            {"section_id": 2, "question_id": 4, "question_reqinasses": 1},  # 5
            {"section_id": 3, "question_id": 5, "question_reqinasses": 0},  # 6
        ]

    def test_for_create_GRP_value(self):
        self.view.set_group_flags(self.questions)

        values = [True, False, False, True, False, False, True]

        for i, value in enumerate(values):
            try:
                self.assertEqual(value, self.questions[i].get("createGRP"))
            except AssertionError:
                raise AssertionError(
                    f"self.questions[{i}] {value} != {self.questions[i].get('createGRP')}"
                )

    def test_for_grp_cannot_delete_value(self):
        self.view.set_group_flags(self.questions)

        values = [True, None, None, True, None, None, False]

        for i, value in enumerate(values):
            try:
                self.assertEqual(value, self.questions[i].get("grpCannotDelete"))
            except AssertionError:
                raise AssertionError(
                    f"self.questions[{i}] {value} != {self.questions[i].get('grpCannotDelete')}"
                )

    def test_for_close_qst_value(self):
        self.view.set_group_flags(self.questions)

        values = [False, False, False, False, False, False, True]

        for i, value in enumerate(values):
            try:
                self.assertEqual(value, self.questions[i].get("closeQst"))
            except AssertionError:
                raise AssertionError(
                    f"self.questions[{i}] {value} != {self.questions[i].get('closeQst')}"
                )

    def test_for_close_grp_value(self):
        self.view.set_group_flags(self.questions)

        values = [False, False, False, False, False, False, True]

        for i, value in enumerate(values):
            try:
                self.assertEqual(value, self.questions[i].get("closeGrp"))
            except AssertionError:
                raise AssertionError(
                    f"self.questions[{i}] {value} != {self.questions[i].get('closeGrp')}"
                )

    def test_for_has_questions_value(self):
        self.view.set_group_flags(self.questions)

        values = [True, True, False, True, False, True, True]

        for i, value in enumerate(values):
            try:
                self.assertEqual(value, self.questions[i].get("hasQuestions"))
            except AssertionError:
                raise AssertionError(
                    f"self.questions[{i}] {value} != {self.questions[i].get('hasQuestions')}"
                )


class TestCreateAssessmentGroupView(ViewBaseTest):
    view_class = CreateAssessmentGroupView
    body = {
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "456",
        "section_name": "Group 1",
        "section_content": "Content of Group 1",
    }
    request_body = json.dumps(body)

    def test_has_validators(self):
        self.assertEqual(self.view.validators, (ProjectExistsValidator,))

    def test_has_valid_fields(self):
        self.assertEqual(
            self.view.valid_fields,
            (
                TextField("project_cod"),
                TextField("user_owner"),
                TextField("ass_cod"),
                TextField("section_name"),
                TextField("section_content"),
            ),
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
    def test_post_success(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_have_the_basic_structure_assessment,
        mock_add_assessment_group,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 200)
        self.assertIn(mock_add_assessment_group.return_value[1], response.body.decode())

        # Verify that all the patched methods were called
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_have_the_basic_structure_assessment.assert_called_with(
            self.body["user_owner"],
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_add_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
            "API",
        )

    @patch(
        "climmob.views.Api.projectAssessments.addAssessmentGroup",
        return_value=(False, "Error"),
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
    def test_post_error_at_add(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_have_the_basic_structure_assessment,
        mock_add_assessment_group,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(mock_add_assessment_group.return_value[1], response.body.decode())

        # Verify that all the patched methods were called
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_have_the_basic_structure_assessment.assert_called_with(
            self.body["user_owner"],
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_add_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
            "API",
        )

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
    def test_post_started_data_collection(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot update data collection moments. You already started the data collection",
            response.body.decode(),
        )

        # Verify that all the patched methods were called
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_post_no_access(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to create groups.",
            response.body.decode(),
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
    def test_post_assessment_not_exist(
        self,
        mock_assessment_exists,
        mock_get_the_project_id_for_owner,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )

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
    def test_post_group_name_repeated(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_have_the_basic_structure_assessment,
        mock_add_assessment_group,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is already a group with this name.", response.body.decode()
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_have_the_basic_structure_assessment.assert_called_with(
            self.body["user_owner"],
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_add_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
            "API",
        )


class TestUpdateAssessmentGroupView(ViewBaseTest):
    view_class = UpdateAssessmentGroupView
    body = {
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "456",
        "group_cod": "789",
        "section_name": "Updated Group",
        "section_content": "Updated content of the group",
    }
    request_body = json.dumps(body)

    def test_has_validators(self):
        self.assertEqual(self.view.validators, (ProjectExistsValidator,))

    def test_has_valid_fields(self):
        self.assertEqual(
            self.view.valid_fields,
            (
                TextField("project_cod"),
                TextField("user_owner"),
                TextField("ass_cod"),
                TextField("group_cod"),
                TextField("section_name"),
                TextField("section_content"),
            ),
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
    def test_post_success(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_modify_assessment_group,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            mock_modify_assessment_group.return_value[1], response.body.decode()
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )
        mock_modify_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )

    @patch(
        "climmob.views.Api.projectAssessments.modifyAssessmentGroup",
        return_value=(False, "Error"),
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
    def test_post_error_to_modify(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_modify_assessment_group,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            mock_modify_assessment_group.return_value[1], response.body.decode()
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )
        mock_modify_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )

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
    def test_post_allready_started_collection(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot update data collection moments. You already started the data collection",
            response.body.decode(),
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_post_no_access(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to update groups.",
            response.body.decode(),
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )

    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_post_assessment_not_exist(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.exitsAssessmentGroup", return_value=False
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
    def test_post_group_not_exist(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not a group with that code.", response.body.decode())

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )

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
    def test_post_group_name_repeated(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_modify_assessment_group,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is already a group with this name.", response.body.decode()
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )
        mock_modify_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )


class TestDeleteAssessmentGroupView(ViewBaseTest):
    view_class = DeleteAssessmentGroupView
    body = {
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "456",
        "group_cod": "789",
    }
    request_body = json.dumps(body)

    def test_has_validators(self):
        self.assertEqual(self.view.validators, (ProjectExistsValidator,))

    def test_has_valid_fields(self):
        self.assertEqual(
            self.view.valid_fields,
            (
                TextField("project_cod"),
                TextField("user_owner"),
                TextField("ass_cod"),
                TextField("group_cod"),
            ),
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
    def test_post_success(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_canDeleteTheAssessmentGroup,
        mock_deleteAssessmentGroup,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            mock_deleteAssessmentGroup.return_value[1], response.body.decode()
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )
        mock_canDeleteTheAssessmentGroup.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view.request,
        )
        mock_deleteAssessmentGroup.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.body["group_cod"],
            self.view.request,
        )

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
    def test_post_started_data_collection(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot update data collection moments. You already started the data collection",
            response.body.decode(),
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )

    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_post_assessment_not_exist(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_post_no_access(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to delete groups.",
            response.body.decode(),
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.exitsAssessmentGroup", return_value=False
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
    def test_post_group_not_exist(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not a group with that code.", response.body.decode())

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )

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
    def test_post_group_cannot_be_deleted(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_canDeleteTheAssessmentGroup,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You can not delete this group because you have questions required for the assessment.",
            response.body.decode(),
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        self.assertTrue(mock_exits_assessment_group.called)
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )
        mock_canDeleteTheAssessmentGroup.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view.request,
        )

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
    def test_post_deletion_failed(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_canDeleteTheAssessmentGroup,
        mock_deleteAssessmentGroup,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            mock_deleteAssessmentGroup.return_value[1], response.body.decode()
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        self.assertTrue(mock_exits_assessment_group.called)
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )
        mock_canDeleteTheAssessmentGroup.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view.request,
        )
        mock_deleteAssessmentGroup.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.body["group_cod"],
            self.view.request,
        )


class TestReadPossibleQuestionForAssessmentGroupView(ViewBaseTest):
    view_class = ReadPossibleQuestionForAssessmentGroupView
    body = {"project_cod": "123", "user_owner": "owner", "ass_cod": "ass123"}
    request_body = json.dumps(body)

    def test_has_validators(self):
        self.assertEqual(self.view.validators, (ProjectExistsValidator,))

    def test_has_valid_fields(self):
        self.assertEqual(
            self.view.valid_fields,
            (
                TextField("project_cod"),
                TextField("user_owner"),
                TextField("ass_cod"),
            ),
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
    def test_get_success(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_questions_options,
        mock_available_assessment_questions,
    ):
        response = self.view.get()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertEqual(
            response_data["Questions"], mock_available_assessment_questions.return_value
        )
        self.assertEqual(
            response_data["QuestionsOptions"],
            mock_questions_options.return_value,
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_available_assessment_questions.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_questions_options.assert_called_with(
            self.view.user.login,
            self.body["user_owner"],
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_get_access_not_allow_action(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        response = self.view.get()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to do this action.",
            response.body.decode(),
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )

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
    def test_get_access_already_start_data_collection(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_assessment_status,
    ):
        response = self.view.get()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot update data collection moments. You already started the data collection.",
            response.body.decode(),
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_assessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )

    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_get_assessment_not_exist(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
    ):
        response = self.view.get()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )


class TestAddQuestionToGroupAssessmentView(ViewBaseTest):
    view_class = AddQuestionToGroupAssessmentView
    body = {
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "ass123",
        "group_cod": "group123",
        "question_id": "q123",
        "question_user_name": "question_user",
    }
    request_body = json.dumps(body)

    def test_has_validators(self):
        self.assertEqual(self.view.validators, (ProjectExistsValidator,))

    def test_has_valid_fields(self):
        self.assertEqual(
            self.view.valid_fields,
            (
                TextField("project_cod"),
                TextField("user_owner"),
                TextField("ass_cod"),
                TextField("group_cod"),
                TextField("question_id"),
                TextField("question_user_name"),
            ),
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
    def test_post_success(
        self,
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
        response = self.view.post()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The question was added to the data collection moment.",
            response.body.decode(),
        )

        # Verify that all the patched methods were called
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_the_user_belongs_to_the_project.assert_called_with(
            self.body["question_user_name"],
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
                "section_id": self.body["group_cod"],
            },
            self.view,
        )
        mock_get_question_data.assert_called_with(
            self.body["question_user_name"],
            self.body["question_id"],
            self.view.request,
        )
        mock_can_use_the_question_assessment.assert_called_with(
            self.body["question_user_name"],
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.body["question_id"],
            self.view.request,
        )
        mock_add_assessment_question_to_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
                "section_id": self.body["group_cod"],
            },
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.addAssessmentQuestionToGroup",
        return_value=(False, "Error."),
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
    def test_post_error_add(
        self,
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
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            mock_add_assessment_question_to_group.return_value[1],
            response.body.decode(),
        )

        # Verify that all the patched methods were called
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_the_user_belongs_to_the_project.assert_called_with(
            self.body["question_user_name"],
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
                "section_id": self.body["group_cod"],
            },
            self.view,
        )
        mock_get_question_data.assert_called_with(
            self.body["question_user_name"],
            self.body["question_id"],
            self.view.request,
        )
        mock_can_use_the_question_assessment.assert_called_with(
            self.body["question_user_name"],
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.body["question_id"],
            self.view.request,
        )
        mock_add_assessment_question_to_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
                "section_id": self.body["group_cod"],
            },
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.getQuestionData",
        return_value=(False, False),
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
    def test_post_question_no_question_id(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_the_user_belongs_to_the_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_get_question_data,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID.",
            response.body.decode(),
        )

        # Verify that all the patched methods were called
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_the_user_belongs_to_the_project.assert_called_with(
            self.body["question_user_name"],
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )
        mock_get_question_data.assert_called_with(
            self.body["question_user_name"],
            self.body["question_id"],
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.canUseTheQuestionAssessment",
        return_value=False,
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
    def test_post_question_cannot_be_used(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_the_user_belongs_to_the_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_get_question_data,
        mock_can_use_the_question_assessment,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The question is already assigned to the data collection moment or cannot be used in this section.",
            response.body.decode(),
        )

        # Verify that all the patched methods were called
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_the_user_belongs_to_the_project.assert_called_with(
            self.body["question_user_name"],
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )
        mock_get_question_data.assert_called_with(
            self.body["question_user_name"],
            self.body["question_id"],
            self.view.request,
        )
        mock_can_use_the_question_assessment.assert_called_with(
            self.body["question_user_name"],
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.body["question_id"],
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_post_access_not_allow_to_add(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to add question to groups.",
            response.body.decode(),
        )

        # Verify that all the patched methods were called
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.theUserBelongsToTheProject",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_post_user_not_belong_to_project(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_the_user_belongs_to_the_project,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are trying to add a question from a user that does not belong to this project.",
            response.body.decode(),
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_the_user_belongs_to_the_project.assert_called_with(
            self.body["question_user_name"],
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )

    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
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
    def test_post_assessment_not_exist(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_the_user_belongs_to_the_project,
        mock_assessment_exists,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_the_user_belongs_to_the_project.assert_called_with(
            self.body["question_user_name"],
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.projectAsessmentStatus",
        return_value=False,
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
    def test_post_assessment_already_started(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_the_user_belongs_to_the_project,
        mock_assessment_exists,
        mock_project_asessment_status,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot update data collection moments. You already started the data collection.",
            response.body.decode(),
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_the_user_belongs_to_the_project.assert_called_with(
            self.body["question_user_name"],
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )

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
    def test_post_group_not_exist(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_the_user_belongs_to_the_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not a group with that code.", response.body.decode())
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_the_user_belongs_to_the_project.assert_called_with(
            self.body["question_user_name"],
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )


class TestDeleteQuestionFromGroupAssessmentView(ViewBaseTest):
    view_class = DeleteQuestionFromGroupAssessmentView
    body = {
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "ass123",
        "group_cod": "group123",
        "question_id": "q123",
        "question_user_name": "question_user",
    }
    request_body = json.dumps(body)

    def test_has_validators(self):
        self.assertEqual(self.view.validators, (ProjectExistsValidator,))

    def test_has_valid_fields(self):
        self.assertEqual(
            self.view.valid_fields,
            (
                TextField("project_cod"),
                TextField("user_owner"),
                TextField("ass_cod"),
                TextField("group_cod"),
                TextField("question_id"),
                TextField("question_user_name"),
            ),
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
    def test_post_success(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_get_question_data,
        mock_exits_question_in_group_assessment,
        mock_delete_assessment_question_from_group,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            mock_delete_assessment_question_from_group.return_value[1],
            response.body.decode(),
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )
        mock_get_question_data.assert_called_with(
            self.body["question_user_name"],
            self.body["question_id"],
            self.view.request,
        )
        mock_exits_question_in_group_assessment.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view.request,
        )
        mock_delete_assessment_question_from_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.deleteAssessmentQuestionFromGroup",
        return_value=(False, "Error to delete."),
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
    def test_post_error_to_delete(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_get_question_data,
        mock_exits_question_in_group_assessment,
        mock_delete_assessment_question_from_group,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            mock_delete_assessment_question_from_group.return_value[1],
            response.body.decode(),
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )
        mock_get_question_data.assert_called_with(
            self.body["question_user_name"],
            self.body["question_id"],
            self.view.request,
        )
        mock_exits_question_in_group_assessment.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view.request,
        )
        mock_delete_assessment_question_from_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.exitsQuestionInGroupAssessment",
        return_value=False,
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
    def test_post_no_exist_question(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_get_question_data,
        mock_exits_question_in_group_assessment,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID in this group.",
            response.body.decode(),
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )
        mock_get_question_data.assert_called_with(
            self.body["question_user_name"],
            self.body["question_id"],
            self.view.request,
        )
        mock_exits_question_in_group_assessment.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.exitsAssessmentGroup", return_value=False
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
    def test_post_no_group_whit_this_code(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not a group with that code.", response.body.decode())
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )

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
    def test_post_already_started_data_collection(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
    ):
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot update data collection moments. You already started the data collection.",
            response.body.decode(),
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )

    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_post_already_no_data_collection(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
    ):
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_post_no_access(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to delete questions from a group.",
            response.body.decode(),
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
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
    def test_post_question_not_exist(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_get_question_data,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID.", response.body.decode()
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )
        mock_get_question_data.assert_called_with(
            self.body["question_user_name"],
            self.body["question_id"],
            self.view.request,
        )

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
    def test_post_question_required(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_exits_assessment_group,
        mock_get_question_data,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You can not delete this question because is required for this data collection moment.",
            response.body.decode(),
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_exits_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "section_private": None,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )
        mock_get_question_data.assert_called_with(
            self.body["question_user_name"],
            self.body["question_id"],
            self.view.request,
        )


class TestOrderAssessmentQuestionsView(ViewBaseTest):
    view_class = OrderAssessmentQuestionsView
    body = {
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
    request_body = json.dumps(body)

    def test_has_validators(self):
        self.assertEqual(self.view.validators, (ProjectExistsValidator,))

    def test_has_valid_fields(self):
        self.assertEqual(
            self.view.valid_fields,
            (
                TextField("project_cod"),
                TextField("user_owner"),
                TextField("ass_cod"),
                TextField("order"),
            ),
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
    def test_post_success(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type,
        mock_assessment_exists,
        mock_assessment_status,
        mock_get_assessment_group,
        mock_get_assessment_questions_api,
        mock_save_assessment_order,
    ):
        response = self.view.post()
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The order of the groups and questions has been changed.",
            response.body.decode(),
        )

        # Verify that the mocked methods were called with expected arguments
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_assessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_get_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )
        mock_get_assessment_questions_api.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )
        mock_save_assessment_order.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            json.loads(self.body["order"]),
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_post_no_permission(
        self, mock_get_the_project_id_for_owner, mock_get_access_type
    ):
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to order the questions.",
            response.body.decode(),
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )

    @patch("climmob.views.Api.projectAssessments.assessmentExists", return_value=False)
    @patch(
        "climmob.views.Api.projectAssessments.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectAssessments.getTheProjectIdForOwner", return_value=1
    )
    def test_post_assessment_not_exist(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type,
        mock_assessment_exists,
    ):
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )

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
    def test_post_data_collection_started(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type,
        mock_assessment_exists,
        mock_assessment_status,
    ):
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot update data collection moments. You already started the data collection.",
            response.body.decode(),
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_assessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )

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
    def test_post_invalid_order_json(
        self,
        mock_assessment_status,
        mock_assessment_exists,
        mock_get_access_type,
        mock_get_the_project_id_for_owner,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "ass_cod": "ass123",
                "order": "invalid_json",
            }
        )
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON order.", response.body.decode())

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_assessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )

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
    def test_post_questions_outside_groups(
        self,
        mock_assessment_status,
        mock_assessment_exists,
        mock_get_access_type,
        mock_get_the_project_id_for_owner,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "123",
                "user_owner": "owner",
                "ass_cod": "ass123",
                "order": json.dumps([{"type": "question", "id": "QST1"}]),
            }
        )
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Questions cannot be outside a group", response.body.decode())

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_assessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
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
    def test_post_groups_not_in_form(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_get_assessment_group,
    ):
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are ordering groups that are not part of the form.",
            response.body.decode(),
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_get_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )

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
    def test_post_questions_not_in_form(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_get_assessment_group,
        mock_get_assessment_questions_api,
    ):
        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are ordering questions that are not part of the form.",
            response.body.decode(),
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_get_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )
        mock_get_assessment_questions_api.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )

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
    def test_post_save_order_fails(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_access_type_for_project,
        mock_assessment_exists,
        mock_project_asessment_status,
        mock_get_assessment_group,
        mock_get_assessment_questions_api,
        mock_save_assessment_order,
    ):
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            mock_save_assessment_order.return_value[1],
            response.body.decode(),
        )

        mock_get_the_project_id_for_owner.assert_called_with(
            self.body["user_owner"], self.body["project_cod"], self.view.request
        )
        mock_get_access_type_for_project.assert_called_with(
            self.view.user.login,
            mock_get_the_project_id_for_owner.return_value,
            self.view.request,
        )
        mock_assessment_exists.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_project_asessment_status.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            self.view.request,
        )
        mock_get_assessment_group.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )
        mock_get_assessment_questions_api.assert_called_with(
            self.body
            | {
                "user_name": self.view.user.login,
                "project_id": mock_get_the_project_id_for_owner.return_value,
            },
            self.view,
        )
        mock_save_assessment_order.assert_called_with(
            mock_get_the_project_id_for_owner.return_value,
            self.body["ass_cod"],
            json.loads(self.body["order"]),
            self.view.request,
        )


if __name__ == "__main__":
    unittest.main()
