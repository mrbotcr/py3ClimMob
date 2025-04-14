import unittest
from unittest.mock import MagicMock, patch

from pyramid.httpexceptions import HTTPNotFound

from climmob.views.validators.BaseValidator import BaseValidator
from climmob.views.validators.ProjectExistsValidator import ProjectExistsValidator


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
