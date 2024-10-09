import unittest
from unittest.mock import MagicMock, patch

from pyramid.httpexceptions import HTTPNotFound, HTTPFound

from climmob.views.extra_form import ExtraFormPostView


class TestExtraFormPostView(unittest.TestCase):
    def setUp(self):
        # Initial setup for the tests
        self.mock_request = MagicMock()
        self.mock_request.method = "POST"
        self.mock_request.route_url.return_value = "/dashboard"
        self.view = ExtraFormPostView(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"
        self.view.getPostDict = MagicMock(
            return_value={
                "csrf_token": "dummy_token",
                "field1": "value1",
                "field2": "value2",
            }
        )

    def tearDown(self):
        # Stop all patches after each test
        patch.stopall()

    @patch(
        "climmob.views.extra_form.getActiveForm",
        return_value=(True, {"form_id": "12345"}),
    )
    @patch("climmob.views.extra_form.addExtraFormAnswers", return_value=(True, ""))
    def test_process_view_post_with_active_form(
        self, mock_addExtraFormAnswers, mock_getActiveForm
    ):
        # Test case for when there is an active form

        # Call the method under test
        response = self.view.processView()

        # Check that returnRawViewResult is True
        self.assertTrue(self.view.returnRawViewResult)

        # Check that the response is a redirect to /dashboard
        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(response.location, "/dashboard")

        # Verify that getActiveForm was called correctly
        mock_getActiveForm.assert_called_once_with(self.mock_request, "test_user")

        # Expected data for addExtraFormAnswers
        expected_info1 = {
            "form_id": "12345",
            "user_name": "test_user",
            "answer_field": "field1",
            "answer_date": unittest.mock.ANY,
            "answer_data": "value1",
        }
        expected_info2 = {
            "form_id": "12345",
            "user_name": "test_user",
            "answer_field": "field2",
            "answer_date": unittest.mock.ANY,
            "answer_data": "value2",
        }

        # Verify that addExtraFormAnswers was called correctly for each field
        mock_addExtraFormAnswers.assert_any_call(expected_info1, self.mock_request)
        mock_addExtraFormAnswers.assert_any_call(expected_info2, self.mock_request)

    @patch("climmob.views.extra_form.getActiveForm", return_value=(False, None))
    def test_process_view_post_without_active_form(self, mock_getActiveForm):
        # Test case for when there is no active form

        # Verify that HTTPNotFound is raised
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

        # Verify that getActiveForm was called correctly
        mock_getActiveForm.assert_called_once_with(self.mock_request, "test_user")

    def test_process_view_get_request(self):
        # Test case for when the request method is GET

        # Change the request method to GET
        self.mock_request.method = "GET"

        # Verify that HTTPNotFound is raised
        with self.assertRaises(HTTPNotFound):
            self.view.processView()


if __name__ == "__main__":
    unittest.main()
