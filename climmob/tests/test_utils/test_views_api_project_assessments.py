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
    CloneAssessmentApiView,
)
from climmob.views.validators import TextField, IntegerField, BinaryField
from climmob.views.validators.ProjectExistsValidator import ProjectExistsValidator
from climmob.views.validators.assessment import AssessmentExistsValidator
from climmob.views.validators.project import (
    CanEditProjectValidator,
    ProjectOpenValidator,
)


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
        cls.patchers["assessmentExists"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.assessmentExists",
            ),
            "return_value": True,
        }
        cls.patchers["projectAsessmentStatus"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.projectAsessmentStatus",
            ),
            "return_value": True,
        }

        for key in cls.patchers:
            cls.mocks[key] = cls.patchers[key]["patch"].start()

    def tearDown(self):
        if self.get_mock("getTheProjectIdForOwner").called:
            self.get_mock("getTheProjectIdForOwner").assert_called_once_with(
                self.body["user_owner"], self.body["project_cod"], self.view.request
            )
        if self.get_mock("getAccessTypeForProject").called:
            self.get_mock("getAccessTypeForProject").assert_called_once_with(
                self.view.user.login,
                self.get_mock("getTheProjectIdForOwner").return_value,
                self.view.request,
            )
        if self.get_mock("assessmentExists").called:
            self.get_mock("assessmentExists").assert_called_once_with(
                self.get_mock("getTheProjectIdForOwner").return_value,
                self.body["ass_cod"],
                self.view.request,
            )
        if self.get_mock("projectAsessmentStatus").called:
            self.get_mock("projectAsessmentStatus").assert_called_once_with(
                self.get_mock("getTheProjectIdForOwner").return_value,
                self.body["ass_cod"],
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
            self.get_mock("getProjectAssessments").assert_called_once_with(
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

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getProjectAssessments").assert_called_once()


class TestAddNewAssessmentView(ProjectAssessmentBaseTest):
    view_class = AddNewAssessmentView
    body = {
        "project_cod": "123",
        "user_owner": "owner",
        "ass_desc": "Description",
        "ass_days": "10",
        "ass_final": "Yes",
    }
    request_body = json.dumps(body)

    @classmethod
    def setUpClass(cls):
        cls.patchers["addProjectAssessment"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.addProjectAssessment",
            ),
            "return_value": (True, "Assessment added successfully"),
        }
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.get_mock("addProjectAssessment").called:
            self.get_mock("addProjectAssessment").assert_called_once_with(
                self.body
                | {
                    "user_name": self.view.user.login,
                    "userOwner": self.body["user_owner"],
                    "project_id": self.get_mock("getTheProjectIdForOwner").return_value,
                },
                self.view.request,
                "API",
            )

    def test_has_validators(self):
        self.assertEqual(
            self.view.validators,
            (
                ProjectExistsValidator,
                ProjectOpenValidator,
            ),
        )

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

    def test_post_success(self):
        response = self.view.post()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            self.get_mock("addProjectAssessment").return_value[1],
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("addProjectAssessment").assert_called_once()

    def test_post_no_access(self):
        self.get_mock("getAccessTypeForProject").return_value = 4

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to add assessments.",
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()

    def test_post_add_assessment_failed(self):
        self.get_mock("addProjectAssessment").return_value = (
            False,
            "Error adding assessment",
        )
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            self.get_mock("addProjectAssessment").return_value[1],
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("addProjectAssessment").assert_called_once()


class TestUpdateProjectAssessmentView(ProjectAssessmentBaseTest):
    view_class = UpdateProjectAssessmentView
    body = {
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "ass123",
        "ass_desc": "Description",
        "ass_days": "10",
    }
    request_body = json.dumps(body)

    @classmethod
    def setUpClass(cls):
        cls.patchers["modifyProjectAssessment"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.modifyProjectAssessment",
            ),
            "return_value": (True, "Data collection updated successfully."),
        }
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.get_mock("modifyProjectAssessment").called:
            self.get_mock("modifyProjectAssessment").assert_called_once_with(
                self.body
                | {
                    "user_name": self.view.user.login,
                    "project_id": self.get_mock("getTheProjectIdForOwner").return_value,
                },
                self.view.request,
            )

    def test_has_validators(self):
        self.assertEqual(
            self.view.validators, (ProjectExistsValidator, ProjectOpenValidator)
        )

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

    def test_post_success(self):
        response = self.view.post()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            self.get_mock("modifyProjectAssessment").return_value[1],
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("modifyProjectAssessment").assert_called_once()

    def test_post_no_access(self):
        self.get_mock("getAccessTypeForProject").return_value = 4

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to update assessments.",
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()

    def test_post_assessment_not_exist(self):
        self.get_mock("assessmentExists").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()

    def test_post_update_assessment_failed(self):
        self.get_mock("modifyProjectAssessment").return_value = (
            False,
            "Error updating assessment",
        )

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            self.get_mock("modifyProjectAssessment").return_value[1],
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("modifyProjectAssessment").assert_called_once()


