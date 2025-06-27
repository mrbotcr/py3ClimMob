from unittest.mock import MagicMock, patch

from climmob.tests.test_utils.common import ViewBaseTest
from climmob.views.assessment import CloneAssessmentView


class AssessmentPrivateViewBaseTest(ViewBaseTest):
    @classmethod
    def setUpClass(cls):
        cls.patchers["HTTPFound"] = {
            "patch": patch(
                "climmob.views.assessment.HTTPFound",
            ),
            "return_value": MagicMock(),
        }
        super().setUpClass()


class TestCloneAssessmentView(AssessmentPrivateViewBaseTest):
    view_class = CloneAssessmentView

    def setUp(self):
        super().setUp()
        self.request.assessmentid = MagicMock(str)

    @classmethod
    def setUpClass(cls):
        cls.patchers["clone_assessment"] = {
            "patch": patch(
                "climmob.views.assessment.clone_assessment",
            ),
            "return_value": True,
        }
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.get_mock("clone_assessment").called:
            self.get_mock("clone_assessment").assert_called_once_with(
                self.view,
                self.view.context.active_project_id,
                self.request.assessmentid,
            )

    def test_post_success(self):
        result = self.view.post()

        self.assertEqual(result, self.get_mock("HTTPFound").return_value)

        self.get_mock("HTTPFound").assert_called_once_with(
            location=self.request.route_url.return_value
        )

        self.request.route_url.assert_called_once_with(
            "assessment", user=self.view.request.user, project=self.view.request.project
        )

        self.get_mock("clone_assessment").assert_called_once()
        self.request.session.flash.called_once_with(
            "The assessment was successfully cloned"
        )

    def test_post_failure(self):
        self.get_mock("clone_assessment").return_value = False

        result = self.view.post()

        self.assertEqual(result, self.get_mock("HTTPFound").return_value)

        self.get_mock("clone_assessment").assert_called_once()
        self.request.session.flash.called_once_with(
            "Error. The assessment could not be cloned"
        )
