from unittest.mock import patch, MagicMock, call

from climmob.processes import (
    get_project_assessment_info,
    clone_assessment,
    get_assessment_questions_unformatted,
    add_assessment_question,
    copy_assessment_questions,
    copy_assessment_sections,
)
from climmob.tests.test_utils.test_processes import DBProcessBaseTest


class TestAssessmentDBProcess(DBProcessBaseTest):
    @classmethod
    def setUpClass(cls):
        cls.patchers["mapFromSchema"] = {
            "patch": patch("climmob.processes.db.assessment.mapFromSchema"),
            "return_value": MagicMock(),
        }
        cls.patchers["mapToSchema"] = {
            "patch": patch("climmob.processes.db.assessment.mapToSchema"),
            "return_value": MagicMock(),
        }

        super().setUpClass()


class TestGetProjectAssessmentInfo(TestAssessmentDBProcess):
    def setUp(self):
        super().setUp()
        self.process = get_project_assessment_info

    def test_success(self):
        expected = self.get_mock("mapFromSchema").return_value
        project_id = 1
        assessment_id = 1

        result = self.process(project_id, assessment_id, self.request)

        self.assertEqual(result, expected)
        self.get_mock("mapFromSchema").assert_called_once_with(
            self.session.return_value
        )


class TestCloneAssessment(TestAssessmentDBProcess):
    def setUp(self):
        super().setUp()
        self.process = clone_assessment

        self.project_id = 1
        self.assessment_id = 1

        self.view = MagicMock(request=self.request)

    @classmethod
    def setUpClass(cls):
        cls.patchers["get_project_assessment_info"] = {
            "patch": patch(
                "climmob.processes.db.assessment.get_project_assessment_info"
            ),
            "return_value": {"key": "value"},
        }
        cls.patchers["add_project_assessment_clone"] = {
            "patch": patch(
                "climmob.processes.db.assessment.add_project_assessment_clone"
            ),
            "return_value": (True, MagicMock()),
        }
        cls.patchers["copy_assessment_sections"] = {
            "patch": patch("climmob.processes.db.assessment.copy_assessment_sections"),
            "return_value": True,
        }
        cls.patchers["copy_assessment_questions"] = {
            "patch": patch("climmob.processes.db.assessment.copy_assessment_questions"),
            "return_value": True,
        }

        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.get_mock("get_project_assessment_info").called:
            self.get_mock("get_project_assessment_info").assert_called_once_with(
                self.project_id, self.assessment_id, self.request
            )
        if self.get_mock("add_project_assessment_clone").called:
            self.get_mock("add_project_assessment_clone").assert_called_once_with(
                self.patchers["get_project_assessment_info"]["return_value"]
                | {"ass_status": 0, "ass_final": 0},
                self.request,
            )
        if self.get_mock("copy_assessment_sections").called:
            self.get_mock("copy_assessment_sections").assert_called_once_with(
                self.view,
                self.project_id,
                self.assessment_id,
                self.get_mock("add_project_assessment_clone").return_value[1],
            )
        if self.get_mock("copy_assessment_questions").called:
            self.get_mock("copy_assessment_questions").assert_called_once_with(
                self.view,
                self.project_id,
                self.assessment_id,
                self.get_mock("add_project_assessment_clone").return_value[1],
            )

    def test_success(self):
        result = self.process(self.view, self.project_id, self.assessment_id)

        self.assertTrue(result)

        self.get_mock("get_project_assessment_info").assert_called_once()
        self.get_mock("add_project_assessment_clone").assert_called_once()
        self.get_mock("copy_assessment_sections").assert_called_once()
        self.get_mock("copy_assessment_questions").assert_called_once()

    def test_assessment_not_added(self):
        self.get_mock("add_project_assessment_clone").return_value = (False, None)

        result = self.process(self.view, self.project_id, self.assessment_id)

        self.assertFalse(result)

        self.get_mock("get_project_assessment_info").assert_called_once()
        self.get_mock("add_project_assessment_clone").assert_called_once()

    def test_sections_not_cloned(self):
        self.get_mock("copy_assessment_sections").return_value = False

        result = self.process(self.view, self.project_id, self.assessment_id)

        self.assertFalse(result)

        self.get_mock("get_project_assessment_info").assert_called_once()
        self.get_mock("add_project_assessment_clone").assert_called_once()
        self.get_mock("copy_assessment_sections").assert_called_once()

    def test_questions_not_cloned(self):
        self.get_mock("copy_assessment_questions").return_value = False

        result = self.process(self.view, self.project_id, self.assessment_id)

        self.assertFalse(result)

        self.get_mock("get_project_assessment_info").assert_called_once()
        self.get_mock("add_project_assessment_clone").assert_called_once()
        self.get_mock("copy_assessment_sections").assert_called_once()
        self.get_mock("copy_assessment_questions").assert_called_once()


class TestGetAssessmentQuestionsUnformatted(TestAssessmentDBProcess):
    def setUp(self):
        super().setUp()
        self.process = get_assessment_questions_unformatted

    def test_success(self):
        expected = self.get_mock("mapFromSchema").return_value
        project_id = 1
        assessment_id = 1

        result = self.process(project_id, assessment_id, self.request)

        self.assertEqual(result, expected)
        self.get_mock("mapFromSchema").assert_called_once_with(
            self.session.return_value
        )


