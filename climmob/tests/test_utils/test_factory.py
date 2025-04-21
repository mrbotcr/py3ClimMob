import unittest
from unittest.mock import MagicMock

from climmob.utility.factory import factory


class TestFactory(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request.matchdict = {"user": "test_user", "project": "test_project"}

    def test_factory(self):

        factory(self.request)

        self.assertEqual(self.request.user, self.request.matchdict["user"])
        self.assertEqual(self.request.project, self.request.matchdict["project"])
