import unittest
from unittest.mock import MagicMock

from pyramid.httpexceptions import HTTPForbidden

from climmob.utility.project import ProjectAdmin
from climmob.views.validators import *


class TestSectionOnlyForAdminValidator(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.view = MagicMock()
        self.request.context = self.view
        self.view.user = MagicMock()

        self.mock_translation = lambda x: x
        self.request.translate = self.mock_translation
        self.view._ = self.mock_translation

    def test_no_admin_redirect(self):
        self.view.user.admin = ProjectAdmin.NO.value
        validator = SectionOnlyForAdminValidator(self.request)
        validator._ = lambda x: x
        with self.assertRaises(HTTPForbidden) as context:
            validator.run()
        self.assertEqual(
            "The permissions you have in ClimMob do not allow you to access this section.",
            context.exception.detail,
        )

    def test_no_admin_redirect_noparam(self):
        self.view.user.admin = None
        validator = SectionOnlyForAdminValidator(self.request)
        validator._ = lambda x: x
        with self.assertRaises(HTTPForbidden) as context:
            validator.run()
        self.assertEqual(
            "The permissions you have in ClimMob do not allow you to access this section.",
            context.exception.detail,
        )


class TestSectionOnlyForAdminJsonValidator(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.view = MagicMock()
        self.request.context = self.view
        self.view.user = MagicMock()

        self.mock_translation = lambda x: x
        self.request.translate = self.mock_translation
        self.view._ = self.mock_translation

    def test_no_admin_redirect(self):
        self.view.user.admin = ProjectAdmin.NO.value
        validator = SectionOnlyForAdminJsonValidator(self.request)
        validator._ = lambda x: x
        result = validator.run()
        self.assertEqual(
            result["message"],
            "The permissions you have in ClimMob do not allow you to access this section.",
        )

    def test_no_admin_redirect_noparam(self):
        self.view.user.admin = None
        validator = SectionOnlyForAdminJsonValidator(self.request)
        validator._ = lambda x: x
        result = validator.run()
        self.assertEqual(
            result["message"],
            "The permissions you have in ClimMob do not allow you to access this section.",
        )
