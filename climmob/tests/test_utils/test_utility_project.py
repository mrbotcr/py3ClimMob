import unittest
from climmob.utility.project import *


class TestProject(unittest.TestCase):
    def test_project_access_type_get_dict(self):
        expected = {"Owner": 1, "Admin": 2, "Editor": 3, "Member": 4}
        self.assertEqual(project_access_type_get_dict(), expected)

    def test_project_admin_get_dict(self):
        expected = {"Yes": 1, "No": 0}
        self.assertEqual(project_admin_get_dict(), expected)

    def test_project_climmob_analytics_get_dict(self):
        expected = {"Verify": 2, "Yes": 1, "No": 0}
        self.assertEqual(project_climmob_analytics_get_dict(), expected)

    def test_project_active_get_dict(self):
        expected = {"Yes": 1, "No": 0}
        self.assertEqual(project_active_get_dict(), expected)

    def test_project_checked_get_dict(self):
        expected = {"Yes": 1, "No": 0}
        self.assertEqual(project_checked_get_dict(), expected)