class TestDeleteProjectAssessmentView(ProjectAssessmentBaseTest):
    view_class = DeleteProjectAssessmentView
    body = {"project_cod": "123", "user_owner": "owner", "ass_cod": "ass123"}
    request_body = json.dumps(body)

    @classmethod
    def setUpClass(cls):
        cls.patchers["deleteProjectAssessment"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.deleteProjectAssessment",
            ),
            "return_value": (True, ""),
        }
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.get_mock("deleteProjectAssessment").called:
            self.get_mock("deleteProjectAssessment").assert_called_once_with(
                self.body["user_owner"],
                self.get_mock("getTheProjectIdForOwner").return_value,
                self.body["project_cod"],
                self.body["ass_cod"],
                self.view.request,
            )

    def test_has_validators(self):
        self.assertEqual(
            self.view.validators, (ProjectExistsValidator, ProjectOpenValidator)
        )

    def test_has_valid_fields(self):
        self.assertEqual(
            self.view.valid_fields,
            (TextField("project_cod"), TextField("user_owner"), TextField("ass_cod")),
        )

    def test_post_success(self):
        response = self.view.post()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Data collection moment deleted successfully.",
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("deleteProjectAssessment").assert_called_once()

    def test_post_no_access(self):
        self.get_mock("getAccessTypeForProject").return_value = 4

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to delete assessments.",
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()

    def test_post_assessment_not_exist(self):
        self.get_mock("assessmentExists").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()

    def test_post_assessment_cannot_be_deleted(self):
        self.get_mock("projectAsessmentStatus").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You can not delete this group because you have questions required for the data collection moment.",
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()

    def test_post_delete_assessment_failed(self):
        self.get_mock("deleteProjectAssessment").return_value = (
            False,
            "Error deleting assessment",
        )

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            self.get_mock("deleteProjectAssessment").return_value[1],
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("deleteProjectAssessment").assert_called_once()


class TestCloneAssessmentApiView(ProjectAssessmentBaseTest):
    view_class = CloneAssessmentApiView
    body = {"project_cod": "123", "user_owner": "owner", "ass_cod": "ass123"}
    request_body = json.dumps(body)

    @classmethod
    def setUpClass(cls):
        cls.patchers["clone_assessment"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.clone_assessment",
            ),
            "return_value": True,
        }
        super().setUpClass()

    def tearDown(self):
        if self.get_mock("clone_assessment").called:
            self.get_mock("clone_assessment").assert_called_once_with(
                self.view,
                self.view.context.active_project_id,
                self.body["ass_cod"],
            )

    def test_has_validators(self):
        self.assertEqual(
            self.view.validators,
            (
                ProjectExistsValidator,
                CanEditProjectValidator,
                AssessmentExistsValidator,
                ProjectOpenValidator,
            ),
        )

    def test_has_valid_fields(self):
        self.assertEqual(
            self.view.valid_fields,
            (TextField("project_cod"), TextField("user_owner"), TextField("ass_cod")),
        )

    def test_success(self):
        response = self.view.post()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Assessment cloned successfully.", response.body.decode())

        self.get_mock("clone_assessment").assert_called_once()

    def test_error(self):
        self.get_mock("clone_assessment").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 500)
        self.assertIn("Could not clone the assessment.", response.body.decode())

        self.get_mock("clone_assessment").assert_called_once()


