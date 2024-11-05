import json
import unittest
from unittest.mock import patch, MagicMock

from climmob.views.Api.dashboard import readProjectDetails_view


class TestReadProjectDetailsView(unittest.TestCase):
    def setUp(self):
        self.view = readProjectDetails_view(MagicMock())
        self.view.request.method = "GET"
        self.view.request.body = json.dumps({"project_cod": "test_project"})
        self.view.user = MagicMock(login="test_user")
        self.view.body = json.dumps({"project_cod": "test_project"})

    def mock_translation(self, message):
        return message

    @patch("climmob.views.Api.dashboard.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.dashboard.getProjectData",
        return_value={"name": "Test Project"},
    )
    @patch("climmob.views.Api.dashboard.getProjectProgress", return_value=(50, 25))
    def test_process_view_success(
        self, mock_getProjectProgress, mock_getProjectData, mock_projectExists
    ):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertEqual(response_data["project"]["name"], "Test Project")
        self.assertEqual(response_data["progress"], 50)
        self.assertEqual(response_data["pcompleted"], 25)

    @patch("climmob.views.Api.dashboard.projectExists", return_value=False)
    def test_process_view_project_not_exists(self, mock_projectExists):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no a project with that code.", response.body.decode())

    def test_process_view_invalid_json(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.body = '{"wrong_key": "value"}'
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON", response.body.decode())

    def test_process_view_invalid_body(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.body = None
        self.view.body = None

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )

    def test_process_view_post_method(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.method = "POST"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())


if __name__ == "__main__":
    unittest.main()
