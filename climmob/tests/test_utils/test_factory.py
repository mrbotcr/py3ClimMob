import unittest
from unittest.mock import MagicMock

from climmob.utility.factory import factory


class TestFactory(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request.matchdict = {"user": "test_user", "project": "test_project"}
        self.request.user = None
        self.request.project = None

    def test_factory(self):

        factory(self.request)

        self.assertEqual(self.request.user, self.request.matchdict["user"])
        self.assertEqual(self.request.project, self.request.matchdict["project"])

    def test_factory_attribute_already_used(self):
        self.request.matchdict["method"] = "test_method"

        self.request.method = "GET"

        with self.assertRaises(AttributeError) as context:
            factory(self.request)

        self.assertEqual(self.request.method, "GET")

        self.assertEqual(
            str(context.exception), "request already has attribute 'method'"
        )