class TestReadProjectAssessmentStructureView(ProjectAssessmentBaseTest):
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

    @classmethod
    def setUpClass(cls):
        cls.patchers["getAssessmentQuestions"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.getAssessmentQuestions",
            ),
            "return_value": [{}],
        }
        cls.patchers["getProjectData"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.getProjectData",
            ),
            "return_value": {
                "project_label_a": "Label A",
                "project_label_b": "Label B",
                "project_label_c": "Label C",
            },
        }
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.get_mock("getAssessmentQuestions").called:
            self.get_mock("getAssessmentQuestions").assert_called_once_with(
                self.body["user_owner"],
                self.get_mock("getTheProjectIdForOwner").return_value,
                self.body["ass_cod"],
                self.view.request,
                [
                    self.get_mock("getProjectData").return_value["project_label_a"],
                    self.get_mock("getProjectData").return_value["project_label_b"],
                    self.get_mock("getProjectData").return_value["project_label_c"],
                ],
                onlyShowTheBasicQuestions=True,
            )
        if self.get_mock("getProjectData").called:
            self.get_mock("getProjectData").assert_called_once_with(
                self.get_mock("getTheProjectIdForOwner").return_value, self.view.request
            )

    def test_get_success(self):
        with patch.object(self.view, "set_group_flags") as mock_set_group_flags:
            response = self.view.get()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertEqual(
            response_data, self.get_mock("getAssessmentQuestions").return_value
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("getProjectData").assert_called_once()
        self.get_mock("getAssessmentQuestions").assert_called_once()

        mock_set_group_flags.assert_called_once_with(
            self.get_mock("getAssessmentQuestions").return_value
        )

    def test_get_assessment_not_exist(self):
        self.get_mock("assessmentExists").return_value = False

        response = self.view.get()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()


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


class TestCreateAssessmentGroupView(ProjectAssessmentBaseTest):
    view_class = CreateAssessmentGroupView
    body = {
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "456",
        "section_name": "Group 1",
        "section_content": "Content of Group 1",
    }
    request_body = json.dumps(body)

    @classmethod
    def setUpClass(cls):
        cls.patchers["add_assessment_group"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.add_assessment_group",
            ),
            "return_value": (True, "Group added successfully"),
        }
        cls.patchers["haveTheBasicStructureAssessment"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.haveTheBasicStructureAssessment",
            ),
            "return_value": True,
        }
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.get_mock("add_assessment_group").called:
            self.get_mock("add_assessment_group").assert_called_once_with(
                self.body
                | {
                    "user_name": self.view.user.login,
                    "section_private": None,
                    "project_id": self.get_mock("getTheProjectIdForOwner").return_value,
                },
                self.view,
                "API",
            )
        if self.get_mock("haveTheBasicStructureAssessment").called:
            self.get_mock("haveTheBasicStructureAssessment").assert_called_once_with(
                self.body["user_owner"],
                self.get_mock("getTheProjectIdForOwner").return_value,
                self.body["ass_cod"],
                self.view.request,
            )

    def test_has_validators(self):
        self.assertEqual(
            self.view.validators, (ProjectExistsValidator, ProjectOpenValidator)
        )

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

    def test_post_success(self):
        response = self.view.post()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            self.get_mock("add_assessment_group").return_value[1],
            response.body.decode(),
        )

        # Verify that all the patched methods were called
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("haveTheBasicStructureAssessment").assert_called_once()
        self.get_mock("add_assessment_group").assert_called_once()

    def test_post_error_at_add(self):
        self.get_mock("add_assessment_group").return_value = (False, "Error")
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            self.get_mock("add_assessment_group").return_value[1],
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("haveTheBasicStructureAssessment").assert_called_once()
        self.get_mock("add_assessment_group").assert_called_once()

    def test_post_started_data_collection(self):
        self.get_mock("projectAsessmentStatus").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot update data collection moments. You already started the data collection",
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()

    def test_post_no_access(self):
        self.get_mock("getAccessTypeForProject").return_value = 4

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to create groups.",
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()

    def test_post_assessment_not_exist(self):
        self.get_mock("assessmentExists").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()

    def test_post_group_name_repeated(self):
        self.get_mock("add_assessment_group").return_value = (False, "repeated")

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is already a group with this name.", response.body.decode()
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("haveTheBasicStructureAssessment").assert_called_once()
        self.get_mock("add_assessment_group").assert_called_once()