class TestAddAssessmentQuestion(TestAssessmentDBProcess):
    def setUp(self):
        super().setUp()
        self.process = add_assessment_question

    def test_success(self):
        question = MagicMock()

        result = self.process(question, self.request)

        self.assertEqual(result, (True, ""))
        self.get_mock("mapFromSchema").assert_called_once_with(
            self.session.return_value
        )

    def test_repeated(self):
        self.get_mock("mapFromSchema").return_value = [MagicMock()]

        question = MagicMock()

        result = self.process(question, self.request)

        self.assertEqual(result, (False, "repeated"))
        self.get_mock("mapFromSchema").assert_called_once_with(
            self.session.return_value
        )

    def test_adding_failure(self):
        self.session.get_mock().add.side_effect = Exception

        question = MagicMock()

        result = self.process(question, self.request)

        self.assertEqual(result[0], False)
        self.get_mock("mapFromSchema").assert_called_once_with(
            self.session.return_value
        )


class TestCopyAssessmentQuestions(TestAssessmentDBProcess):
    def setUp(self):
        super().setUp()
        self.process = copy_assessment_questions

        self.project_id = 1
        self.src_assessment_id = 1
        self.other_assessment_id = 2

        self.view = MagicMock(request=self.request)

    @classmethod
    def setUpClass(cls):
        cls.patchers["get_assessment_questions_unformatted"] = {
            "patch": patch(
                "climmob.processes.db.assessment.get_assessment_questions_unformatted"
            ),
            "return_value": [{"key1": "value1"}, {"key2": "value2"}],
        }
        cls.patchers["add_assessment_question"] = {
            "patch": patch("climmob.processes.db.assessment.add_assessment_question"),
            "return_value": (True, MagicMock()),
        }

        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.get_mock("get_assessment_questions_unformatted").called:
            self.get_mock(
                "get_assessment_questions_unformatted"
            ).assert_called_once_with(
                self.project_id, self.src_assessment_id, self.request
            )

    def test_success(self):
        questions = self.patchers["get_assessment_questions_unformatted"][
            "return_value"
        ]

        result = self.process(
            self.view, self.project_id, self.src_assessment_id, self.other_assessment_id
        )

        self.assertTrue(result)
        self.get_mock("get_assessment_questions_unformatted").assert_called_once()
        expected_parameters = [
            question
            | {
                "ass_cod": self.other_assessment_id,
                "section_assessment": self.other_assessment_id,
            }
            for question in questions
        ]
        self.get_mock("add_assessment_question").assert_has_calls(
            [call(value, self.request) for value in expected_parameters],
            any_order=False,
        )

    def test_question_not_copied(self):
        self.get_mock("add_assessment_question").return_value = (False, None)
        questions = self.patchers["get_assessment_questions_unformatted"][
            "return_value"
        ]

        result = self.process(
            self.view, self.project_id, self.src_assessment_id, self.other_assessment_id
        )

        self.assertFalse(result)

        self.get_mock("get_assessment_questions_unformatted").assert_called_once()

        self.get_mock("add_assessment_question").assert_called_once_with(
            questions[0]
            | {
                "ass_cod": self.other_assessment_id,
                "section_assessment": self.other_assessment_id,
            },
            self.request,
        )


class TestCopyAssessmentSections(TestAssessmentDBProcess):
    def setUp(self):
        super().setUp()
        self.process = copy_assessment_sections

        self.project_id = 1
        self.src_assessment_id = 1
        self.other_assessment_id = 2

        self.view = MagicMock(request=self.request)

    @classmethod
    def setUpClass(cls):
        cls.patchers["get_all_assessment_groups"] = {
            "patch": patch("climmob.processes.db.assessment.get_all_assessment_groups"),
            "return_value": [{"key1": "value1"}, {"key2": "value2"}],
        }
        cls.patchers["addAssessmentGroup"] = {
            "patch": patch("climmob.processes.db.assessment.addAssessmentGroup"),
            "return_value": (True, MagicMock()),
        }

        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.get_mock("get_all_assessment_groups").called:
            self.get_mock("get_all_assessment_groups").assert_called_once_with(
                {"project_id": self.project_id, "ass_cod": self.src_assessment_id},
                self.request,
            )

    def test_success(self):
        sections = self.patchers["get_all_assessment_groups"]["return_value"]

        result = self.process(
            self.view, self.project_id, self.src_assessment_id, self.other_assessment_id
        )

        self.assertTrue(result)
        self.get_mock("get_all_assessment_groups").assert_called_once()
        expected_parameters = [
            section
            | {
                "ass_cod": self.other_assessment_id,
            }
            for section in sections
        ]
        self.get_mock("addAssessmentGroup").assert_has_calls(
            [call(value, self.view) for value in expected_parameters],
            any_order=False,
        )

    def test_question_not_copied(self):
        self.get_mock("addAssessmentGroup").return_value = (False, None)
        sections = self.patchers["get_all_assessment_groups"]["return_value"]

        result = self.process(
            self.view, self.project_id, self.src_assessment_id, self.other_assessment_id
        )

        self.assertFalse(result)

        self.get_mock("get_all_assessment_groups").assert_called_once()

        self.get_mock("addAssessmentGroup").assert_called_once_with(
            sections[0]
            | {
                "ass_cod": self.other_assessment_id,
            },
            self.view,
        )
