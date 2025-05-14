import json
import unittest
from unittest.mock import MagicMock, patch, call

from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest

from climmob.views.classes import apiView, privateView
from climmob.views.validators.BaseValidator import BaseValidator
from climmob.views.validators.ProjectExistsValidator import ProjectExistsValidator
from climmob.views.validators.question.QuestionMinMaxValidator import (
    QuestionMinMaxValidator,
)


class TestBaseValidator(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()

        self.validator = BaseValidator(self.request)

    def test_run(self):
        with self.assertRaises(NotImplementedError):
            self.validator.run()


class TestProjectExistsValidator(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request.matchdict = {"user": "test_user", "project": "test_project"}

        self.view = MagicMock()
        self.view.user = MagicMock()
        self.view.user.login = "test_user_login"
        self.view.request = self.request

        self.validator = ProjectExistsValidator(self.view)

    @patch(
        "climmob.views.validators.ProjectExistsValidator.projectExists",
        return_value=True,
    )
    def test_run_valid(self, mock_project_exists):
        result = self.validator.run()

        mock_project_exists.assert_called_once_with(
            self.validator.view.user.login,
            self.request.matchdict["user"],
            self.request.matchdict["project"],
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
            self.request.matchdict["user"],
            self.request.matchdict["project"],
            self.request,
        )

class TestQuestionValidator(unittest.TestCase):

    def test_init_for_api(self):
        view = MagicMock(apiView)
        view.body = '{"test_key": "test_value"}'
        validator = QuestionMinMaxValidator(view)

        self.assertEqual(validator.question, json.loads(validator.view.body))

    def test_init_for_private(self):
        view = MagicMock(privateView)
        view.getPostDict.return_value = {"test_key": "test_value"}
        validator = QuestionMinMaxValidator(view)

        self.assertEqual(validator.question, validator.view.getPostDict.return_value)

class TestQuestionMinMaxValidator(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.view = MagicMock()
        self.view.request = self.request

        self.validator = QuestionMinMaxValidator(self.view)

    @patch(
        "climmob.views.validators.question"
        ".QuestionMinMaxValidator.is_type_numerical",
        return_value=False,
    )
    def test_run_non_numerical_question(self, mock_is_numerical):
        self.validator.question["question_min"] = MagicMock()
        self.validator.question["question_max"] = MagicMock()
        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        self.assertEqual(
            str(context.exception),
            "Non-numerical questions may not have min nor max set",
        )

    @patch(
        "climmob.views.validators.question"
        ".QuestionMinMaxValidator.is_type_numerical",
        return_value=True,
    )
    @patch(
        "climmob.views.validators.question.QuestionMinMaxValidator.float",
        side_effect=float,
    )
    def test_run_with_both_min_and_max(self, mock_float, mock_is_numerical):
        self.validator.question["question_min"] = 1
        self.validator.question["question_max"] = 2

        self.validator.run()

        expected_parameters = [
            self.validator.question["question_min"],
            self.validator.question["question_max"],
        ]

        mock_float.assert_has_calls(
            [call(param) for param in expected_parameters], any_order=False
        )

    @patch(
        "climmob.views.validators.question"
        ".QuestionMinMaxValidator.is_type_numerical",
        return_value=True,
    )
    def test_run_max_less_than_min(self, mock_is_numerical):
        self.validator.question["question_min"] = 2
        self.validator.question["question_max"] = 1

        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        self.assertEqual(
            str(context.exception), "The minimum must be less than the maximum"
        )

    @patch(
        "climmob.views.validators.question"
        ".QuestionMinMaxValidator.is_type_numerical",
        return_value=True,
    )
    def test_run_min_not_a_number(self, mock_is_numerical):
        self.validator.question["question_min"] = "abc"
        self.validator.question["question_max"] = 1

        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        self.assertEqual(str(context.exception), "The minimum must be a number")

    @patch(
        "climmob.views.validators.question"
        ".QuestionMinMaxValidator.is_type_numerical",
        return_value=True,
    )
    def test_run_max_not_a_number(self, mock_is_numerical):
        self.validator.question["question_min"] = 1
        self.validator.question["question_max"] = "abc"

        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        self.assertEqual(str(context.exception), "The maximum must be a number")

    @patch(
        "climmob.views.validators.question"
        ".QuestionMinMaxValidator.is_type_numerical",
        return_value=True,
    )
    def test_run_empty_turns_into_none(self, mock_is_numerical):
        self.validator.question["question_min"] = ""
        self.validator.question["question_max"] = ""

        self.validator.run()

        self.assertIsNone(self.validator.question["question_min"])
        self.assertIsNone(self.validator.question["question_max"])

    @patch(
        "climmob.views.validators.question"
        ".QuestionMinMaxValidator.is_type_numerical",
        return_value=True,
    )
    @patch(
        "climmob.views.validators.question.QuestionMinMaxValidator.float",
        side_effect=float,
    )
    def test_run_not_min_valid_max_is_success(self, mock_float, mock_is_numerical):
        self.validator.question["question_max"] = 5

        self.validator.run()

        mock_float.assert_called_once_with(self.validator.question["question_max"])

    @patch(
        "climmob.views.validators.question"
        ".QuestionMinMaxValidator.is_type_numerical",
        return_value=True,
    )
    @patch(
        "climmob.views.validators.question.QuestionMinMaxValidator.float",
        side_effect=float,
    )
    def test_run_not_max_valid_min_is_success(self, mock_float, mock_is_numerical):
        self.validator.question["question_min"] = 5

        self.validator.run()

        mock_float.assert_called_once_with(self.validator.question["question_min"])

    @patch(
        "climmob.views.validators.question"
        ".QuestionMinMaxValidator.is_type_numerical",
        return_value=True,
    )
    @patch(
        "climmob.views.validators.question.QuestionMinMaxValidator.float",
        side_effect=float,
    )
    def test_run_equals(self, mock_float, mock_is_numerical):
        self.validator.question["question_min"] = 5
        self.validator.question["question_max"] = 5

        expected_parameters = [
            self.validator.question["question_min"],
            self.validator.question["question_max"],
        ]

        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        mock_float.assert_has_calls(
            [call(param) for param in expected_parameters], any_order=False
        )

        self.assertEqual(
            str(context.exception), "The minimum must be less than the maximum"
        )

    @patch(
        "climmob.views.validators.question"
        ".QuestionMinMaxValidator.is_type_numerical",
        return_value=True,
    )
    @patch(
        "climmob.views.validators.question.QuestionMinMaxValidator.float",
        side_effect=float,
    )
    def test_run_both_zeros(self, mock_float, mock_is_numerical):
        self.validator.question["question_min"] = 0
        self.validator.question["question_max"] = 0

        expected_parameters = [
            self.validator.question["question_min"],
            self.validator.question["question_max"],
        ]

        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        mock_float.assert_has_calls(
            [call(param) for param in expected_parameters], any_order=False
        )

        self.assertEqual(
            str(context.exception), "The minimum must be less than the maximum"
        )

    @patch(
        "climmob.views.validators.question"
        ".QuestionMinMaxValidator.is_type_numerical",
        return_value=True,
    )
    @patch(
        "climmob.views.validators.question.QuestionMinMaxValidator.float",
        side_effect=float,
    )
    def test_run_min_zero_max_positive(self, mock_float, mock_is_numerical):
        self.validator.question["question_min"] = 0
        self.validator.question["question_max"] = 5

        self.validator.run()

        expected_parameters = [
            self.validator.question["question_min"],
            self.validator.question["question_max"],
        ]

        mock_float.assert_has_calls(
            [call(param) for param in expected_parameters], any_order=False
        )

    @patch(
        "climmob.views.validators.question"
        ".QuestionMinMaxValidator.is_type_numerical",
        return_value=True,
    )
    @patch(
        "climmob.views.validators.question.QuestionMinMaxValidator.float",
        side_effect=float,
    )
    def test_run_max_zero_min_positive(self, mock_float, mock_is_numerical):
        self.validator.question["question_min"] = 5
        self.validator.question["question_max"] = 0

        expected_parameters = [
            self.validator.question["question_min"],
            self.validator.question["question_max"],
        ]

        with self.assertRaises(HTTPBadRequest) as context:
            self.validator.run()

        mock_float.assert_has_calls(
            [call(param) for param in expected_parameters], any_order=False
        )

        self.assertEqual(
            str(context.exception), "The minimum must be less than the maximum"
        )