class TestUpdateAssessmentGroupView(ProjectAssessmentBaseTest):
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

    @classmethod
    def setUpClass(cls):
        cls.patchers["modifyAssessmentGroup"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.modifyAssessmentGroup",
            ),
            "return_value": (True, "Group updated successfully"),
        }
        cls.patchers["exitsAssessmentGroup"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.exitsAssessmentGroup",
            ),
            "return_value": True,
        }
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.get_mock("modifyAssessmentGroup").called:
            self.get_mock("modifyAssessmentGroup").assert_called_once_with(
                self.body
                | {
                    "user_name": self.view.user.login,
                    "section_private": None,
                    "project_id": self.get_mock("getTheProjectIdForOwner").return_value,
                },
                self.view,
            )
        if self.get_mock("exitsAssessmentGroup").called:
            self.get_mock("exitsAssessmentGroup").assert_called_once_with(
                self.body
                | {
                    "user_name": self.view.user.login,
                    "section_private": None,
                    "project_id": self.get_mock("getTheProjectIdForOwner").return_value,
                },
                self.view,
            )

    def test_has_validators(self):
        self.assertEqual(
            self.view.validators, (ProjectExistsValidator, ProjectOpenValidator)
        )

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

    def test_post_success(self):
        response = self.view.post()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            self.get_mock("modifyAssessmentGroup").return_value[1],
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()
        self.get_mock("modifyAssessmentGroup").assert_called_once()

    def test_post_error_to_modify(self):
        self.get_mock("modifyAssessmentGroup").return_value = (False, "Error")
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            self.get_mock("modifyAssessmentGroup").return_value[1],
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()
        self.get_mock("modifyAssessmentGroup").assert_called_once()

    def test_post_already_started_collection(self):
        self.get_mock("projectAsessmentStatus").return_value = False
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot update data collection moments. You already started the data collection",
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()

    def test_post_no_access(self):
        self.get_mock("getAccessTypeForProject").return_value = 4

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to update groups.",
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()

    def test_post_assessment_not_exist(self):
        self.get_mock("assessmentExists").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()

    def test_post_group_not_exist(self):
        self.get_mock("exitsAssessmentGroup").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not a group with that code.", response.body.decode())

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()

    def test_post_group_name_repeated(self):
        self.get_mock("modifyAssessmentGroup").return_value = (False, "repeated")
        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is already a group with this name.", response.body.decode()
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()
        self.get_mock("modifyAssessmentGroup").assert_called_once()


