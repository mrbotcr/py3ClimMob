import json
import unittest
from unittest.mock import MagicMock, patch, call, ANY

from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest

from climmob.views.classes import apiView, privateView
from climmob.views.validators.BaseValidator import BaseValidator
from climmob.views.validators.ProjectExistsValidator import ProjectExistsValidator
from climmob.views.validators.question.QuestionMinMaxValidator import (
    QuestionMinMaxValidator,
)
from climmob.views.validators.question.QuestionUpdateMinMaxValidator import (
    QuestionUpdateMinMaxValidator,
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
