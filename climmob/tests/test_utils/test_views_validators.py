import json
import unittest
from unittest.mock import MagicMock, patch, call, ANY

from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPBadRequest,
    HTTPForbidden,
    HTTPFound,
)

from climmob.tests.test_utils.common import BaseTest
from climmob.views.classes import apiView, privateView
from climmob.views.validators import FieldValidation, TextField
from climmob.views.validators.BaseValidator import BaseValidator
from climmob.views.validators.ProjectExistsValidator import ProjectExistsValidator
from climmob.views.validators.assessment import AssessmentExistsValidator
from climmob.views.validators.field.FieldValidator import FieldValidator
from climmob.views.validators.project import (
    CanEditProjectValidator,
    HasAccessToProjectValidator,
)

from climmob.views.validators.question.QuestionMinMaxValidator import (
    QuestionMinMaxValidator,
)
from climmob.views.validators.question.QuestionUpdateMinMaxValidator import (
    QuestionUpdateMinMaxValidator,
)
from climmob.views.validators.session import NotLoggedInValidator


class TestBaseValidator(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()

        self.validator = BaseValidator(self.request)

    def test_run(self):
        with self.assertRaises(NotImplementedError):
            self.validator.run()


class TestProjectExistsValidator(unittest.TestCase):
    def test_init_for_api(self):
        view = MagicMock(apiView)
        view.request = MagicMock()
        view.request.translate = lambda s: s
        view.body = '{"user_owner": "test_owner", "project_cod": "test_cod"}'

        validator = ProjectExistsValidator(view)

        body = json.loads(view.body)

        self.assertEqual(validator.project_owner_username, body["user_owner"])
        self.assertEqual(validator.project_cod, body["project_cod"])

    def test_init_for_private(self):
        view = MagicMock(privateView)
        view.request = MagicMock()
        view.request.translate = lambda s: s
        view.request.user = "test_owner"
        view.request.project = "test_cod"

        validator = ProjectExistsValidator(view)

        self.assertEqual(validator.project_owner_username, view.request.user)
        self.assertEqual(validator.project_cod, view.request.project)

    def test_init_for_unknown_type(self):
        view = MagicMock()
        view.request = MagicMock()
        view.request.translate = lambda s: s

        with self.assertRaises(TypeError):
            validator = ProjectExistsValidator(view)


class TestProjectExistsValidatorRun(unittest.TestCase):
    @patch(
        "climmob.views.validators.ProjectExistsValidator"
        ".ProjectExistsValidator.extract"
    )
    def setUp(self, mock_extract):
        self.request = MagicMock()

        self.view = MagicMock()
        self.view.user = MagicMock()
        self.view.user.login = "test_user_login"
        self.view.request = self.request

        self.validator = ProjectExistsValidator(self.view)
        self.validator.project_owner_username = "test_user"
        self.validator.project_cod = "test_project"

    @patch(
        "climmob.views.validators.ProjectExistsValidator.projectExists",
        return_value=True,
    )
    def test_run_valid(self, mock_project_exists):
        result = self.validator.run()

        mock_project_exists.assert_called_once_with(
            self.validator.view.user.login,
            self.validator.project_owner_username,
            self.validator.project_cod,
            self.request,
        )

        self.assertEqual(result, None)

    @patch(
        "climmob.views.validators.ProjectExistsValidator.projectExists",
        return_value=False,
    )
    def test_run_invalid(self, mock_project_exists):
        with self.assertRaises(HTTPNotFound):
            self.validator.run()

        mock_project_exists.assert_called_once_with(
            self.validator.view.user.login,
            self.validator.project_owner_username,
            self.validator.project_cod,
            self.request,
        )


class TestCanEditProjectValidatorRun(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.view = MagicMock()
        self.view.request = self.request

        self.validator = CanEditProjectValidator(self.view)

    def test_run_valid(self):
        self.validator.run()

    def test_run_invalid(self):
        self.view.context.access_type = 4
        with self.assertRaises(HTTPForbidden):
            self.validator.run()


class TestHasAccessToProjectValidatorRun(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.view = MagicMock()
        self.view.request = self.request

        self.validator = HasAccessToProjectValidator(self.view)

    def test_run_valid(self):
        self.view.context.access_type = MagicMock(int)
        self.validator.run()

    def test_run_invalid(self):
        self.view.context.access_type = None
        with self.assertRaises(HTTPForbidden):
            self.validator.run()


class TestAssessmentExistsValidator(unittest.TestCase):
    def test_init_for_api(self):
        view = MagicMock(apiView)
        view.request = MagicMock()
        view.body = '{"ass_cod": "assessment_123"}'

        validator = AssessmentExistsValidator(view)

        body = json.loads(view.body)

        self.assertEqual(validator.ass_cod, body["ass_cod"])

    def test_init_for_private(self):
        view = MagicMock(privateView)
        view.request = MagicMock()
        view.request.translate = lambda s: s
        view.request.assessmentid = "assessment_123"

        validator = AssessmentExistsValidator(view)

        self.assertEqual(validator.ass_cod, view.request.assessmentid)

    def test_init_for_unknown_type(self):
        view = MagicMock()
        view.request = MagicMock()
        view.request.translate = lambda s: s

        with self.assertRaises(TypeError):
            AssessmentExistsValidator(view)


class TestAssessmentExistsValidatorRun(unittest.TestCase):
    @patch("climmob.views.validators.assessment.AssessmentExistsValidator.extract")
    def setUp(self, mock_extract):
        self.request = MagicMock()

        self.view = MagicMock()
        self.view.request = self.request

        self.validator = AssessmentExistsValidator(self.view)
        self.validator.ass_cod = "assessment_123"

    @patch(
        "climmob.views.validators.assessment.assessment_exists_validator.assessmentExists",
        return_value=True,
    )
    def test_run_valid(self, mock_assessment_exists):
        result = self.validator.run()

        mock_assessment_exists.assert_called_once_with(
            self.validator.view.context.active_project_id,
            self.validator.ass_cod,
            self.request,
        )

        self.assertEqual(result, None)

    @patch(
        "climmob.views.validators.assessment.assessment_exists_validator.assessmentExists",
        return_value=False,
    )
    def test_run_invalid(self, mock_assessment_exists):
        with self.assertRaises(HTTPNotFound):
            self.validator.run()

        mock_assessment_exists.assert_called_once_with(
            self.validator.view.context.active_project_id,
            self.validator.ass_cod,
            self.request,
        )


class TestQuestionMinMaxValidator(unittest.TestCase):
    def test_init_for_api(self):
        view = MagicMock(apiView)
        view.request = MagicMock()
        view.request.translate = lambda s: s
        view.body = '{"test_key": "test_value"}'
        validator = QuestionMinMaxValidator(view)

        self.assertEqual(validator.question, json.loads(validator.view.body))

    def test_init_for_private(self):
        view = MagicMock(privateView)
        view.request = MagicMock()
        view.request.translate = lambda s: s
        view.getPostDict.return_value = {"test_key": "test_value"}
        validator = QuestionMinMaxValidator(view)

        self.assertEqual(validator.question, validator.view.getPostDict.return_value)

    def test_init_for_unknown_type(self):
        view = MagicMock()
        view.request = MagicMock()
        view.request.translate = lambda s: s

        with self.assertRaises(TypeError):
            validator = QuestionMinMaxValidator(view)


class TestQuestionMinMaxValidatorRun(unittest.TestCase):
    @patch(
        "climmob.views.validators.question" ".QuestionMinMaxValidator.issubclass",
        return_value=True,
    )
    def setUp(self, mock_issubclass):
        self.request = MagicMock()
        self.request.translate = lambda s: s
        self.view = MagicMock()
        self.view.request = self.request

        self.validator = QuestionMinMaxValidator(self.view)

        self.mock_is_type_numerical.reset_mock()
        self.mock_float_parse.reset_mock()
        self.mock_extract_question.reset_mock()

        self.mock_is_type_numerical.return_value = True

    @classmethod
    def setUpClass(cls):
        cls.patcher_is_type_numerical = patch(
            "climmob.views.validators.question"
            ".QuestionMinMaxValidator.is_type_numerical"
        )

        cls.patcher_float_parse = patch(
            "climmob.views.validators.question.QuestionMinMaxValidator.QuestionMinMaxValidator.float_parse",
            side_effect=QuestionMinMaxValidator.float_parse,
            autospec=True,
        )

        cls.patcher_extract_question = patch(
            "climmob.views.validators.question"
            ".QuestionMinMaxValidator.QuestionMinMaxValidator"
            ".extract_question"
        )

        cls.mock_is_type_numerical = cls.patcher_is_type_numerical.start()
        cls.mock_float_parse = cls.patcher_float_parse.start()
        cls.mock_extract_question = cls.patcher_extract_question.start()

        cls.mock_is_type_numerical.return_value = True

    @classmethod
    def tearDownClass(cls):
        cls.patcher_is_type_numerical.stop()
        cls.patcher_float_parse.stop()
        cls.patcher_extract_question.stop()

    def test_run_non_numerical_question(self):
        self.mock_is_type_numerical.return_value = False
        self.validator.question["question_min"] = MagicMock()
        self.validator.question["question_max"] = MagicMock()
        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        self.assertEqual(
            str(context.exception),
            "Non-numerical questions may not have min nor max set",
        )

    def test_run_with_both_min_and_max(self):
        self.validator.question["question_min"] = 1
        self.validator.question["question_max"] = 2

        self.validator.run()

        expected_parameters = [
            (self.validator.question["question_min"], "question_min"),
            (self.validator.question["question_max"], "question_max"),
        ]

        self.mock_float_parse.assert_has_calls(
            [call(self.validator, value, name) for value, name in expected_parameters],
            any_order=False,
        )

    def test_run_max_less_than_min(self):
        self.validator.question["question_min"] = 2
        self.validator.question["question_max"] = 1

        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        self.assertEqual(
            str(context.exception), "The minimum must be less than the maximum"
        )

    def test_run_min_not_a_number(self):
        self.validator.question["question_min"] = "abc"
        self.validator.question["question_max"] = 1

        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        self.assertEqual(str(context.exception), "question_min must be a number")

    def test_run_max_not_a_number(self):
        self.validator.question["question_min"] = 1
        self.validator.question["question_max"] = "abc"

        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        self.assertEqual(str(context.exception), "question_max must be a number")

    def test_run_empty_turns_into_none(self):
        self.validator.question["question_min"] = ""
        self.validator.question["question_max"] = ""

        self.validator.run()

        self.assertIsNone(self.validator.min)
        self.assertIsNone(self.validator.max)

    def test_run_not_min_valid_max_is_success(self):
        self.validator.question["question_max"] = 5

        self.validator.run()

        self.mock_float_parse.assert_called_once_with(
            self.validator, self.validator.question["question_max"], "question_max"
        )

    def test_run_not_max_valid_min_is_success(self):
        self.validator.question["question_min"] = 5

        self.validator.run()

        self.mock_float_parse.assert_called_once_with(
            self.validator, self.validator.question["question_min"], "question_min"
        )

    def test_run_equals(self):
        self.validator.question["question_min"] = 5
        self.validator.question["question_max"] = 5

        expected_parameters = [
            (self.validator.question["question_min"], "question_min"),
            (self.validator.question["question_max"], "question_max"),
        ]

        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        self.mock_float_parse.assert_has_calls(
            [call(self.validator, value, name) for value, name in expected_parameters],
            any_order=False,
        )

        self.assertEqual(
            str(context.exception), "The minimum must be less than the maximum"
        )

    def test_run_both_zeros(self):
        self.validator.question["question_max"] = 0
        self.validator.question["question_min"] = 0

        expected_parameters = [
            (self.validator.question["question_min"], "question_min"),
            (self.validator.question["question_max"], "question_max"),
        ]

        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        self.mock_float_parse.assert_has_calls(
            [call(self.validator, value, name) for value, name in expected_parameters],
            any_order=False,
        )

        self.assertEqual(
            str(context.exception), "The minimum must be less than the maximum"
        )

    def test_run_min_zero_max_positive(self):
        self.validator.question["question_min"] = 0
        self.validator.question["question_max"] = 5

        self.validator.run()

        expected_parameters = [
            (self.validator.question["question_min"], "question_min"),
            (self.validator.question["question_max"], "question_max"),
        ]

        self.mock_float_parse.assert_has_calls(
            [call(self.validator, value, name) for value, name in expected_parameters],
            any_order=False,
        )

    def test_run_max_zero_min_positive(self):
        self.validator.question["question_min"] = 5
        self.validator.question["question_max"] = 0

        expected_parameters = [
            (self.validator.question["question_min"], "question_min"),
            (self.validator.question["question_max"], "question_max"),
        ]

        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        self.mock_float_parse.assert_has_calls(
            [call(self.validator, value, name) for value, name in expected_parameters],
            any_order=False,
        )

        self.assertEqual(
            str(context.exception), "The minimum must be less than the maximum"
        )


class TestQuestionUpdateMinMaxValidator(unittest.TestCase):
    @patch(
        "climmob.views.validators.question"
        ".QuestionUpdateMinMaxValidator.QuestionUpdateMinMaxValidator"
        ".get_question_data",
        return_value={"question_min": ANY, "question_max": ANY, "question_dtype": ANY},
    )
    @patch(
        "climmob.views.validators.question" ".QuestionMinMaxValidator.issubclass",
        return_value=True,
    )
    def setUp(self, mock_issubclass, mock_get_question_data):
        self.request = MagicMock()
        self.view = MagicMock()
        self.view.request = self.request
        self.validator = QuestionUpdateMinMaxValidator(self.view)

    @patch(
        "climmob.views.validators.question"
        ".QuestionUpdateMinMaxValidator.QuestionUpdateMinMaxValidator"
        ".get_question_data"
    )
    @patch(
        "climmob.views.validators.question" ".QuestionMinMaxValidator.issubclass",
        return_value=True,
    )
    def test_init(self, mock_issubclass, mock_get_question_data):
        mock_get_question_data.return_value = MagicMock()
        validator = QuestionUpdateMinMaxValidator(self.view)
        self.assertEqual(validator.old_question, mock_get_question_data.return_value)

    @patch(
        "climmob.views.validators.question"
        ".QuestionUpdateMinMaxValidator.getQuestionData"
    )
    def test_get_question_data(self, mock_get_question_from_db):
        question = MagicMock()
        mock_get_question_from_db.return_value = (question, ANY)

        result = self.validator.get_question_data()

        mock_get_question_from_db.assert_called_once_with(
            self.validator.view.user.login,
            self.validator.question.get("question_id"),
            self.validator.view.request,
        )
        self.assertEqual(result, question)

    @patch(
        "climmob.views.validators.question.QuestionMinMaxValidator"
        ".QuestionMinMaxValidator.set_min_max"
    )
    def test_set_min_max_from_old_question(self, mock_set_min_max):
        self.validator.set_min_max()

        mock_set_min_max.assert_called_once()

        self.assertEqual(
            self.validator.min, self.validator.old_question["question_min"]
        )
        self.assertEqual(
            self.validator.max, self.validator.old_question["question_max"]
        )

    @patch(
        "climmob.views.validators.question.QuestionMinMaxValidator"
        ".QuestionMinMaxValidator.set_question_dtype"
    )
    def test_set_question_dtype(self, mock_set_question_dtype):
        self.validator.set_question_dtype()

        mock_set_question_dtype.assert_called_once()

        self.assertEqual(
            self.validator.question_dtype, self.validator.old_question["question_dtype"]
        )


class TestFieldValidator(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request.translate = lambda x: x
        self.view = MagicMock()
        self.view.request = self.request
        self.view.valid_fields = None
        self.view.body = '{"test_key": "test_value"}'
        self.validator = FieldValidator(self.view)

    def test_init(self):
        for validation in FieldValidation:
            if validation != FieldValidation.SUCCESS:
                self.assertEqual(self.validator.invalid_fields[validation], [])

    def test_run_for_view_with_valid_fields_none(self):
        self.view.valid_fields = None
        self.validator.run()

    def test_run_for_view_with_empty_valid_fields(self):
        self.view.valid_fields = ()
        expected_msg = FieldValidation.UNALLOWED.value + "test_key"

        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        self.assertEqual(str(context.exception), expected_msg)

    def test_run_for_view_with_valid_fields_none_empty_body(self):
        self.view.valid_fields = None
        self.view.body = "{}"
        self.validator.run()

    def test_run_with_unallowed_fields(self):
        unallowed_key = MagicMock(str)
        self.view.body = '{"' + str(unallowed_key) + '": "test_value"}'

        self.view.valid_fields = (TextField("key_1"),)

        expected_msg = FieldValidation.UNALLOWED.value + str(unallowed_key)

        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        self.assertEqual(str(context.exception), expected_msg)

    def test_run_with_missing_fields(self):
        self.view.body = "{}"

        required_key = MagicMock(str)
        self.view.valid_fields = (TextField(str(required_key), required=True),)

        expected_msg = FieldValidation.MISSING.value + str(required_key)

        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        self.assertEqual(str(context.exception), expected_msg)

    def test_run_with_blank_fields(self):

        not_blank_key = MagicMock(str)
        self.view.body = '{"' + str(not_blank_key) + '": ""}'

        self.view.valid_fields = (TextField(str(not_blank_key), not_blank=True),)

        expected_msg = FieldValidation.BLANK.value + str(not_blank_key)

        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        self.assertEqual(str(context.exception), expected_msg)

    def test_run_blank_required(self):

        not_blank_key = MagicMock(str)
        required_key = MagicMock(str)
        self.view.body = '{"' + str(not_blank_key) + '": ""}'

        self.view.valid_fields = (
            TextField(str(not_blank_key), not_blank=True),
            TextField(str(required_key), required=True),
        )

        expected_msg = FieldValidation.MISSING.value + str(required_key)

        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        self.assertEqual(str(context.exception), expected_msg)

    def test_run_required_blank(self):

        required_key = MagicMock(str)
        not_blank_key = MagicMock(str)

        self.view.body = '{"' + str(not_blank_key) + '": ""}'

        self.view.valid_fields = (
            TextField(str(required_key), required=True),
            TextField(str(not_blank_key), not_blank=True),
        )

        expected_msg = FieldValidation.MISSING.value + str(required_key)

        with self.assertRaises(HTTPBadRequest) as context, patch.object(
            self.validator,
            "add_invalid_field",
            side_effect=self.validator.add_invalid_field,
        ) as mock_add_invalid_field:
            self.validator.run()

        self.assertEqual(str(context.exception), expected_msg)
        mock_add_invalid_field.assert_called_once()


class TestNotLoggedInValidator(BaseTest):
    def setUp(self):
        super().setUp()
        self.request = MagicMock()
        self.view = MagicMock()
        self.view.request = self.request
        self.view.get_policy = MagicMock()
        self.validator = NotLoggedInValidator(self.view)
        self.username = "test_user"

    @classmethod
    def setUpClass(cls):
        cls.patchers["getUserData"] = {
            "patch": patch(
                "climmob.views.validators.session.not_logged_in_validator.getUserData"
            )
        }
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.view.get_policy.called:
            self.view.get_policy.assert_called_once_with("main")
        if self.get_mock("getUserData").called:
            self.get_mock("getUserData").assert_called_once_with(
                self.username,
                self.view.request,
            )

    def test_is_user_logged_in_true(self):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = (
            "{'login': '" + self.username + "', 'group': 'mainApp'}"
        )
        self.view.get_policy.return_value = mock_policy

        with self.assertRaises(HTTPFound):
            self.validator.run()
        self.view.get_policy.assert_called_once()
        self.get_mock("getUserData").assert_called_once()

    def test_is_user_logged_in_no_user(self):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        self.view.get_policy.return_value = mock_policy

        self.validator.run()
        self.view.get_policy.assert_called_once()
        self.get_mock("getUserData").assert_not_called()

    def test_is_user_logged_in_no_invalid_user(self):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = (
            "{'login': '" + self.username + "', 'group': 'mainApp'}"
        )
        self.view.get_policy.return_value = mock_policy
        self.get_mock("getUserData").return_value = None

        self.validator.run()
        self.view.get_policy.assert_called_once()
        self.get_mock("getUserData").assert_called()

    def test_is_user_logged_in_no_invalid_group(self):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = (
            "{'login': '" + self.username + "', 'group': 'test_group'}"
        )
        self.view.get_policy.return_value = mock_policy

        self.validator.run()
        self.view.get_policy.assert_called_once()
        self.get_mock("getUserData").assert_not_called()