class TestDeleteAssessmentGroupView(ProjectAssessmentBaseTest):
    view_class = DeleteAssessmentGroupView
    body = {
        "project_cod": "123",
        "user_owner": "owner",
        "ass_cod": "456",
        "group_cod": "789",
    }
    request_body = json.dumps(body)

    @classmethod
    def setUpClass(cls):
        cls.patchers["exitsAssessmentGroup"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.exitsAssessmentGroup",
            ),
            "return_value": True,
        }
        cls.patchers["canDeleteTheAssessmentGroup"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.canDeleteTheAssessmentGroup",
            ),
            "return_value": True,
        }
        cls.patchers["deleteAssessmentGroup"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.deleteAssessmentGroup",
            ),
            "return_value": (True, "Group deleted successfully"),
        }
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.get_mock("exitsAssessmentGroup").called:
            self.get_mock("exitsAssessmentGroup").assert_called_once_with(
                self.body
                | {
                    "user_name": self.view.user.login,
                    "section_private": None,
                    "project_id": self.get_mock("getTheProjectIdForOwner").return_value,
                },
                self.view,
            )
        if self.get_mock("canDeleteTheAssessmentGroup").called:
            self.get_mock("canDeleteTheAssessmentGroup").assert_called_once_with(
                self.body
                | {
                    "user_name": self.view.user.login,
                    "section_private": None,
                    "project_id": self.get_mock("getTheProjectIdForOwner").return_value,
                },
                self.view.request,
            )
        if self.get_mock("deleteAssessmentGroup").called:
            self.get_mock("deleteAssessmentGroup").assert_called_once_with(
                self.get_mock("getTheProjectIdForOwner").return_value,
                self.body["ass_cod"],
                self.body["group_cod"],
                self.view.request,
            )

    def test_has_validators(self):
        self.assertEqual(
            self.view.validators, (ProjectExistsValidator, ProjectOpenValidator)
        )

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

    def test_post_success(self):
        response = self.view.post()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            self.get_mock("deleteAssessmentGroup").return_value[1],
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()
        self.get_mock("canDeleteTheAssessmentGroup").assert_called_once()
        self.get_mock("deleteAssessmentGroup").assert_called_once()

    def test_post_started_data_collection(self):
        self.get_mock("projectAsessmentStatus").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot update data collection moments. You already started the data collection",
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()

    def test_post_assessment_not_exist(self):
        self.get_mock("assessmentExists").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()

    def test_post_no_access(self):
        self.get_mock("getAccessTypeForProject").return_value = 4

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to delete groups.",
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()

    def test_post_group_not_exist(self):
        self.get_mock("exitsAssessmentGroup").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not a group with that code.", response.body.decode())

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()

    def test_post_group_cannot_be_deleted(self):
        self.get_mock("canDeleteTheAssessmentGroup").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You can not delete this group because you have questions required for the assessment.",
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()
        self.get_mock("canDeleteTheAssessmentGroup").assert_called_once()

    def test_post_deletion_failed(self):
        self.get_mock("deleteAssessmentGroup").return_value = (False, "Deletion failed")

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            self.get_mock("deleteAssessmentGroup").return_value[1],
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()
        self.get_mock("canDeleteTheAssessmentGroup").assert_called_once()
        self.get_mock("deleteAssessmentGroup").assert_called_once()


class TestReadPossibleQuestionForAssessmentGroupView(ProjectAssessmentBaseTest):
    view_class = ReadPossibleQuestionForAssessmentGroupView
    body = {"project_cod": "123", "user_owner": "owner", "ass_cod": "ass123"}
    request_body = json.dumps(body)

    def test_has_validators(self):
        self.assertEqual(
            self.view.validators,
            (
                ProjectExistsValidator,
                ProjectOpenValidator,
            ),
        )

    def test_has_valid_fields(self):
        self.assertEqual(
            self.view.valid_fields,
            (
                TextField("project_cod"),
                TextField("user_owner"),
                TextField("ass_cod"),
            ),
        )

    @classmethod
    def setUpClass(cls):
        cls.patchers["availableAssessmentQuestions"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.availableAssessmentQuestions",
            ),
            "return_value": ["Question 1", "Question 2"],
        }
        cls.patchers["QuestionsOptions"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.QuestionsOptions",
            ),
            "return_value": {"Option 1": "Value 1"},
        }
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.get_mock("availableAssessmentQuestions").called:
            self.get_mock("availableAssessmentQuestions").assert_called_once_with(
                self.get_mock("getTheProjectIdForOwner").return_value,
                self.body["ass_cod"],
                self.view.request,
            )
        if self.get_mock("QuestionsOptions").called:
            self.get_mock("QuestionsOptions").assert_called_once_with(
                self.view.user.login,
                self.body["user_owner"],
                self.view.request,
            )

    def test_get_success(self):
        response = self.view.get()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertEqual(
            response_data["Questions"],
            self.get_mock("availableAssessmentQuestions").return_value,
        )
        self.assertEqual(
            response_data["QuestionsOptions"],
            self.get_mock("QuestionsOptions").return_value,
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("availableAssessmentQuestions").assert_called_once()
        self.get_mock("QuestionsOptions").assert_called_once()

    def test_get_access_not_allow_action(self):
        self.get_mock("getAccessTypeForProject").return_value = 4

        response = self.view.get()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to do this action.",
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()

    def test_get_access_already_start_data_collection(self):
        self.get_mock("projectAsessmentStatus").return_value = False

        response = self.view.get()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot update data collection moments. You already started the data collection.",
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()

    def test_get_assessment_not_exist(self):
        self.get_mock("assessmentExists").return_value = False

        response = self.view.get()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()


class TestAddQuestionToGroupAssessmentView(ProjectAssessmentBaseTest):
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

    @classmethod
    def setUpClass(cls):
        cls.patchers["exitsAssessmentGroup"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.exitsAssessmentGroup",
            ),
            "return_value": True,
        }
        cls.patchers["addAssessmentQuestionToGroup"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.addAssessmentQuestionToGroup",
            ),
            "return_value": (True, ""),
        }
        cls.patchers["canUseTheQuestionAssessment"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.canUseTheQuestionAssessment",
            ),
            "return_value": True,
        }
        cls.patchers["getQuestionData"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.getQuestionData",
            ),
            "return_value": (True, True),
        }
        cls.patchers["theUserBelongsToTheProject"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.theUserBelongsToTheProject",
            ),
            "return_value": True,
        }
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.get_mock("addAssessmentQuestionToGroup").called:
            self.get_mock("addAssessmentQuestionToGroup").assert_called_once_with(
                self.body
                | {
                    "user_name": self.view.user.login,
                    "section_private": None,
                    "project_id": self.get_mock("getTheProjectIdForOwner").return_value,
                    "section_id": self.body["group_cod"],
                },
                self.view.request,
            )
        if self.get_mock("canUseTheQuestionAssessment").called:
            self.get_mock("canUseTheQuestionAssessment").assert_called_once_with(
                self.body["question_user_name"],
                self.get_mock("getTheProjectIdForOwner").return_value,
                self.body["ass_cod"],
                self.body["question_id"],
                self.view.request,
            )
        if self.get_mock("getQuestionData").called:
            self.get_mock("getQuestionData").assert_called_once_with(
                self.body["question_user_name"],
                self.body["question_id"],
                self.view.request,
            )
        if self.get_mock("exitsAssessmentGroup").called:
            self.get_mock("exitsAssessmentGroup").assert_called_once_with(
                self.body
                | {
                    "user_name": self.view.user.login,
                    "section_private": None,
                    "project_id": self.get_mock("getTheProjectIdForOwner").return_value,
                },
                self.view,
            )
        if self.get_mock("theUserBelongsToTheProject").called:
            self.get_mock("theUserBelongsToTheProject").assert_called_once_with(
                self.body["question_user_name"],
                self.get_mock("getTheProjectIdForOwner").return_value,
                self.view.request,
            )

    def test_has_validators(self):
        self.assertEqual(
            self.view.validators,
            (
                ProjectExistsValidator,
                ProjectOpenValidator,
            ),
        )

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

    def test_post_success(self):
        response = self.view.post()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The question was added to the data collection moment.",
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("theUserBelongsToTheProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()
        self.get_mock("getQuestionData").assert_called_once()
        self.get_mock("canUseTheQuestionAssessment").assert_called_once()
        self.get_mock("addAssessmentQuestionToGroup").assert_called_once()

    def test_post_error_add(self):
        self.get_mock("addAssessmentQuestionToGroup").return_value = (False, "Error.")

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            self.get_mock("addAssessmentQuestionToGroup").return_value[1],
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("theUserBelongsToTheProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()
        self.get_mock("getQuestionData").assert_called_once()
        self.get_mock("canUseTheQuestionAssessment").assert_called_once()
        self.get_mock("addAssessmentQuestionToGroup").assert_called_once()

    def test_post_question_no_question_id(self):
        self.get_mock("getQuestionData").return_value = (False, False)

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID.",
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("theUserBelongsToTheProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()
        self.get_mock("getQuestionData").assert_called_once()

    def test_post_question_cannot_be_used(self):
        self.get_mock("canUseTheQuestionAssessment").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The question is already assigned to the data collection moment or cannot be used in this section.",
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("theUserBelongsToTheProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()
        self.get_mock("getQuestionData").assert_called_once()
        self.get_mock("canUseTheQuestionAssessment").assert_called_once()

    def test_post_access_not_allow_to_add(self):
        self.get_mock("getAccessTypeForProject").return_value = 4

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to add question to groups.",
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()

    def test_post_user_not_belong_to_project(self):
        self.get_mock("theUserBelongsToTheProject").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are trying to add a question from a user that does not belong to this project.",
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("theUserBelongsToTheProject").assert_called_once()

    def test_post_assessment_not_exist(self):
        self.get_mock("assessmentExists").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("theUserBelongsToTheProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()

    def test_post_assessment_already_started(self):
        self.get_mock("projectAsessmentStatus").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot update data collection moments. You already started the data collection.",
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("theUserBelongsToTheProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()

    def test_post_group_not_exist(self):
        self.get_mock("exitsAssessmentGroup").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not a group with that code.", response.body.decode())
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("theUserBelongsToTheProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()


class TestDeleteQuestionFromGroupAssessmentView(ProjectAssessmentBaseTest):
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

    @classmethod
    def setUpClass(cls):
        cls.patchers["deleteAssessmentQuestionFromGroup"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.deleteAssessmentQuestionFromGroup",
            ),
            "return_value": (True, "Question deleted successfully."),
        }
        cls.patchers["exitsQuestionInGroupAssessment"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.exitsQuestionInGroupAssessment",
            ),
            "return_value": True,
        }
        cls.patchers["getQuestionData"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.getQuestionData",
            ),
            "return_value": ({"question_reqinasses": 0}, True),
        }
        cls.patchers["exitsAssessmentGroup"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.exitsAssessmentGroup",
            ),
            "return_value": True,
        }
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        self.body |= {
            "user_name": self.view.user.login,
            "section_private": None,
            "project_id": self.get_mock("getTheProjectIdForOwner").return_value,
        }
        if self.get_mock("deleteAssessmentQuestionFromGroup").called:
            self.get_mock("deleteAssessmentQuestionFromGroup").assert_called_once_with(
                self.body,
                self.view.request,
            )
        if self.get_mock("exitsQuestionInGroupAssessment").called:
            self.get_mock("exitsQuestionInGroupAssessment").assert_called_once_with(
                self.body,
                self.view.request,
            )
        if self.get_mock("getQuestionData").called:
            self.get_mock("getQuestionData").assert_called_once_with(
                self.body["question_user_name"],
                self.body["question_id"],
                self.view.request,
            )
        if self.get_mock("exitsAssessmentGroup").called:
            self.get_mock("exitsAssessmentGroup").assert_called_once_with(
                self.body,
                self.view,
            )

    def test_has_validators(self):
        self.assertEqual(
            self.view.validators, (ProjectExistsValidator, ProjectOpenValidator)
        )

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

    def test_post_success(self):
        response = self.view.post()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            self.get_mock("deleteAssessmentQuestionFromGroup").return_value[1],
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()
        self.get_mock("getQuestionData").assert_called_once()
        self.get_mock("exitsQuestionInGroupAssessment").assert_called_once()
        self.get_mock("deleteAssessmentQuestionFromGroup").assert_called_once()

    def test_post_error_to_delete(self):
        self.get_mock("deleteAssessmentQuestionFromGroup").return_value = (
            False,
            "Error to delete.",
        )

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            self.get_mock("deleteAssessmentQuestionFromGroup").return_value[1],
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()
        self.get_mock("getQuestionData").assert_called_once()
        self.get_mock("exitsQuestionInGroupAssessment").assert_called_once()
        self.get_mock("deleteAssessmentQuestionFromGroup").assert_called_once()

    def test_post_no_exist_question(self):
        self.get_mock("exitsQuestionInGroupAssessment").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID in this group.",
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()
        self.get_mock("getQuestionData").assert_called_once()
        self.get_mock("exitsQuestionInGroupAssessment").assert_called_once()

    def test_post_no_group_whit_this_code(self):
        self.get_mock("exitsAssessmentGroup").return_value = False

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not a group with that code.", response.body.decode())
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()

    def test_post_already_started_data_collection(self):
        self.get_mock("projectAsessmentStatus").return_value = False

        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot update data collection moments. You already started the data collection.",
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()

    def test_post_already_no_data_collection(self):
        self.get_mock("assessmentExists").return_value = False

        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()

    def test_post_no_access(self):
        self.get_mock("getAccessTypeForProject").return_value = 4

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to delete questions from a group.",
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()

    def test_post_question_not_exist(self):
        self.get_mock("getQuestionData").return_value = (None, False)

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID.", response.body.decode()
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()
        self.get_mock("getQuestionData").assert_called_once()

    def test_post_question_required(self):
        self.get_mock("getQuestionData").return_value = (
            {"question_reqinasses": 1},
            True,
        )

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You can not delete this question because is required for this data collection moment.",
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("exitsAssessmentGroup").assert_called_once()
        self.get_mock("getQuestionData").assert_called_once()


class TestOrderAssessmentQuestionsView(ProjectAssessmentBaseTest):
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

    @classmethod
    def setUpClass(cls):
        cls.patchers["saveAssessmentOrder"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.saveAssessmentOrder",
            ),
            "return_value": (True, ""),
        }
        cls.patchers["getAssessmentQuestionsApi"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.getAssessmentQuestionsApi",
            ),
            "return_value": [1, 2, 3],
        }
        cls.patchers["getAssessmentGroup"] = {
            "patch": patch(
                "climmob.views.Api.projectAssessments.getAssessmentGroup",
            ),
            "return_value": [1, 2],
        }
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        self.body |= {
            "user_name": self.view.user.login,
            "project_id": self.get_mock("getTheProjectIdForOwner").return_value,
        }
        if self.get_mock("saveAssessmentOrder").called:
            self.get_mock("saveAssessmentOrder").assert_called_once_with(
                self.get_mock("getTheProjectIdForOwner").return_value,
                self.body["ass_cod"],
                json.loads(self.body["order"]),
                self.view.request,
            )
        if self.get_mock("getAssessmentQuestionsApi").called:
            self.get_mock("getAssessmentQuestionsApi").assert_called_once_with(
                self.body,
                self.view,
            )
        if self.get_mock("getAssessmentGroup").called:
            self.get_mock("getAssessmentGroup").assert_called_once_with(
                self.body,
                self.view,
            )

    def test_has_validators(self):
        self.assertEqual(
            self.view.validators, (ProjectExistsValidator, ProjectOpenValidator)
        )

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

    def test_post_success(self):
        response = self.view.post()
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The order of the groups and questions has been changed.",
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("getAssessmentGroup").assert_called_once()
        self.get_mock("getAssessmentQuestionsApi").assert_called_once()
        self.get_mock("saveAssessmentOrder").assert_called_once()

    def test_post_no_permission(self):
        self.get_mock("getAccessTypeForProject").return_value = 4

        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to order the questions.",
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()

    def test_post_assessment_not_exist(self):
        self.get_mock("assessmentExists").return_value = False

        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no data collection with that code.", response.body.decode()
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()

    def test_post_data_collection_started(self):
        self.get_mock("projectAsessmentStatus").return_value = False

        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot update data collection moments. You already started the data collection.",
            response.body.decode(),
        )
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()

    def test_post_invalid_order_json(self):
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
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()

    def test_post_questions_outside_groups(self):
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
        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()

    def test_post_groups_not_in_form(self):
        self.get_mock("getAssessmentGroup").return_value = [1]

        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are ordering groups that are not part of the form.",
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("getAssessmentGroup").assert_called_once()

    def test_post_questions_not_in_form(self):
        self.get_mock("getAssessmentQuestionsApi").return_value = [1, 2]

        response = self.view.post()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are ordering questions that are not part of the form.",
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("getAssessmentGroup").assert_called_once()
        self.get_mock("getAssessmentQuestionsApi").assert_called_once()

    def test_post_save_order_fails(self):
        self.get_mock("saveAssessmentOrder").return_value = (
            False,
            "Error saving order",
        )

        response = self.view.post()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            self.get_mock("saveAssessmentOrder").return_value[1],
            response.body.decode(),
        )

        self.get_mock("getTheProjectIdForOwner").assert_called_once()
        self.get_mock("getAccessTypeForProject").assert_called_once()
        self.get_mock("assessmentExists").assert_called_once()
        self.get_mock("projectAsessmentStatus").assert_called_once()
        self.get_mock("getAssessmentGroup").assert_called_once()
        self.get_mock("getAssessmentQuestionsApi").assert_called_once()
        self.get_mock("saveAssessmentOrder").assert_called_once()


if __name__ == "__main__":
    unittest.main()
